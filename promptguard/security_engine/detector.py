"""
Async Security Detector - Core threat detection engine with async inference
Integrated with Vigil-LLM for multi-scanner prompt injection detection
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class AsyncSecurityDetector:
    """
    Async, preloaded ML inference with proper separation of concerns
    Runs Vigil-LLM scanners in parallel for comprehensive threat detection
    """
    
    def __init__(self, config):
        self.config = config
        self.ml_model = None
        self.semantic_model = None
        self.vigil_scanner = None
        self.executor = None
        self.is_initialized = False
        self.inference_queue = asyncio.Queue()
        self.model_pool = []
        self.initialization_time = None
    
    async def initialize(self):
        """
        Called on startup - load all ML models once
        Runs in background threads to avoid blocking
        """
        
        if self.is_initialized:
            return
        
        logger.info("Initializing AsyncSecurityDetector...")
        start_time = datetime.now()
        
        try:
            # Load ML detector model
            logger.info("Loading ML detector model...")
            self.ml_model = await self._load_detector_model()
            
            # Load semantic model
            logger.info("Loading semantic embedding model...")
            if self.config.ENABLE_SEMANTIC_ANALYSIS:
                self.semantic_model = await self._load_semantic_model()
            
            # Initialize Vigil-LLM scanner (parallel detection)
            logger.info("Initializing Vigil-LLM scanner...")
            from promptguard.security_engine.vigil_scanner import AsyncVigilScanner
            self.vigil_scanner = AsyncVigilScanner(self.config)
            await self.vigil_scanner.initialize()
            
            self.is_initialized = True
            self.initialization_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"AsyncSecurityDetector initialized in {self.initialization_time:.2f}s"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize detector: {e}")
            raise
    
    async def _load_detector_model(self):
        """Load DeBERTa model (non-blocking)"""
        
        from transformers import pipeline
        
        loop = asyncio.get_event_loop()
        
        def sync_load():
            return pipeline(
                "text-classification",
                model=self.config.ML_MODEL_NAME,
                device=self.config.ML_DEVICE,
                truncation=True,
                max_length=self.config.ML_MAX_LENGTH,
            )
        
        return await loop.run_in_executor(None, sync_load)
    
    async def _load_semantic_model(self):
        """Load sentence transformer model"""
        
        from sentence_transformers import SentenceTransformer
        
        loop = asyncio.get_event_loop()
        
        def sync_load():
            return SentenceTransformer(self.config.SEMANTIC_MODEL_NAME)
        
        return await loop.run_in_executor(None, sync_load)
    
    # ==========================================
    # MAIN ANALYSIS ENDPOINTS
    # ==========================================
    async def analyze_async(self, prompt: str) -> Dict[str, Any]:
        """
        Main analysis endpoint (non-blocking)
        Runs Vigil scanners in parallel with internal analysis
        Returns comprehensive threat assessment
        """
        
        if not self.is_initialized:
            raise RuntimeError("Detector not initialized")
        
        loop = asyncio.get_event_loop()
        
        # Run both internal analysis and Vigil scanners in parallel
        internal_result, vigil_result = await asyncio.gather(
            loop.run_in_executor(None, self._sync_analyze, prompt),
            self.vigil_scanner.scan_prompt(prompt) if self.vigil_scanner else asyncio.sleep(0, None)
        )
        
        # Merge results
        result = {
            **internal_result,
            "vigil_scan": vigil_result if vigil_result else None
        }
        
        # Adjust risk score if Vigil detected threats
        if vigil_result and vigil_result.get("detections"):
            vigil_risk = vigil_result.get("aggregated_risk", 0.0)
            # Weight Vigil results: 30% Vigil, 70% internal analysis
            original_risk = result.get("risk_score", 0.0)
            result["risk_score"] = round(
                (0.7 * original_risk) + (0.3 * vigil_risk),
                3
            )
            
            # If Vigil detected threats, increase blocking threshold
            if vigil_risk > 0.6:
                result["status"] = "blocked"
                result["block_reason"] = "Vigil-LLM threat detection"
        
        return result
    
    def _sync_analyze(self, prompt: str) -> Dict[str, Any]:
        """Synchronous analysis (runs in thread pool)"""
        
        # Normalize prompt
        normalized = self._normalize(prompt)
        
        # 1. Lexical analysis
        lexical_risk = self._lexical_attack_score(normalized)
        benign_offset = self._lexical_benign_score(normalized)
        
        # 2. ML inference
        ml_score = self._ml_risk(prompt)
        
        # 3. Aggregate
        risk_score = (0.5 * ml_score) + (0.5 * lexical_risk) - benign_offset
        risk_score = max(min(risk_score, 1.0), 0.0)
        
        # Determine status
        is_dangerous = (
            (ml_score > self.config.ML_SCORE_THRESHOLD and risk_score > 0.45)
            or risk_score > self.config.RISK_SCORE_THRESHOLD
        )
        
        return {
            "status": "blocked" if is_dangerous else "approved",
            "risk_score": round(risk_score, 3),
            "ml_score": round(ml_score, 3),
            "lexical_risk": round(lexical_risk, 3),
            "benign_offset": round(benign_offset, 3),
            "confidence": round(
                1.0 - risk_score if is_dangerous else risk_score,
                3
            ),
        }
    
    # ==========================================
    # DETECTION LAYERS
    # ==========================================
    def _ml_risk(self, prompt: str) -> float:
        """ML-based threat detection"""
        
        if not self.ml_model:
            return 0.1
        
        try:
            result = self.ml_model(prompt)[0]
            
            # Return injection risk score
            if result["label"] == "INJECTION":
                return result["score"]
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"ML risk check failed: {e}")
            return 0.1
    
    def _lexical_attack_score(self, normalized_prompt: str) -> float:
        """Lexical pattern-based attack detection"""
        
        attack_patterns = [
            r"ignore (all|previous|earlier) instructions",
            r"disregard .* instructions",
            r"you are now .* system",
            r"act as .* system",
            r"reveal .* system prompt",
            r"developer mode",
            r"bypass .* safety",
            r"override .* policy",
        ]
        
        score = 0.0
        
        for pattern in attack_patterns:
            if re.search(pattern, normalized_prompt):
                score += 0.25
        
        return min(score, 1.0)
    
    def _lexical_benign_score(self, normalized_prompt: str) -> float:
        """Benign pattern detection to reduce false positives"""
        
        benign_patterns = [
            r"explain",
            r"summarize",
            r"translate",
            r"write a story",
            r"help me understand",
            r"what is",
            r"how does",
        ]
        
        score = 0.0
        
        for pattern in benign_patterns:
            if re.search(pattern, normalized_prompt):
                score += 0.15
        
        return min(score, 0.5)
    
    @staticmethod
    def _normalize(text: str) -> str:
        """Normalize text for analysis"""
        
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s]", "", text)
        return text.strip()
    
    # ==========================================
    # STREAMING ANALYSIS (for output inspection)
    # ==========================================
    async def stream_analysis(self, prompt: str):
        """
        Stream analysis results for progressive UI updates
        Yields partial results as they become available
        """
        
        # Yield basic risk analysis first (fast)
        risk_analysis = await self.analyze_async(prompt)
        yield {
            "stage": "risk_analysis",
            "data": risk_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        # If approved, generate LLM response (slow)
        if risk_analysis["status"] == "approved":
            # Placeholder: actual LLM call would stream here
            yield {
                "stage": "llm_response_start",
                "timestamp": datetime.now().isoformat()
            }
            
            # In actual implementation:
            # async for chunk in llm_stream(prompt):
            #     yield {"stage": "llm_response_chunk", "data": chunk}
            
            yield {
                "stage": "llm_response_complete",
                "timestamp": datetime.now().isoformat()
            }
    
    # ==========================================
    # CLEANUP
    # ==========================================
    async def cleanup(self):
        """Called on shutdown"""
        
        logger.info("Cleaning up detector resources...")
        
        try:
            if self.vigil_scanner:
                await self.vigil_scanner.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up Vigil scanner: {e}")
        
        self.ml_model = None
        self.semantic_model = None
        self.vigil_scanner = None
        self.is_initialized = False
