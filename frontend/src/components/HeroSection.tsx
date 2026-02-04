import { motion } from "framer-motion";
import { ShieldCheck, ArrowRight, Sparkles } from "lucide-react";

const HeroSection = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="text-center mb-8 md:mb-10"
    >
      {/* Trust badge above headline */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
        className="inline-flex items-center gap-2 px-4 py-2 mb-6 rounded-full bg-primary/10 border border-primary/20"
      >
        <ShieldCheck className="w-4 h-4 text-primary" />
        <span className="text-sm font-medium text-primary">Enterprise-grade prompt security</span>
        <Sparkles className="w-3.5 h-3.5 text-primary/70" />
      </motion.div>

      {/* Main headline - action-oriented */}
      <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-4 leading-tight">
        Stop Injection Attacks
        <br />
        <span className="gradient-text">Before They Reach Your LLM</span>
      </h2>
      
      {/* Subheadline - clear value prop */}
      <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-6">
        Every prompt is scanned in real-time. Threats are blocked instantly.
        <br className="hidden md:block" />
        Your AI stays safe, your users stay productive.
      </p>

      {/* Quick trust indicators */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex flex-wrap justify-center gap-4 md:gap-6 text-sm text-muted-foreground"
      >
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-safe" />
          <span>No API keys exposed</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-safe" />
          <span>SOC 2 compliant</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-safe" />
          <span>Works with any LLM</span>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default HeroSection;
