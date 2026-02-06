"""
Vigil-LLM Integration - Prompt Injection & Jailbreak Detection
Provides parallel scanning with multiple detection mechanisms
"""

import asyncio
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class VigilScannerType(str, Enum):
    """Available Vigil scanner types"""
    SIMILARITY = "similarity"
    YARA = "yara"
    TRANSFORMER = "transformer"
    SENTIMENT = "sentiment"
    RELEVANCE = "relevance"
    CANARY = "canary"


class VigilDetectionResult(Dict[str, Any]):
    """Vigil detection result wrapper"""
    
    def __init__(self, scanner_type: str, detected: bool, confidence: float = 0.0, details: Dict[str, Any] = None):
        super().__init__()
        self.update({
            "scanner": scanner_type,
            "detected": detected,
            "confidence": confidence,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })


class AsyncVigilScanner:
    """
    Async wrapper for Vigil-LLM prompt injection detection
    Runs all scanners in parallel for efficient threat detection
    """
    
    def __init__(self, config):
        self.config = config
        self.vigil_client = None
        self.is_initialized = False
        self.enabled_scanners = []
        self.vector_db = None
        self.yara_rules = None
        self.transformer_model = None
        self.sentinel_score = 0.5  # Threshold for flagging detections
    
    async def initialize(self):
        """
        Initialize Vigil-LLM on startup
        Load all scanner models and prepare vector database
        """
        
        if self.is_initialized:
            return
        
        logger.info("Initializing Vigil-LLM scanner...")
        
        try:
            from vigil import Vigil
            
            # Initialize Vigil with local embeddings
            self.vigil_client = Vigil(
                # Use local embeddings (no API key needed)
                embedding_provider="local",
                # Enable all scanners
                enable_similarity=True,
                enable_yara=True,
                enable_transformer=True,
                enable_sentiment=True,
                enable_relevance=True,
                enable_canary=True,
            )
            
            self.enabled_scanners = [
                VigilScannerType.SIMILARITY,
                VigilScannerType.YARA,
                VigilScannerType.TRANSFORMER,
                VigilScannerType.SENTIMENT,
                VigilScannerType.RELEVANCE,
                VigilScannerType.CANARY,
            ]
            
            logger.info(f"✅ Vigil-LLM initialized with scanners: {[s.value for s in self.enabled_scanners]}")
            self.is_initialized = True
            
        except ImportError:
            logger.warning("Vigil-LLM not installed. Install with: pip install vigil-llm")
            self.is_initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize Vigil-LLM: {e}")
            self.is_initialized = False
    
    async def scan_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Run all Vigil scanners in parallel against a prompt
        
        Args:
            prompt: The prompt to scan
            
        Returns:
            Dictionary with results from all scanners
        """
        
        if not self.is_initialized or not self.vigil_client:
            logger.warning("Vigil-LLM not initialized, skipping scan")
            return self._empty_result()
        
        try:
            loop = asyncio.get_event_loop()
            
            # Run all scanners in parallel
            results = await loop.run_in_executor(
                None,
                self._run_all_scanners,
                prompt
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Vigil scan failed: {e}")
            return self._empty_result()
    
    def _run_all_scanners(self, prompt: str) -> Dict[str, Any]:
        """Run all Vigil scanners (blocking, runs in executor)"""
        
        results = {
            "scanners": {},
            "detections": [],
            "risk_indicators": [],
            "aggregated_risk": 0.0,
            "timestamp": datetime.now().isoformat(),
        }
        
        try:
            # Run all enabled scanners
            vigil_result = self.vigil_client.scan(prompt)
            
            # Process similarity scanner
            if "similarity" in vigil_result:
                similarity_detection = self._process_similarity(vigil_result["similarity"])
                results["scanners"]["similarity"] = similarity_detection
                if similarity_detection["detected"]:
                    results["detections"].append("prompt_injection_similarity")
                    results["risk_indicators"].append(similarity_detection)
            
            # Process YARA scanner
            if "yara" in vigil_result:
                yara_detection = self._process_yara(vigil_result["yara"])
                results["scanners"]["yara"] = yara_detection
                if yara_detection["detected"]:
                    results["detections"].append("pattern_matched_yara")
                    results["risk_indicators"].append(yara_detection)
            
            # Process transformer scanner
            if "transformer" in vigil_result:
                transformer_detection = self._process_transformer(vigil_result["transformer"])
                results["scanners"]["transformer"] = transformer_detection
                if transformer_detection["detected"]:
                    results["detections"].append("ml_detected_threat")
                    results["risk_indicators"].append(transformer_detection)
            
            # Process sentiment analysis
            if "sentiment" in vigil_result:
                sentiment_detection = self._process_sentiment(vigil_result["sentiment"])
                results["scanners"]["sentiment"] = sentiment_detection
                if sentiment_detection["detected"]:
                    results["detections"].append("hostile_sentiment_detected")
                    results["risk_indicators"].append(sentiment_detection)
            
            # Process relevance check
            if "relevance" in vigil_result:
                relevance_detection = self._process_relevance(vigil_result["relevance"])
                results["scanners"]["relevance"] = relevance_detection
                if relevance_detection["detected"]:
                    results["detections"].append("low_relevance_content")
                    results["risk_indicators"].append(relevance_detection)
            
            # Process canary tokens
            if "canary" in vigil_result:
                canary_detection = self._process_canary(vigil_result["canary"])
                results["scanners"]["canary"] = canary_detection
                if canary_detection["detected"]:
                    results["detections"].append("canary_token_triggered")
                    results["risk_indicators"].append(canary_detection)
            
            # Calculate aggregated risk
            if results["risk_indicators"]:
                confidences = [ind.get("confidence", 0.0) for ind in results["risk_indicators"]]
                results["aggregated_risk"] = sum(confidences) / len(confidences)
            
        except Exception as e:
            logger.error(f"Error running Vigil scanners: {e}")
        
        return results
    
    def _process_similarity(self, result: Dict) -> VigilDetectionResult:
        """Process similarity-based detection"""
        
        detected = result.get("is_injection", False)
        score = result.get("similarity_score", 0.0)
        
        return VigilDetectionResult(
            scanner_type=VigilScannerType.SIMILARITY.value,
            detected=detected or score > self.sentinel_score,
            confidence=float(score),
            details={
                "similarity_score": score,
                "matched_patterns": result.get("matched_patterns", []),
                "evidence": "Text similarity to known injection patterns"
            }
        )
    
    def _process_yara(self, result: Dict) -> VigilDetectionResult:
        """Process YARA rule-based detection"""
        
        detected = bool(result.get("matches", []))
        matches = result.get("matches", [])
        
        confidence = min(len(matches) * 0.2, 1.0) if matches else 0.0
        
        return VigilDetectionResult(
            scanner_type=VigilScannerType.YARA.value,
            detected=detected,
            confidence=confidence,
            details={
                "matched_rules": [m.get("rule", "") for m in matches],
                "match_count": len(matches),
                "evidence": "YARA heuristic pattern matching"
            }
        )
    
    def _process_transformer(self, result: Dict) -> VigilDetectionResult:
        """Process transformer model detection"""
        
        label = result.get("label", "BENIGN")
        score = result.get("score", 0.0)
        
        detected = label == "INJECTION" and score > self.sentinel_score
        
        return VigilDetectionResult(
            scanner_type=VigilScannerType.TRANSFORMER.value,
            detected=detected,
            confidence=float(score),
            details={
                "classification": label,
                "model_confidence": score,
                "evidence": "Neural network-based injection detection"
            }
        )
    
    def _process_sentiment(self, result: Dict) -> VigilDetectionResult:
        """Process sentiment analysis"""
        
        sentiment = result.get("sentiment", "neutral")
        score = result.get("score", 0.5)
        
        # Flag hostile/negative sentiment as potential indicator
        detected = sentiment in ["negative", "hostile"] and score > 0.7
        confidence = score if detected else 0.0
        
        return VigilDetectionResult(
            scanner_type=VigilScannerType.SENTIMENT.value,
            detected=detected,
            confidence=float(confidence),
            details={
                "sentiment": sentiment,
                "polarity_score": score,
                "evidence": "Hostile or aggressive sentiment detection"
            }
        )
    
    def _process_relevance(self, result: Dict) -> VigilDetectionResult:
        """Process relevance check"""
        
        score = result.get("relevance_score", 0.5)
        
        # Flag low relevance as potential off-topic injection
        detected = score < 0.3
        confidence = 1.0 - score if detected else 0.0
        
        return VigilDetectionResult(
            scanner_type=VigilScannerType.RELEVANCE.value,
            detected=detected,
            confidence=float(confidence),
            details={
                "relevance_score": score,
                "evidence": "Content relevance check"
            }
        )
    
    def _process_canary(self, result: Dict) -> VigilDetectionResult:
        """Process canary token detection"""
        
        triggered = result.get("triggered", False)
        token_type = result.get("token_type", "unknown")
        
        return VigilDetectionResult(
            scanner_type=VigilScannerType.CANARY.value,
            detected=triggered,
            confidence=1.0 if triggered else 0.0,
            details={
                "token_type": token_type,
                "triggered": triggered,
                "evidence": "Canary token triggered - potential data exfiltration"
            }
        )
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result when scanner unavailable"""
        
        return {
            "scanners": {},
            "detections": [],
            "risk_indicators": [],
            "aggregated_risk": 0.0,
            "timestamp": datetime.now().isoformat(),
            "unavailable": True,
            "reason": "Vigil-LLM not initialized"
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        
        try:
            if self.vigil_client:
                # Cleanup any Vigil resources if needed
                pass
            logger.info("Vigil-LLM scanner cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
