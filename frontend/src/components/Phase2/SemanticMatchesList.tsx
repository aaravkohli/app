import { motion } from "framer-motion";
import { Database, AlertCircle, CheckCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface SemanticMatch {
  pattern_name?: string;
  similarity_score?: number;
  category?: string;
  description?: string;
}

interface SemanticAnalysis {
  detected_matches?: SemanticMatch[];
  similarity_threshold?: number;
  semantic_description?: string;
}

interface SemanticMatchesListProps {
  analysis?: SemanticAnalysis;
}

const SemanticMatchesList = ({ analysis }: SemanticMatchesListProps) => {
  if (!analysis || !analysis.detected_matches) return null;

  if (analysis.detected_matches.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="p-4 bg-green-50 dark:bg-green-950/20 border-2 border-green-200 dark:border-green-900">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-sm text-green-900 dark:text-green-100">
                No Semantic Matches Found
              </h4>
              <p className="text-xs text-green-700 dark:text-green-300 mt-1">
                This prompt does not closely match known attack patterns in our database.
              </p>
            </div>
          </div>
        </Card>
      </motion.div>
    );
  }

  const sortedMatches = [...analysis.detected_matches].sort(
    (a, b) => (b.similarity_score ?? 0) - (a.similarity_score ?? 0)
  );

  const getCategoryColor = (category?: string): string => {
    switch (category?.toLowerCase()) {
      case "critical":
      case "high-risk":
        return "bg-red-100 dark:bg-red-950/30 text-red-800 dark:text-red-200";
      case "medium":
      case "medium-risk":
        return "bg-yellow-100 dark:bg-yellow-950/30 text-yellow-800 dark:text-yellow-200";
      case "low":
      case "low-risk":
        return "bg-green-100 dark:bg-green-950/30 text-green-800 dark:text-green-200";
      default:
        return "bg-blue-100 dark:bg-blue-950/30 text-blue-800 dark:text-blue-200";
    }
  };

  const getSimilarityColor = (score: number): string => {
    if (score > 0.85) return "text-red-600 dark:text-red-400";
    if (score > 0.7) return "text-orange-600 dark:text-orange-400";
    if (score > 0.5) return "text-yellow-600 dark:text-yellow-400";
    return "text-green-600 dark:text-green-400";
  };

  return (
    <div className="space-y-4">
      {/* Description */}
      {analysis.semantic_description && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-sm text-muted-foreground p-3 bg-muted/20 rounded-md"
        >
          {analysis.semantic_description}
        </motion.p>
      )}

      {/* Matches List */}
      <div className="space-y-3">
        {sortedMatches.map((match, index) => (
          <motion.div
            key={`${match.pattern_name}-${index}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + index * 0.05 }}
          >
            <Card className="p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3">
                {/* Icon */}
                <Database className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />

                {/* Content */}
                <div className="flex-1">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <h4 className="font-semibold text-sm text-foreground">
                        {match.pattern_name || "Known Attack Pattern"}
                      </h4>
                      {match.category && (
                        <Badge
                          className={`mt-1 text-xs ${getCategoryColor(
                            match.category
                          )}`}
                        >
                          {match.category}
                        </Badge>
                      )}
                    </div>

                    {/* Similarity Score */}
                    <div className="text-right">
                      <div
                        className={`font-bold text-lg ${getSimilarityColor(
                          match.similarity_score ?? 0
                        )}`}
                      >
                        {((match.similarity_score ?? 0) * 100).toFixed(0)}%
                      </div>
                      <span className="text-xs text-muted-foreground">
                        match
                      </span>
                    </div>
                  </div>

                  {/* Description */}
                  {match.description && (
                    <p className="text-xs text-muted-foreground mb-3">
                      {match.description}
                    </p>
                  )}

                  {/* Similarity Bar */}
                  <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{
                        width: `${(match.similarity_score ?? 0) * 100}%`,
                      }}
                      transition={{ delay: 0.2 + index * 0.05, duration: 0.5 }}
                      className={`h-full ${
                        (match.similarity_score ?? 0) > 0.85
                          ? "bg-red-500"
                          : (match.similarity_score ?? 0) > 0.7
                            ? "bg-orange-500"
                            : (match.similarity_score ?? 0) > 0.5
                              ? "bg-yellow-500"
                              : "bg-green-500"
                      }`}
                    />
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Threshold Info */}
      {analysis.similarity_threshold !== undefined && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-xs text-muted-foreground p-3 bg-muted/10 rounded-md"
        >
          Matches shown above {(analysis.similarity_threshold * 100).toFixed(0)}% similarity threshold
        </motion.div>
      )}
    </div>
  );
};

export default SemanticMatchesList;
