import { motion } from "framer-motion";
import { Zap, Lightbulb, FileText, HelpCircle, Code } from "lucide-react";

interface ExamplePromptsProps {
  onSelect: (prompt: string) => void;
  disabled?: boolean;
}

const examples = [
  {
    icon: Lightbulb,
    label: "Creative",
    shortPrompt: "Write a poem about autumn",
    fullPrompt: "Write a short poem about the beauty of autumn leaves falling in a quiet forest",
  },
  {
    icon: Code,
    label: "Technical",
    shortPrompt: "Explain HTTPS encryption",
    fullPrompt: "Explain how HTTPS encryption protects data transmitted between a browser and server",
  },
  {
    icon: HelpCircle,
    label: "Research",
    shortPrompt: "Compare energy sources",
    fullPrompt: "What are the key differences between renewable and non-renewable energy sources?",
  },
  {
    icon: FileText,
    label: "Practical",
    shortPrompt: "Quick breakfast ideas",
    fullPrompt: "Suggest 5 healthy breakfast ideas that can be prepared in under 10 minutes",
  },
];

const ExamplePrompts = ({ onSelect, disabled }: ExamplePromptsProps) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="w-full"
    >
      <div className="flex items-center gap-2 mb-3">
        <Zap className="w-4 h-4 text-primary" />
        <span className="text-sm font-medium text-muted-foreground">
          Quick examples
        </span>
        <span className="text-xs text-muted-foreground/60">— click to try</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {examples.map((example, index) => {
          const Icon = example.icon;
          return (
            <motion.button
              key={index}
              variants={itemVariants}
              onClick={() => onSelect(example.fullPrompt)}
              disabled={disabled}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              className="
                group p-3 rounded-xl text-left
                bg-muted/30 hover:bg-muted/50
                border border-border/50 hover:border-primary/30
                transition-all duration-200
                disabled:opacity-50 disabled:cursor-not-allowed
                disabled:hover:scale-100 disabled:hover:y-0
              "
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div className="p-1 rounded-md bg-primary/10 text-primary">
                  <Icon className="w-3 h-3" />
                </div>
                <span className="text-xs font-medium text-primary">{example.label}</span>
              </div>
              <p className="text-sm text-foreground group-hover:text-primary transition-colors line-clamp-2">
                {example.shortPrompt}
              </p>
            </motion.button>
          );
        })}
      </div>
    </motion.div>
  );
};

export default ExamplePrompts;
