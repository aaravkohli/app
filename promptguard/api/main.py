"""
FastAPI Application - Async-first security gateway
"""

import uuid
import time
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from promptguard.config.settings import settings
from promptguard.api.schemas import (
    AnalysisRequest, AnalysisResponse, RiskOnlyResponse,
    BatchAnalysisRequest, BatchAnalysisResponse,
    ThreatAnalysisDetail, ContentRiskAnalysis, ThreatIntentAnalysis,
    HealthCheckResponse, ErrorResponse, EscalationLevel,
    DecisionAction, IntentType,
    IntentAnalysisResponse, EscalationAnalysisResponse,
    SemanticAnalysisResponse, ContextAnomalyDetection, UserProfileRisk,
    SemanticSimilarityMatch, PromptInjectionTechniques
)
from promptguard.security_engine.detector import AsyncSecurityDetector
from promptguard.security_engine.phase2_detector import Phase2SecurityDetector
from promptguard.cache.caching import CacheStrategy, RequestDeduplicator
from promptguard.observability.metrics import MetricsCollector

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Global instances
detector: Optional[AsyncSecurityDetector] = None
phase2_detector: Optional[Phase2SecurityDetector] = None
cache: Optional[CacheStrategy] = None
deduplicator: Optional[RequestDeduplicator] = None
metrics: Optional[MetricsCollector] = None
startup_time: Optional[datetime] = None


# ==========================================
# Startup / Shutdown Events
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    
    global detector, phase2_detector, cache, deduplicator, metrics, startup_time
    
    # ========== STARTUP ==========
    startup_time = datetime.now()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    try:
        # Initialize Phase 1 detector
        logger.info("Initializing Phase 1 security detector...")
        detector = AsyncSecurityDetector(settings)
        await detector.initialize()
        
        # Initialize Phase 2 detector (wraps Phase 1)
        if settings.ENABLE_INTENT_CLASSIFICATION or settings.ENABLE_SEMANTIC_ANALYSIS:
            logger.info("Initializing Phase 2 multi-dimensional threat detection...")
            phase2_detector = Phase2SecurityDetector(detector, settings)
            await phase2_detector.initialize()
            logger.info("✅ Phase 2 security intelligence initialized")
        
        # Initialize caching
        logger.info("Initializing cache layer...")
        cache = CacheStrategy(enable_memory=True, enable_redis=settings.ENABLE_REDIS)
        
        # Initialize deduplicator
        deduplicator = RequestDeduplicator()
        
        # Initialize metrics
        metrics = MetricsCollector()
        
        logger.info("✅ All systems initialized successfully")
        logger.info(f"API available at http://{settings.HOST}:{settings.PORT}")
        if phase2_detector:
            logger.info("Phase 2 features enabled: Intent classification, Semantic analysis, Context tracking")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield  # App runs here
    
    # ========== SHUTDOWN ==========
    logger.info("Shutting down...")
    
    try:
        if detector:
            await detector.cleanup()
        if cache:
            cache.clear()
        
        logger.info("✅ Shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# ==========================================
# FastAPI Application
# ==========================================
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade AI security gateway with multi-layer threat detection",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)


# ==========================================
# Request/Response Middleware
# ==========================================
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    """Add request ID and timing to all requests"""
    
    request.state.request_id = str(uuid.uuid4())
    request.state.start_time = time.time()
    
    response = await call_next(request)
    
    # Add timing headers
    process_time = time.time() - request.state.start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request.state.request_id
    
    return response


# ==========================================
# Health Check Endpoint
# ==========================================
@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint for monitoring
    Returns system status and uptime
    """
    
    uptime = (datetime.now() - startup_time).total_seconds()
    
    return HealthCheckResponse(
        status="operational",
        version=settings.APP_VERSION,
        timestamp=datetime.now().isoformat(),
        uptime_seconds=uptime
    )


# ==========================================
# Main Analysis Endpoint
# ==========================================
@app.post("/api/v2/analyze", response_model=AnalysisResponse)
async def analyze(
    request_data: AnalysisRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    phase2: bool = Query(False, description="Enable Phase 2 multi-dimensional analysis")
) -> AnalysisResponse:
    """
    Analyze prompt for security threats and generate AI response
    
    - **prompt**: User's prompt to analyze
    - **user_id**: Optional user ID for context tracking
    - **session_id**: Optional session ID for conversation history
    - **policy**: Security policy (strict, balanced, permissive)
    - **include_rewrite**: Include suggested rewrite for blocked prompts
    - **phase2**: Enable Phase 2 multi-dimensional threat detection
    """
    
    request_id = request.state.request_id
    start_time = time.time()
    
    try:
        # Validate prompt
        prompt = request_data.prompt.strip()
        
        if len(prompt) < 1:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if len(prompt) > settings.MAX_PROMPT_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt exceeds {settings.MAX_PROMPT_LENGTH} character limit"
            )
        
        # Use Phase 2 if available and requested
        use_phase2 = phase2 and phase2_detector is not None
        cache_key = f"{prompt}:phase2:{use_phase2}"
        
        # Check cache first
        cache_hit = False
        cached_result = await cache.get(cache_key)
        
        if cached_result:
            cache_hit = True
            analysis_data = cached_result
            logger.info(f"Cache hit for prompt (Phase2={use_phase2}): {prompt[:50]}...")
        else:
            if use_phase2:
                # Run Phase 2 multi-dimensional analysis
                logger.info(f"Analyzing prompt with Phase 2 (user={request_data.user_id}, session={request_data.session_id}): {prompt[:50]}...")
                analysis_data = await phase2_detector.analyze_full_phase2(
                    prompt=prompt,
                    user_id=request_data.user_id,
                    session_id=request_data.session_id
                )
            else:
                # Run Phase 1 base analysis
                logger.info(f"Analyzing prompt with Phase 1: {prompt[:50]}...")
                analysis_data = await deduplicator.execute_once(prompt, detector)
            
            # Cache result
            background_tasks.add_task(
                cache.set,
                cache_key,
                analysis_data,
                ttl=settings.CACHE_TTL
            )
        
        # Record metrics
        analysis_time_ms = round((time.time() - start_time) * 1000, 2)
        
        if metrics:
            metrics.record_analysis(
                duration_ms=analysis_time_ms,
                risk_score=(
                    analysis_data.get('combined_risk_score', 0.0)
                    if use_phase2 else analysis_data.get("risk_score", 0.0)
                ),
                cache_hit=cache_hit,
                policy=request_data.policy
            )
        
        # Extract base analysis
        base_analysis = (
            analysis_data.get('base_analysis', analysis_data)
            if use_phase2 else analysis_data
        )
        
        # Extract Vigil scan results if available
        vigil_analysis_data = base_analysis.get('vigil_scan', {})
        vigil_analysis = None
        
        if vigil_analysis_data and not vigil_analysis_data.get('unavailable'):
            from promptguard.api.schemas import VigilAnalysisResponse, VigilScannerResult
            
            # Convert vigil results to response schema
            scanners = {}
            for scanner_name, scanner_result in vigil_analysis_data.get('scanners', {}).items():
                if isinstance(scanner_result, dict):
                    scanners[scanner_name] = VigilScannerResult(**scanner_result)
            
            vigil_analysis = VigilAnalysisResponse(
                scanners=scanners,
                detections=vigil_analysis_data.get('detections', []),
                risk_indicators=vigil_analysis_data.get('risk_indicators', []),
                aggregated_risk=vigil_analysis_data.get('aggregated_risk', 0.0),
                timestamp=vigil_analysis_data.get('timestamp', datetime.now().isoformat())
            )
        
        # Build threat analysis detail
        threat_analysis = ThreatAnalysisDetail(
            intent=ThreatIntentAnalysis(
                primary_intent="unknown",
                confidence=0.5,
                all_intents=[],
                risk_factor=0.0
            ),
            content_risk=ContentRiskAnalysis(
                lexical_risk=base_analysis.get("lexical_risk", 0.0),
                semantic_risk=0.0,
                benign_offset=base_analysis.get("benign_offset", 0.15),
                suspicious_entities=[],
                overall_content_risk=base_analysis.get("risk_score", 0.0)
            ),
            risk_score=base_analysis.get("risk_score", 0.0),
            ml_score=base_analysis.get("ml_score", 0.0)
        )
        
        # Determine decision based on combined risk
        final_risk = (
            analysis_data.get('combined_risk_score', 0.0)
            if use_phase2 else base_analysis.get("risk_score", 0.0)
        )
        
        decision = (
            DecisionAction.BLOCKED
            if final_risk > settings.RISK_SCORE_THRESHOLD
            else DecisionAction.APPROVED
        )
        
        # Build Phase 2 fields if available
        intent_analysis = None
        escalation_analysis = None
        semantic_analysis = None
        context_anomalies = None
        user_risk_profile = None
        
        if use_phase2:
            intent_analysis = build_phase2_intent_analysis(analysis_data)
            escalation_analysis = build_phase2_escalation_analysis(analysis_data)
            semantic_analysis = build_phase2_semantic_analysis(analysis_data)
            context_anomalies = build_phase2_context_anomalies(analysis_data)
            user_risk_profile = build_phase2_user_profile(analysis_data)
            
            # Record interaction for future learning
            if request_data.user_id and request_data.session_id and intent_analysis:
                background_tasks.add_task(
                    phase2_detector.record_interaction,
                    user_id=request_data.user_id,
                    session_id=request_data.session_id,
                    prompt=prompt,
                    intent=intent_analysis.primary_intent.value,
                    risk_score=final_risk,
                    response_time_ms=analysis_time_ms,
                    was_blocked=(decision == DecisionAction.BLOCKED)
                )
        
        # Build response
        response_obj = AnalysisResponse(
            status=decision,
            decision_confidence=base_analysis.get("confidence", 0.85),
            prompt=prompt,
            analysis=threat_analysis,
            vigil_analysis=vigil_analysis,
            intent_analysis=intent_analysis,
            escalation_analysis=escalation_analysis,
            semantic_analysis=semantic_analysis,
            context_anomalies=context_anomalies,
            user_risk_profile=user_risk_profile,
            response=(
                "✅ Safe prompt approved for processing"
                if decision == DecisionAction.APPROVED
                else None
            ),
            block_reason=(
                "Prompt pattern matches known injection attack"
                if decision == DecisionAction.BLOCKED
                else None
            ),
            analysis_time_ms=analysis_time_ms,
            cache_hit=cache_hit,
            request_id=request_id
        )
        
        return response_obj
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================================
# Risk Analysis Only (Lightweight)
# ==========================================
@app.post("/api/v2/analyze/risk", response_model=RiskOnlyResponse)
async def analyze_risk_only(
    request_data: AnalysisRequest,
    request: Request
) -> RiskOnlyResponse:
    """
    Lightweight risk analysis without LLM response
    Useful for quick threat detection (200-500ms)
    """
    
    request_id = request.state.request_id
    start_time = time.time()
    
    try:
        prompt = request_data.prompt.strip()
        
        # Check cache
        cache_hit = False
        cached_result = await cache.get(prompt)
        
        if cached_result:
            cache_hit = True
            analysis_data = cached_result
        else:
            analysis_data = await detector.analyze_async(prompt)
        
        analysis_time_ms = round((time.time() - start_time) * 1000, 2)
        
        return RiskOnlyResponse(
            status="blocked" if analysis_data["status"] == "blocked" else "safe",
            analysis={
                "risk": analysis_data["risk_score"],
                "ml_score": analysis_data["ml_score"],
                "lexical_risk": analysis_data["lexical_risk"],
                "benign_offset": analysis_data["benign_offset"]
            },
            analysis_time_ms=analysis_time_ms,
            cache_hit=cache_hit
        )
    
    except Exception as e:
        logger.error(f"Risk analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Batch Analysis
# ==========================================
@app.post("/api/v2/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(
    batch_request: BatchAnalysisRequest,
    request: Request
) -> BatchAnalysisResponse:
    """
    Analyze multiple prompts efficiently
    Maximum 10 prompts per batch
    """
    
    start_time = time.time()
    results = []
    
    try:
        for prompt in batch_request.prompts:
            analysis = await detector.analyze_async(prompt)
            
            results.append({
                "prompt": prompt,
                "status": analysis["status"],
                "risk": analysis["risk_score"]
            })
        
        total_time_ms = round((time.time() - start_time) * 1000, 2)
        
        return BatchAnalysisResponse(
            results=results,
            total_time_ms=total_time_ms
        )
    
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Error Handlers
# ==========================================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Generic exception handler"""
    
    logger.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": datetime.now().isoformat()
        }
    )


# ==========================================
# Custom OpenAPI Schema
# ==========================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Enterprise-grade AI security gateway",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://github.com/promptguard/promptguard"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ==========================================
# Phase 2 Helper Functions
# ==========================================
def build_phase2_intent_analysis(phase2_data: dict) -> Optional[IntentAnalysisResponse]:
    """Convert Phase 2 intent analysis to response model"""
    try:
        intent_data = phase2_data.get('phase2', {}).get('intent_analysis')
        if not intent_data:
            return None
        
        return IntentAnalysisResponse(
            primary_intent=IntentType(intent_data['primary_intent']),
            confidence=intent_data['confidence'],
            secondary_intent=(
                IntentType(intent_data['secondary_intent'])
                if intent_data.get('secondary_intent') else None
            ),
            secondary_confidence=intent_data.get('secondary_confidence'),
            attack_type_description=intent_data.get('attack_type_description', ''),
            intent_risk_score=intent_data.get('intent_risk_score', 0.0)
        )
    except Exception as e:
        logger.error(f"Error building intent analysis: {e}")
        return None


def build_phase2_escalation_analysis(phase2_data: dict) -> Optional[EscalationAnalysisResponse]:
    """Convert Phase 2 escalation analysis to response model"""
    try:
        esc_data = phase2_data.get('phase2', {}).get('semantic_analysis')
        if not esc_data:
            return None
        
        esc_analysis = phase2_data.get('phase2', {}).get('context_analysis', {}).get('escalation_analysis', {})
        
        escalation_level = EscalationLevel.LOW
        if esc_analysis.get('escalation_score', 0) > 0.7:
            escalation_level = EscalationLevel.CRITICAL
        elif esc_analysis.get('escalation_score', 0) > 0.5:
            escalation_level = EscalationLevel.HIGH
        elif esc_analysis.get('escalation_score', 0) > 0.3:
            escalation_level = EscalationLevel.MEDIUM
        
        return EscalationAnalysisResponse(
            is_escalating=esc_analysis.get('is_escalating', False),
            escalation_score=esc_analysis.get('escalation_score', 0.0),
            escalation_level=escalation_level,
            patterns_detected=esc_analysis.get('patterns_detected', []),
            history_length=esc_analysis.get('history_length', 0),
            unique_attack_types=esc_analysis.get('unique_attack_types', 0)
        )
    except Exception as e:
        logger.error(f"Error building escalation analysis: {e}")
        return None


def build_phase2_semantic_analysis(phase2_data: dict) -> Optional[SemanticAnalysisResponse]:
    """Convert Phase 2 semantic analysis to response model"""
    try:
        sem_data = phase2_data.get('phase2', {}).get('semantic_analysis')
        if not sem_data:
            return None
        
        matches = [
            SemanticSimilarityMatch(
                similarity_score=m['similarity_score'],
                matched_attack_pattern=m['matched_attack_pattern'],
                attack_type=m['attack_type'],
                confidence=m['confidence']
            )
            for m in sem_data.get('semantic_matches', [])
        ]
        
        injection_data = sem_data.get('prompt_injection_techniques', {})
        injection_techniques = PromptInjectionTechniques(
            has_injection_markers=injection_data.get('has_injection_markers', False),
            detected_techniques=injection_data.get('detected_techniques', []),
            injection_score=injection_data.get('injection_score', 0.0),
            technique_count=injection_data.get('technique_count', 0)
        )
        
        return SemanticAnalysisResponse(
            semantic_matches=matches,
            prompt_injection_techniques=injection_techniques,
            overall_semantic_risk=sem_data.get('overall_semantic_risk', 0.0)
        )
    except Exception as e:
        logger.error(f"Error building semantic analysis: {e}")
        return None


def build_phase2_context_anomalies(phase2_data: dict) -> Optional[ContextAnomalyDetection]:
    """Convert Phase 2 context anomalies to response model"""
    try:
        ctx_data = phase2_data.get('phase2', {}).get('context_analysis')
        if not ctx_data:
            return None
        
        anomalies = ctx_data.get('context_anomalies', {})
        
        return ContextAnomalyDetection(
            has_anomalies=anomalies.get('has_anomalies', False),
            anomaly_score=anomalies.get('anomaly_score', 0.0),
            detected_patterns=anomalies.get('detected_patterns', []),
            block_rate=anomalies.get('block_rate', 0.0),
            risk_increase=anomalies.get('risk_increase', 0.0),
            session_age_minutes=ctx_data.get('session_context', {}).get('session_age_minutes', 0.0),
            turn_number=ctx_data.get('session_context', {}).get('total_turns', 0)
        )
    except Exception as e:
        logger.error(f"Error building context anomalies: {e}")
        return None


def build_phase2_user_profile(phase2_data: dict) -> Optional[UserProfileRisk]:
    """Convert Phase 2 user profile to response model"""
    try:
        user_data = phase2_data.get('phase2', {}).get('context_analysis', {}).get('user_risk_profile')
        if not user_data:
            return None
        
        return UserProfileRisk(
            user_id=user_data.get('user_id', 'unknown'),
            abuse_score=user_data.get('abuse_score', 0.0),
            is_suspicious=user_data.get('is_suspicious', False),
            total_requests=user_data.get('total_requests', 0),
            block_rate=user_data.get('block_rate', 0.0),
            average_risk_score=user_data.get('average_risk_score', 0.0),
            unique_intents=user_data.get('unique_intents', []),
            request_frequency=user_data.get('request_frequency', 0.0)
        )
    except Exception as e:
        logger.error(f"Error building user profile: {e}")
        return None


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "promptguard.api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
