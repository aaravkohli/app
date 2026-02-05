"""Core security detection engine

Phase 1: Async ML-based threat detection
- detector.py: AsyncSecurityDetector with DeBERTa model

Phase 2: Multi-dimensional threat analysis
- intent_classifier.py: 7-category intent classification + escalation detection
- context_tracker.py: Conversation history + user profiling
- semantic_analyzer.py: Pattern matching + prompt injection detection
- phase2_detector.py: Integrated multi-dimensional detector
"""

from .detector import AsyncSecurityDetector
from .intent_classifier import IntentClassifier, IntentType, IntentEscalationDetector
from .context_tracker import ContextManager, ConversationContext, UserProfile
from .semantic_analyzer import SemanticAnalyzer, PatternDatabase
from .phase2_detector import Phase2SecurityDetector

__all__ = [
    'AsyncSecurityDetector',
    'Phase2SecurityDetector',
    'IntentClassifier',
    'IntentType',
    'IntentEscalationDetector',
    'ContextManager',
    'ConversationContext',
    'UserProfile',
    'SemanticAnalyzer',
    'PatternDatabase',
]
