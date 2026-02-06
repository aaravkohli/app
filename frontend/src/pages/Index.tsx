import { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import PromptInput from "@/components/PromptInput";
import FileUploader from "@/components/FileUploader";
import RiskMeter, { RiskLevel } from "@/components/RiskMeter";
import RiskBreakdown from "@/components/RiskBreakdown";
import ResultCard, { ResultStatus, ThreatType } from "@/components/ResultCard";
import ExamplePrompts from "@/components/ExamplePrompts";
import SecurityBadge from "@/components/SecurityBadge";
import SecurityConfidence from "@/components/SecurityConfidence";
import VigilScannerResult from "@/components/VigilScannerResult";
import { apiService } from "@/lib/apiService.ts";
import { Shield, ArrowRight } from "lucide-react";

const detectThreatType = (prompt: string): ThreatType => {
  const lowerPrompt = prompt.toLowerCase();

  if (/ignore.*instructions|disregard.*instructions|override.*instructions/i.test(lowerPrompt)) return "instruction-override";
  if (/reveal.*prompt|show.*instructions|display.*system/i.test(lowerPrompt)) return "prompt-extraction";
  if (/act as|pretend to be|you are now|role.*play/i.test(lowerPrompt)) return "role-hijacking";
  if (/jailbreak|bypass.*security|bypass.*safety|developer mode/i.test(lowerPrompt)) return "jailbreak-attempt";

  return "general-injection";
};

interface AnalysisResult {
  riskLevel: RiskLevel;
  riskScore: number;
  mlRisk: number;
  lexicalRisk: number;
  benignOffset: number;
  status: ResultStatus;
  response?: string;
  blockReason?: string;
  suggestedRewrite?: string;
  sanitizedPrompt?: {
    text: string;
    notes: string;
    timeMs?: number;
    issuesAddressed?: string[];
    fallback?: boolean;
  };
  threatType?: ThreatType;
  analysisTime?: number;
  phase2Data?: any;
  combinedAnalysis?: any;
}

const Index = () => {
  const [prompt, setPrompt] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[] | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setPrompt("");
        setResult(null);
        setShowAnalysis(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const analyzePrompt = useCallback(async (enablePhase2 = false) => {
    if (!prompt.trim() && !selectedFiles?.length) return;

    const startTime = performance.now();
    setIsAnalyzing(true);
    setShowAnalysis(true);
    setResult(null);

    try {
      let apiResult: any;

      if (selectedFiles?.length) {
        apiResult = await apiService.analyzeFile(selectedFiles, prompt);
        setSelectedFiles(null);
      } else {
        apiResult = await apiService.analyzePrompt(prompt, enablePhase2);
      }

      const analysisTime = Math.round(performance.now() - startTime);

      const normalized = apiResult.analysis ? apiResult : {
        status: (apiResult.risk_score ?? 0) > 0.6 ? "blocked" : "approved",
        response: apiResult.response,
        analysis: {
          risk: apiResult.risk_score ?? 0,
          ml_score: apiResult.ml_score ?? 0,
          lexical_risk: apiResult.lexical_risk ?? 0,
          benign_offset: apiResult.benign_offset ?? 0,
        },
        combinedAnalysis: apiResult.combined_analysis,
        vigil_analysis: apiResult.vigil_analysis,
      };

      const riskLevel =
        normalized.analysis.risk > 0.6 ? "high" :
        normalized.analysis.risk > 0.3 ? "medium" : "low";

      setResult({
        riskLevel,
        riskScore: Math.round(normalized.analysis.risk * 100),
        mlRisk: Math.round((normalized.analysis.ml_score ?? 0) * 100),
        lexicalRisk: Math.round((normalized.analysis.lexical_risk ?? 0) * 100),
        benignOffset: Math.round((normalized.analysis.benign_offset ?? 0) * 100),
        status: normalized.status,
        response: normalized.response,
        blockReason: normalized.blockReason,
        sanitizedPrompt: normalized.sanitizedPrompt, // NEW: Include sanitized prompt
        threatType: prompt.trim() ? detectThreatType(prompt) : null,
        analysisTime,
        phase2Data: normalized,
        combinedAnalysis: normalized.combinedAnalysis,
      });

    } catch (err: any) {
      console.error("Analysis error:", err);
      setResult({
        riskLevel: "high",
        riskScore: 0,
        mlRisk: 0,
        lexicalRisk: 0,
        benignOffset: 0,
        status: "blocked",
        blockReason: `Connection error: ${err.message || "Unable to reach the API server. Please ensure the backend is running on port 5000."}`
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [prompt, selectedFiles]);
  
  // Handler for using sanitized prompt suggestion
  const handleUseSuggestion = useCallback((suggestion: string) => {
    setPrompt(suggestion);
    setResult(null);
    setShowAnalysis(false);
  }, []);

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <Header />

      <main className="container max-w-6xl mx-auto px-4 py-8">
        <HeroSection />
        <SecurityBadge />

        <div className="grid lg:grid-cols-5 gap-6">

          <div className="lg:col-span-3 space-y-6">

            <PromptInput
              value={prompt}
              onChange={setPrompt}
              onSubmit={analyzePrompt}
              isAnalyzing={isAnalyzing}
              canSubmit={!!selectedFiles?.length}
            />

            <FileUploader
              onFilesSelected={(f) =>
                setSelectedFiles((prev) => (prev ? [...prev, ...f] : [...f]))
              }
              autoAnalyze={false}
            />

            <ExamplePrompts onSelect={setPrompt} disabled={isAnalyzing} />

            <AnimatePresence mode="wait">
              {result?.status && (
                <ResultCard {...result} onUseSuggestion={handleUseSuggestion} />
              )}
            </AnimatePresence>

          </div>

          <div className="lg:col-span-2 space-y-6">

            {(showAnalysis || result) && (
              <>
                <RiskMeter
                  riskLevel={result?.riskLevel || "analyzing"}
                  riskScore={result?.riskScore || 0}
                  isAnalyzing={isAnalyzing}
                />

                {result && (
                  <SecurityConfidence
                    mlRisk={result.mlRisk}
                    lexicalRisk={result.lexicalRisk}
                    benignOffset={result.benignOffset}
                    status={result.status}
                  />
                )}

                <RiskBreakdown
                  mlRisk={result?.mlRisk || 0}
                  lexicalRisk={result?.lexicalRisk || 0}
                  benignOffset={result?.benignOffset || 0}
                  isAnalyzing={isAnalyzing}
                />

                {result?.phase2Data?.vigil_analysis && (
                  <VigilScannerResult
                    scanners={Object.entries(result.phase2Data.vigil_analysis.scanners || {}).map(([name,data]:any)=>({
                      name,
                      confidence: data?.confidence ?? data?.score ?? 0,
                      detected: (data?.confidence ?? data?.score ?? 0) > 0.5
                    }))}
                    aggregatedRisk={result.phase2Data.vigil_analysis.aggregated_risk ?? 0}
                    isAnalyzing={isAnalyzing}
                  />
                )}

              </>
            )}

          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;