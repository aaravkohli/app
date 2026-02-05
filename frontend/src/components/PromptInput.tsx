import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, X, Shield, AlertCircle, Keyboard, CheckCircle2, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: (enablePhase2: boolean) => void;
  isAnalyzing: boolean;
  maxLength?: number;
}

const PromptInput = ({
  value,
  onChange,
  onSubmit,
  isAnalyzing,
  maxLength = 2000,
}: PromptInputProps) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [isFocused, setIsFocused] = useState(false);
  const [enablePhase2, setEnablePhase2] = useState(() => {
    // Load from localStorage
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("promptguard_phase2_enabled");
      return saved === "true";
    }
    return false;
  });
  const [ripples, setRipples] = useState<{ id: number; x: number; y: number }[]>([]);

  const charCount = value.length;
  const charPercentage = (charCount / maxLength) * 100;
  const isNearLimit = charPercentage > 80;
  const isAtLimit = charPercentage >= 100;

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 300)}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && !isAnalyzing && value.trim()) {
      e.preventDefault();
      onSubmit(enablePhase2);
    }
  };

  const handleButtonClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const id = Date.now();
    
    setRipples((prev) => [...prev, { id, x, y }]);
    setTimeout(() => {
      setRipples((prev) => prev.filter((r) => r.id !== id));
    }, 600);
    
    onSubmit(enablePhase2);
  };

  const handlePhase2Toggle = () => {
    const newValue = !enablePhase2;
    setEnablePhase2(newValue);
    // Save to localStorage
    if (typeof window !== "undefined") {
      localStorage.setItem("promptguard_phase2_enabled", String(newValue));
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="w-full"
    >
      <div
        className={`
          relative glass-card transition-all duration-300
          ${isFocused ? "ring-2 ring-primary/50 glow-primary" : ""}
        `}
      >
        {/* Security checkpoint indicator */}
        <div className="absolute -top-3 left-6 flex items-center gap-2 px-3 py-1 rounded-full bg-card border border-border/50 text-xs">
          <Shield className="w-3 h-3 text-primary" />
          <span className="text-muted-foreground">Security checkpoint active</span>
          <div className="w-1.5 h-1.5 rounded-full bg-safe animate-pulse" />
        </div>

        {/* Scanning animation overlay when analyzing */}
        <AnimatePresence>
          {isAnalyzing && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 rounded-xl overflow-hidden pointer-events-none z-10"
            >
              <div className="absolute inset-0 bg-primary/5" />
              <div className="absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-primary/20 to-transparent scan-animation" />
              {/* Scanning lines effect */}
              <div className="absolute inset-0 opacity-30">
                {[...Array(8)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute left-0 right-0 h-px bg-primary/50"
                    style={{ top: `${12.5 * (i + 1)}%` }}
                    initial={{ scaleX: 0, opacity: 0 }}
                    animate={{ scaleX: 1, opacity: [0, 1, 0] }}
                    transition={{ 
                      duration: 1, 
                      delay: i * 0.1,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="p-4 md:p-6 pt-6">
          {/* Header with enhanced guidance */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-foreground">
                  Enter your prompt
                </span>
                <span className="text-xs text-muted-foreground">
                  — it will be analyzed before processing
                </span>
              </div>
            </div>
            <AnimatePresence>
              {value && (
                <motion.button
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  onClick={() => onChange("")}
                  className="p-1.5 rounded-md hover:bg-muted/50 text-muted-foreground hover:text-foreground transition-colors"
                  title="Clear prompt (Esc)"
                >
                  <X className="w-4 h-4" />
                </motion.button>
              )}
            </AnimatePresence>
          </div>

          {/* Textarea with better placeholder */}
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value.slice(0, maxLength))}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyDown={handleKeyDown}
            placeholder="Type your prompt here... Example: 'Explain quantum computing in simple terms' or 'Write a product description for...'"
            disabled={isAnalyzing}
            className="
              w-full min-h-[120px] bg-transparent resize-none
              text-foreground placeholder:text-muted-foreground/40
              focus:outline-none text-base md:text-lg leading-relaxed
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          />

          {/* Footer with enhanced UX */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-border/50">
            {/* Left side - Character counter + status + Phase 2 toggle */}
            <div className="flex items-center gap-4">
              {/* Character counter */}
              <div className="flex items-center gap-2">
                <div className="w-20 h-1.5 bg-muted rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full rounded-full transition-colors ${
                      isAtLimit
                        ? "bg-danger"
                        : isNearLimit
                        ? "bg-warning"
                        : "bg-primary/50"
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(charPercentage, 100)}%` }}
                    transition={{ duration: 0.2 }}
                  />
                </div>
                <span
                  className={`text-xs font-mono transition-colors ${
                    isAtLimit
                      ? "text-danger"
                      : isNearLimit
                      ? "text-warning"
                      : "text-muted-foreground"
                  }`}
                >
                  {charCount.toLocaleString()}/{maxLength.toLocaleString()}
                </span>
              </div>
              
              <AnimatePresence>
                {isNearLimit && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    className="flex items-center gap-1 text-warning"
                  >
                    <AlertCircle className="w-3 h-3" />
                    <span className="text-xs">Near limit</span>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Ready indicator when has text */}
              <AnimatePresence>
                {value.trim() && !isAnalyzing && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    className="flex items-center gap-1 text-safe"
                  >
                    <CheckCircle2 className="w-3 h-3" />
                    <span className="text-xs">Ready to analyze</span>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Phase 2 Toggle */}
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                onClick={handlePhase2Toggle}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-md transition-colors border ${
                  enablePhase2
                    ? "bg-purple-500/10 border-purple-500/30 text-purple-600 dark:text-purple-400 hover:bg-purple-500/20"
                    : "bg-muted/30 border-border/50 text-muted-foreground hover:bg-muted/50"
                }`}
                title="Enable advanced multi-dimensional threat analysis"
              >
                <Zap className="w-3 h-3" />
                <span className="text-xs font-medium">Phase 2</span>
                {enablePhase2 && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="inline-block ml-0.5"
                  >
                    ✓
                  </motion.span>
                )}
              </motion.button>
            </div>

            {/* Right side - Shortcut hint + Submit button */}
            <div className="flex items-center gap-4">
              {/* Keyboard shortcut - more prominent */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="hidden md:flex items-center gap-1.5 px-2 py-1 rounded-md bg-muted/30 border border-border/50"
              >
                <Keyboard className="w-3 h-3 text-muted-foreground" />
                <kbd className="text-xs font-mono text-muted-foreground">⌘</kbd>
                <span className="text-xs text-muted-foreground">+</span>
                <kbd className="text-xs font-mono text-muted-foreground">↵</kbd>
              </motion.div>

              {/* Submit button - enhanced */}
              <Button
                onClick={handleButtonClick}
                disabled={!value.trim() || isAnalyzing}
                className={`
                  relative overflow-hidden
                  px-6 py-2.5 rounded-lg font-semibold
                  transition-all duration-200
                  disabled:opacity-50 disabled:cursor-not-allowed
                  ${!value.trim() || isAnalyzing 
                    ? 'bg-muted text-muted-foreground' 
                    : 'btn-primary text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:scale-[1.02]'
                  }
                `}
              >
                {ripples.map((ripple) => (
                  <span
                    key={ripple.id}
                    className="ripple"
                    style={{ left: ripple.x, top: ripple.y, width: 20, height: 20 }}
                  />
                ))}
                <span className="relative z-10 flex items-center gap-2">
                  {isAnalyzing ? (
                    <>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      >
                        <Shield className="w-4 h-4" />
                      </motion.div>
                      <span>Scanning...</span>
                    </>
                  ) : (
                    <>
                      <Shield className="w-4 h-4" />
                      <span>Analyze & Generate</span>
                      <Send className="w-4 h-4" />
                    </>
                  )}
                </span>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default PromptInput;
