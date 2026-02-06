import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  File as FileIcon,
  Image,
  Video,
  Code,
  Folder,
  X,
  AlertCircle,
  CheckCircle,
  Loader,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { apiService, AnalysisResponse } from "@/lib/apiService.ts";

interface FileUploaderProps {
  onAnalysisComplete?: (result: AnalysisResponse) => void;
  onError?: (error: string) => void;
  autoAnalyze?: boolean;
  onFilesSelected?: (files: File[]) => void;
}

interface UploadedFile {
  id: string;
  file: File;
  type: "image" | "video" | "code" | "document" | "archive" | "other";
  status: "pending" | "uploading" | "analyzing" | "complete" | "error";
  result?: AnalysisResponse;
  error?: string;
}

const FileUploader = ({ onAnalysisComplete, onError, autoAnalyze = true, onFilesSelected }: FileUploaderProps) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const resetFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const getFileType = (file: File): UploadedFile["type"] => {
    const ext = file.name.split(".").pop()?.toLowerCase() || "";

    if (["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"].includes(ext)) {
      return "image";
    }
    if (["mp4", "avi", "mov", "mkv", "flv", "wmv", "webm"].includes(ext)) {
      return "video";
    }
    if (["py", "js", "ts", "java", "cpp", "c", "cs", "go", "rs", "php", "rb", "sh"].includes(ext)) {
      return "code";
    }
    if (["zip", "rar", "7z", "tar", "gz", "bz2"].includes(ext)) {
      return "archive";
    }
    if (["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv"].includes(ext)) {
      return "document";
    }

    return "other";
  };

  const getFileIcon = (type: UploadedFile["type"]) => {
    switch (type) {
      case "image":
        return <Image className="w-4 h-4" />;
      case "video":
        return <Video className="w-4 h-4" />;
      case "code":
        return <Code className="w-4 h-4" />;
      case "archive":
        return <Folder className="w-4 h-4" />;
      default:
        return <FileIcon className="w-4 h-4" />;
    }
  };

  const analyzeSingleFile = async (uploadedFile: UploadedFile) => {
    setFiles((prev) => prev.map((f) => (f.id === uploadedFile.id ? { ...f, status: "uploading" } : f)));

    try {
      setFiles((prev) => prev.map((f) => (f.id === uploadedFile.id ? { ...f, status: "analyzing" } : f)));

      let result: AnalysisResponse;

      switch (uploadedFile.type) {
        case "image":
          result = await apiService.analyzeImage(uploadedFile.file);
          break;
        case "video":
          result = await apiService.analyzeVideo(uploadedFile.file);
          break;
        case "code":
          result = await apiService.analyzeCode(uploadedFile.file);
          break;
        default:
          result = await apiService.analyzeFile(uploadedFile.file);
      }

      setFiles((prev) =>
        prev.map((f) => (f.id === uploadedFile.id ? { ...f, status: "complete", result } : f))
      );

      onAnalysisComplete?.(result);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Analysis failed";
      setFiles((prev) => prev.map((f) => (f.id === uploadedFile.id ? { ...f, status: "error", error: errorMsg } : f)));
      onError?.(errorMsg);
    }
  };

  const handleFiles = (fileList: FileList | null) => {
    if (!fileList) return;

    const fileArray = Array.from(fileList);

    // If parent wants the selected files for combined submit, notify and skip auto-analysis
    if (!autoAnalyze) {
      onFilesSelected?.(fileArray);

      // reflect selection in UI without starting analysis
      const newFiles: UploadedFile[] = fileArray.map((file) => ({
        id: `${file.name}-${Date.now()}`,
        file,
        type: getFileType(file),
        status: "pending",
      }));

      setFiles((prev) => [...prev, ...newFiles]);
      resetFileInput();
      return;
    }

    const newFiles: UploadedFile[] = fileArray.map((file) => ({
      id: `${file.name}-${Date.now()}`,
      file,
      type: getFileType(file),
      status: "pending",
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    // Auto-analyze files
    newFiles.forEach((f) => analyzeSingleFile(f));
    resetFileInput();
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    if (e.currentTarget === e.target) {
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
    resetFileInput();
  };

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case "critical":
        return "text-red-600 bg-red-50";
      case "high":
        return "text-orange-600 bg-orange-50";
      case "medium":
        return "text-yellow-600 bg-yellow-50";
      case "low":
        return "text-green-600 bg-green-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const pendingCount = files.filter((f) => f.status === "pending").length;
  const uploadingCount = files.filter((f) => f.status === "uploading").length;
  const analyzingCount = files.filter((f) => f.status === "analyzing").length;
  const completeCount = files.filter((f) => f.status === "complete").length;
  const errorCount = files.filter((f) => f.status === "error").length;

  return (
    <div className="w-full space-y-4">
      {/* Drag and Drop Area */}
      <motion.div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center
          transition-all duration-200 cursor-pointer
          ${
            isDragging
              ? "border-primary bg-primary/5 scale-105"
              : "border-border hover:border-primary/50"
          }
        `}
        whileHover={{ scale: 1.02 }}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
        />

        <div className="flex flex-col items-center gap-3">
          <Upload className="w-10 h-10 text-muted-foreground" />
          <div>
            <p className="font-medium text-foreground">
              Drag and drop files here or click to browse
            </p>
            <p className="text-sm text-muted-foreground">
              Supports: Images, Videos, Code, Documents, Archives
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
          >
            Select Files
          </Button>
        </div>
      </motion.div>

      {/* Files List */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-2"
          >
            <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
              <span>
                {uploadingCount + analyzingCount > 0
                  ? `Processing ${uploadingCount + analyzingCount} file(s)...`
                  : pendingCount > 0
                  ? `Ready to analyze ${pendingCount} file(s)`
                  : `Completed ${completeCount} file(s)${errorCount ? `, ${errorCount} error(s)` : ""}`}
              </span>
              <span>
                {files.length} total
              </span>
            </div>
            {files.map((uploadedFile) => (
              <motion.div
                key={uploadedFile.id}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center gap-3 p-3 rounded-lg border border-border bg-card"
              >
                {/* File Icon */}
                <div className="flex-shrink-0">
                  {uploadedFile.status === "uploading" ||
                  uploadedFile.status === "analyzing" ? (
                    <Loader className="w-5 h-5 animate-spin text-primary" />
                  ) : uploadedFile.status === "complete" ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : uploadedFile.status === "error" ? (
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  ) : (
                    getFileIcon(uploadedFile.type)
                  )}
                </div>

                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium truncate">
                      {uploadedFile.file.name}
                    </p>
                    <span className="text-xs text-muted-foreground">
                      {(uploadedFile.file.size / 1024).toFixed(2)} KB
                    </span>
                  </div>

                  {/* Status or Risk Level */}
                  {uploadedFile.status === "uploading" && (
                    <p className="text-xs text-muted-foreground">Uploading...</p>
                  )}
                  {uploadedFile.status === "analyzing" && (
                    <p className="text-xs text-muted-foreground">Analyzing...</p>
                  )}
                  {uploadedFile.status === "complete" && uploadedFile.result && (
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-medium ${getRiskColor(uploadedFile.result.risk_level)}`}>
                        {uploadedFile.result.risk_level.toUpperCase()}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        Risk: {Math.round(uploadedFile.result.risk_score * 100)}%
                      </span>
                      {uploadedFile.result.threats.length > 0 && (
                        <span className="text-xs text-orange-600">
                          {uploadedFile.result.threats.length} threat(s)
                        </span>
                      )}
                    </div>
                  )}
                  {uploadedFile.status === "error" && (
                    <p className="text-xs text-red-600">{uploadedFile.error}</p>
                  )}
                </div>

                {/* Remove Button */}
                <button
                  onClick={() => removeFile(uploadedFile.id)}
                  className="flex-shrink-0 p-1 hover:bg-muted rounded transition-colors"
                >
                  <X className="w-4 h-4 text-muted-foreground hover:text-foreground" />
                </button>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Detailed Results */}
      {files.some((f) => f.status === "complete" && f.result?.threats.length) && (
        <Alert className="border-orange-200 bg-orange-50">
          <AlertCircle className="h-4 w-4 text-orange-600" />
          <AlertDescription className="text-orange-900">
            <strong>Threats Detected:</strong>
            {files
              .filter((f) => f.result?.threats.length)
              .map((f) => (
                <div key={f.id} className="mt-2">
                  <p className="font-medium text-sm">{f.file.name}:</p>
                  <ul className="text-xs mt-1 space-y-1">
                    {f.result?.threats.slice(0, 3).map((threat, idx) => (
                      <li key={idx} className="ml-4">
                        • {threat.type}: {threat.description}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default FileUploader;
