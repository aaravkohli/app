/**
 * API Service for PromptGuard Frontend
 * Handles all communication with the backend safe_llm API server
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

interface AnalysisResponse {
  status: "approved" | "blocked";
  prompt: string;
  analysis: {
    risk: number;
    ml_score: number;
    lexical_risk: number;
    benign_offset: number;
    adaptive_phrases: number;
  };
  response?: string;
  blockReason?: string;
  suggestedRewrite?: string;
  analysisTime: number;
  // Vigil-LLM Multi-Scanner Detection (NEW)
  vigil_analysis?: {
    scanners: Record<string, {
      scanner: string;
      detected: boolean;
      confidence: number;
      details: any;
    }>;
    detections: string[];
    aggregated_risk: number;
  };
  // Phase 2 fields
  intent_analysis?: any;
  escalation_analysis?: any;
  semantic_analysis?: any;
  context_anomalies?: any;
  user_risk_profile?: any;
}

interface ErrorResponse {
  error: string;
}

export const apiService = {
  /**
   * Check if API server is running
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      return response.ok;
    } catch (error) {
      console.error("Health check failed:", error);
      return false;
    }
  },

  /**
   * Analyze a prompt for threats and generate response
   * @param prompt - User's input prompt
   * @param enablePhase2 - Enable Phase 2 multi-dimensional analysis
   * @returns Analysis result with status, metrics, response, and optional Phase 2 insights
   */
  async analyzePrompt(prompt: string, enablePhase2: boolean = false): Promise<AnalysisResponse> {
    if (!prompt.trim()) {
      throw new Error("Prompt cannot be empty");
    }

    if (prompt.length > 2000) {
      throw new Error("Prompt exceeds 2000 character limit");
    }

    try {
      console.log(`📤 Sending prompt to API: "${prompt.substring(0, 50)}..."`);
      const url = new URL(`${API_BASE_URL}/analyze`);
      if (enablePhase2) {
        url.searchParams.append("phase2", "true");
      }

      const response = await fetch(url.toString(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || `API error: ${response.status}`);
      }

      const result = await response.json();
      console.log(`📥 Received response for prompt: "${prompt.substring(0, 50)}..."`);
      console.log(`   Status: ${result.status}`);
      console.log(`   Response length: ${result.response?.length || 0} chars`);
      if (result.vigil_analysis) {
        console.log(`   🛡️ Vigil Detections: ${result.vigil_analysis.detections.length} scanners triggered`);
        console.log(`   Vigil Risk Score: ${(result.vigil_analysis.aggregated_risk * 100).toFixed(1)}%`);
      }
      if (enablePhase2 && result.intent_analysis) {
        console.log(`   Phase 2 Intent: ${result.intent_analysis.primary_intent}`);
      }
      console.log(`   Full result:`, result);
      return result;
    } catch (error) {
      console.error("Prompt analysis failed:", error);
      throw error;
    }
  },

  /**
   * Analyze prompt for threats only (lightweight)
   * @param prompt - User's input prompt
   * @returns Risk analysis without LLM response
   */
  async analyzeRiskOnly(
    prompt: string
  ): Promise<Omit<AnalysisResponse, "response" | "blockReason">> {
    if (!prompt.trim()) {
      throw new Error("Prompt cannot be empty");
    }

    try {
      const response = await fetch(`${API_BASE_URL}/analyze/risk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || `API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Risk analysis failed:", error);
      throw error;
    }
  },

  /**
   * Analyze multiple prompts in batch
   * @param prompts - Array of prompts to analyze
   * @returns Array of analysis results
   */
  async analyzeBatch(
    prompts: string[]
  ): Promise<{ results: Array<{ prompt: string; status: string; risk: number }> }> {
    if (!prompts || prompts.length === 0) {
      throw new Error("Prompts array cannot be empty");
    }

    if (prompts.length > 10) {
      throw new Error("Maximum 10 prompts per batch");
    }

    try {
      const response = await fetch(`${API_BASE_URL}/analyze/batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompts }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || `API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Batch analysis failed:", error);
      throw error;
    }
  },

  /**
   * Analyze an uploaded file (PDF/DOCX/TXT)
   * @param file - File to upload
   */
  async analyzeFile(file: File | File[], text?: string): Promise<any> {
    const formData = new FormData();
    if (Array.isArray(file)) {
      file.forEach((f) => formData.append("file", f));
    } else {
      formData.append("file", file);
    }
    if (text && text.trim()) {
      formData.append("text", text.trim());
    }

    try {
      const response = await fetch(`${API_BASE_URL}/analyze/file`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || `API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("File analysis failed:", error);
      throw error;
    }
  },
};

export type { AnalysisResponse };
