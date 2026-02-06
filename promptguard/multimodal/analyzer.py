"""
Main Multimodal Analyzer - Orchestrates analysis of different input types
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum

from .text_analyzer import TextAnalyzer
from .image_analyzer import ImageAnalyzer
from .video_analyzer import VideoAnalyzer
from .file_analyzer import FileAnalyzer

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InputType(str, Enum):
    """Supported input types"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    PDF = "pdf"
    CODE = "code"
    DOCUMENT = "document"
    FOLDER = "folder"
    ARCHIVE = "archive"


class MultimodalAnalyzer:
    """
    Analyzes multiple input types for security threats
    """

    # File extensions mapping
    EXTENSION_MAPPING = {
        # Images
        "jpg": InputType.IMAGE, "jpeg": InputType.IMAGE, "png": InputType.IMAGE,
        "gif": InputType.IMAGE, "bmp": InputType.IMAGE, "webp": InputType.IMAGE,
        "svg": InputType.IMAGE, "ico": InputType.IMAGE,
        
        # Videos
        "mp4": InputType.VIDEO, "avi": InputType.VIDEO, "mov": InputType.VIDEO,
        "mkv": InputType.VIDEO, "flv": InputType.VIDEO, "wmv": InputType.VIDEO,
        "webm": InputType.VIDEO, "m4v": InputType.VIDEO,
        
        # PDFs
        "pdf": InputType.PDF,
        
        # Code files
        "py": InputType.CODE, "js": InputType.CODE, "ts": InputType.CODE,
        "java": InputType.CODE, "cpp": InputType.CODE, "c": InputType.CODE,
        "cs": InputType.CODE, "go": InputType.CODE, "rs": InputType.CODE,
        "php": InputType.CODE, "rb": InputType.CODE, "swift": InputType.CODE,
        "sh": InputType.CODE, "bash": InputType.CODE, "bat": InputType.CODE,
        "ps1": InputType.CODE, "gradle": InputType.CODE, "xml": InputType.CODE,
        "json": InputType.CODE, "yaml": InputType.CODE, "yml": InputType.CODE,
        
        # Documents
        "txt": InputType.DOCUMENT, "doc": InputType.DOCUMENT, "docx": InputType.DOCUMENT,
        "xls": InputType.DOCUMENT, "xlsx": InputType.DOCUMENT, "ppt": InputType.DOCUMENT,
        "pptx": InputType.DOCUMENT, "odt": InputType.DOCUMENT, "csv": InputType.DOCUMENT,
        
        # Archives
        "zip": InputType.ARCHIVE, "rar": InputType.ARCHIVE, "7z": InputType.ARCHIVE,
        "tar": InputType.ARCHIVE, "gz": InputType.ARCHIVE, "bz2": InputType.ARCHIVE,
    }

    def __init__(self):
        """Initialize all analyzers"""
        self.text_analyzer = TextAnalyzer()
        self.image_analyzer = ImageAnalyzer()
        self.video_analyzer = VideoAnalyzer()
        self.file_analyzer = FileAnalyzer()
        logger.info("✅ Multimodal Analyzer initialized")

    async def analyze(self, input_data: Any, input_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze input data and return security assessment

        Args:
            input_data: The input to analyze (text, file path, bytes, etc.)
            input_type: Optional explicit input type

        Returns:
            Dict with analysis results including risk level and details
        """
        logger.info(f"🔍 Starting multimodal analysis for input type: {input_type}")

        # Determine input type if not provided
        if not input_type:
            input_type = self._detect_input_type(input_data)

        try:
            if input_type == InputType.TEXT or input_type == "text":
                result = await self.text_analyzer.analyze(input_data)
            elif input_type == InputType.IMAGE or input_type == "image":
                result = await self.image_analyzer.analyze(input_data)
            elif input_type == InputType.VIDEO or input_type == "video":
                result = await self.video_analyzer.analyze(input_data)
            elif input_type == InputType.PDF or input_type == "pdf":
                result = await self.file_analyzer.analyze_pdf(input_data)
            elif input_type == InputType.CODE or input_type == "code":
                result = await self.file_analyzer.analyze_code(input_data)
            elif input_type == InputType.DOCUMENT or input_type == "document":
                result = await self.file_analyzer.analyze_document(input_data)
            elif input_type == InputType.FOLDER or input_type == "folder":
                result = await self.analyze_folder(input_data)
            elif input_type == InputType.ARCHIVE or input_type == "archive":
                result = await self.file_analyzer.analyze_archive(input_data)
            else:
                result = await self.file_analyzer.analyze(input_data)

            logger.info(f"✅ Analysis complete - Risk Level: {result.get('risk_level')}")
            return result

        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            return {
                "risk_level": "high",
                "risk_score": 0.9,
                "error": str(e),
                "input_type": input_type,
                "message": "Error during analysis - treating as high risk"
            }

    async def analyze_folder(self, folder_path: str) -> Dict[str, Any]:
        """
        Recursively analyze all files in a folder

        Args:
            folder_path: Path to the folder

        Returns:
            Combined analysis of all files
        """
        logger.info(f"📁 Analyzing folder: {folder_path}")

        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return {
                "risk_level": "high",
                "risk_score": 0.95,
                "error": "Folder not found or not a directory",
                "input_type": "folder"
            }

        results = {
            "risk_level": "low",
            "risk_score": 0.0,
            "input_type": "folder",
            "folder_path": str(folder),
            "files_analyzed": 0,
            "risks_found": [],
            "summary": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0
            }
        }

        # Analyze each file
        for file_path in folder.rglob("*"):
            if file_path.is_file():
                try:
                    ext = file_path.suffix.lower().lstrip(".")
                    input_type = self.EXTENSION_MAPPING.get(ext, InputType.DOCUMENT)

                    file_result = await self.analyze(str(file_path), input_type)
                    results["files_analyzed"] += 1

                    # Update summary
                    risk_level = file_result.get("risk_level", "low")
                    results["summary"][risk_level] = results["summary"].get(risk_level, 0) + 1

                    # If risk found, add to list
                    if risk_level in ["high", "critical"]:
                        results["risks_found"].append({
                            "file": str(file_path.relative_to(folder)),
                            "risk_level": risk_level,
                            "risk_score": file_result.get("risk_score", 0),
                            "details": file_result.get("threats", [])
                        })

                except Exception as e:
                    logger.warning(f"⚠️ Failed to analyze {file_path}: {str(e)}")
                    results["summary"]["high"] = results["summary"].get("high", 0) + 1

        # Calculate overall risk
        if results["risks_found"]:
            results["risk_level"] = "critical" if results["summary"]["critical"] > 0 else "high"
            results["risk_score"] = min(0.95, 0.5 + (len(results["risks_found"]) * 0.1))
        elif results["summary"]["high"] > 0:
            results["risk_level"] = "high"
            results["risk_score"] = 0.7
        elif results["summary"]["medium"] > 0:
            results["risk_level"] = "medium"
            results["risk_score"] = 0.5
        else:
            results["risk_level"] = "low"
            results["risk_score"] = 0.2

        logger.info(f"📁 Folder analysis complete - Overall Risk: {results['risk_level']}")
        return results

    def _detect_input_type(self, input_data: Any) -> InputType:
        """
        Auto-detect input type from input data

        Args:
            input_data: The input data to analyze

        Returns:
            Detected InputType
        """
        # If it's a string, check if it's a file path
        if isinstance(input_data, str):
            # If it's text content (not a file path)
            if not os.path.exists(input_data):
                return InputType.TEXT

            # It's a file path
            path = Path(input_data)
            ext = path.suffix.lower().lstrip(".")

            if path.is_dir():
                return InputType.FOLDER

            return self.EXTENSION_MAPPING.get(ext, InputType.DOCUMENT)

        # If it's bytes, assume it's a file
        if isinstance(input_data, bytes):
            return InputType.DOCUMENT

        # Default to text
        return InputType.TEXT

    def get_supported_types(self) -> List[str]:
        """Get list of supported file types"""
        return list(self.EXTENSION_MAPPING.keys())
