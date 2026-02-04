import { motion } from "framer-motion";
import { TrendingUp, CheckCircle2, AlertTriangle } from "lucide-react";

interface SecurityConfidenceProps {
  mlRisk: number;
  lexicalRisk: number;
  benignOffset: number;
  status: "approved" | "blocked";
}

const SecurityConfidence = ({
  mlRisk,
  lexicalRisk,
  benignOffset,
  status,
}: SecurityConfidenceProps) => {
  // Confidence = how sure the system is about its decision
  const baseConfidence = (mlRisk + lexicalRisk) / 2;
  const adjustedConfidence = Math.max(
    0,
    Math.min(100, baseConfidence * (1 - benignOffset / 100))
  );
  const confidence = Math.round(adjustedConfidence);

  const getConfidenceMessage = () => {
    if (confidence > 90) {
      return status === "blocked"
        ? "Very high confidence this is a threat"
        : "Very high confidence this is safe";
    }
    if (confidence > 70) {
      return status === "blocked"
        ? "High confidence, threat pattern detected"
        : "High confidence, safe to process";
    }
    if (confidence > 50) {
      return status === "blocked"
        ? "Moderate confidence, some concerning patterns"
        : "Moderate confidence, appears safe";
    }
    return "Borderline case — consider reviewing";
  };

  const getConfidenceColor = () => {
    if (confidence > 85) return "from-safe to-safe/60";
    if (confidence > 70) return "from-primary to-primary/60";
    if (confidence > 50) return "from-warning to-warning/60";
    return "from-muted to-muted/60";
  };

  const getConfidenceBg = () => {
    if (confidence > 85) return "bg-safe/10";
    if (confidence > 70) return "bg-primary/10";
    if (confidence > 50) return "bg-warning/10";
    return "bg-muted/10";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className={`p-4 rounded-xl border border-border/50 ${getConfidenceBg()}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Decision Confidence
          </span>
          {confidence > 75 && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
            >
              <CheckCircle2 className="w-4 h-4 text-safe" />
            </motion.div>
          )}
          {confidence < 60 && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
            >
              <AlertTriangle className="w-4 h-4 text-warning" />
            </motion.div>
          )}
        </div>
        <motion.div
          key={confidence}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2"
        >
          <span className="text-lg font-bold text-foreground">{confidence}%</span>
          <TrendingUp className="w-4 h-4 text-primary opacity-50" />
        </motion.div>
      </div>

      {/* Visual meter */}
      <div className="relative h-2 bg-muted rounded-full overflow-hidden mb-3">
        <motion.div
          className={`h-full rounded-full bg-gradient-to-r ${getConfidenceColor()}`}
          initial={{ width: 0 }}
          animate={{ width: `${confidence}%` }}
          transition={{
            duration: 0.8,
            ease: "easeOut",
          }}
        />
        {/* Shimmer effect */}
        <motion.div
          className="absolute inset-y-0 w-1/4 bg-white/30 blur-sm"
          initial={{ x: "-100%" }}
          animate={{ x: "400%" }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      </div>

      {/* Interpretation text */}
      <motion.p
        key={`confidence-${confidence}`}
        initial={{ opacity: 0, y: -5 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-xs text-muted-foreground leading-relaxed"
      >
        {getConfidenceMessage()}
        {confidence < 70 && confidence > 50 && (
          <span className="block mt-1 text-warning">
            💡 Tip: The system detected ambiguous signals. Review carefully if needed.
          </span>
        )}
      </motion.p>

      {/* Confidence breakdown */}
      <div className="mt-3 pt-3 border-t border-border/30">
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="flex flex-col items-center">
            <span className="text-muted-foreground font-mono text-[10px]">
              ML: {mlRisk}%
            </span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-muted-foreground font-mono text-[10px]">
              Pattern: {lexicalRisk}%
            </span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-safe font-mono text-[10px]">
              Benign: {benignOffset}%
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default SecurityConfidence;
