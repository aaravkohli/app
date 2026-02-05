"""
File Security Analyzer - Analyzes various file types
Supports: Code, Documents, PDFs, Archives
"""

import logging
import zipfile
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class FileAnalyzer:
    """Analyzes various file types for security threats"""

    # Dangerous code patterns
    DANGEROUS_CODE_PATTERNS = {
        "remote_execution": [
            r"os\.system",
            r"subprocess\.",
            r"eval\(",
            r"exec\(",
            r"shell=True",
            r"WinExec",
            r"CreateProcess",
            r"Runtime\.exec",
        ],
        "file_operations": [
            r"open\(",
            r"read\(",
            r"write\(",
            r"delete\(",
            r"rmdir",
            r"remove\(",
        ],
        "network": [
            r"socket\.",
            r"requests\.get",
            r"urllib",
            r"http\.client",
            r"curl",
            r"wget",
        ],
        "registry_access": [
            r"winreg\.",
            r"HKEY_",
            r"RegOpenKey",
            r"RegCreateKey",
        ],
    }

    def __init__(self):
        """Initialize file analyzer"""
        logger.info("✅ File Analyzer initialized")

    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a file based on its type

        Args:
            file_path: Path to the file

        Returns:
            Analysis results
        """
        path = Path(file_path)
        ext = path.suffix.lower().lstrip(".")

        if ext == "py" or ext == "txt" and self._is_code(file_path):
            return await self.analyze_code(file_path)
        elif ext == "pdf":
            return await self.analyze_pdf(file_path)
        elif ext in ["zip", "rar", "7z", "tar", "gz"]:
            return await self.analyze_archive(file_path)
        else:
            return await self.analyze_document(file_path)

    async def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze code files for security threats

        Args:
            file_path: Path to code file

        Returns:
            Analysis results
        """
        logger.info(f"📄 Analyzing code file: {file_path}")

        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "risk_level": "high",
                    "risk_score": 0.9,
                    "error": "File not found",
                    "input_type": "code"
                }

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content:
                return {
                    "risk_level": "low",
                    "risk_score": 0.1,
                    "input_type": "code",
                    "file_name": path.name,
                    "threats": [],
                    "message": "Empty file"
                }

            # Analyze code
            threats = []
            risk_score = 0.0

            for category, patterns in self.DANGEROUS_CODE_PATTERNS.items():
                for pattern in patterns:
                    import re
                    if re.search(pattern, content, re.IGNORECASE):
                        threat_weight = 0.8 if category in ["remote_execution", "registry_access"] else 0.5
                        threats.append({
                            "type": category,
                            "pattern": pattern,
                            "severity": "high" if threat_weight > 0.7 else "medium"
                        })
                        risk_score += threat_weight * 0.05

            # Check for hardcoded secrets
            secret_risk = self._check_hardcoded_secrets(content)
            if secret_risk > 0:
                threats.append({
                    "type": "hardcoded_secrets",
                    "description": "Potential hardcoded credentials or API keys",
                    "severity": "high"
                })
                risk_score += secret_risk

            # Check for SQL injection vulnerabilities
            if self._check_sql_injection(content):
                threats.append({
                    "type": "sql_injection_risk",
                    "description": "Potential SQL injection vulnerability",
                    "severity": "high"
                })
                risk_score += 0.3

            # Check for insecure random
            if self._check_insecure_random(content):
                threats.append({
                    "type": "insecure_random",
                    "description": "Use of insecure random number generation",
                    "severity": "medium"
                })
                risk_score += 0.15

            risk_score = min(1.0, risk_score)
            risk_level = self._score_to_level(risk_score)

            result = {
                "risk_level": risk_level,
                "risk_score": round(risk_score, 3),
                "input_type": "code",
                "file_name": path.name,
                "file_size": path.stat().st_size,
                "line_count": len(content.split("\n")),
                "threats": threats,
            }

            logger.info(f"✅ Code analysis complete - Risk: {risk_level}")
            return result

        except Exception as e:
            logger.error(f"❌ Code analysis failed: {str(e)}")
            return {
                "risk_level": "high",
                "risk_score": 0.8,
                "error": str(e),
                "input_type": "code"
            }

    async def analyze_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze PDF files for threats

        Args:
            file_path: Path to PDF file

        Returns:
            Analysis results
        """
        logger.info(f"📕 Analyzing PDF: {file_path}")

        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "risk_level": "high",
                    "risk_score": 0.9,
                    "error": "PDF not found",
                    "input_type": "pdf"
                }

            with open(file_path, "rb") as f:
                data = f.read()

            if not data.startswith(b"%PDF"):
                return {
                    "risk_level": "high",
                    "risk_score": 0.85,
                    "error": "Invalid PDF signature",
                    "input_type": "pdf"
                }

            threats = []
            risk_score = 0.0

            # Check for embedded JavaScript
            if b"/JavaScript" in data or b"/JS" in data:
                threats.append({
                    "type": "embedded_javascript",
                    "description": "PDF contains embedded JavaScript",
                    "severity": "high"
                })
                risk_score += 0.5

            # Check for embedded files
            if b"/EmbeddedFile" in data or b"/Launch" in data:
                threats.append({
                    "type": "embedded_file",
                    "description": "PDF contains embedded executable or file",
                    "severity": "high"
                })
                risk_score += 0.6

            # Check for openaction (auto-execute)
            if b"/OpenAction" in data:
                threats.append({
                    "type": "auto_execute",
                    "description": "PDF has OpenAction (may auto-execute)",
                    "severity": "high"
                })
                risk_score += 0.5

            # Check for XFA forms (potential exploit vector)
            if b"/XFA" in data:
                threats.append({
                    "type": "xfa_form",
                    "description": "PDF contains XFA form (potential exploit)",
                    "severity": "medium"
                })
                risk_score += 0.3

            # Check for suspicious objects
            if b"/ObjStm" in data:
                threats.append({
                    "type": "object_stream",
                    "description": "PDF uses object streams (potential obfuscation)",
                    "severity": "medium"
                })
                risk_score += 0.2

            risk_score = min(1.0, risk_score)
            risk_level = self._score_to_level(risk_score)

            result = {
                "risk_level": risk_level,
                "risk_score": round(risk_score, 3),
                "input_type": "pdf",
                "file_name": path.name,
                "file_size": path.stat().st_size,
                "threats": threats,
            }

            logger.info(f"✅ PDF analysis complete - Risk: {risk_level}")
            return result

        except Exception as e:
            logger.error(f"❌ PDF analysis failed: {str(e)}")
            return {
                "risk_level": "high",
                "risk_score": 0.8,
                "error": str(e),
                "input_type": "pdf"
            }

    async def analyze_archive(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze archive files (ZIP, RAR, etc.)

        Args:
            file_path: Path to archive file

        Returns:
            Analysis results
        """
        logger.info(f"📦 Analyzing archive: {file_path}")

        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "risk_level": "high",
                    "risk_score": 0.9,
                    "error": "Archive not found",
                    "input_type": "archive"
                }

            threats = []
            risk_score = 0.0

            if path.suffix.lower() == ".zip":
                try:
                    with zipfile.ZipFile(file_path, "r") as zf:
                        # Check for suspicious file names
                        for name in zf.namelist():
                            # Check for double extensions
                            if name.count(".") > 1:
                                parts = name.split(".")
                                if self._is_dangerous_extension(parts[-2]):
                                    threats.append({
                                        "type": "double_extension",
                                        "description": f"File with suspicious double extension: {name}",
                                        "severity": "high"
                                    })
                                    risk_score += 0.3

                            # Check for path traversal
                            if ".." in name or name.startswith("/"):
                                threats.append({
                                    "type": "path_traversal",
                                    "description": f"Suspicious path in archive: {name}",
                                    "severity": "high"
                                })
                                risk_score += 0.4

                            # Check for executable
                            if any(name.endswith(ext) for ext in [".exe", ".bat", ".sh", ".ps1"]):
                                threats.append({
                                    "type": "executable",
                                    "description": f"Archive contains executable: {name}",
                                    "severity": "high"
                                })
                                risk_score += 0.3

                        # Check for suspicious compression ratios
                        total_compressed = sum(info.compress_size for info in zf.infolist())
                        total_uncompressed = sum(info.file_size for info in zf.infolist())

                        if total_compressed > 0:
                            ratio = total_uncompressed / total_compressed
                            if ratio > 100:  # Zip bomb indicator
                                threats.append({
                                    "type": "zip_bomb",
                                    "description": f"Suspicious compression ratio: {ratio:.1f}x",
                                    "severity": "high"
                                })
                                risk_score += 0.5

                except zipfile.BadZipFile:
                    threats.append({
                        "type": "corrupted_archive",
                        "description": "Archive appears corrupted or invalid",
                        "severity": "high"
                    })
                    risk_score += 0.6

            else:
                # For non-ZIP archives, just check basic properties
                file_size = path.stat().st_size
                if file_size > 100 * 1024 * 1024:  # > 100MB
                    risk_score += 0.2

            risk_score = min(1.0, risk_score)
            risk_level = self._score_to_level(risk_score)

            result = {
                "risk_level": risk_level,
                "risk_score": round(risk_score, 3),
                "input_type": "archive",
                "file_name": path.name,
                "file_size": path.stat().st_size,
                "threats": threats,
            }

            logger.info(f"✅ Archive analysis complete - Risk: {risk_level}")
            return result

        except Exception as e:
            logger.error(f"❌ Archive analysis failed: {str(e)}")
            return {
                "risk_level": "high",
                "risk_score": 0.8,
                "error": str(e),
                "input_type": "archive"
            }

    async def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze document files (DOCX, XLSX, etc.)

        Args:
            file_path: Path to document file

        Returns:
            Analysis results
        """
        logger.info(f"📃 Analyzing document: {file_path}")

        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "risk_level": "high",
                    "risk_score": 0.9,
                    "error": "Document not found",
                    "input_type": "document"
                }

            with open(file_path, "rb") as f:
                data = f.read()

            threats = []
            risk_score = 0.0

            # Check for OLE2 signature (Office documents)
            if data.startswith(b"\xd0\xcf\x11\xe0"):
                # Check for suspicious embedded objects
                if b"PowerShell" in data or b"cmd.exe" in data:
                    threats.append({
                        "type": "embedded_script",
                        "description": "Document contains suspicious script",
                        "severity": "high"
                    })
                    risk_score += 0.5

                if b"ActiveXObject" in data:
                    threats.append({
                        "type": "activex",
                        "description": "Document uses ActiveX",
                        "severity": "high"
                    })
                    risk_score += 0.4

            # Check for OOXML format
            elif data.startswith(b"PK\x03\x04"):
                # It's likely DOCX/XLSX/PPTX (ZIP-based)
                try:
                    with zipfile.ZipFile(file_path, "r") as zf:
                        # Check for macros
                        macro_files = [f for f in zf.namelist() if "macro" in f.lower()]
                        if macro_files:
                            threats.append({
                                "type": "macros",
                                "description": f"Document contains macros: {len(macro_files)} file(s)",
                                "severity": "high"
                            })
                            risk_score += 0.4

                        # Check for external connections
                        for name in zf.namelist():
                            if "customXml" in name or "externalData" in name:
                                threats.append({
                                    "type": "external_connection",
                                    "description": "Document may load external content",
                                    "severity": "medium"
                                })
                                risk_score += 0.3
                                break
                except Exception:
                    risk_score += 0.1

            risk_score = min(1.0, risk_score)
            risk_level = self._score_to_level(risk_score)

            result = {
                "risk_level": risk_level,
                "risk_score": round(risk_score, 3),
                "input_type": "document",
                "file_name": path.name,
                "file_size": path.stat().st_size,
                "threats": threats,
            }

            logger.info(f"✅ Document analysis complete - Risk: {risk_level}")
            return result

        except Exception as e:
            logger.error(f"❌ Document analysis failed: {str(e)}")
            return {
                "risk_level": "high",
                "risk_score": 0.8,
                "error": str(e),
                "input_type": "document"
            }

    def _check_hardcoded_secrets(self, content: str) -> float:
        """Check for hardcoded secrets"""
        import re
        patterns = [
            r"api[_-]?key\s*=",
            r"password\s*=",
            r"secret[_-]?key\s*=",
            r"auth[_-]?token\s*=",
            r"access[_-]?token\s*=",
        ]

        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return 0.4
        return 0.0

    def _check_sql_injection(self, content: str) -> bool:
        """Check for SQL injection vulnerabilities"""
        import re
        patterns = [
            r"query.*\+.*input",
            r"format\(.*query",
            r"sql.*\+.*user",
        ]
        return any(re.search(p, content, re.IGNORECASE) for p in patterns)

    def _check_insecure_random(self, content: str) -> bool:
        """Check for insecure random"""
        import re
        patterns = [
            r"Math\.random",
            r"random\.randint",
            r"rand\(",
        ]
        return any(re.search(p, content, re.IGNORECASE) for p in patterns)

    def _is_code(self, file_path: str) -> bool:
        """Check if file looks like code"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(500)
            code_indicators = ["def ", "function ", "class ", "import ", "const ", "var "]
            return any(indicator in content for indicator in code_indicators)
        except:
            return False

    def _is_dangerous_extension(self, ext: str) -> bool:
        """Check if extension is dangerous"""
        dangerous = ["exe", "bat", "ps1", "cmd", "com", "sh", "bash", "py"]
        return ext.lower() in dangerous

    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 0.7:
            return "critical" if score >= 0.85 else "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
