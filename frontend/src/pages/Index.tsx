import { useState, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import PromptInput from "@/components/PromptInput";
import RiskMeter, { RiskLevel } from "@/components/RiskMeter";
import RiskBreakdown from "@/components/RiskBreakdown";
import ResultCard, { ResultStatus, ThreatType } from "@/components/ResultCard";
import ExamplePrompts from "@/components/ExamplePrompts";
import SecurityBadge from "@/components/SecurityBadge";
import SecurityConfidence from "@/components/SecurityConfidence";
import { apiService, type AnalysisResponse } from "@/lib/apiService";
import { Shield, ArrowRight, AlertCircle } from "lucide-react";

// Threat type detection
const detectThreatType = (prompt: string): ThreatType => {
  const lowerPrompt = prompt.toLowerCase();
  
  if (/ignore.*instructions|disregard.*instructions|override.*instructions/i.test(lowerPrompt)) {
    return "instruction-override";
  }
  if (/reveal.*prompt|show.*instructions|display.*system/i.test(lowerPrompt)) {
    return "prompt-extraction";
  }
  if (/act as|pretend to be|you are now|role.*play/i.test(lowerPrompt)) {
    return "role-hijacking";
  }
  if (/jailbreak|bypass.*security|bypass.*safety|developer mode/i.test(lowerPrompt)) {
    return "jailbreak-attempt";
  }
  
  return "general-injection";
};

// Simulated analysis results
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
  threatType?: ThreatType;
  analysisTime?: number;
  phase2Data?: any;
}

const Index = () => {
  const [prompt, setPrompt] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  // Keyboard shortcut for Escape to clear
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && prompt) {
        setPrompt("");
        setShowAnalysis(false);
        setResult(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [prompt]);

  const analyzePrompt = useCallback(async (enablePhase2: boolean = false) => {
    if (!prompt.trim()) return;

    const startTime = performance.now();
    setIsAnalyzing(true);
    setShowAnalysis(true);
    setResult(null);

    try {
      console.log(`🔍 Starting analysis for: "${prompt.substring(0, 50)}..."`);
      const apiResult = await apiService.analyzePrompt(prompt, enablePhase2);
      const analysisTime = Math.round(performance.now() - startTime);

      console.log(`✅ Analysis complete. Setting result state.`);
      console.log(`   Response preview: ${apiResult.response?.substring(0, 50)}...`);

      // Convert API response to UI result format
      const riskLevel = apiResult.analysis.risk > 0.6 ? "high" : apiResult.analysis.risk > 0.3 ? "medium" : "low";
      
      const newResult = {
        riskLevel: riskLevel as RiskLevel,
        riskScore: Math.round(apiResult.analysis.risk * 100),
        mlRisk: Math.round(apiResult.analysis.ml_score * 100),
        lexicalRisk: Math.round(apiResult.analysis.lexical_risk * 100),
        benignOffset: Math.round(apiResult.analysis.benign_offset * 100),
        status: apiResult.status as ResultStatus,
        response: apiResult.response,
        blockReason: apiResult.blockReason || "Security policy violation detected",
        suggestedRewrite: apiResult.suggestedRewrite,
        threatType: detectThreatType(prompt),
        analysisTime,
        // Pass Phase 2 data if available
        phase2Data: enablePhase2 ? {
          intent_analysis: apiResult.intent_analysis,
          escalation_analysis: apiResult.escalation_analysis,
          semantic_analysis: apiResult.semantic_analysis,
          context_anomalies: apiResult.context_anomalies,
          user_risk_profile: apiResult.user_risk_profile,
        } : undefined,
      };
      
      console.log(`   Setting result state:`, newResult);
      setResult(newResult);
    } catch (error) {
      console.error("Analysis failed:", error);
      
      // Show error state to user
      setResult({
        riskLevel: "high",
        riskScore: 0,
        mlRisk: 0,
        lexicalRisk: 0,
        benignOffset: 0,
        status: "error" as any,
        blockReason: `Analysis service unavailable: ${error instanceof Error ? error.message : "Unknown error"}`,
        analysisTime: Math.round(performance.now() - startTime),
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [prompt]);

  const handleExampleSelect = (examplePrompt: string) => {
    setPrompt(examplePrompt);
    setShowAnalysis(false);
    setResult(null);
  };

  const handleUseSuggestion = (suggestion: string) => {
    setPrompt(suggestion);
    setShowAnalysis(false);
    setResult(null);
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background gradient effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-primary/3 rounded-full blur-3xl" />
        <div className="absolute top-1/3 right-0 w-[300px] h-[300px] bg-safe/5 rounded-full blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Header />

        <main className="flex-1 container max-w-6xl mx-auto px-4 py-8 md:py-12">
          {/* Hero section */}
          <HeroSection />

          {/* Security badges */}
          <div className="mb-10">
            <SecurityBadge />
          </div>

          {/* Main content grid */}
          <div className="grid lg:grid-cols-5 gap-6">
            {/* Left column - Input and Examples */}
            <div className="lg:col-span-3 space-y-6">
              <PromptInput
                value={prompt}
                onChange={setPrompt}
                onSubmit={analyzePrompt}
                isAnalyzing={isAnalyzing}
              />

              <ExamplePrompts
                onSelect={handleExampleSelect}
                disabled={isAnalyzing}
              />

              {/* Result card */}
              <AnimatePresence mode="wait">
                {result?.status && (
                  <ResultCard
                    key={`${result.status}-${result.analysisTime}`}
                    status={result.status}
                    response={result.response}
                    blockReason={result.blockReason}
                    suggestedRewrite={result.suggestedRewrite}
                    threatType={result.threatType}
                    analysisTime={result.analysisTime}
                    phase2Data={result.phase2Data}
                    onUseSuggestion={handleUseSuggestion}
                  />
                )}
              </AnimatePresence>
            </div>

            {/* Right column - Analysis panel */}
            <div className="lg:col-span-2 space-y-6">
              <AnimatePresence>
                {(showAnalysis || result) && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-6"
                  >
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
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Placeholder when no analysis */}
              {!showAnalysis && !result && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="glass-card p-8 text-center"
                >
                  <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-muted/50 flex items-center justify-center float">
                    <motion.div
                      animate={{ scale: [1, 1.05, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <Shield className="w-8 h-8 text-muted-foreground" />
                    </motion.div>
                  </div>
                  <h3 className="font-semibold text-foreground mb-2">
                    Security Analysis Panel
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Enter a prompt to see real-time threat detection and risk scoring
                  </p>
                  <div className="flex items-center justify-center gap-2 text-xs text-primary">
                    <span>Try an example</span>
                    <ArrowRight className="w-3 h-3" />
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </main>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="py-6 text-center text-sm text-muted-foreground border-t border-border/30"
        >
          <div className="container max-w-6xl mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-primary" />
                <span>PromptGuard — Enterprise AI Security Gateway</span>
              </p>
              <div className="flex items-center gap-4 text-xs">
                <span className="flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-safe" />
                  System operational
                </span>
                <span>v1.0.0</span>
              </div>
            </div>
          </div>
        </motion.footer>
      </div>
    </div>
  );
};

export default Index;
