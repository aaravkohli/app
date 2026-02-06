"""
Advanced Text Analyzer using NLP and semantic analysis
"""

import re
import logging
from typing import Dict, Any, List, Tuple
import json

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """Advanced text analysis with NLP capabilities"""

    # Threat patterns with weights
    THREAT_PATTERNS = {
        # Prompt injection
        "prompt_injection": {
            "patterns": [
                r"ignore.*instructions",
                r"disregard.*instructions",
                r"override.*instructions",
                r"forget.*instructions",
                r"system.*prompt",
                r"reveal.*instructions",
                r"show.*system.*prompt",
                r"what.*instructions",
            ],
            "weight": 0.9,
            "description": "Potential prompt injection attack"
        },
        # Code injection
        "code_injection": {
            "patterns": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"__import__",
                r"subprocess",
                r"os\.system",
                r"shell.*command",
                r"command.*injection",
            ],
            "weight": 0.85,
            "description": "Potential code injection"
        },
        # SQL injection
        "sql_injection": {
            "patterns": [
                r"union\s+select",
                r"drop\s+table",
                r"insert\s+into",
                r"delete\s+from",
                r"update\s+.*\s+set",
                r"or\s+1\s*=\s*1",
            ],
            "weight": 0.8,
            "description": "Potential SQL injection"
        },
        # XSS/Script injection
        "xss_injection": {
            "patterns": [
                r"<script",
                r"javascript:",
                r"onerror\s*=",
                r"onclick\s*=",
                r"onload\s*=",
                r"<iframe",
                r"<object",
                r"<embed",
            ],
            "weight": 0.75,
            "description": "Potential XSS/Script injection"
        },
        # Malware/Phishing indicators
        "phishing": {
            "patterns": [
                r"verify.*account",
                r"confirm.*password",
                r"update.*payment",
                r"suspicious.*activity",
                r"click.*link.*urgent",
                r"enter.*credentials",
            ],
            "weight": 0.7,
            "description": "Potential phishing content"
        },
        # Sensitive data exfiltration
        "data_exfiltration": {
            "patterns": [
                r"api.*key",
                r"secret.*key",
                r"password",
                r"credit.*card",
                r"ssn",
                r"private.*key",
                r"access.*token",
            ],
            "weight": 0.65,
            "description": "Reference to sensitive data"
        },
    }

    # Benign/Safe patterns
    SAFE_PATTERNS = {
        "educational": [
            r"explain",
            r"how to",
            r"tutorial",
            r"learn",
            r"guide",
            r"help me",
            r"what is",
        ],
        "general_query": [
            r"what",
            r"when",
            r"where",
            r"why",
            r"who",
            r"summarize",
            r"describe",
        ],
        "creative": [
            r"write.*story",
            r"create.*poem",
            r"generate.*image",
            r"compose",
            r"design",
        ]
    }

    def __init__(self):
        """Initialize text analyzer"""
        logger.info("✅ Text Analyzer initialized")

    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive text analysis

        Args:
            text: Text content to analyze

        Returns:
            Analysis results with risk assessment
        """
        logger.info(f"📝 Analyzing text: {text[:60]}...")

        if not text or not isinstance(text, str):
            return {
                "risk_level": "low",
                "risk_score": 0.0,
                "input_type": "text",
                "message": "Empty or invalid text"
            }

        # Perform various analyses
        injection_risk = self._check_injection_threats(text)
        safe_score = self._check_safe_patterns(text)
        semantic_risk = self._analyze_semantic_threats(text)
        complexity_risk = self._check_text_complexity(text)

        # Aggregate results
        threats = []
        total_risk = 0.0
        weights = 0.0

        for threat_type, details in injection_risk.items():
            if details["score"] > 0:
                threats.append({
                    "type": threat_type,
                    "score": details["score"],
                    "description": details["description"],
                    "indicators": details["indicators"]
                })
                total_risk += details["score"] * details["weight"]
                weights += details["weight"]

        # Add semantic threats
        if semantic_risk["score"] > 0:
            threats.append({
                "type": "semantic_threat",
                "score": semantic_risk["score"],
                "description": semantic_risk["description"],
                "indicators": semantic_risk["indicators"]
            })
            total_risk += semantic_risk["score"] * 0.6
            weights += 0.6

        # Calculate final risk
        if weights > 0:
            risk_score = min(1.0, total_risk / weights)
        else:
            risk_score = 0.0

        # Apply safe offset
        risk_score = max(0.0, risk_score - safe_score)

        # Add complexity factor
        risk_score = min(1.0, risk_score + (complexity_risk * 0.1))

        # Determine risk level
        risk_level = self._score_to_level(risk_score)

        result = {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 3),
            "input_type": "text",
            "text_length": len(text),
            "word_count": len(text.split()),
            "threats": threats,
            "safe_patterns_detected": len([t for t in threats if "safe" in str(t).lower()]) > 0,
            "complexity": {
                "has_special_chars": bool(re.search(r"[!@#$%^&*()_+=\-\[\]{}|;:,.<>?/~`]", text)),
                "has_urls": bool(re.search(r"https?://", text)),
                "has_code": self._detect_code_syntax(text),
            }
        }

        logger.info(f"✅ Text analysis complete - Risk: {risk_level} ({risk_score})")
        return result

    def _check_injection_threats(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Check for injection-type threats"""
        text_lower = text.lower()
        results = {}

        for threat_type, config in self.THREAT_PATTERNS.items():
            score = 0.0
            indicators = []

            for pattern in config["patterns"]:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 1.0 / len(config["patterns"])
                    indicators.append(pattern)

            results[threat_type] = {
                "score": min(1.0, score),
                "weight": config["weight"],
                "description": config["description"],
                "indicators": indicators[:3]  # Top 3 indicators
            }

        return results

    def _check_safe_patterns(self, text: str) -> float:
        """Check for safe/benign patterns"""
        text_lower = text.lower()
        total_matches = 0
        total_patterns = sum(len(patterns) for patterns in self.SAFE_PATTERNS.values())

        for category, patterns in self.SAFE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    total_matches += 1

        # Return offset (0-0.3)
        return min(0.3, (total_matches / total_patterns) * 0.3) if total_patterns > 0 else 0.0

    def _analyze_semantic_threats(self, text: str) -> Dict[str, Any]:
        """Analyze semantic/contextual threats"""
        threats = {
            "score": 0.0,
            "description": "No semantic threats detected",
            "indicators": []
        }

        # Check for context-based threats
        if self._is_manipulative_language(text):
            threats["score"] += 0.3
            threats["indicators"].append("manipulative_language")

        if self._is_social_engineering(text):
            threats["score"] += 0.4
            threats["indicators"].append("social_engineering")

        if self._is_obfuscated(text):
            threats["score"] += 0.3
            threats["indicators"].append("obfuscation")

        threats["score"] = min(1.0, threats["score"])
        if threats["indicators"]:
            threats["description"] = f"Potential semantic threats: {', '.join(threats['indicators'])}"

        return threats

    def _check_text_complexity(self, text: str) -> float:
        """Analyze text complexity as indicator of potential threat"""
        complexity_score = 0.0

        # Multiple consecutive special characters
        if re.search(r"[!@#$%^&*()_+=\-\[\]{}|;:,.<>?/~`]{3,}", text):
            complexity_score += 0.2

        # Unusual character encoding patterns
        if re.search(r"\\x[0-9a-f]{2}", text, re.IGNORECASE):
            complexity_score += 0.2

        # Mixed case unusual patterns
        if re.search(r"[A-Z]{5,}[a-z]+[A-Z]", text):
            complexity_score += 0.1

        # Excessive numbers
        if len(re.findall(r"\d+", text)) > len(text.split()) / 2:
            complexity_score += 0.1

        return min(1.0, complexity_score)

    def _is_manipulative_language(self, text: str) -> bool:
        """Detect manipulative language patterns"""
        patterns = [
            r"you (must|have to|should) immediately",
            r"urgent",
            r"act now",
            r"limited time",
            r"don't (think|worry)",
            r"trust me",
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def _is_social_engineering(self, text: str) -> bool:
        """Detect social engineering attempts"""
        patterns = [
            r"verify.*identity",
            r"confirm.*account",
            r"update.*information",
            r"suspicious.*activity",
            r"unusual.*access",
            r"temporary.*block",
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def _is_obfuscated(self, text: str) -> bool:
        """Detect obfuscated or encoded content"""
        # Base64 patterns
        if re.search(r"[A-Za-z0-9+/]{20,}={0,2}", text):
            return True

        # Hex encoding
        if re.search(r"0x[0-9a-f]{8,}", text, re.IGNORECASE):
            return True

        # Unicode escapes
        if re.search(r"\\u[0-9a-f]{4}", text, re.IGNORECASE):
            return True

        return False

    def _detect_code_syntax(self, text: str) -> bool:
        """Detect if text contains code"""
        code_indicators = [
            r"def\s+\w+\s*\(",  # Python function
            r"function\s+\w+\s*\(",  # JS function
            r"class\s+\w+",  # Class definition
            r"if\s*\(",  # If statement
            r"for\s*\(",  # For loop
            r"import\s+",  # Import statement
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in code_indicators)

    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 0.7:
            return "critical" if score >= 0.85 else "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
