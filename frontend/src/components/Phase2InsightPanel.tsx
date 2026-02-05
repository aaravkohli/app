import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Zap,
  BarChart3,
  Database,
  TrendingUp,
  User,
  ChevronDown,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card } from "@/components/ui/card";
import IntentDisplay from "./Phase2/IntentDisplay";
import EscalationIndicator from "./Phase2/EscalationIndicator";
import SemanticMatchesList from "./Phase2/SemanticMatchesList";
import ContextAnomalies from "./Phase2/ContextAnomalies";
import UserRiskProfile from "./Phase2/UserRiskProfile";

interface Phase2Data {
  intent_analysis?: any;
  escalation_analysis?: any;
  semantic_analysis?: any;
  context_anomalies?: any;
  user_risk_profile?: any;
}

interface Phase2InsightPanelProps {
  phase2Data?: Phase2Data;
  isLoading?: boolean;
}

const Phase2InsightPanel = ({
  phase2Data,
  isLoading = false,
}: Phase2InsightPanelProps) => {
  const [expandedTab, setExpandedTab] = useState("intent");
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!phase2Data) return null;

  const hasAnyData =
    phase2Data.intent_analysis ||
    phase2Data.escalation_analysis ||
    phase2Data.semantic_analysis ||
    phase2Data.context_anomalies ||
    phase2Data.user_risk_profile;

  if (!hasAnyData) return null;

  const tabs = [
    {
      id: "intent",
      label: "Intent",
      icon: Zap,
      hasData: !!phase2Data.intent_analysis,
      component: <IntentDisplay analysis={phase2Data.intent_analysis} />,
    },
    {
      id: "escalation",
      label: "Escalation",
      icon: TrendingUp,
      hasData: !!phase2Data.escalation_analysis,
      component: <EscalationIndicator analysis={phase2Data.escalation_analysis} />,
    },
    {
      id: "semantic",
      label: "Semantic",
      icon: Database,
      hasData: !!phase2Data.semantic_analysis,
      component: <SemanticMatchesList analysis={phase2Data.semantic_analysis} />,
    },
    {
      id: "context",
      label: "Behavior",
      icon: BarChart3,
      hasData: !!phase2Data.context_anomalies,
      component: <ContextAnomalies analysis={phase2Data.context_anomalies} />,
    },
    {
      id: "user",
      label: "User",
      icon: User,
      hasData: !!phase2Data.user_risk_profile,
      component: <UserRiskProfile analysis={phase2Data.user_risk_profile} />,
    },
  ].filter((tab) => tab.hasData);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="mt-6 space-y-3"
    >
      {/* Header with Toggle */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 animate-pulse" />
          <h3 className="text-sm font-semibold text-foreground">
            Advanced Security Analysis
          </h3>
        </div>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 hover:bg-muted rounded transition-colors"
          aria-label="Toggle panel"
        >
          <motion.div
            animate={{ rotate: isCollapsed ? -90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          </motion.div>
        </button>
      </div>

      {/* Tabs Panel */}
      <AnimatePresence mode="wait">
        {!isCollapsed && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="overflow-hidden border-gradient bg-gradient-to-br from-background to-muted/20">
              {tabs.length > 0 ? (
                <Tabs
                  value={expandedTab}
                  onValueChange={setExpandedTab}
                  className="w-full"
                >
                  {/* Tabs List */}
                  <TabsList className="w-full justify-start rounded-none border-b bg-muted/30 p-0 h-auto">
                    {tabs.map((tab) => {
                      const TabIcon = tab.icon;
                      return (
                        <TabsTrigger
                          key={tab.id}
                          value={tab.id}
                          className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent px-4 py-3 flex items-center gap-2"
                        >
                          <TabIcon className="w-4 h-4" />
                          <span className="text-sm font-medium">{tab.label}</span>
                        </TabsTrigger>
                      );
                    })}
                  </TabsList>

                  {/* Tab Contents */}
                  {tabs.map((tab) => (
                    <motion.div
                      key={tab.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <TabsContent
                        value={tab.id}
                        className="p-6 m-0 min-h-[300px]"
                      >
                        {isLoading ? (
                          <div className="flex items-center justify-center h-64">
                            <div className="space-y-3 w-full">
                              <div className="h-4 bg-muted rounded animate-pulse" />
                              <div className="h-4 bg-muted rounded animate-pulse w-5/6" />
                              <div className="h-4 bg-muted rounded animate-pulse w-4/6" />
                            </div>
                          </div>
                        ) : (
                          tab.component
                        )}
                      </TabsContent>
                    </motion.div>
                  ))}
                </Tabs>
              ) : (
                <div className="p-6 text-center text-muted-foreground">
                  <p className="text-sm">
                    Advanced analysis data will appear here
                  </p>
                </div>
              )}
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Stats Summary */}
      {tabs.length > 0 && !isCollapsed && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-5 gap-2 px-1"
        >
          {tabs.map((tab) => {
            const TabIcon = tab.icon;
            return (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setExpandedTab(tab.id)}
                className={`p-2 rounded-lg transition-colors text-xs font-medium flex flex-col items-center gap-1 ${
                  expandedTab === tab.id
                    ? "bg-primary/10 text-primary"
                    : "bg-muted/50 text-muted-foreground hover:bg-muted"
                }`}
              >
                <TabIcon className="w-4 h-4" />
                <span className="text-xs text-center">{tab.label}</span>
              </motion.button>
            );
          })}
        </motion.div>
      )}
    </motion.div>
  );
};

export default Phase2InsightPanel;
