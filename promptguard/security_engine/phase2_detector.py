"""
Phase 2 Enhancement: Multi-Dimensional Threat Detection

Integrates intent classification, escalation detection, semantic analysis,
and context tracking into the core security detector.
"""

import logging
from typing import Optional, Dict, Any
import asyncio

logger = logging.getLogger(__name__)


class Phase2SecurityDetector:
    """
    Wraps AsyncSecurityDetector with Phase 2 multi-dimensional threat analysis.
    Integrates:
    - Intent classification (7 attack types)
    - Escalation detection (pattern analysis)
    - Semantic similarity search
    - Context anomaly detection
    - User risk profiling
    """

    def __init__(self, base_detector, config):
        """
        Initialize Phase 2 detector.
        
        Args:
            base_detector: AsyncSecurityDetector instance from Phase 1
            config: Configuration object
        """
        self.base_detector = base_detector
        self.config = config
        
        # Phase 2 components (initialized on demand)
        self.intent_classifier = None
        self.semantic_analyzer = None
        self.context_manager = None
        self.escalation_detectors = {}  # Per-session

    async def initialize(self):
        """Initialize all Phase 2 components"""
        try:
            # Initialize base detector first
            if not self.base_detector.is_initialized:
                await self.base_detector.initialize()
            
            # Initialize Phase 2 components
            logger.info("Initializing Phase 2 security intelligence...")
            
            # Intent classifier
            if self.config.ENABLE_INTENT_CLASSIFICATION:
                from .intent_classifier import IntentClassifier, IntentEscalationDetector
                self.intent_classifier = IntentClassifier()
                await self.intent_classifier.initialize()
                logger.info("✅ Intent classifier initialized")
            
            # Semantic analyzer
            if self.config.ENABLE_SEMANTIC_ANALYSIS:
                from .semantic_analyzer import SemanticAnalyzer
                self.semantic_analyzer = SemanticAnalyzer()
                await self.semantic_analyzer.initialize()
                logger.info("✅ Semantic analyzer initialized")
            
            # Context manager
            if self.config.ENABLE_CONTEXT_TRACKING:
                from .context_tracker import ContextManager
                self.context_manager = ContextManager()
                logger.info("✅ Context manager initialized")
            
            logger.info("Phase 2 security intelligence initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Phase 2: {e}")
            raise

    async def analyze_full_phase2(
        self,
        prompt: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full Phase 2 analysis with all dimensions.
        
        Args:
            prompt: The prompt to analyze
            user_id: User identifier for context tracking
            session_id: Session identifier for conversation context
            
        Returns:
            Dictionary with complete threat analysis including all Phase 2 dimensions
        """
        
        # Run Phase 1 base analysis
        base_analysis = await self.base_detector.analyze_async(prompt)
        
        phase2_data = {
            'base_analysis': base_analysis,
            'phase2': {}
        }
        
        # Run Phase 2 analyses in parallel
        tasks = []
        
        # 1. Intent classification
        if self.intent_classifier:
            tasks.append(self._analyze_intent(prompt))
        else:
            tasks.append(asyncio.sleep(0))  # No-op
        
        # 2. Semantic analysis
        if self.semantic_analyzer:
            tasks.append(self._analyze_semantic(prompt))
        else:
            tasks.append(asyncio.sleep(0))
        
        # 3. Context analysis
        if self.context_manager and user_id and session_id:
            tasks.append(self._analyze_context(prompt, user_id, session_id))
        else:
            tasks.append(asyncio.sleep(0))
        
        # Run all Phase 2 analyses in parallel
        intent_result, semantic_result, context_result = await asyncio.gather(*tasks)
        
        if intent_result:
            phase2_data['phase2']['intent_analysis'] = intent_result
        
        if semantic_result:
            phase2_data['phase2']['semantic_analysis'] = semantic_result
        
        if context_result:
            phase2_data['phase2']['context_analysis'] = context_result
        
        # Calculate combined risk score considering all dimensions
        combined_risk = self._calculate_combined_risk(phase2_data)
        phase2_data['combined_risk_score'] = combined_risk
        
        return phase2_data

    async def _analyze_intent(self, prompt: str) -> Optional[Dict]:
        """Run intent classification"""
        try:
            if not self.intent_classifier:
                return None
            
            intent_analysis = await self.intent_classifier.classify_async(prompt)
            
            return {
                'primary_intent': intent_analysis.primary_intent.value,
                'confidence': intent_analysis.confidence,
                'secondary_intent': (
                    intent_analysis.secondary_intent.value
                    if intent_analysis.secondary_intent else None
                ),
                'secondary_confidence': intent_analysis.secondary_confidence,
                'attack_type_description': intent_analysis.attack_type_description,
                'intent_risk_score': self.intent_classifier.get_intent_risk_score(
                    intent_analysis.primary_intent
                ),
                'all_intent_scores': intent_analysis.intent_scores or {}
            }
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return None

    async def _analyze_semantic(self, prompt: str) -> Optional[Dict]:
        """Run semantic analysis"""
        try:
            if not self.semantic_analyzer:
                return None
            
            # Find semantically similar attacks
            semantic_matches = await self.semantic_analyzer.analyze_semantic_similarity(
                prompt,
                top_k=3
            )
            
            # Detect prompt injection techniques
            injection_techniques = await self.semantic_analyzer.detect_prompt_injection_techniques(
                prompt
            )
            
            return {
                'semantic_matches': [
                    {
                        'similarity_score': m.similarity_score,
                        'matched_attack_pattern': m.matched_attack_pattern,
                        'attack_type': m.attack_type,
                        'confidence': m.confidence
                    }
                    for m in semantic_matches
                ],
                'prompt_injection_techniques': injection_techniques,
                'overall_semantic_risk': max(
                    [m.similarity_score for m in semantic_matches] + [0.0]
                ) or injection_techniques.get('injection_score', 0.0)
            }
        except Exception as e:
            logger.error(f"Semantic analysis error: {e}")
            return None

    async def _analyze_context(
        self,
        prompt: str,
        user_id: str,
        session_id: str
    ) -> Optional[Dict]:
        """Run context and escalation analysis"""
        try:
            if not self.context_manager:
                return None
            
            # Get or create conversation context
            session_context = self.context_manager.get_or_create_session(user_id, session_id)
            
            # Get user profile
            user_profile = self.context_manager.get_user_profile(user_id)
            
            # Detect context anomalies
            anomalies = session_context.detect_context_anomalies()
            
            # Get escalation detector for this session
            if session_id not in self.escalation_detectors:
                from .intent_classifier import IntentEscalationDetector
                self.escalation_detectors[session_id] = IntentEscalationDetector()
            
            # Record intent for escalation tracking
            # (This will be updated after intent classification)
            escalation_data = self.escalation_detectors[session_id].detect_escalation()
            
            return {
                'session_context': {
                    'session_age_minutes': session_context.get_context_summary()['session_age_minutes'],
                    'total_turns': session_context.total_turns,
                    'block_rate': session_context.blocked_turns / max(1, session_context.total_turns),
                    'unique_intents': session_context.get_context_summary()['unique_intents'],
                    'policy_violations': session_context.policy_violations
                },
                'context_anomalies': anomalies,
                'escalation_analysis': {
                    'is_escalating': escalation_data['is_escalating'],
                    'escalation_score': escalation_data['escalation_score'],
                    'patterns_detected': escalation_data['pattern'].split(', ') if escalation_data['pattern'] != 'none_detected' else [],
                    'confidence': escalation_data['confidence'],
                    'history_length': escalation_data['history_length'],
                    'unique_attack_types': escalation_data.get('unique_attack_types', 0)
                },
                'user_risk_profile': {
                    'user_id': user_profile.user_id,
                    'abuse_score': user_profile.abuse_score,
                    'is_suspicious': user_profile.is_suspicious,
                    'total_requests': user_profile.total_requests,
                    'block_rate': (
                        user_profile.blocked_requests / user_profile.total_requests
                        if user_profile.total_requests > 0 else 0.0
                    ),
                    'average_risk_score': user_profile.average_risk_score,
                    'unique_intents': list(user_profile.unique_intents),
                    'request_frequency': user_profile.request_frequency
                }
            }
        except Exception as e:
            logger.error(f"Context analysis error: {e}")
            return None

    def _calculate_combined_risk(self, phase2_data: Dict) -> float:
        """
        Calculate combined risk score from all Phase 2 dimensions.
        
        Weights:
        - Base ML risk: 40%
        - Intent risk: 25%
        - Semantic risk: 20%
        - Escalation risk: 15%
        """
        base_analysis = phase2_data.get('base_analysis', {})
        base_risk = base_analysis.get('risk_score', 0.0)
        
        intent_risk = 0.0
        if 'intent_analysis' in phase2_data['phase2']:
            intent_data = phase2_data['phase2']['intent_analysis']
            intent_risk = intent_data.get('intent_risk_score', 0.0)
        
        semantic_risk = 0.0
        if 'semantic_analysis' in phase2_data['phase2']:
            semantic_data = phase2_data['phase2']['semantic_analysis']
            semantic_risk = semantic_data.get('overall_semantic_risk', 0.0)
        
        escalation_risk = 0.0
        if 'context_analysis' in phase2_data['phase2']:
            context_data = phase2_data['phase2']['context_analysis']
            escalation_data = context_data.get('escalation_analysis', {})
            escalation_risk = escalation_data.get('escalation_score', 0.0)
        
        # Weighted combination
        combined_risk = (
            (base_risk * 0.40) +
            (intent_risk * 0.25) +
            (semantic_risk * 0.20) +
            (escalation_risk * 0.15)
        )
        
        return min(combined_risk, 1.0)

    def record_interaction(
        self,
        user_id: str,
        session_id: str,
        prompt: str,
        intent: str,
        risk_score: float,
        response_time_ms: float,
        was_blocked: bool = False
    ):
        """
        Record interaction for learning and profiling.
        Called after analysis to update context and profiles.
        """
        try:
            if not self.context_manager:
                return
            
            # Update context
            session_context = self.context_manager.get_or_create_session(user_id, session_id)
            session_context.add_turn(
                prompt=prompt,
                intent=intent,
                risk_score=risk_score,
                response_time_ms=response_time_ms
            )
            
            if was_blocked:
                session_context.policy_violations += 1
            
            # Update user profile
            self.context_manager.update_user_profile(
                user_id=user_id,
                intent=intent,
                risk_score=risk_score,
                was_blocked=was_blocked
            )
            
            # Update escalation detector
            from .intent_classifier import IntentType
            if session_id not in self.escalation_detectors:
                from .intent_classifier import IntentEscalationDetector
                self.escalation_detectors[session_id] = IntentEscalationDetector()
            
            try:
                intent_enum = IntentType(intent)
            except ValueError:
                intent_enum = IntentType.BENIGN
            
            self.escalation_detectors[session_id].record_intent(intent_enum, risk_score)
            
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")

    def get_system_statistics(self) -> Dict:
        """Get system-wide statistics"""
        stats = {
            'phase2_enabled': True,
            'components': {
                'intent_classifier': self.intent_classifier is not None,
                'semantic_analyzer': self.semantic_analyzer is not None,
                'context_manager': self.context_manager is not None
            }
        }
        
        if self.context_manager:
            stats['context_statistics'] = self.context_manager.get_statistics()
        
        return stats
