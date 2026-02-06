import { motion } from "framer-motion";
import { Shield, AlertTriangle, CheckCircle, Zap } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface VigilScanner {
  name: string;
  confidence: number;
  detected: boolean;
}

interface VigilScannerResultProps {
  scanners: VigilScanner[];
  aggregatedRisk: number;
  isAnalyzing?: boolean;
}

const scannerDescriptions: Record<string, { short: string; long: string }> = {
  similarity: {
    short: "Semantic similarity to known attacks",
    long: "Uses transformer embeddings to detect prompts similar to known injection attacks in the training database.",
  },
  yara: {
    short: "Pattern matching against known signatures",
    long: "Scans for known injection patterns, keywords, and signatures from 10,000+ security rules.",
  },
  transformer: {
    short: "Neural network-based detection",
    long: "Transformer model trained on injection datasets to detect adversarial patterns and attack structures.",
  },
  sentiment: {
    short: "Anomalous tone or sentiment",
    long: "Analyzes emotional tone and sentiment; unusual patterns can indicate prompt injection attempts.",
  },
  relevance: {
    short: "Prompt relevance and coherence",
    long: "Scores how relevant and coherent the prompt is relative to typical user requests.",
  },
  canary: {
    short: "Canary token detection",
    long: "Detects embedded canary tokens used to identify when prompt injection is successful.",
  },
};

const VigilScannerResult = ({
  scanners,
  aggregatedRisk,
  isAnalyzing = false,
}: VigilScannerResultProps) => {
  const detectionCount = scanners.filter((s) => s.detected).length;
  const riskLevel =
    aggregatedRisk > 0.7
      ? "critical"
      : aggregatedRisk > 0.5
        ? "high"
        : aggregatedRisk > 0.3
          ? "medium"
          : "low";

  const riskColors = {
    critical: "from-red-500 to-red-600",
    high: "from-orange-500 to-orange-600",
    medium: "from-yellow-500 to-yellow-600",
    low: "from-green-500 to-green-600",
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.05 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 },
  };

  const getScannerIcon = (detected: boolean) => {
    return detected ? (
      <AlertTriangle className="w-4 h-4 text-red-500" />
    ) : (
      <CheckCircle className="w-4 h-4 text-green-500" />
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="rounded-lg border border-border/50 bg-card/50 p-6 backdrop-blur-sm"
    >
      {/* Header with Vigil branding */}
      <div className="flex items-center gap-3 mb-6">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30">
          <Zap className="w-4 h-4 text-purple-500" />
          <span className="text-sm font-semibold text-purple-600 dark:text-purple-400">
            Vigil-LLM Analysis
          </span>
        </div>
        <span className="text-xs text-muted-foreground">6-Scanner Detection</span>
      </div>

      {/* Aggregated Risk Score */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-foreground">
            Vigil Aggregated Risk
          </span>
          <span className={`text-2xl font-bold bg-gradient-to-r ${riskColors[riskLevel]} bg-clip-text text-transparent`}>
            {(aggregatedRisk * 100).toFixed(0)}%
          </span>
        </div>
        <div className="w-full bg-secondary/50 rounded-full h-2 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${aggregatedRisk * 100}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className={`h-full bg-gradient-to-r ${riskColors[riskLevel]}`}
          />
        </div>
        <div className="flex justify-between mt-2">
          <span className="text-xs text-muted-foreground">Safe</span>
          <span className="text-xs text-muted-foreground">Dangerous</span>
        </div>
      </div>

      {/* Detection Summary */}
      <div className="mb-6 p-3 bg-secondary/30 rounded-lg border border-border/30">
        <div className="flex items-center gap-2 text-sm">
          <Shield className="w-4 h-4 text-primary" />
          <span className="font-medium">
            {detectionCount} of {scanners.length} scanners detected threats
          </span>
        </div>
      </div>

      {/* Scanners Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 gap-3"
      >
        {scanners.map((scanner, index) => (
          <motion.div
            key={scanner.name}
            variants={itemVariants}
            className={`p-3 rounded-lg border transition-all ${
              scanner.detected
                ? "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800"
                : "bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="flex items-center gap-2 cursor-help">
                      {getScannerIcon(scanner.detected)}
                      <span className="text-sm font-medium text-foreground capitalize truncate">
                        {scanner.name.replace("-", " ")}
                      </span>
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-xs">
                    <p className="text-xs">
                      {
                        scannerDescriptions[scanner.name]?.long ||
                        `${scanner.name} detection scanner`
                      }
                    </p>
                  </TooltipContent>
                </Tooltip>

                <div className="mt-1 flex items-center gap-2">
                  <div className="flex-1 bg-secondary/40 rounded h-1.5 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${scanner.confidence * 100}%` }}
                      transition={{ duration: 0.6, delay: 0.1 + index * 0.05 }}
                      className={`h-full ${
                        scanner.detected ? "bg-red-500" : "bg-green-500"
                      }`}
                    />
                  </div>
                  <span className="text-xs font-semibold text-muted-foreground whitespace-nowrap">
                    {(scanner.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Loading state */}
      {isAnalyzing && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950/30 rounded-lg border border-blue-200 dark:border-blue-800 flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" />
            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-100" />
            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce delay-200" />
          </div>
          <span className="text-xs text-blue-600 dark:text-blue-400 ml-2">
            Vigil scanners analyzing...
          </span>
        </div>
      )}

      {/* Footer note */}
      <div className="mt-6 pt-4 border-t border-border/30">
        <p className="text-xs text-muted-foreground">
          <span className="font-semibold">Vigil-LLM</span> uses 6 independent
          detection engines to identify prompt injection attempts. Combined with
          PromptGuard's internal analysis, results are weighted at{" "}
          <span className="font-semibold">70% internal + 30% Vigil</span> for
          final risk decisions.
        </p>
      </div>
    </motion.div>
  );
};

export default VigilScannerResult;
