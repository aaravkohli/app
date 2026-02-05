import { motion } from "framer-motion";
import { AlertCircle, TrendingUp, CheckCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface EscalationAnalysis {
  escalation_score?: number;
  escalation_level?: string;
  detected_patterns?: string[];
  escalation_description?: string;
  risk_increase?: number;
}

interface EscalationIndicatorProps {
  analysis?: EscalationAnalysis;
}

const EscalationIndicator = ({ analysis }: EscalationIndicatorProps) => {
  if (!analysis) return null;

  const escalationScore = analysis.escalation_score ?? 0;
  const level = analysis.escalation_level || "unknown";

  const getLevelColor = (lvl: string): string => {
    switch (lvl.toLowerCase()) {
      case "critical":
        return "bg-red-500";
      case "high":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-green-500";
      default:
        return "bg-blue-500";
    }
  };

  const getLevelBgColor = (lvl: string): string => {
    switch (lvl.toLowerCase()) {
      case "critical":
        return "bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-900";
      case "high":
        return "bg-orange-50 dark:bg-orange-950/20 border-orange-200 dark:border-orange-900";
      case "medium":
        return "bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-900";
      case "low":
        return "bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-900";
      default:
        return "bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900";
    }
  };

  return (
    <div className="space-y-4">
      {/* Escalation Score Card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card
          className={`p-6 border-2 ${
            getLevelBgColor(level)
          }`}
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Score Gauge */}
            <div className="flex flex-col items-center justify-center">
              <div className="relative w-32 h-32">
                {/* Background circle */}
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="8"
                    className="text-muted/20"
                  />
                  {/* Progress circle */}
                  <motion.circle
                    cx="64"
                    cy="64"
                    r="56"
                    fill="none"
                    stroke={`url(#gradient-${level})`}
                    strokeWidth="8"
                    strokeDasharray={`${escalationScore * 351.86} 351.86`}
                    initial={{ strokeDasharray: "0 351.86" }}
                    animate={{
                      strokeDasharray: `${escalationScore * 351.86} 351.86`,
                    }}
                    transition={{ duration: 1, delay: 0.2 }}
                  />
                  <defs>
                    <linearGradient
                      id={`gradient-${level}`}
                      x1="0%"
                      y1="0%"
                      x2="100%"
                      y2="100%"
                    >
                      <stop offset="0%" stopColor="#ef4444" />
                      <stop offset="100%" stopColor="#f97316" />
                    </linearGradient>
                  </defs>
                </svg>

                {/* Center text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-bold">
                    {(escalationScore * 100).toFixed(0)}
                  </span>
                  <span className="text-xs text-muted-foreground">score</span>
                </div>
              </div>

              {/* Score description */}
              <p className="text-xs text-muted-foreground mt-2 text-center">
                {escalationScore > 0.7
                  ? "Critical escalation detected"
                  : escalationScore > 0.4
                    ? "Moderate escalation risk"
                    : "Low escalation risk"}
              </p>
            </div>

            {/* Details */}
            <div className="flex flex-col justify-between">
              {/* Level Badge */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Escalation Level</h4>
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <Badge
                    className={`${getLevelColor(level)} text-white capitalize px-3 py-1`}
                  >
                    {level}
                  </Badge>
                </motion.div>
              </div>

              {/* Risk Increase */}
              {analysis.risk_increase !== undefined && (
                <div className="mt-4">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-orange-500" />
                    <span className="text-sm font-medium">Risk Increase</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{
                        width: `${Math.min(analysis.risk_increase * 100, 100)}%`,
                      }}
                      transition={{ delay: 0.3, duration: 0.5 }}
                      className="h-full bg-gradient-to-r from-orange-400 to-red-500"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    +{(analysis.risk_increase * 100).toFixed(1)}%
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Description */}
          {analysis.escalation_description && (
            <div className="mt-4 pt-4 border-t border-current/10">
              <p className="text-sm text-muted-foreground">
                {analysis.escalation_description}
              </p>
            </div>
          )}
        </Card>
      </motion.div>

      {/* Detected Patterns */}
      {analysis.detected_patterns && analysis.detected_patterns.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="space-y-2">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase">
              Escalation Patterns
            </h4>
            <div className="space-y-2">
              {analysis.detected_patterns.map((pattern, index) => (
                <motion.div
                  key={pattern}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.25 + index * 0.05 }}
                  className="flex items-start gap-2 p-2 bg-muted/30 rounded-md"
                >
                  <AlertCircle className="w-4 h-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                  <span className="text-sm text-muted-foreground">{pattern}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default EscalationIndicator;
