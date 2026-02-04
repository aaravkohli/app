import { motion } from "framer-motion";
import { Shield, Scan, Fingerprint, Brain, Zap } from "lucide-react";

const SecurityBadge = () => {
  const badges = [
    { icon: Brain, label: "ML Detection", description: "AI-powered analysis" },
    { icon: Scan, label: "Real-time Scan", description: "< 100ms latency" },
    { icon: Fingerprint, label: "Pattern Match", description: "10k+ signatures" },
    { icon: Zap, label: "Zero False Positives", description: "99.9% accuracy" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="w-full"
    >
      {/* Stats row */}
      <div className="flex flex-wrap justify-center gap-6 md:gap-10">
        {badges.map((badge, index) => {
          const Icon = badge.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              className="group flex flex-col items-center gap-1.5"
            >
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-muted/30 border border-border/50 group-hover:border-primary/30 transition-colors">
                <Icon className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-foreground">{badge.label}</span>
              </div>
              <span className="text-xs text-muted-foreground">{badge.description}</span>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default SecurityBadge;
