import { motion } from "framer-motion";
import { Shield, ShieldAlert, ShieldCheck, ShieldX, TrendingUp, TrendingDown } from "lucide-react";

export type RiskLevel = "low" | "medium" | "high" | "analyzing";

interface RiskMeterProps {
  riskLevel: RiskLevel;
  riskScore: number; // 0-100
  isAnalyzing: boolean;
}

const RiskMeter = ({ riskLevel, riskScore, isAnalyzing }: RiskMeterProps) => {
  const getRiskConfig = () => {
    if (isAnalyzing) {
      return {
        icon: Shield,
        label: "Scanning Prompt",
        color: "text-primary",
        bgColor: "bg-primary/10",
        borderColor: "border-primary/30",
        fillClass: "risk-low",
        description: "Analyzing patterns and intent...",
        trend: null,
      };
    }

    switch (riskLevel) {
      case "low":
        return {
          icon: ShieldCheck,
          label: "Low Risk",
          color: "text-safe",
          bgColor: "bg-safe/10",
          borderColor: "border-safe/30",
          fillClass: "risk-low",
          description: "Safe to process — no threats detected",
          trend: "down" as const,
        };
      case "medium":
        return {
          icon: ShieldAlert,
          label: "Medium Risk",
          color: "text-warning",
          bgColor: "bg-warning/10",
          borderColor: "border-warning/30",
          fillClass: "risk-medium",
          description: "Some patterns detected, proceed with caution",
          trend: null,
        };
      case "high":
        return {
          icon: ShieldX,
          label: "High Risk",
          color: "text-danger",
          bgColor: "bg-danger/10",
          borderColor: "border-danger/30",
          fillClass: "risk-high",
          description: "Injection patterns detected — blocked",
          trend: "up" as const,
        };
      default:
        return {
          icon: Shield,
          label: "Ready",
          color: "text-muted-foreground",
          bgColor: "bg-muted/10",
          borderColor: "border-border",
          fillClass: "",
          description: "Waiting for input...",
          trend: null,
        };
    }
  };

  const config = getRiskConfig();
  const IconComponent = config.icon;
  const TrendIcon = config.trend === "up" ? TrendingUp : config.trend === "down" ? TrendingDown : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
      className={`glass-card p-4 md:p-5 border ${config.borderColor}`}
    >
      {/* Threat indicator pulse background when analyzing */}
      {isAnalyzing && (
        <motion.div
          className="absolute inset-0 rounded-lg"
          animate={{
            boxShadow: [
              "inset 0 0 0 0px rgba(59, 130, 246, 0.2)",
              "inset 0 0 0 2px rgba(59, 130, 246, 0.3)",
              "inset 0 0 0 4px rgba(59, 130, 246, 0.1)",
              "inset 0 0 0 0px rgba(59, 130, 246, 0)"
            ]
          }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-4 relative z-10">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Threat Level
        </span>
        {!isAnalyzing && riskLevel !== "analyzing" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-mono ${config.bgColor} ${config.color}`}
          >
            {TrendIcon && <TrendIcon className="w-3 h-3" />}
            <span>{riskScore}%</span>
          </motion.div>
        )}
      </div>

      <div className="flex items-center gap-4 mb-4 relative z-10">
        {/* Icon with pulse animation */}
        <div className={`relative p-3 rounded-xl ${config.bgColor}`}>
          {isAnalyzing && (
            <>
              <div className="absolute inset-0 rounded-xl bg-primary/20 pulse-ring" />
              <div className="absolute inset-0 rounded-xl bg-primary/10 pulse-ring" style={{ animationDelay: "0.5s" }} />
            </>
          )}
          <motion.div
            animate={isAnalyzing ? { scale: [1, 1.1, 1] } : {}}
            transition={{ duration: 1, repeat: isAnalyzing ? Infinity : 0 }}
          >
            <IconComponent className={`w-6 h-6 ${config.color}`} />
          </motion.div>
        </div>

        <div className="flex-1">
          <h3 className={`font-semibold text-lg ${config.color}`}>{config.label}</h3>
          <p className="text-sm text-muted-foreground">{config.description}</p>
        </div>
      </div>

      {/* Risk meter bar */}
      <div className="relative z-10">
        <div className="risk-meter-track h-3 rounded-full">
          <motion.div
            className={`risk-meter-fill h-full rounded-full ${config.fillClass}`}
            initial={{ width: "0%" }}
            animate={{ 
              width: isAnalyzing ? ["0%", "60%", "30%", "80%", "50%"] : `${riskScore}%` 
            }}
            transition={
              isAnalyzing 
                ? { duration: 2, repeat: Infinity, ease: "easeInOut" }
                : { duration: 0.5, ease: "easeOut" }
            }
          />
        </div>
        
        {/* Threshold markers */}
        <div className="absolute top-0 left-[33%] w-px h-3 bg-warning/30" />
        <div className="absolute top-0 left-[66%] w-px h-3 bg-danger/30" />
      </div>

      {/* Risk level indicators */}
      <div className="flex justify-between mt-2 text-xs relative z-10">
        <span className="text-safe">Safe</span>
        <span className="text-warning">Caution</span>
        <span className="text-danger">Blocked</span>
      </div>
    </motion.div>
  );
};

export default RiskMeter;
