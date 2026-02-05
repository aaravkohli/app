import { motion } from "framer-motion";
import {
  ShieldAlert,
  Shield,
  Zap,
  Database,
  AlertTriangle,
  Lock,
  Brain,
} from "lucide-react";
import { Card } from "@/components/ui/card";

interface IntentAnalysis {
  primary_intent?: string;
  intent_scores?: Record<string, number>;
  confidence?: number;
  intent_description?: string;
}

interface IntentDisplayProps {
  analysis?: IntentAnalysis;
}

const IntentDisplay = ({ analysis }: IntentDisplayProps) => {
  if (!analysis) return null;

  const intentIcons: Record<string, React.ComponentType<any>> = {
    "instruction-override": Lock,
    "prompt-extraction": Database,
    "role-hijacking": Zap,
    "jailbreak-attempt": ShieldAlert,
    "data-exfiltration": Database,
    "policy-violation": AlertTriangle,
    "other": Brain,
  };

  const intentColors: Record<string, string> = {
    "instruction-override": "text-red-500",
    "prompt-extraction": "text-orange-500",
    "role-hijacking": "text-yellow-500",
    "jailbreak-attempt": "text-red-600",
    "data-exfiltration": "text-orange-600",
    "policy-violation": "text-yellow-600",
    "other": "text-blue-500",
  };

  const intentBgColors: Record<string, string> = {
    "instruction-override": "bg-red-50 dark:bg-red-950/20",
    "prompt-extraction": "bg-orange-50 dark:bg-orange-950/20",
    "role-hijacking": "bg-yellow-50 dark:bg-yellow-950/20",
    "jailbreak-attempt": "bg-red-50 dark:bg-red-950/20",
    "data-exfiltration": "bg-orange-50 dark:bg-orange-950/20",
    "policy-violation": "bg-yellow-50 dark:bg-yellow-950/20",
    "other": "bg-blue-50 dark:bg-blue-950/20",
  };

  const sortedIntents = Object.entries(analysis.intent_scores || {}).sort(
    ([, a], [, b]) => b - a
  );

  return (
    <div className="space-y-4">
      {/* Primary Intent */}
      {analysis.primary_intent && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card
            className={`p-4 border-2 ${
              intentBgColors[analysis.primary_intent] ||
              "bg-blue-50 dark:bg-blue-950/20"
            }`}
          >
            <div className="flex items-start gap-3">
              {(() => {
                const Icon =
                  intentIcons[analysis.primary_intent] || ShieldAlert;
                return (
                  <Icon
                    className={`w-5 h-5 mt-0.5 flex-shrink-0 ${
                      intentColors[analysis.primary_intent] || "text-blue-500"
                    }`}
                  />
                );
              })()}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-semibold text-sm capitalize">
                    {analysis.primary_intent.replace(/-/g, " ")}
                  </h4>
                  {analysis.confidence !== undefined && (
                    <span className="text-xs font-medium px-2 py-1 rounded bg-white/50 dark:bg-black/30">
                      {(analysis.confidence * 100).toFixed(1)}% confidence
                    </span>
                  )}
                </div>
                {analysis.intent_description && (
                  <p className="text-xs text-muted-foreground">
                    {analysis.intent_description}
                  </p>
                )}
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Intent Scores Bar Chart */}
      {sortedIntents.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-muted-foreground uppercase">
              Attack Type Analysis
            </h4>
            <div className="space-y-2">
              {sortedIntents.slice(0, 7).map(([intent, score], index) => (
                <motion.div
                  key={intent}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.25 + index * 0.05 }}
                  className="flex items-center gap-2"
                >
                  {/* Label */}
                  <div className="w-24 text-xs font-medium text-muted-foreground capitalize">
                    {intent.replace(/-/g, " ")}
                  </div>

                  {/* Bar */}
                  <div className="flex-1 h-6 bg-muted rounded-sm overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${score * 100}%` }}
                      transition={{ delay: 0.3 + index * 0.05, duration: 0.5 }}
                      className={`h-full ${
                        score > 0.7
                          ? "bg-red-500"
                          : score > 0.4
                            ? "bg-yellow-500"
                            : "bg-green-500"
                      }`}
                    />
                  </div>

                  {/* Score */}
                  <div className="w-12 text-right text-xs font-semibold">
                    {(score * 100).toFixed(0)}%
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Legend */}
      {sortedIntents.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-3 gap-2 mt-4"
        >
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-sm bg-red-500" />
            <span className="text-muted-foreground">High Risk</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-sm bg-yellow-500" />
            <span className="text-muted-foreground">Medium Risk</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <div className="w-3 h-3 rounded-sm bg-green-500" />
            <span className="text-muted-foreground">Low Risk</span>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default IntentDisplay;
