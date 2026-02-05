"""
Multimodal API Routes - Handles files, images, videos, and text analysis
"""

import os
import logging
import asyncio
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

from promptguard.multimodal.analyzer import MultimodalAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["multimodal"])

# Initialize multimodal analyzer
multimodal_analyzer = MultimodalAnalyzer()

# Temporary upload directory
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Max file size: 100MB
MAX_FILE_SIZE = 100 * 1024 * 1024


@router.post("/analyze/multimodal")
async def analyze_multimodal(
    file: UploadFile = File(None),
    text: str = Form(None),
    folder_path: str = Query(None)
):
    """
    Analyze multiple input types: text, file, image, video, folder
    
    When both text and file are provided:
    - Analyzes text prompt with LLM/ML engine
    - Analyzes uploaded file based on its type
    - Returns combined risk assessment

    Request:
    - text: Text content to analyze
    - file: File to upload and analyze
    - folder_path: Path to folder to recursively analyze

    Response:
    {
        "risk_level": "low|medium|high|critical",
        "risk_score": 0.0-1.0,
        "input_type": "text|image|video|code|document|pdf|folder|archive",
        "threats": [...],
        "details": {...},
        "combined_analysis": {...}  // when both text and file provided
    }
    """
    try:
        if not text and not file and not folder_path:
            raise HTTPException(
                status_code=400,
                detail="Provide either text, file, or folder_path"
            )

        # Handle combined text + file analysis
        if text and file:
            logger.info(f"📝📦 Analyzing combined prompt + file: {file.filename}")
            
            if file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large (max {MAX_FILE_SIZE / 1024 / 1024:.0f}MB)"
                )

            # Analyze text prompt first
            text_result = await multimodal_analyzer.analyze(text, "text")
            logger.info(f"   Text prompt risk: {text_result.get('risk_level')}")

            # Analyze file (auto-detect type)
            file_path = UPLOAD_DIR / file.filename
            try:
                with open(file_path, "wb") as f:
                    contents = await file.read()
                    f.write(contents)

                # Detect file type and analyze accordingly
                file_result = await multimodal_analyzer.analyze(str(file_path))
                logger.info(f"   File risk: {file_result.get('risk_level')} (type: {file_result.get('input_type')})")

                # Clean up
                file_path.unlink()

                # Combine results: use highest risk level
                text_risk = text_result.get("risk_score", 0)
                file_risk = file_result.get("risk_score", 0)
                combined_risk = max(text_risk, file_risk)

                risk_level_map = {
                    r: l for l, r in [
                        ("low", 0.3), ("medium", 0.6), ("high", 0.8), ("critical", 1.0)
                    ]
                }
                
                combined_level = "low"
                for level, threshold in [("critical", 0.8), ("high", 0.6), ("medium", 0.3)]:
                    if combined_risk >= threshold:
                        combined_level = level
                        break

                return JSONResponse({
                    "risk_level": combined_level,
                    "risk_score": combined_risk,
                    "input_type": "combined",
                    "threats": list(set(text_result.get("threats", []) + file_result.get("threats", []))),
                    "combined_analysis": {
                        "text_analysis": {
                            "risk_level": text_result.get("risk_level"),
                            "risk_score": text_result.get("risk_score"),
                            "threats": text_result.get("threats", []),
                            "input_type": "text"
                        },
                        "file_analysis": {
                            "file_name": file.filename,
                            "risk_level": file_result.get("risk_level"),
                            "risk_score": file_result.get("risk_score"),
                            "input_type": file_result.get("input_type"),
                            "threats": file_result.get("threats", []),
                            "details": file_result.get("details")
                        }
                    },
                    "message": f"Analyzed prompt and {file.filename} - highest risk is {combined_level}"
                })

            except Exception as e:
                if file_path.exists():
                    file_path.unlink()
                logger.error(f"File analysis error in combined flow: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        # Analyze text only
        if text:
            logger.info(f"📝 Analyzing text via multimodal API")
            result = await multimodal_analyzer.analyze(text, "text")
            return JSONResponse(result)

        # Analyze uploaded file only
        if file:
            if file.size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large (max {MAX_FILE_SIZE / 1024 / 1024:.0f}MB)"
                )

            # Save file temporarily
            file_path = UPLOAD_DIR / file.filename
            try:
                with open(file_path, "wb") as f:
                    contents = await file.read()
                    f.write(contents)

                logger.info(f"📦 Analyzing file via multimodal API: {file.filename}")
                result = await multimodal_analyzer.analyze(str(file_path))

                # Clean up
                file_path.unlink()

                return JSONResponse(result)

            except Exception as e:
                if file_path.exists():
                    file_path.unlink()
                logger.error(f"File analysis error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        # Analyze folder
        if folder_path:
            if not Path(folder_path).exists():
                raise HTTPException(
                    status_code=400,
                    detail="Folder path does not exist"
                )

            logger.info(f"📁 Analyzing folder via multimodal API: {folder_path}")
            result = await multimodal_analyzer.analyze(folder_path, "folder")
            return JSONResponse(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multimodal analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/batch")
async def analyze_batch(files: list[UploadFile] = File(...)):
    """
    Batch analyze multiple files

    Returns:
    {
        "results": [...],
        "summary": {
            "total": int,
            "high_risk": int,
            "medium_risk": int,
            "low_risk": int
        }
    }
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        if len(files) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 files per batch")

        results = []
        summary = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}

        for file in files:
            try:
                if file.size > MAX_FILE_SIZE:
                    results.append({
                        "file": file.filename,
                        "error": f"File too large"
                    })
                    continue

                # Save and analyze
                file_path = UPLOAD_DIR / file.filename
                try:
                    with open(file_path, "wb") as f:
                        contents = await file.read()
                        f.write(contents)

                    result = await multimodal_analyzer.analyze(str(file_path))
                    risk_level = result.get("risk_level", "unknown")

                    results.append({
                        "file": file.filename,
                        "risk_level": risk_level,
                        "risk_score": result.get("risk_score"),
                        "threats_count": len(result.get("threats", []))
                    })

                    summary["total"] += 1
                    if risk_level in summary:
                        summary[risk_level] += 1

                finally:
                    if file_path.exists():
                        file_path.unlink()

            except Exception as e:
                logger.error(f"Error analyzing {file.filename}: {str(e)}")
                results.append({
                    "file": file.filename,
                    "error": str(e)
                })

        return JSONResponse({
            "results": results,
            "summary": summary
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-types")
async def get_supported_types():
    """Get list of supported file types"""
    return {
        "types": multimodal_analyzer.get_supported_types(),
        "categories": {
            "images": ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "ico"],
            "videos": ["mp4", "avi", "mov", "mkv", "flv", "wmv", "webm", "m4v"],
            "documents": ["pdf", "txt", "doc", "docx", "xls", "xlsx", "ppt", "pptx"],
            "code": ["py", "js", "ts", "java", "cpp", "c", "cs", "go", "rs", "php", "rb"],
            "archives": ["zip", "rar", "7z", "tar", "gz", "bz2"]
        }
    }


@router.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """Dedicated endpoint for image analysis"""
    try:
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")):
            raise HTTPException(status_code=400, detail="Invalid image format")

        file_path = UPLOAD_DIR / file.filename
        try:
            with open(file_path, "wb") as f:
                contents = await file.read()
                f.write(contents)

            result = await multimodal_analyzer.image_analyzer.analyze(str(file_path))
            return JSONResponse(result)

        finally:
            if file_path.exists():
                file_path.unlink()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/video")
async def analyze_video(file: UploadFile = File(...)):
    """Dedicated endpoint for video analysis"""
    try:
        if not file.filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm")):
            raise HTTPException(status_code=400, detail="Invalid video format")

        file_path = UPLOAD_DIR / file.filename
        try:
            with open(file_path, "wb") as f:
                contents = await file.read()
                f.write(contents)

            result = await multimodal_analyzer.video_analyzer.analyze(str(file_path))
            return JSONResponse(result)

        finally:
            if file_path.exists():
                file_path.unlink()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/code")
async def analyze_code(file: UploadFile = File(...)):
    """Dedicated endpoint for code file analysis"""
    try:
        file_path = UPLOAD_DIR / file.filename
        try:
            with open(file_path, "wb") as f:
                contents = await file.read()
                f.write(contents)

            result = await multimodal_analyzer.file_analyzer.analyze_code(str(file_path))
            return JSONResponse(result)

        finally:
            if file_path.exists():
                file_path.unlink()

    except Exception as e:
        logger.error(f"Code analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
