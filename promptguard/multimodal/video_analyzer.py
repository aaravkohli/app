"""
Video Security Analyzer - Detects threats in videos
"""

import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """Analyzes videos for security threats"""

    def __init__(self):
        """Initialize video analyzer"""
        logger.info("✅ Video Analyzer initialized")

    async def analyze(self, video_path: str) -> Dict[str, Any]:
        """
        Analyze video file for security threats

        Args:
            video_path: Path to the video file

        Returns:
            Analysis results
        """
        logger.info(f"🎬 Analyzing video: {video_path}")

        try:
            path = Path(video_path)
            if not path.exists():
                return {
                    "risk_level": "high",
                    "risk_score": 0.9,
                    "error": "Video file not found",
                    "input_type": "video"
                }

            file_size = path.stat().st_size
            if file_size == 0:
                return {
                    "risk_level": "high",
                    "risk_score": 0.85,
                    "error": "Empty video file",
                    "input_type": "video"
                }

            # Perform analysis
            threats = []
            risk_score = 0.0

            # Check file structure
            structure_risk = await self._check_file_structure(video_path)
            if structure_risk["score"] > 0:
                threats.append({
                    "type": "invalid_structure",
                    "score": structure_risk["score"],
                    "description": structure_risk["description"]
                })
                risk_score += structure_risk["score"] * 0.3

            # Check for embedded malware
            malware_risk = await self._check_embedded_content(video_path)
            if malware_risk["score"] > 0:
                threats.append({
                    "type": "embedded_threat",
                    "score": malware_risk["score"],
                    "description": malware_risk["description"]
                })
                risk_score += malware_risk["score"] * 0.5

            # Check for polyglot files
            polyglot_risk = await self._check_polyglot(video_path)
            if polyglot_risk["score"] > 0:
                threats.append({
                    "type": "polyglot_file",
                    "score": polyglot_risk["score"],
                    "description": polyglot_risk["description"]
                })
                risk_score += polyglot_risk["score"] * 0.4

            # Check metadata
            metadata_risk = await self._check_metadata(video_path)
            if metadata_risk["score"] > 0:
                threats.append({
                    "type": "suspicious_metadata",
                    "score": metadata_risk["score"],
                    "description": metadata_risk["description"]
                })
                risk_score += metadata_risk["score"] * 0.2

            risk_score = min(1.0, risk_score)
            risk_level = self._score_to_level(risk_score)

            result = {
                "risk_level": risk_level,
                "risk_score": round(risk_score, 3),
                "input_type": "video",
                "file_path": str(path),
                "file_size": file_size,
                "file_name": path.name,
                "threats": threats,
            }

            logger.info(f"✅ Video analysis complete - Risk: {risk_level}")
            return result

        except Exception as e:
            logger.error(f"❌ Video analysis failed: {str(e)}")
            return {
                "risk_level": "high",
                "risk_score": 0.8,
                "error": str(e),
                "input_type": "video"
            }

    async def _check_file_structure(self, video_path: str) -> Dict[str, Any]:
        """Check if video has valid structure"""
        try:
            with open(video_path, "rb") as f:
                header = f.read(12)

            risk_score = 0.0
            details = []

            # Check common video signatures
            valid_signatures = [
                (b"ftyp", "MP4/MOV"),
                (b"RIFF", "AVI/WAV"),
                (b"\x1a\x45\xdf\xa3", "Matroska"),
                (b"FLV\x01", "FLV"),
            ]

            has_valid_sig = any(sig in header for sig, _ in valid_signatures)

            if not has_valid_sig:
                risk_score += 0.4
                details.append("Unknown or missing video signature")

            return {
                "score": risk_score,
                "description": "Invalid video structure detected" if details else "Valid video structure"
            }

        except Exception as e:
            logger.warning(f"File structure check failed: {str(e)}")
            return {"score": 0.2, "description": "Structure check error"}

    async def _check_embedded_content(self, video_path: str) -> Dict[str, Any]:
        """Check for embedded malicious content"""
        try:
            with open(video_path, "rb") as f:
                data = f.read()

            risk_score = 0.0

            # Check for embedded executables
            if b"MZ\x90\x00" in data:  # PE executable
                risk_score += 0.7

            # Check for embedded archives
            if b"PK\x03\x04" in data:  # ZIP
                risk_score += 0.3

            if b"%PDF" in data:  # PDF
                risk_score += 0.2

            # Check for suspicious commands
            suspicious = [b"cmd.exe", b"powershell", b"bash", b"/bin/sh"]
            for cmd in suspicious:
                if cmd in data:
                    risk_score += 0.2

            return {
                "score": min(1.0, risk_score),
                "description": "Potential embedded malware detected" if risk_score > 0 else "No embedded threats"
            }

        except Exception as e:
            logger.warning(f"Embedded content check failed: {str(e)}")
            return {"score": 0.0, "description": "Embedded check error"}

    async def _check_polyglot(self, video_path: str) -> Dict[str, Any]:
        """Check if file is a polyglot (multiple file types)"""
        try:
            with open(video_path, "rb") as f:
                data = f.read()

            risk_score = 0.0

            # Multiple file signatures = polyglot
            signatures = [
                (b"ftyp", "MP4"),
                (b"RIFF", "AVI"),
                (b"PK\x03\x04", "ZIP"),
                (b"%PDF", "PDF"),
                (b"MZ", "PE"),
                (b"\x7fELF", "ELF"),
                (b"GIF", "GIF"),
                (b"\xff\xd8\xff", "JPEG"),
                (b"\x89PNG", "PNG"),
            ]

            found_sigs = sum(1 for sig, _ in signatures if sig in data)

            if found_sigs > 1:
                risk_score = min(1.0, found_sigs * 0.3)

            return {
                "score": risk_score,
                "description": f"Polyglot file detected ({found_sigs} signatures)" if risk_score > 0 else "No polyglot indicators"
            }

        except Exception as e:
            logger.warning(f"Polyglot check failed: {str(e)}")
            return {"score": 0.0, "description": "Polyglot check error"}

    async def _check_metadata(self, video_path: str) -> Dict[str, Any]:
        """Check video metadata"""
        try:
            with open(video_path, "rb") as f:
                data = f.read()

            risk_score = 0.0

            # Look for suspicious metadata tags
            suspicious_patterns = [
                b"<script",
                b"javascript:",
                b"onclick=",
                b"onerror=",
            ]

            for pattern in suspicious_patterns:
                if pattern in data:
                    risk_score += 0.3

            return {
                "score": min(1.0, risk_score),
                "description": "Suspicious metadata detected" if risk_score > 0 else "Metadata OK"
            }

        except Exception as e:
            logger.warning(f"Metadata check failed: {str(e)}")
            return {"score": 0.0, "description": "Metadata check error"}

    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 0.7:
            return "critical" if score >= 0.85 else "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
