import { motion } from "framer-motion";
import {
  User,
  AlertCircle,
  BarChart3,
  Shield,
  TrendingUp,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface UserProfileRisk {
  user_id?: string;
  abuse_score?: number;
  risk_level?: string;
  suspicious_indicators?: string[];
  previous_attacks?: number;
  trust_score?: number;
  profile_description?: string;
}

interface UserRiskProfileProps {
  analysis?: UserProfileRisk;
}

const UserRiskProfile = ({ analysis }: UserRiskProfileProps) => {
  if (!analysis) return null;

  const abuseScore = analysis.abuse_score ?? 0;
  const trustScore = analysis.trust_score ?? (1 - abuseScore);
  const riskLevel = analysis.risk_level || "unknown";

  const getRiskColor = (level: string): string => {
    switch (level.toLowerCase()) {
      case "critical":
        return "text-red-600 dark:text-red-400";
      case "high":
        return "text-orange-600 dark:text-orange-400";
      case "medium":
        return "text-yellow-600 dark:text-yellow-400";
      case "low":
        return "text-green-600 dark:text-green-400";
      default:
        return "text-blue-600 dark:text-blue-400";
    }
  };

  const getRiskBgColor = (level: string): string => {
    switch (level.toLowerCase()) {
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
      {/* Main Risk Card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card
          className={`p-6 border-2 ${getRiskBgColor(riskLevel)}`}
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Risk Indicators */}
            <div className="space-y-4">
              {/* Risk Level */}
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className={`w-5 h-5 ${getRiskColor(riskLevel)}`} />
                  <span className="text-sm font-semibold text-muted-foreground">
                    Risk Level
                  </span>
                </div>
                <Badge
                  className={`capitalize px-3 py-1 ${
                    riskLevel === "critical"
                      ? "bg-red-600 text-white"
                      : riskLevel === "high"
                        ? "bg-orange-600 text-white"
                        : riskLevel === "medium"
                          ? "bg-yellow-600 text-white"
                          : riskLevel === "low"
                            ? "bg-green-600 text-white"
                            : "bg-blue-600 text-white"
                  }`}
                >
                  {riskLevel}
                </Badge>
              </div>

              {/* User ID if available */}
              {analysis.user_id && (
                <div className="text-xs text-muted-foreground">
                  <span className="font-medium">User ID:</span>
                  <br />
                  <code className="text-xs bg-muted/50 px-2 py-1 rounded">
                    {analysis.user_id.substring(0, 20)}...
                  </code>
                </div>
              )}

              {/* Previous Attacks */}
              {analysis.previous_attacks !== undefined && (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-4 h-4 text-orange-500" />
                    <span className="text-sm font-semibold text-muted-foreground">
                      Previous Attacks
                    </span>
                  </div>
                  <div className="text-2xl font-bold">
                    {analysis.previous_attacks}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    blocked attempts on record
                  </p>
                </div>
              )}
            </div>

            {/* Scores Section */}
            <div className="space-y-4">
              {/* Abuse Score Gauge */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-muted-foreground">
                    Abuse Score
                  </span>
                  <span className="text-xl font-bold text-red-600 dark:text-red-400">
                    {(abuseScore * 100).toFixed(0)}
                  </span>
                </div>
                <div className="h-3 bg-muted rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${abuseScore * 100}%` }}
                    transition={{ delay: 0.2, duration: 0.5 }}
                    className="h-full bg-gradient-to-r from-red-400 to-red-600"
                  />
                </div>
              </div>

              {/* Trust Score Gauge */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-muted-foreground">
                    Trust Score
                  </span>
                  <span className="text-xl font-bold text-green-600 dark:text-green-400">
                    {(trustScore * 100).toFixed(0)}
                  </span>
                </div>
                <div className="h-3 bg-muted rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${trustScore * 100}%` }}
                    transition={{ delay: 0.25, duration: 0.5 }}
                    className="h-full bg-gradient-to-r from-green-400 to-green-600"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Description */}
          {analysis.profile_description && (
            <div className="mt-4 pt-4 border-t border-current/10">
              <p className="text-sm text-muted-foreground">
                {analysis.profile_description}
              </p>
            </div>
          )}
        </Card>
      </motion.div>

      {/* Suspicious Indicators */}
      {analysis.suspicious_indicators &&
        analysis.suspicious_indicators.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase">
                Suspicious Indicators
              </h4>

              <div className="space-y-2">
                {analysis.suspicious_indicators.map((indicator, index) => (
                  <motion.div
                    key={indicator}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.25 + index * 0.05 }}
                    className="flex items-start gap-2 p-3 bg-red-50 dark:bg-red-950/20 rounded-md border border-red-200/50 dark:border-red-900/50"
                  >
                    <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-muted-foreground">
                      {indicator}
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

      {/* Risk Assessment Summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="flex items-start gap-2 p-3 bg-muted/30 rounded-md border border-border/50"
      >
        <Shield className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
        <div className="flex-1 text-xs text-muted-foreground">
          <p>
            This user profile has been assessed based on behavioral patterns,
            historical attack attempts, and current request characteristics.
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default UserRiskProfile;
