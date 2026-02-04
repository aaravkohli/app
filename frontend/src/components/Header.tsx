import { motion } from "framer-motion";
import { Shield, Github, Lock, CheckCircle2 } from "lucide-react";

const Header = () => {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full px-4 md:px-8 py-4 flex items-center justify-between border-b border-border/30"
    >
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/20 rounded-xl blur-lg animate-glow-pulse" />
          <div className="relative p-2.5 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
            <Shield className="w-6 h-6 text-primary" />
          </div>
        </div>
        <div>
          <h1 className="text-lg font-semibold text-foreground">
            Prompt<span className="gradient-text">Guard</span>
          </h1>
          <p className="text-xs text-muted-foreground -mt-0.5">
            AI Security Gateway
          </p>
        </div>
      </div>

      {/* Center - Security Status (prominent) */}
      <div className="hidden md:flex items-center gap-3">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="flex items-center gap-3 px-4 py-2 rounded-full bg-safe/10 border border-safe/30 shadow-lg shadow-safe/10"
        >
          <div className="relative">
            <div className="absolute inset-0 bg-safe rounded-full blur-sm animate-pulse opacity-50" />
            <div className="relative w-2.5 h-2.5 rounded-full bg-safe" />
          </div>
          <div className="flex items-center gap-2">
            <Lock className="w-3.5 h-3.5 text-safe" />
            <span className="text-sm font-medium text-safe">Gateway Protected</span>
          </div>
          <CheckCircle2 className="w-4 h-4 text-safe" />
        </motion.div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Mobile security indicator */}
        <div className="md:hidden flex items-center gap-2 px-3 py-1.5 rounded-full bg-safe/10 border border-safe/20">
          <div className="w-2 h-2 rounded-full bg-safe animate-pulse" />
          <span className="text-xs font-medium text-safe">Protected</span>
        </div>
        
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 rounded-lg hover:bg-muted/50 text-muted-foreground hover:text-foreground transition-colors"
        >
          <Github className="w-5 h-5" />
        </a>
      </div>
    </motion.header>
  );
};

export default Header;
