"""
Intent Classification Module

Detects the intent/attack type of a prompt using zero-shot classification.
Classifies prompts into 7 categories:
- Jailbreak: Attempts to override model constraints
- Prompt Injection: Injecting conflicting instructions
- Data Extraction: Trying to extract training data or system info
- Adversarial: Testing model robustness with adversarial examples
- Misuse: Legitimate requests for harmful content (NSFW, violence, etc.)
- Confusion: Confusing or nonsensical prompts designed to break the model
- Unknown/Benign: Normal legitimate requests
"""

from enum import Enum
from typing import Dict, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class IntentType(str, Enum):
    """Seven main attack/intent types"""
    JAILBREAK = "jailbreak"              # Override model constraints
    PROMPT_INJECTION = "prompt_injection"  # Inject conflicting instructions
    DATA_EXTRACTION = "data_extraction"    # Extract training/system data
    ADVERSARIAL = "adversarial"            # Test model robustness
    MISUSE = "misuse"                      # Request harmful but legitimate content
    CONFUSION = "confusion"                # Confusing/nonsensical attacks
    BENIGN = "benign"                      # Legitimate request


@dataclass
class IntentAnalysis:
    """Result of intent classification"""
    primary_intent: IntentType
    confidence: float  # 0.0-1.0
    secondary_intent: Optional[IntentType] = None
    secondary_confidence: Optional[float] = None
    intent_scores: Optional[Dict[str, float]] = None  # All 7 scores
    attack_type_description: Optional[str] = None


class IntentClassifier:
    """
    Zero-shot intent classifier for detecting attack types.
    
    Uses zero-shot classification to identify which of 7 intents
    a prompt most closely matches, without requiring training data.
    """

    # Define all 7 intent types with descriptions for zero-shot classification
    INTENT_DESCRIPTIONS = {
        IntentType.JAILBREAK: (
            "The prompt tries to manipulate or override the AI's safety constraints, "
            "restrictions, or values to make it ignore instructions and behave dangerously."
        ),
        IntentType.PROMPT_INJECTION: (
            "The prompt tries to inject new instructions, change the conversation context, "
            "or hijack the model's behavior by inserting special formatting or commands."
        ),
        IntentType.DATA_EXTRACTION: (
            "The prompt attempts to extract sensitive information like training data, "
            "system prompts, user data, API keys, credentials, or internal model details."
        ),
        IntentType.ADVERSARIAL: (
            "The prompt uses adversarial techniques like misspellings, obfuscation, "
            "or encoding to test the model's robustness and find vulnerabilities."
        ),
        IntentType.MISUSE: (
            "The prompt requests explicitly harmful, illegal, or prohibited content "
            "like violence, illegal activities, NSFW content, hate speech, or harassment."
        ),
        IntentType.CONFUSION: (
            "The prompt is confusing, nonsensical, or designed to break the model "
            "with contradictions, paradoxes, or incomprehensible input."
        ),
        IntentType.BENIGN: (
            "This is a normal, legitimate request asking for helpful information, "
            "explanations, creative content, or productive assistance."
        ),
    }

    def __init__(self, enable_semantic: bool = False):
        """
        Initialize intent classifier.
        
        Args:
            enable_semantic: If True, use semantic similarity. If False, use zero-shot.
        """
        self.enable_semantic = enable_semantic
        self.classifier = None
        self.semantic_model = None
        
        # Intent risk mapping (which intents are most dangerous)
        self.intent_risk_weights = {
            IntentType.JAILBREAK: 0.95,
            IntentType.PROMPT_INJECTION: 0.90,
            IntentType.DATA_EXTRACTION: 0.85,
            IntentType.ADVERSARIAL: 0.70,
            IntentType.MISUSE: 0.80,
            IntentType.CONFUSION: 0.50,
            IntentType.BENIGN: 0.0,
        }

    async def initialize(self):
        """
        Load zero-shot classification model asynchronously.
        
        Uses transformers library's zero-shot-classification pipeline.
        Models available: facebook/bart-large-mnli, cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
        """
        try:
            from transformers import pipeline
            import asyncio
            
            # Load in thread pool (non-blocking)
            loop = asyncio.get_event_loop()
            self.classifier = await loop.run_in_executor(
                None,
                self._load_classifier
            )
            logger.info("Intent classifier initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize intent classifier: {e}")
            self.classifier = None

    def _load_classifier(self):
        """Load the zero-shot classifier (runs in thread pool)"""
        from transformers import pipeline
        
        # Use efficient model for zero-shot classification
        # facebook/bart-large-mnli is accurate, nli-distilroberta-base is faster
        return pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device_map="auto"
        )

    async def classify_async(
        self,
        prompt: str,
        return_all_scores: bool = True
    ) -> IntentAnalysis:
        """
        Classify the intent of a prompt asynchronously.
        
        Args:
            prompt: The prompt to classify
            return_all_scores: If True, return scores for all 7 intents
            
        Returns:
            IntentAnalysis with primary intent, confidence, and optional all scores
        """
        if not self.classifier:
            logger.warning("Intent classifier not initialized, returning BENIGN")
            return IntentAnalysis(
                primary_intent=IntentType.BENIGN,
                confidence=0.5,
                attack_type_description="Classifier unavailable, defaulting to benign"
            )

        try:
            import asyncio
            
            # Run classification in thread pool (non-blocking)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._classify_sync,
                prompt,
                return_all_scores
            )
            return result
        except Exception as e:
            logger.error(f"Error during intent classification: {e}")
            return IntentAnalysis(
                primary_intent=IntentType.BENIGN,
                confidence=0.5,
                attack_type_description=f"Classification error: {str(e)}"
            )

    def _classify_sync(self, prompt: str, return_all_scores: bool) -> IntentAnalysis:
        """
        Synchronous classification logic (runs in executor).
        Uses zero-shot classification with all 7 intent descriptions.
        """
        intent_texts = list(self.INTENT_DESCRIPTIONS.values())
        intent_labels = [intent.value for intent in IntentType]

        # Truncate prompt if too long (model input limit)
        truncated_prompt = prompt[:512]

        # Run zero-shot classification
        result = self.classifier(
            truncated_prompt,
            intent_labels,
            multi_class=False  # Only assign one primary intent
        )

        # Extract results
        primary_label = result["labels"][0]
        primary_confidence = result["scores"][0]
        primary_intent = IntentType(primary_label)

        # Get secondary intent if available
        secondary_intent = None
        secondary_confidence = None
        if len(result["labels"]) > 1:
            secondary_intent = IntentType(result["labels"][1])
            secondary_confidence = result["scores"][1]

        # Build all scores dict if requested
        intent_scores = None
        if return_all_scores:
            intent_scores = {
                label: score
                for label, score in zip(result["labels"], result["scores"])
            }

        # Build attack type description
        attack_description = self._get_attack_description(primary_intent, primary_confidence)

        return IntentAnalysis(
            primary_intent=primary_intent,
            confidence=primary_confidence,
            secondary_intent=secondary_intent,
            secondary_confidence=secondary_confidence,
            intent_scores=intent_scores,
            attack_type_description=attack_description
        )

    def _get_attack_description(self, intent: IntentType, confidence: float) -> str:
        """Generate human-readable description of detected intent"""
        descriptions = {
            IntentType.JAILBREAK: (
                f"🚨 Potential jailbreak attempt (confidence: {confidence:.1%}) - "
                "Trying to override model constraints and safety guidelines"
            ),
            IntentType.PROMPT_INJECTION: (
                f"⚠️ Possible prompt injection (confidence: {confidence:.1%}) - "
                "Attempting to inject new instructions or hijack behavior"
            ),
            IntentType.DATA_EXTRACTION: (
                f"🔒 Data extraction attempt (confidence: {confidence:.1%}) - "
                "Trying to extract training data, credentials, or system information"
            ),
            IntentType.ADVERSARIAL: (
                f"🧪 Adversarial test (confidence: {confidence:.1%}) - "
                "Using adversarial techniques to test model robustness"
            ),
            IntentType.MISUSE: (
                f"⛔ Harmful content request (confidence: {confidence:.1%}) - "
                "Requesting prohibited or harmful content"
            ),
            IntentType.CONFUSION: (
                f"❓ Confusing input (confidence: {confidence:.1%}) - "
                "Nonsensical or paradoxical content designed to break the model"
            ),
            IntentType.BENIGN: (
                f"✅ Legitimate request (confidence: {confidence:.1%}) - "
                "Normal, benign, and safe request for assistance"
            ),
        }
        return descriptions.get(intent, f"Unknown intent: {intent.value}")

    def get_intent_risk_score(self, intent: IntentType) -> float:
        """
        Get risk score for a specific intent (0.0-1.0).
        Higher = more dangerous.
        """
        return self.intent_risk_weights.get(intent, 0.5)

    def get_confidence_threshold(self) -> float:
        """
        Get minimum confidence threshold for intent classification.
        Below this threshold, we're uncertain about intent.
        """
        return 0.65  # Require 65%+ confidence


class IntentEscalationDetector:
    """
    Detect escalation patterns in conversation history.
    Identifies when attack sophistication increases over time.
    """

    def __init__(self, history_window: int = 10):
        """
        Initialize escalation detector.
        
        Args:
            history_window: Number of recent prompts to track
        """
        self.history_window = history_window
        self.intent_history = []  # List of (IntentType, float, timestamp)

    def record_intent(self, intent: IntentType, confidence: float):
        """Record a detected intent"""
        from datetime import datetime
        self.intent_history.append((intent, confidence, datetime.now()))
        
        # Keep only recent history
        if len(self.intent_history) > self.history_window:
            self.intent_history = self.intent_history[-self.history_window:]

    def detect_escalation(self) -> Dict[str, any]:
        """
        Detect if attack sophistication is escalating.
        
        Returns:
            {
                'is_escalating': bool,
                'escalation_score': 0.0-1.0,
                'pattern': str,
                'confidence': float
            }
        """
        if len(self.intent_history) < 2:
            return {
                'is_escalating': False,
                'escalation_score': 0.0,
                'pattern': 'insufficient_history',
                'confidence': 0.0
            }

        intents = [intent for intent, _, _ in self.intent_history]
        confidences = [conf for _, conf, _ in self.intent_history]

        # Check for patterns
        patterns_detected = []
        escalation_score = 0.0

        # Pattern 1: Repeated attacks increasing in confidence
        if len(set(intents[-3:])) == 1:  # Same intent 3 times
            avg_conf_early = sum(confidences[:-3]) / max(1, len(confidences[:-3]))
            avg_conf_recent = sum(confidences[-3:]) / 3
            if avg_conf_recent > avg_conf_early + 0.1:
                patterns_detected.append("increasing_confidence")
                escalation_score += 0.4

        # Pattern 2: Progression from benign to malicious
        if intents[0] == IntentType.BENIGN and intents[-1] != IntentType.BENIGN:
            patterns_detected.append("benign_to_malicious")
            escalation_score += 0.3

        # Pattern 3: Multiple attack types (sophisticated multi-vector)
        unique_attacks = len(set(i for i in intents if i != IntentType.BENIGN))
        if unique_attacks >= 3:
            patterns_detected.append("multi_vector_attack")
            escalation_score += 0.3

        # Pattern 4: High confidence attacks
        if all(c > 0.8 for c in confidences[-3:]):
            patterns_detected.append("high_confidence_pattern")
            escalation_score += 0.2

        escalation_score = min(escalation_score, 1.0)

        return {
            'is_escalating': escalation_score > 0.5,
            'escalation_score': escalation_score,
            'pattern': ', '.join(patterns_detected) if patterns_detected else 'none_detected',
            'confidence': min(escalation_score * 0.9, 1.0),  # Reduce confidence for pattern detection
            'history_length': len(self.intent_history),
            'unique_attack_types': unique_attacks
        }

    def clear_history(self):
        """Clear conversation history (e.g., when user changes)"""
        self.intent_history = []
