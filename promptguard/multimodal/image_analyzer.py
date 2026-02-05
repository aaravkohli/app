"""
Image Security Analyzer - Detects threats in images
"""

import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Analyzes images for security threats"""

    # Threat indicators in images
    THREAT_INDICATORS = {
        "malware_artifacts": {
            "description": "Suspicious binary/hex content in image metadata",
            "weight": 0.8
        },
        "steganography": {
            "description": "Potential hidden data in image",
            "weight": 0.6
        },
        "phishing_content": {
            "description": "Image contains phishing indicators",
            "weight": 0.7
        },
        "suspicious_qr": {
            "description": "QR code present - potential phishing",
            "weight": 0.5
        },
        "text_injection": {
            "description": "Text overlay with injection keywords",
            "weight": 0.6
        }
    }

    def __init__(self):
        """Initialize image analyzer"""
        logger.info("✅ Image Analyzer initialized")

    async def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image for security threats

        Args:
            image_path: Path to the image file

        Returns:
            Analysis results
        """
        logger.info(f"🖼️ Analyzing image: {image_path}")

        try:
            path = Path(image_path)
            if not path.exists():
                return {
                    "risk_level": "high",
                    "risk_score": 0.9,
                    "error": "Image file not found",
                    "input_type": "image"
                }

            # Check file integrity
            file_size = path.stat().st_size
            if file_size == 0:
                return {
                    "risk_level": "high",
                    "risk_score": 0.85,
                    "error": "Empty image file",
                    "input_type": "image"
                }

            # Perform analysis
            threats = []
            risk_score = 0.0

            # Check metadata
            metadata_risk = await self._check_metadata(image_path)
            if metadata_risk["score"] > 0:
                threats.append({
                    "type": "metadata_threat",
                    "score": metadata_risk["score"],
                    "description": metadata_risk["description"],
                    "details": metadata_risk["details"]
                })
                risk_score += metadata_risk["score"] * 0.3

            # Check for steganography indicators
            stego_risk = await self._check_steganography(image_path)
            if stego_risk["score"] > 0:
                threats.append({
                    "type": "steganography",
                    "score": stego_risk["score"],
                    "description": stego_risk["description"]
                })
                risk_score += stego_risk["score"] * 0.4

            # Check for embedded malware signatures
            malware_risk = await self._check_malware_signatures(image_path)
            if malware_risk["score"] > 0:
                threats.append({
                    "type": "malware_signature",
                    "score": malware_risk["score"],
                    "description": malware_risk["description"]
                })
                risk_score += malware_risk["score"] * 0.5

            # Check for suspicious binary content
            binary_risk = await self._check_suspicious_binary(image_path)
            if binary_risk["score"] > 0:
                threats.append({
                    "type": "suspicious_binary",
                    "score": binary_risk["score"],
                    "description": binary_risk["description"]
                })
                risk_score += binary_risk["score"] * 0.3

            risk_score = min(1.0, risk_score)
            risk_level = self._score_to_level(risk_score)

            result = {
                "risk_level": risk_level,
                "risk_score": round(risk_score, 3),
                "input_type": "image",
                "file_path": str(path),
                "file_size": file_size,
                "file_name": path.name,
                "threats": threats,
            }

            logger.info(f"✅ Image analysis complete - Risk: {risk_level}")
            return result

        except Exception as e:
            logger.error(f"❌ Image analysis failed: {str(e)}")
            return {
                "risk_level": "high",
                "risk_score": 0.8,
                "error": str(e),
                "input_type": "image"
            }

    async def _check_metadata(self, image_path: str) -> Dict[str, Any]:
        """Check image metadata for threats"""
        try:
            # Try to read metadata using PIL if available
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS

                img = Image.open(image_path)
                exif = img._getexif() if hasattr(img, "_getexif") else None

                risk_score = 0.0
                details = []

                if exif:
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)

                        # Check for suspicious metadata
                        if isinstance(value, str):
                            if len(value) > 500:  # Unusually long value
                                risk_score += 0.15
                                details.append(f"Unusually long {tag} field")

                            if any(keyword in value.lower() for keyword in
                                   ["script", "eval", "exec", "malware", "exploit"]):
                                risk_score += 0.25
                                details.append(f"Suspicious keyword in {tag}")

                return {
                    "score": min(1.0, risk_score),
                    "description": "Suspicious metadata detected" if details else "Metadata OK",
                    "details": details[:3]
                }

            except ImportError:
                # PIL not available, do basic checks
                return {
                    "score": 0.1,
                    "description": "Basic metadata check (PIL not available)",
                    "details": []
                }

        except Exception as e:
            logger.warning(f"Metadata check failed: {str(e)}")
            return {"score": 0.2, "description": "Metadata check error", "details": []}

    async def _check_steganography(self, image_path: str) -> Dict[str, Any]:
        """Check for steganography indicators"""
        try:
            with open(image_path, "rb") as f:
                data = f.read()

            risk_score = 0.0

            # Check for embedded archives
            if b"PK\x03\x04" in data:  # ZIP signature
                risk_score += 0.4
            if b"%PDF" in data:  # PDF signature
                risk_score += 0.3
            if b"MZ" in data:  # PE executable
                risk_score += 0.6

            # Check for embedded executables
            suspicious_signatures = [
                (b"\x4d\x5a", 0.8),  # MZ (PE)
                (b"\x7fELF", 0.8),  # ELF
                (b"#!/", 0.5),  # Script
            ]

            for sig, weight in suspicious_signatures:
                if sig in data:
                    risk_score += weight * 0.2

            return {
                "score": min(1.0, risk_score),
                "description": "Potential steganography/embedded content detected" if risk_score > 0 else "No steganography detected"
            }

        except Exception as e:
            logger.warning(f"Steganography check failed: {str(e)}")
            return {"score": 0.1, "description": "Steganography check error"}

    async def _check_malware_signatures(self, image_path: str) -> Dict[str, Any]:
        """Check for known malware signatures"""
        try:
            with open(image_path, "rb") as f:
                data = f.read()

            risk_score = 0.0

            # Common malware signatures
            malware_sigs = [
                (b"CreateRemoteThread", 0.8),
                (b"WinExec", 0.8),
                (b"ShellExecute", 0.7),
                (b"cmd.exe", 0.6),
                (b"powershell", 0.6),
            ]

            for sig, weight in malware_sigs:
                if sig in data:
                    risk_score += weight * 0.1

            return {
                "score": min(1.0, risk_score),
                "description": "Potential malware signature detected" if risk_score > 0 else "No malware signatures detected"
            }

        except Exception as e:
            logger.warning(f"Malware signature check failed: {str(e)}")
            return {"score": 0.0, "description": "Signature check error"}

    async def _check_suspicious_binary(self, image_path: str) -> Dict[str, Any]:
        """Check for suspicious binary content"""
        try:
            with open(image_path, "rb") as f:
                data = f.read()

            # Check entropy (high entropy might indicate compression/encryption)
            entropy = self._calculate_entropy(data)
            risk_score = 0.0

            if entropy > 7.8:  # Very high entropy
                risk_score += 0.3

            # Check for unusually long null bytes
            if data.count(b"\x00") > len(data) * 0.3:
                risk_score += 0.2

            # Check for suspicious patterns
            if b"\x00\x00\x00" in data:
                risk_score += 0.15

            return {
                "score": min(1.0, risk_score),
                "description": f"Binary content analysis (entropy: {entropy:.2f})"
            }

        except Exception as e:
            logger.warning(f"Binary check failed: {str(e)}")
            return {"score": 0.0, "description": "Binary check error"}

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0

        entropy = 0.0
        for i in range(256):
            freq = data.count(bytes([i]))
            if freq > 0:
                p = freq / len(data)
                entropy -= p * (p.__log__() if p > 0 else 0)

        return entropy / 8.0  # Normalize to 0-1

    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 0.7:
            return "critical" if score >= 0.85 else "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
