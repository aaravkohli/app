import { motion } from "framer-motion";
import { Brain, FileText, Heart, HelpCircle, Info } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface RiskFactor {
  id: string;
  label: string;
  value: number;
  icon: React.ElementType;
  description: string;
  tooltip: string;
}

interface RiskBreakdownProps {
  mlRisk: number;
  lexicalRisk: number;
  benignOffset: number;
  isAnalyzing: boolean;
}

const RiskBreakdown = ({
  mlRisk,
  lexicalRisk,
  benignOffset,
  isAnalyzing,
}: RiskBreakdownProps) => {
  const getColor = (value: number, isPositive: boolean) => {
    if (isPositive) {
      return value > 50 ? "text-safe" : value > 25 ? "text-warning" : "text-danger";
    }
    return value > 60 ? "text-danger" : value > 30 ? "text-warning" : "text-safe";
  };

  const factors: RiskFactor[] = [
    {
      id: "ml",
      label: "ML Risk Score",
      value: mlRisk,
      icon: Brain,
      description: getColor(mlRisk, false),
      tooltip: "Our neural network's confidence that this prompt contains malicious patterns. Lower is better.",
    },
    {
      id: "lexical",
      label: "Pattern Match",
      value: lexicalRisk,
      icon: FileText,
      description: getColor(lexicalRisk, false),
      tooltip: "Matches against 10,000+ known injection signatures and keywords. Lower is better.",
    },
    {
      id: "benign",
      label: "Benign Intent",
      value: benignOffset,
      icon: Heart,
      description: "text-safe",
      tooltip: "Positive signals indicating legitimate, helpful intent. Higher is better — this reduces your overall risk.",
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { opacity: 1, x: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="glass-card p-4 md:p-5"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold text-foreground">Analysis Breakdown</h3>
          <Tooltip>
            <TooltipTrigger>
              <Info className="w-4 h-4 text-muted-foreground hover:text-foreground transition-colors cursor-help" />
            </TooltipTrigger>
            <TooltipContent side="top" className="max-w-xs">
              <p className="text-sm">
                Three-factor analysis: ML detection finds novel attacks, Pattern matching catches known signatures, 
                and Benign intent recognizes legitimate requests.
              </p>
            </TooltipContent>
          </Tooltip>
        </div>
        {isAnalyzing && (
          <span className="text-xs text-primary animate-pulse">Processing...</span>
        )}
      </div>

      <div className="space-y-4">
        {factors.map((factor) => {
          const Icon = factor.icon;
          const colorClass = factor.id === "benign" 
            ? "text-safe" 
            : getColor(factor.value, false);
          const bgColorClass = factor.id === "benign"
            ? "bg-safe"
            : factor.value > 60
            ? "bg-danger"
            : factor.value > 30
            ? "bg-warning"
            : "bg-safe";

          return (
            <motion.div
              key={factor.id}
              variants={itemVariants}
              className="relative"
            >
              <div className="flex items-center justify-between mb-2">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <div className="flex items-center gap-2 cursor-help group">
                      <div className={`p-1.5 rounded-md bg-muted/50 ${colorClass} group-hover:bg-muted transition-colors`}>
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <span className="text-sm font-medium text-foreground group-hover:text-primary transition-colors">
                        {factor.label}
                      </span>
                      <HelpCircle className="w-3 h-3 text-muted-foreground/50 group-hover:text-muted-foreground transition-colors" />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="left" className="max-w-xs">
                    <p className="text-sm">{factor.tooltip}</p>
                  </TooltipContent>
                </Tooltip>

                <motion.div
                  className={`flex items-center gap-1.5 ${colorClass}`}
                  key={factor.value}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.2 }}
                >
                  <span className="text-sm font-mono font-semibold">
                    {isAnalyzing ? "..." : `${factor.value}%`}
                  </span>
                  {!isAnalyzing && factor.id === "benign" && factor.value > 50 && (
                    <span className="text-xs bg-safe/20 px-1.5 py-0.5 rounded">Good</span>
                  )}
                  {!isAnalyzing && factor.id !== "benign" && factor.value < 20 && (
                    <span className="text-xs bg-safe/20 px-1.5 py-0.5 rounded text-safe">Low</span>
                  )}
                  {!isAnalyzing && factor.id !== "benign" && factor.value > 60 && (
                    <span className="text-xs bg-danger/20 px-1.5 py-0.5 rounded text-danger">High</span>
                  )}
                </motion.div>
              </div>

              {/* Progress bar */}
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <motion.div
                  className={`h-full rounded-full ${bgColorClass}`}
                  initial={{ width: "0%" }}
                  animate={{
                    width: isAnalyzing
                      ? ["0%", "50%", "25%", "75%", "40%"]
                      : `${factor.value}%`,
                  }}
                  transition={
                    isAnalyzing
                      ? { duration: 1.5, repeat: Infinity, ease: "easeInOut" }
                      : { duration: 0.5, delay: 0.2, ease: "easeOut" }
                  }
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Summary insight */}
      {!isAnalyzing && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-4 pt-4 border-t border-border/50"
        >
          <p className="text-xs text-muted-foreground">
            {mlRisk < 20 && lexicalRisk < 20 && benignOffset > 60
              ? "✓ All indicators show this is a safe, legitimate request."
              : mlRisk > 60 || lexicalRisk > 60
              ? "⚠ High-risk patterns detected. Review the prompt carefully."
              : "◐ Mixed signals detected. The request appears mostly safe."}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};

export default RiskBreakdown;
