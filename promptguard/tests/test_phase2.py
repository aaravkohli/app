"""
Phase 2 Security Intelligence Tests

Tests for:
- Intent classification
- Escalation detection
- Semantic analysis
- Context tracking
- Multi-dimensional threat detection
"""

import pytest
import asyncio
from datetime import datetime, timedelta

# Import Phase 2 components
try:
    from promptguard.security_engine.intent_classifier import (
        IntentClassifier, IntentType, IntentEscalationDetector
    )
    from promptguard.security_engine.context_tracker import (
        ContextManager, ConversationContext, UserProfile
    )
    from promptguard.security_engine.semantic_analyzer import (
        SemanticAnalyzer, PatternDatabase
    )
except ImportError:
    pytest.skip("Phase 2 modules not available", allow_module_level=True)


# ==========================================
# Intent Classification Tests
# ==========================================
class TestIntentClassifier:
    """Test intent classification"""
    
    def test_intent_type_enum(self):
        """Test IntentType enum values"""
        assert IntentType.JAILBREAK.value == "jailbreak"
        assert IntentType.PROMPT_INJECTION.value == "prompt_injection"
        assert IntentType.DATA_EXTRACTION.value == "data_extraction"
        assert IntentType.ADVERSARIAL.value == "adversarial"
        assert IntentType.MISUSE.value == "misuse"
        assert IntentType.CONFUSION.value == "confusion"
        assert IntentType.BENIGN.value == "benign"
    
    def test_intent_classifier_init(self):
        """Test classifier initialization"""
        classifier = IntentClassifier()
        
        # Check description dict is populated
        assert len(classifier.INTENT_DESCRIPTIONS) == 7
        for intent in IntentType:
            assert intent in classifier.INTENT_DESCRIPTIONS
    
    def test_intent_risk_weights(self):
        """Test intent risk weighting"""
        classifier = IntentClassifier()
        
        # Jailbreak should be highest risk
        assert classifier.get_intent_risk_score(IntentType.JAILBREAK) == 0.95
        
        # Benign should be zero risk
        assert classifier.get_intent_risk_score(IntentType.BENIGN) == 0.0
        
        # Data extraction should be very high risk
        assert classifier.get_intent_risk_score(IntentType.DATA_EXTRACTION) == 0.85


# ==========================================
# Escalation Detection Tests
# ==========================================
class TestIntentEscalationDetector:
    """Test escalation pattern detection"""
    
    def test_escalation_detector_init(self):
        """Test escalation detector initialization"""
        detector = IntentEscalationDetector()
        assert detector.intent_history == []
        assert len(detector.intent_history) == 0
    
    def test_record_intent(self):
        """Test recording intents"""
        detector = IntentEscalationDetector(history_window=10)
        
        detector.record_intent(IntentType.BENIGN, 0.9)
        detector.record_intent(IntentType.JAILBREAK, 0.95)
        
        assert len(detector.intent_history) == 2
        assert detector.intent_history[0][0] == IntentType.BENIGN
        assert detector.intent_history[1][0] == IntentType.JAILBREAK
    
    def test_escalation_with_insufficient_history(self):
        """Test escalation detection with insufficient history"""
        detector = IntentEscalationDetector()
        detector.record_intent(IntentType.BENIGN, 0.9)
        
        result = detector.detect_escalation()
        assert result['is_escalating'] == False
        assert result['escalation_score'] == 0.0
        assert result['pattern'] == 'insufficient_history'
    
    def test_escalation_benign_to_malicious(self):
        """Test detection of benign-to-malicious escalation"""
        detector = IntentEscalationDetector()
        
        # Start with benign
        detector.record_intent(IntentType.BENIGN, 0.5)
        detector.record_intent(IntentType.BENIGN, 0.4)
        
        # Escalate to attack
        detector.record_intent(IntentType.JAILBREAK, 0.95)
        detector.record_intent(IntentType.PROMPT_INJECTION, 0.90)
        
        result = detector.detect_escalation()
        assert result['is_escalating'] == True
        assert 'benign_to_malicious' in result['pattern']
        assert result['escalation_score'] > 0.5
    
    def test_clear_history(self):
        """Test clearing escalation history"""
        detector = IntentEscalationDetector()
        detector.record_intent(IntentType.JAILBREAK, 0.95)
        
        assert len(detector.intent_history) == 1
        
        detector.clear_history()
        assert len(detector.intent_history) == 0


# ==========================================
# Context Tracking Tests
# ==========================================
class TestConversationContext:
    """Test conversation context tracking"""
    
    def test_context_creation(self):
        """Test creating conversation context"""
        ctx = ConversationContext(
            user_id="user123",
            session_id="session456"
        )
        
        assert ctx.user_id == "user123"
        assert ctx.session_id == "session456"
        assert ctx.total_turns == 0
        assert ctx.is_expired() == False
    
    def test_add_turn(self):
        """Test adding turns to context"""
        ctx = ConversationContext("user123", "session456")
        
        ctx.add_turn(
            prompt="Hello",
            intent="benign",
            risk_score=0.1,
            response_time_ms=50.0
        )
        
        assert ctx.total_turns == 1
        assert len(ctx.turns) == 1
        assert ctx.turns[0].prompt == "Hello"
    
    def test_block_tracking(self):
        """Test tracking blocked prompts"""
        ctx = ConversationContext("user123", "session456")
        
        ctx.add_turn("Good request", "benign", 0.1, 50.0)
        ctx.add_turn("Blocked request", "jailbreak", 0.95, 60.0)
        
        assert ctx.total_turns == 2
        assert ctx.blocked_turns == 1
    
    def test_context_expiration(self):
        """Test context TTL expiration"""
        ctx = ConversationContext("user123", "session456", ttl_minutes=1)
        
        # Manually set creation time to past
        ctx.created_at = datetime.now() - timedelta(minutes=2)
        
        assert ctx.is_expired() == True
    
    def test_context_summary(self):
        """Test getting context summary"""
        ctx = ConversationContext("user123", "session456")
        
        ctx.add_turn("req1", "benign", 0.1, 50.0)
        ctx.add_turn("req2", "jailbreak", 0.9, 60.0)
        ctx.add_turn("req3", "benign", 0.2, 55.0)
        
        summary = ctx.get_context_summary()
        
        assert summary['total_turns'] == 3
        assert summary['block_rate'] == pytest.approx(1/3, abs=0.01)
        assert 'benign' in summary['unique_intents']
        assert 'jailbreak' in summary['unique_intents']


class TestContextManager:
    """Test conversation context manager"""
    
    def test_manager_initialization(self):
        """Test context manager init"""
        manager = ContextManager()
        assert len(manager.sessions) == 0
        assert len(manager.user_profiles) == 0
    
    def test_get_or_create_session(self):
        """Test session creation and retrieval"""
        manager = ContextManager()
        
        session1 = manager.get_or_create_session("user1", "sess1")
        assert session1.user_id == "user1"
        assert session1.session_id == "sess1"
        
        # Get same session
        session1_again = manager.get_or_create_session("user1", "sess1")
        assert session1 is session1_again
    
    def test_user_profile_creation(self):
        """Test user profile creation"""
        manager = ContextManager()
        
        profile = manager.get_user_profile("user123")
        assert profile.user_id == "user123"
        assert profile.total_requests == 0
        assert profile.abuse_score == 0.0
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        manager = ContextManager()
        
        manager.update_user_profile("user1", "benign", 0.1, was_blocked=False)
        manager.update_user_profile("user1", "benign", 0.2, was_blocked=False)
        manager.update_user_profile("user1", "jailbreak", 0.95, was_blocked=True)
        
        profile = manager.get_user_profile("user1")
        
        assert profile.total_requests == 3
        assert profile.blocked_requests == 1
        assert len(profile.unique_intents) == 2
    
    def test_statistics(self):
        """Test getting statistics"""
        manager = ContextManager()
        
        manager.get_or_create_session("user1", "sess1")
        manager.get_or_create_session("user1", "sess2")
        manager.get_user_profile("user1")
        
        stats = manager.get_statistics()
        assert stats['active_sessions'] >= 2
        assert stats['total_users'] >= 1


# ==========================================
# Semantic Analysis Tests
# ==========================================
class TestSemanticAnalyzer:
    """Test semantic analysis"""
    
    def test_semantic_analyzer_init(self):
        """Test semantic analyzer initialization"""
        analyzer = SemanticAnalyzer()
        
        assert analyzer.model is None  # Not loaded until initialize()
        assert len(analyzer.attack_patterns_db) > 0
        assert analyzer.threshold == 0.75
    
    def test_attack_patterns_db(self):
        """Test attack patterns database"""
        analyzer = SemanticAnalyzer()
        
        patterns = analyzer.attack_patterns_db
        
        # Should have jailbreak patterns
        assert 'jailbreak_1' in patterns
        assert patterns['jailbreak_1']['type'] == 'jailbreak'
        assert patterns['jailbreak_1']['severity'] == 0.95
        
        # Should have injection patterns
        assert 'injection_1' in patterns
        assert patterns['injection_1']['type'] == 'prompt_injection'
    
    def test_obfuscation_detection(self):
        """Test obfuscation detection"""
        analyzer = SemanticAnalyzer()
        
        # Leetspeak
        obfuscated = "H3ll0 w0rld f0r t3st1ng!"
        assert analyzer._is_obfuscated(obfuscated) == True
        
        # Normal text
        normal = "Hello world for testing!"
        assert analyzer._is_obfuscated(normal) == False


class TestPatternDatabase:
    """Test pattern database"""
    
    def test_pattern_db_init(self):
        """Test pattern database initialization"""
        db = PatternDatabase()
        assert len(db.patterns) == 0
        assert len(db.index_by_type) == 0
    
    def test_add_pattern(self):
        """Test adding patterns"""
        db = PatternDatabase()
        
        db.add_pattern(
            "test_1",
            "Test pattern text",
            "jailbreak",
            0.95,
            ["test", "pattern"]
        )
        
        assert "test_1" in db.patterns
        assert db.patterns["test_1"]["type"] == "jailbreak"
    
    def test_search_by_type(self):
        """Test searching patterns by type"""
        db = PatternDatabase()
        
        db.add_pattern("p1", "Pattern 1", "jailbreak", 0.9, [])
        db.add_pattern("p2", "Pattern 2", "jailbreak", 0.85, [])
        db.add_pattern("p3", "Pattern 3", "injection", 0.8, [])
        
        jailbreak_patterns = db.get_patterns_by_type("jailbreak")
        assert len(jailbreak_patterns) == 2
        assert "p1" in jailbreak_patterns
        assert "p2" in jailbreak_patterns
        
        injection_patterns = db.get_patterns_by_type("injection")
        assert len(injection_patterns) == 1


# ==========================================
# Integration Tests
# ==========================================
class TestPhase2Integration:
    """Integration tests for Phase 2 components"""
    
    def test_intent_escalation_workflow(self):
        """Test complete intent + escalation workflow"""
        classifier = IntentClassifier()
        escalation = IntentEscalationDetector()
        
        # Simulate conversation with escalation
        escalation.record_intent(IntentType.BENIGN, 0.9)
        escalation.record_intent(IntentType.BENIGN, 0.85)
        escalation.record_intent(IntentType.ADVERSARIAL, 0.75)
        escalation.record_intent(IntentType.JAILBREAK, 0.95)
        
        result = escalation.detect_escalation()
        
        # Should detect escalation
        assert result['is_escalating'] or result['escalation_score'] > 0.0
    
    def test_context_anomaly_detection(self):
        """Test context anomaly detection"""
        ctx = ConversationContext("user1", "sess1")
        
        # Add some benign turns
        for i in range(5):
            ctx.add_turn(f"req{i}", "benign", 0.1, 50.0)
        
        # Sudden attack spike
        for i in range(5):
            ctx.add_turn(f"attack{i}", "jailbreak", 0.95, 50.0)
        
        anomalies = ctx.detect_context_anomalies()
        
        # Should detect anomalies
        assert anomalies['anomaly_score'] > 0.0
        assert len(anomalies['detected_patterns']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
