import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  ShieldCheck, 
  ShieldX, 
  Copy, 
  Check, 
  ChevronDown, 
  Lightbulb,
  Sparkles,
  AlertTriangle,
  Database,
  Zap,
  Wand2,
  Info
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import Phase2InsightPanel from "@/components/Phase2InsightPanel";

export type ResultStatus = "approved" | "blocked" | null;
export type ThreatType = 
  | "instruction-override"
  | "prompt-extraction"
  | "role-hijacking"
  | "jailbreak-attempt"
  | "general-injection"
  | null;

interface Phase2Data {
  intent_analysis?: any;
  escalation_analysis?: any;
  semantic_analysis?: any;
  context_anomalies?: any;
  user_risk_profile?: any;
}

interface ResultCardProps {
  status: ResultStatus;
  response?: string;
  blockReason?: string;
  suggestedRewrite?: string;
  threatType?: ThreatType;
  analysisTime?: number;
  phase2Data?: Phase2Data;
  onUseSuggestion?: (suggestion: string) => void;
}

const ResultCard = ({
  status,
  response,
  blockReason,
  suggestedRewrite,
  threatType,
  analysisTime,
  phase2Data,
  onUseSuggestion,
}: ResultCardProps) => {
  const [copied, setCopied] = useState(false);
  const [showReason, setShowReason] = useState(false);
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  // Typewriter effect for response
  useEffect(() => {
    if (status === "approved" && response) {
      setIsTyping(true);
      setDisplayedText("");
      let index = 0;
      
      // Start typewriter effect with a small delay to ensure clean start
      const typewriterInterval = setInterval(() => {
        if (index < response.length) {
          setDisplayedText(response.slice(0, index + 1));
          index++;
        } else {
          setIsTyping(false);
          clearInterval(typewriterInterval);
        }
      }, 15);
      
      return () => {
        clearInterval(typewriterInterval);
      };
    } else if (status === "blocked") {
      setDisplayedText("");
      setIsTyping(false);
    }
  }, [status, response]);

  const handleCopy = async () => {
    if (response) {
      await navigator.clipboard.writeText(response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const threatDescriptions = {
    "instruction-override": {
      title: "Instruction Override Detected",
      description: "Your prompt attempts to override the system's core instructions.",
      icon: AlertTriangle,
      color: "text-danger",
    },
    "prompt-extraction": {
      title: "Prompt Extraction Attempt",
      description: "Your prompt tries to extract or reveal hidden system prompts.",
      icon: Database,
      color: "text-danger",
    },
    "role-hijacking": {
      title: "Role Hijacking Detected",
      description: "Your prompt attempts to change the AI's role or behavior.",
      icon: Zap,
      color: "text-danger",
    },
    "jailbreak-attempt": {
      title: "Jailbreak Attempt Blocked",
      description: "Your prompt uses known jailbreak techniques to bypass security.",
      icon: Wand2,
      color: "text-danger",
    },
    "general-injection": {
      title: "Injection Pattern Detected",
      description: "Your prompt contains patterns commonly used in prompt injection attacks.",
      icon: AlertTriangle,
      color: "text-danger",
    },
  };

  const getThreatConfig = (threat: ThreatType) => {
    if (!threat || threat === null) return null;
    return threatDescriptions[threat];
  };

  if (!status) return null;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={status}
        initial={{ opacity: 0, y: 20, scale: 0.98 }}
        animate={{ 
          opacity: 1, 
          y: 0, 
          scale: 1,
          boxShadow: status === "approved"
            ? [
                "0 0 0 0px rgba(34, 197, 94, 0.4)",
                "0 0 0 20px rgba(34, 197, 94, 0.2)",
                "0 0 0 40px rgba(34, 197, 94, 0)"
              ]
            : [
                "0 0 0 0px rgba(239, 68, 68, 0.4)",
                "0 0 0 20px rgba(239, 68, 68, 0.1)",
              ]
        }}
        transition={{ 
          y: { duration: 0.4, ease: "easeOut" },
          scale: { duration: 0.3, ease: "backOut" },
          opacity: { duration: 0.3 },
          boxShadow: { duration: 0.6, ease: "easeOut" }
        }}
        className={`
          glass-card overflow-hidden
          ${status === "approved" ? "ring-1 ring-safe/30" : "ring-1 ring-danger/30"}
        `}
      >
        {/* Header */}
        <div
          className={`
            p-4 md:p-5 flex items-center gap-4
            ${status === "approved" ? "bg-safe/5" : "bg-danger/5"}
          `}
        >
          {/* Animated shield icon */}
          <div className="relative">
            <motion.div
              className={`
                p-3 rounded-xl shield-animate
                ${status === "approved" ? "bg-safe/10" : "bg-danger/10"}
              `}
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ type: "spring", stiffness: 200, damping: 15 }}
            >
              {status === "approved" ? (
                <ShieldCheck className="w-6 h-6 text-safe" />
              ) : (
                <ShieldX className="w-6 h-6 text-danger" />
              )}
            </motion.div>
            
            {/* Success checkmark animation */}
            {status === "approved" && (
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="absolute -top-1 -right-1 bg-safe rounded-full p-0.5"
              >
                <Check className="w-3 h-3 text-safe-foreground" />
              </motion.div>
            )}
          </div>

          <div className="flex-1">
            <motion.h3
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className={`font-semibold text-lg ${
                status === "approved" ? "text-safe" : "text-danger"
              }`}
            >
              {status === "approved" ? "Prompt Approved" : "Prompt Blocked"}
            </motion.h3>
            <motion.p
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 }}
              className="text-sm text-muted-foreground"
            >
              {status === "approved"
                ? "Your prompt passed security analysis"
                : "Security concerns were detected"}
            </motion.p>
          </div>

          {/* Copy button for approved */}
          {status === "approved" && response && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="text-muted-foreground hover:text-foreground"
            >
              {copied ? (
                <Check className="w-4 h-4 text-safe" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </Button>
          )}
        </div>

        {/* Content */}
        <div className="p-4 md:p-5 pt-0 md:pt-0">
          {status === "approved" && response && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="mt-4"
            >
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-muted-foreground">
                  AI Response
                </span>
              </div>
              <div className="bg-muted/30 rounded-lg p-4 text-foreground leading-relaxed overflow-hidden">
                {displayedText ? (
                  <>
                    <MarkdownRenderer 
                      content={displayedText} 
                      className="prose-sm"
                    />
                    {isTyping && <span className="typewriter-cursor ml-1" />}
                  </>
                ) : (
                  <span className="animate-pulse">Loading response...</span>
                )}
              </div>
            </motion.div>
          )}

          {status === "blocked" && (
            <>
              {/* Threat Type Badge (if available) */}
              {threatType && getThreatConfig(threatType) && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15 }}
                  className="mt-4 p-4 rounded-lg bg-danger/10 border border-danger/20"
                >
                  {(() => {
                    const config = getThreatConfig(threatType);
                    if (!config) return null;
                    const ThreatIcon = config.icon;
                    return (
                      <div className="flex items-start gap-3">
                        <ThreatIcon className={`w-5 h-5 ${config.color} mt-0.5 flex-shrink-0`} />
                        <div className="flex-1">
                          <h4 className={`font-semibold ${config.color} text-sm mb-1`}>
                            {config.title}
                          </h4>
                          <p className="text-sm text-muted-foreground">{config.description}</p>
                        </div>
                      </div>
                    );
                  })()}
                </motion.div>
              )}

              {/* Block reason collapsible */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.25 }}
                className="mt-4"
              >
                <button
                  onClick={() => setShowReason(!showReason)}
                  className="w-full flex items-center justify-between p-3 bg-muted/30 rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-2 text-left">
                    <Info className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Analysis Details</span>
                  </div>
                  <motion.div
                    animate={{ rotate: showReason ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronDown className="w-4 h-4 text-muted-foreground" />
                  </motion.div>
                </button>

                <AnimatePresence>
                  {showReason && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="p-4 mt-2 bg-danger/5 rounded-lg border border-danger/20">
                        <p className="text-sm text-foreground leading-relaxed">
                          {blockReason || 
                            "Our security analysis detected patterns commonly associated with prompt injection attacks. This includes attempts to override instructions, extract system information, or manipulate the AI's behavior in unauthorized ways."}
                        </p>
                        {analysisTime && (
                          <motion.p
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.1 }}
                            className="text-xs text-muted-foreground mt-3 flex items-center gap-1"
                          >
                            <Check className="w-3 h-3 text-safe" />
                            Analyzed and blocked in {analysisTime}ms
                          </motion.p>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>

              {/* Suggested rewrite */}
              {suggestedRewrite && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.35 }}
                  className="mt-4 p-4 bg-primary/5 rounded-lg border border-primary/20"
                >
                  <div className="flex items-start gap-3">
                    <Lightbulb className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h4 className="text-sm font-semibold text-foreground mb-2">
                        💡 Here's a safer way to ask:
                      </h4>
                      <div className="bg-muted/50 rounded-md p-3 mb-3 text-sm text-muted-foreground italic border border-border/50">
                        "{suggestedRewrite}"
                      </div>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => onUseSuggestion?.(suggestedRewrite)}
                        className="text-xs"
                      >
                        <Wand2 className="w-3 h-3 mr-1" />
                        Use this prompt
                      </Button>
                    </div>
                  </div>
                </motion.div>
              )}
            </>
          )}

          {/* Phase 2 Insights Panel */}
          {phase2Data && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <Phase2InsightPanel phase2Data={phase2Data} />
            </motion.div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ResultCard;
