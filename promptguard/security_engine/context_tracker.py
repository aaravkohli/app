"""
Context Tracking Module

Maintains conversation context, user behavior patterns, and session state.
Enables detection of contextual threats and user-specific risk factors.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import logging
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """A single exchange in conversation"""
    prompt: str
    intent: str
    risk_score: float
    timestamp: datetime
    response_time_ms: float
    analysis_details: Optional[Dict] = None


@dataclass
class UserProfile:
    """User-specific behavioral profile"""
    user_id: str
    first_seen: datetime
    last_seen: datetime
    total_requests: int = 0
    blocked_requests: int = 0
    average_risk_score: float = 0.0
    unique_intents: set = field(default_factory=set)
    request_frequency: float = 0.0  # requests per minute
    is_suspicious: bool = False
    abuse_score: float = 0.0  # 0.0-1.0


class ConversationContext:
    """
    Maintains context for a conversation thread.
    Tracks history, patterns, and state across multiple turns.
    """

    def __init__(
        self,
        user_id: str,
        session_id: str,
        window_size: int = 20,
        ttl_minutes: int = 30
    ):
        """
        Initialize conversation context.
        
        Args:
            user_id: Unique user identifier
            session_id: Unique session identifier
            window_size: Number of turns to keep in history
            ttl_minutes: Session time-to-live in minutes
        """
        self.user_id = user_id
        self.session_id = session_id
        self.window_size = window_size
        self.ttl_minutes = ttl_minutes
        
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.turns: List[ConversationTurn] = []
        
        # Aggregate statistics
        self.total_turns = 0
        self.blocked_turns = 0
        self.escalation_detected = False
        self.policy_violations = 0

    def add_turn(
        self,
        prompt: str,
        intent: str,
        risk_score: float,
        response_time_ms: float,
        analysis_details: Optional[Dict] = None
    ):
        """Record a new turn in conversation"""
        turn = ConversationTurn(
            prompt=prompt,
            intent=intent,
            risk_score=risk_score,
            timestamp=datetime.now(),
            response_time_ms=response_time_ms,
            analysis_details=analysis_details
        )
        
        self.turns.append(turn)
        self.total_turns += 1
        self.last_activity = datetime.now()
        
        # Keep only recent turns
        if len(self.turns) > self.window_size:
            self.turns = self.turns[-self.window_size:]
        
        # Update counts
        if risk_score > 0.5:
            self.blocked_turns += 1

    def is_expired(self) -> bool:
        """Check if session has expired"""
        age = datetime.now() - self.created_at
        return age > timedelta(minutes=self.ttl_minutes)

    def get_context_summary(self) -> Dict:
        """Get summary of conversation context"""
        if not self.turns:
            return {
                'session_age_minutes': 0,
                'total_turns': 0,
                'block_rate': 0.0,
                'average_risk_score': 0.0,
                'unique_intents': []
            }

        block_rate = self.blocked_turns / max(1, self.total_turns)
        avg_risk = sum(t.risk_score for t in self.turns) / len(self.turns)
        unique_intents = list(set(t.intent for t in self.turns))
        
        age = (datetime.now() - self.created_at).total_seconds() / 60

        return {
            'session_age_minutes': age,
            'total_turns': self.total_turns,
            'block_rate': block_rate,
            'average_risk_score': avg_risk,
            'unique_intents': unique_intents,
            'blocked_turns': self.blocked_turns,
            'policy_violations': self.policy_violations
        }

    def detect_context_anomalies(self) -> Dict:
        """
        Detect anomalous patterns in conversation.
        
        Returns:
            {
                'has_anomalies': bool,
                'anomaly_score': 0.0-1.0,
                'detected_patterns': [str],
                'risk_increase': float
            }
        """
        if len(self.turns) < 3:
            return {
                'has_anomalies': False,
                'anomaly_score': 0.0,
                'detected_patterns': [],
                'risk_increase': 0.0
            }

        anomaly_score = 0.0
        patterns = []

        # Pattern 1: Sudden increase in risk
        early_risk = sum(t.risk_score for t in self.turns[:-5]) / max(1, len(self.turns[:-5]))
        recent_risk = sum(t.risk_score for t in self.turns[-5:]) / min(5, len(self.turns[-5:]))
        risk_increase = recent_risk - early_risk
        
        if risk_increase > 0.2:
            patterns.append("sudden_risk_increase")
            anomaly_score += 0.3

        # Pattern 2: High block rate (>50% blocked)
        block_rate = self.blocked_turns / max(1, self.total_turns)
        if block_rate > 0.5:
            patterns.append("high_block_rate")
            anomaly_score += 0.25

        # Pattern 3: Policy violations
        if self.policy_violations > 2:
            patterns.append("multiple_policy_violations")
            anomaly_score += 0.25

        # Pattern 4: Suspicious access patterns
        if len(self.turns) > 10 and self.total_turns > 20:
            avg_response_time = sum(t.response_time_ms for t in self.turns) / len(self.turns)
            recent_times = [t.response_time_ms for t in self.turns[-5:]]
            
            # Rapid-fire requests
            if all(t < avg_response_time * 0.5 for t in recent_times):
                patterns.append("rapid_fire_requests")
                anomaly_score += 0.2

        anomaly_score = min(anomaly_score, 1.0)

        return {
            'has_anomalies': anomaly_score > 0.4,
            'anomaly_score': anomaly_score,
            'detected_patterns': patterns,
            'risk_increase': risk_increase,
            'block_rate': block_rate
        }


class ContextManager:
    """
    Manages multiple conversation contexts and user profiles.
    Thread-safe storage for context across requests.
    """

    def __init__(self, max_sessions: int = 10000, cleanup_interval_minutes: int = 60):
        """
        Initialize context manager.
        
        Args:
            max_sessions: Maximum concurrent sessions to track
            cleanup_interval_minutes: Interval for cleanup of expired sessions
        """
        self.max_sessions = max_sessions
        self.cleanup_interval = timedelta(minutes=cleanup_interval_minutes)
        self.last_cleanup = datetime.now()
        
        # Session storage: session_id -> ConversationContext
        self.sessions: Dict[str, ConversationContext] = {}
        
        # User profiles: user_id -> UserProfile
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Global statistics
        self.total_requests = 0
        self.total_blocked = 0

    def get_or_create_session(
        self,
        user_id: str,
        session_id: str
    ) -> ConversationContext:
        """Get or create conversation context"""
        # Periodic cleanup
        if datetime.now() - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired_sessions()

        if session_id not in self.sessions:
            if len(self.sessions) >= self.max_sessions:
                # Remove oldest session
                oldest_id = min(
                    self.sessions.keys(),
                    key=lambda k: self.sessions[k].last_activity
                )
                del self.sessions[oldest_id]

            self.sessions[session_id] = ConversationContext(user_id, session_id)

        return self.sessions[session_id]

    def get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                first_seen=datetime.now(),
                last_seen=datetime.now()
            )
        
        profile = self.user_profiles[user_id]
        profile.last_seen = datetime.now()
        return profile

    def update_user_profile(
        self,
        user_id: str,
        intent: str,
        risk_score: float,
        was_blocked: bool = False
    ):
        """Update user profile with new request"""
        profile = self.get_user_profile(user_id)
        
        profile.total_requests += 1
        if was_blocked:
            profile.blocked_requests += 1
        
        profile.unique_intents.add(intent)
        
        # Update average risk score
        old_avg = profile.average_risk_score
        profile.average_risk_score = (
            (old_avg * (profile.total_requests - 1) + risk_score) /
            profile.total_requests
        )
        
        # Update request frequency
        age_minutes = (datetime.now() - profile.first_seen).total_seconds() / 60
        if age_minutes > 0:
            profile.request_frequency = profile.total_requests / age_minutes
        
        # Calculate abuse score
        self._update_abuse_score(profile)

    def _update_abuse_score(self, profile: UserProfile):
        """Calculate user abuse score (0.0-1.0)"""
        score = 0.0
        
        # Factor 1: Block rate (high block rate = likely abuse)
        if profile.total_requests > 0:
            block_rate = profile.blocked_requests / profile.total_requests
            score += block_rate * 0.4

        # Factor 2: High average risk
        score += min(profile.average_risk_score, 1.0) * 0.3

        # Factor 3: Request frequency (too many requests = abuse)
        if profile.request_frequency > 10:  # >10 req/min
            score += min(profile.request_frequency / 100, 1.0) * 0.2

        # Factor 4: Multiple attack types (sophisticated abuse)
        if len(profile.unique_intents) >= 4:
            score += 0.1

        profile.abuse_score = min(score, 1.0)
        profile.is_suspicious = profile.abuse_score > 0.6

    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired_ids = [
            sid for sid, ctx in self.sessions.items()
            if ctx.is_expired()
        ]
        
        for sid in expired_ids:
            del self.sessions[sid]
        
        logger.info(f"Cleaned up {len(expired_ids)} expired sessions")
        self.last_cleanup = datetime.now()

    def get_statistics(self) -> Dict:
        """Get global statistics"""
        active_sessions = sum(1 for ctx in self.sessions.values() if not ctx.is_expired())
        
        return {
            'active_sessions': active_sessions,
            'total_users': len(self.user_profiles),
            'suspicious_users': sum(1 for p in self.user_profiles.values() if p.is_suspicious),
            'global_block_rate': self._calculate_global_block_rate(),
            'average_abuse_score': self._calculate_avg_abuse_score()
        }

    def _calculate_global_block_rate(self) -> float:
        """Calculate global block rate across all users"""
        total_requests = sum(p.total_requests for p in self.user_profiles.values())
        total_blocked = sum(p.blocked_requests for p in self.user_profiles.values())
        
        if total_requests == 0:
            return 0.0
        return total_blocked / total_requests

    def _calculate_avg_abuse_score(self) -> float:
        """Calculate average abuse score"""
        if not self.user_profiles:
            return 0.0
        return sum(p.abuse_score for p in self.user_profiles.values()) / len(self.user_profiles)
