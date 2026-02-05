import { motion } from "framer-motion";
import {
  AlertTriangle,
  TrendingDown,
  MessageCircle,
  Clock,
  User,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ContextAnomaly {
  anomaly_type?: string;
  severity?: string;
  description?: string;
  recommendation?: string;
}

interface ContextAnomalyDetection {
  detected_anomalies?: ContextAnomaly[];
  anomaly_score?: number;
  behavioral_flags?: Record<string, any>;
  context_description?: string;
}

interface ContextAnomaliesProps {
  analysis?: ContextAnomalyDetection;
}

const ContextAnomalies = ({ analysis }: ContextAnomaliesProps) => {
  if (!analysis) return null;

  const anomalies = analysis.detected_anomalies || [];

  const getAnomalyIcon = (
    anomalyType?: string
  ): React.ComponentType<any> => {
    switch (anomalyType?.toLowerCase()) {
      case "conversation-pattern":
        return MessageCircle;
      case "timing-anomaly":
        return Clock;
      case "behavioral-deviation":
        return User;
      default:
        return AlertTriangle;
    }
  };

  const getSeverityColor = (severity?: string): string => {
    switch (severity?.toLowerCase()) {
      case "critical":
        return "bg-red-100 dark:bg-red-950/30 text-red-800 dark:text-red-200";
      case "high":
        return "bg-orange-100 dark:bg-orange-950/30 text-orange-800 dark:text-orange-200";
      case "medium":
        return "bg-yellow-100 dark:bg-yellow-950/30 text-yellow-800 dark:text-yellow-200";
      case "low":
        return "bg-blue-100 dark:bg-blue-950/30 text-blue-800 dark:text-blue-200";
      default:
        return "bg-gray-100 dark:bg-gray-950/30 text-gray-800 dark:text-gray-200";
    }
  };

  const getSeverityBg = (severity?: string): string => {
    switch (severity?.toLowerCase()) {
      case "critical":
        return "bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-900";
      case "high":
        return "bg-orange-50 dark:bg-orange-950/20 border-orange-200 dark:border-orange-900";
      case "medium":
        return "bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200 dark:border-yellow-900";
      case "low":
        return "bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900";
      default:
        return "bg-gray-50 dark:bg-gray-950/20 border-gray-200 dark:border-gray-900";
    }
  };

  return (
    <div className="space-y-4">
      {/* Anomaly Score */}
      {analysis.anomaly_score !== undefined && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-950/20 dark:to-purple-950/20 border-2 border-indigo-200 dark:border-indigo-900">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-semibold text-foreground">
                  Behavioral Anomaly Score
                </h4>
                <p className="text-xs text-muted-foreground mt-1">
                  Deviation from normal user behavior patterns
                </p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-indigo-600 dark:text-indigo-400">
                  {(analysis.anomaly_score * 100).toFixed(0)}
                </div>
                <span className="text-xs text-muted-foreground">score</span>
              </div>
            </div>

            {/* Score Bar */}
            <div className="mt-3 h-2 bg-muted rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${analysis.anomaly_score * 100}%` }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
              />
            </div>
          </Card>
        </motion.div>
      )}

      {/* Description */}
      {analysis.context_description && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
          className="text-sm text-muted-foreground p-3 bg-muted/20 rounded-md"
        >
          {analysis.context_description}
        </motion.p>
      )}

      {/* Detected Anomalies */}
      {anomalies.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs font-semibold text-muted-foreground uppercase">
            Detected Anomalies ({anomalies.length})
          </h4>

          {anomalies.map((anomaly, index) => {
            const Icon = getAnomalyIcon(anomaly.anomaly_type);
            return (
              <motion.div
                key={`${anomaly.anomaly_type}-${index}`}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + index * 0.05 }}
              >
                <Card
                  className={`p-4 border-2 ${getSeverityBg(anomaly.severity)}`}
                >
                  <div className="flex items-start gap-3">
                    {/* Icon */}
                    <Icon className="w-5 h-5 mt-0.5 flex-shrink-0 text-current" />

                    {/* Content */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h5 className="font-semibold text-sm capitalize">
                          {anomaly.anomaly_type?.replace(/-/g, " ") ||
                            "Unknown Anomaly"}
                        </h5>
                        {anomaly.severity && (
                          <Badge
                            className={`text-xs capitalize ${getSeverityColor(
                              anomaly.severity
                            )}`}
                          >
                            {anomaly.severity}
                          </Badge>
                        )}
                      </div>

                      {/* Description */}
                      {anomaly.description && (
                        <p className="text-xs text-muted-foreground mb-2">
                          {anomaly.description}
                        </p>
                      )}

                      {/* Recommendation */}
                      {anomaly.recommendation && (
                        <div className="flex items-start gap-2 pt-2 border-t border-current/10">
                          <TrendingDown className="w-3 h-3 text-primary flex-shrink-0 mt-0.5" />
                          <p className="text-xs text-muted-foreground">
                            <span className="font-medium">Tip:</span>{" "}
                            {anomaly.recommendation}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Behavioral Flags */}
      {analysis.behavioral_flags &&
        Object.keys(analysis.behavioral_flags).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase">
                Behavioral Flags
              </h4>
              <div className="flex flex-wrap gap-2">
                {Object.entries(analysis.behavioral_flags).map(
                  ([flag, value], index) => (
                    <motion.div
                      key={flag}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.35 + index * 0.05 }}
                    >
                      <Badge
                        variant="outline"
                        className="text-xs capitalize"
                      >
                        {flag}: {String(value)}
                      </Badge>
                    </motion.div>
                  )
                )}
              </div>
            </div>
          </motion.div>
        )}
    </div>
  );
};

export default ContextAnomalies;
