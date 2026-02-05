"""
Request and Response schemas with Pydantic for type-safe validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum


# ==========================================
# Enums
# ==========================================
class DecisionAction(str, Enum):
    APPROVED = "approved"
    BLOCKED = "blocked"
    CHALLENGE = "challenge"
    AUDIT = "audit"
    REWRITE = "rewrite"
    ESCALATE = "escalate"


class EscalationLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IntentType(str, Enum):
    """Seven attack intent types from Phase 2"""
    JAILBREAK = "jailbreak"
    PROMPT_INJECTION = "prompt_injection"
    DATA_EXTRACTION = "data_extraction"
    ADVERSARIAL = "adversarial"
    MISUSE = "misuse"
    CONFUSION = "confusion"
    BENIGN = "benign"


# ==========================================
# Request Schemas
# ==========================================
class AnalysisRequest(BaseModel):
    """Request for security analysis"""
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User prompt to analyze"
    )
    user_id: Optional[str] = Field(
        None,
        description="Optional user ID for context tracking"
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for conversation context"
    )
    policy: Optional[str] = Field(
        "default",
        description="Policy template: strict, balanced, or permissive"
    )
    include_rewrite: bool = Field(
        False,
        description="Include suggested rewrite for blocked prompts"
    )
    
    @validator("prompt")
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace")
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Explain transformers in simple words",
                "user_id": "user123",
                "policy": "balanced",
                "include_rewrite": True
            }
        }


class BatchAnalysisRequest(BaseModel):
    """Request for batch analysis"""
    
    prompts: List[str] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of prompts to analyze"
    )
    policy: Optional[str] = Field("default")
    
    @validator("prompts")
    def validate_prompts(cls, v):
        for prompt in v:
            if not prompt.strip():
                raise ValueError("All prompts must be non-empty")
        return [p.strip() for p in v]
    
    class Config:
        schema_extra = {
            "example": {
                "prompts": [
                    "What is machine learning?",
                    "How do transformers work?"
                ]
            }
        }


# ==========================================
# Response Schemas
# ==========================================
class ThreatIntentAnalysis(BaseModel):
    """Intent classification results"""
    
    primary_intent: str = Field(
        description="Primary detected intent (e.g., jailbreak_attempt)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1)"
    )
    all_intents: List[Dict[str, Any]] = Field(
        description="All detected intents with scores"
    )
    risk_factor: float = Field(
        ge=0.0,
        le=1.0,
        description="Risk weight for this intent"
    )


# ==========================================
# Phase 2: Intent & Escalation Analysis
# ==========================================
class IntentAnalysisResponse(BaseModel):
    """Phase 2: Intent classification with risk scoring"""
    
    primary_intent: IntentType = Field(
        description="Seven-category intent classification"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Intent classification confidence"
    )
    secondary_intent: Optional[IntentType] = None
    secondary_confidence: Optional[float] = None
    attack_type_description: str = Field(
        description="Human-readable attack type description"
    )
    intent_risk_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Risk weight for detected intent"
    )


class EscalationAnalysisResponse(BaseModel):
    """Phase 2: Escalation detection"""
    
    is_escalating: bool = Field(
        description="Whether attack sophistication is escalating"
    )
    escalation_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Escalation severity (0-1)"
    )
    escalation_level: EscalationLevel
    patterns_detected: List[str] = Field(
        default_factory=list,
        description="Detected escalation patterns"
    )
    history_length: int = Field(
        description="Number of turns analyzed"
    )
    unique_attack_types: int = Field(
        description="Number of different attack types seen"
    )


class SemanticSimilarityMatch(BaseModel):
    """Phase 2: Semantic match to known attack pattern"""
    
    similarity_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Cosine similarity to known pattern"
    )
    matched_attack_pattern: str = Field(
        description="The known attack pattern matched"
    )
    attack_type: str = Field(
        description="Type of matched attack"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the match"
    )


class PromptInjectionTechniques(BaseModel):
    """Phase 2: Detected prompt injection techniques"""
    
    has_injection_markers: bool
    detected_techniques: List[str] = Field(
        default_factory=list,
        description="Specific injection techniques found"
    )
    injection_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall injection attack score"
    )
    technique_count: int


class SemanticAnalysisResponse(BaseModel):
    """Phase 2: Full semantic analysis results"""
    
    semantic_matches: List[SemanticSimilarityMatch] = Field(
        default_factory=list,
        description="Similar known attack patterns"
    )
    prompt_injection_techniques: PromptInjectionTechniques
    overall_semantic_risk: float = Field(
        ge=0.0,
        le=1.0,
        description="Combined semantic risk score"
    )


class ContextAnomalyDetection(BaseModel):
    """Phase 2: Conversation context anomalies"""
    
    has_anomalies: bool
    anomaly_score: float = Field(ge=0.0, le=1.0)
    detected_patterns: List[str] = Field(
        default_factory=list,
        description="Anomalous patterns found"
    )
    block_rate: float = Field(
        ge=0.0,
        le=1.0,
        description="Rate of blocked prompts in session"
    )
    risk_increase: float = Field(
        description="Change in risk from early to recent turns"
    )
    session_age_minutes: float
    turn_number: int


class UserProfileRisk(BaseModel):
    """Phase 2: User-specific risk assessment"""
    
    user_id: str
    abuse_score: float = Field(
        ge=0.0,
        le=1.0,
        description="User abuse/misuse score"
    )
    is_suspicious: bool
    total_requests: int
    block_rate: float = Field(ge=0.0, le=1.0)
    average_risk_score: float = Field(ge=0.0, le=1.0)
    unique_intents: List[str]
    request_frequency: float = Field(
        description="Requests per minute"
    )


class ContentRiskAnalysis(BaseModel):
    """Content-level risk analysis"""
    
    lexical_risk: float = Field(
        ge=0.0,
        le=1.0,
        description="Risk from regex patterns"
    )
    semantic_risk: float = Field(
        ge=0.0,
        le=1.0,
        description="Risk from semantic similarity"
    )
    benign_offset: float = Field(
        ge=0.0,
        le=1.0,
        description="Benign pattern offset"
    )
    suspicious_entities: List[str] = Field(
        default_factory=list,
        description="Named entities detected"
    )
    overall_content_risk: float = Field(
        ge=0.0,
        le=1.0
    )


class ContextRiskAnalysis(BaseModel):
    """Conversation context risk"""
    
    turn_number: int
    previous_blocks: int
    block_rate: float = Field(ge=0.0, le=1.0)
    escalation_level: EscalationLevel
    context_multiplier: float
    pattern_risk: float = Field(ge=0.0, le=1.0)


class ThreatAnalysisDetail(BaseModel):
    """Complete threat analysis breakdown"""
    
    intent: ThreatIntentAnalysis
    content_risk: ContentRiskAnalysis
    context_risk: Optional[ContextRiskAnalysis] = None
    risk_score: float = Field(ge=0.0, le=1.0)
    ml_score: float = Field(ge=0.0, le=1.0)


class AnalysisResponse(BaseModel):
    """Response for analysis endpoint (now with Phase 2 multi-dimensional threat analysis)"""
    
    status: DecisionAction = Field(
        description="Security decision"
    )
    decision_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in decision"
    )
    prompt: str = Field(
        description="Echo of user prompt"
    )
    
    # Phase 1: Basic threat analysis
    analysis: ThreatAnalysisDetail = Field(
        description="Detailed threat analysis"
    )
    
    # Phase 2: Multi-dimensional threat analysis
    intent_analysis: Optional[IntentAnalysisResponse] = None
    escalation_analysis: Optional[EscalationAnalysisResponse] = None
    semantic_analysis: Optional[SemanticAnalysisResponse] = None
    context_anomalies: Optional[ContextAnomalyDetection] = None
    user_risk_profile: Optional[UserProfileRisk] = None
    
    # Reasoning
    response: Optional[str] = Field(
        None,
        description="AI-generated response (if approved)"
    )
    block_reason: Optional[str] = Field(
        None,
        description="Reason if blocked"
    )
    suggested_rewrite: Optional[str] = Field(
        None,
        description="Suggested safe rephrase"
    )
    
    # Metadata
    analysis_time_ms: float = Field(
        description="Analysis duration in milliseconds"
    )
    cache_hit: bool = Field(
        default=False,
        description="Whether result was cached"
    )
    request_id: str = Field(
        description="Unique request identifier"
    )


class RiskOnlyResponse(BaseModel):
    """Lightweight risk-only response"""
    
    status: str = Field(description="safe or blocked")
    analysis: Dict[str, float] = Field(
        description="Risk metrics only"
    )
    analysis_time_ms: float
    cache_hit: bool = Field(default=False)


class BatchAnalysisResponse(BaseModel):
    """Batch analysis response"""
    
    results: List[Dict[str, Any]] = Field(
        description="Results for each prompt"
    )
    total_time_ms: float


class HealthCheckResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(default="operational")
    version: str
    gateway: str = "PromptGuard - Secure AI Gateway"
    timestamp: str
    uptime_seconds: float


class ErrorResponse(BaseModel):
    """Error response"""
    
    error: str = Field(description="Error message")
    error_code: Optional[str] = Field(None)
    details: Optional[Dict[str, Any]] = Field(None)
    request_id: Optional[str] = Field(None)
    timestamp: str


# ==========================================
# Internal Schemas (not exposed in API)
# ==========================================
class MLInferenceResult(BaseModel):
    """ML model inference result"""
    
    label: str
    score: float
    raw_output: Dict[str, Any] = {}


class CacheEntry(BaseModel):
    """Cache entry structure"""
    
    key: str
    value: Dict[str, Any]
    created_at: str
    ttl: int
    hits: int = 0
