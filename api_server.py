#!/usr/bin/env python3
"""
API Server for PromptGuard - Secure AI Gateway
Exposes safe_llm backend as REST API for frontend consumption
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from safe_llm import safe_generate, final_risk, call_llm, output_risk, safe_generate_with_sanitization
import time
import logging
import os
from dotenv import load_dotenv
import asyncio
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import re
from PIL import Image
import pytesseract

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vigil-LLM integration (lazy loaded)
vigil_scanner = None

async def get_vigil_scanner():
    """Lazy load Vigil scanner"""
    global vigil_scanner
    if vigil_scanner is None:
        try:
            from promptguard.security_engine.vigil_scanner import AsyncVigilScanner
            from promptguard.config.settings import settings
            vigil_scanner = AsyncVigilScanner(settings)
            await vigil_scanner.initialize()
            logger.info("✅ Vigil-LLM scanner initialized")
        except Exception as e:
            logger.warning(f"⚠️ Vigil-LLM unavailable: {e}")
            vigil_scanner = False  # Mark as unavailable
    return vigil_scanner if vigil_scanner is not False else None

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for production
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

# Get environment configuration
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("FLASK_ENV") == "development"
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 25 * 1024 * 1024))

# ==========================================
# File Text Extraction Helpers
# ==========================================
def _clean_extracted_text(text: str) -> str:
    if not text:
        return ""
    # Fix hyphenated line breaks (e.g., "con-
    # tinue" -> "continue")
    text = re.sub(r"(\w)-\s*\n(\w)", r"\1\2", text)
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse excessive whitespace while preserving paragraphs
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim spaces on each line
    text = "\n".join(line.strip() for line in text.split("\n"))
    return text.strip()


def extract_text_from_pdf_bytes(data: bytes) -> str:
    text_parts = []
    reader = PdfReader(BytesIO(data))
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text.strip():
            text_parts.append(page_text)
    return _clean_extracted_text("\n\n".join(text_parts))


def extract_text_from_docx_bytes(data: bytes) -> str:
    doc = Document(BytesIO(data))
    text = "\n".join([para.text for para in doc.paragraphs if para.text])
    return _clean_extracted_text(text)


def extract_text_from_plaintext_bytes(data: bytes) -> str:
    return _clean_extracted_text(data.decode("utf-8", errors="ignore"))


def extract_text_from_image_bytes(data: bytes) -> str:
    """
    Extract text from image using OCR (Optical Character Recognition).
    Supports: PNG, JPG, JPEG, BMP, TIFF, WebP, GIF
    """
    try:
        image = Image.open(BytesIO(data))
        # Convert RGBA to RGB if necessary for pytesseract compatibility
        if image.mode in ("RGBA", "LA", "P"):
            rgb_image = Image.new("RGB", image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = rgb_image
        
        # Extract text using pytesseract
        extracted_text = pytesseract.image_to_string(image)
        logger.info(f"✅ OCR extraction successful: {len(extracted_text)} chars")
        return _clean_extracted_text(extracted_text)
    except Exception as e:
        logger.error(f"❌ OCR extraction failed: {e}")
        raise ValueError(f"Failed to extract text from image: {str(e)}")


def score_to_level(score: float) -> str:
    if score >= 0.7:
        return "critical" if score >= 0.85 else "high"
    if score >= 0.4:
        return "medium"
    return "low"

# ==========================================
# Health Check Endpoint
# ==========================================
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "operational",
        "version": "1.0.0",
        "gateway": "PromptGuard - Secure AI Gateway"
    }), 200

# ==========================================
# Main Analysis Endpoint
# ==========================================
@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Analyze a prompt for security threats and generate AI response
    
    Request JSON:
    {
        "prompt": "User's prompt text"
    }
    
    Response JSON:
    {
        "status": "approved" | "blocked",
        "prompt": "Echo of user prompt",
        "analysis": {
            "risk": 0.0-1.0,
            "ml_score": 0.0-1.0,
            "lexical_risk": 0.0-1.0,
            "benign_offset": 0.0-1.0,
            "adaptive_phrases": int
        },
        "response": "AI generated response (if approved)",
        "blockReason": "Explanation if blocked",
        "analysisTime": milliseconds
    }
    """
    try:
        # Validate request
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        
        logger.info(f"📬 Received request with prompt: {prompt[:60]}...")
        
        if not prompt:
            logger.warning("Empty prompt received")
            return jsonify({"error": "Prompt cannot be empty"}), 400
        
        if len(prompt) > 2000:
            logger.warning(f"Prompt exceeds limit: {len(prompt)} chars")
            return jsonify({"error": "Prompt exceeds 2000 character limit"}), 400
        
        # Start timer
        start_time = time.time()
        
        # Analyze prompt
        logger.info(f"🔍 Starting analysis...")
        analysis = final_risk(prompt)
        logger.info(f"✅ Analysis complete - Risk: {analysis['risk']}, ML Score: {analysis['ml_score']}, Lexical: {analysis['lexical_risk']}")
        
        # Run Vigil-LLM scanner in parallel
        vigil_result = None
        try:
            scanner = asyncio.run(get_vigil_scanner())
            if scanner:
                vigil_result = asyncio.run(scanner.scan_prompt(prompt))
                logger.info(f"Vigil scan complete: {vigil_result.get('aggregated_risk', 0)}")
            else:
                # Vigil unavailable - create placeholder response
                vigil_result = {
                    "unavailable": True,
                    "message": "Vigil-LLM scanner not available (vigil-llm package not installed)"
                }
        except Exception as e:
            logger.warning(f"Vigil scan failed: {e}")
            vigil_result = {
                "unavailable": True,
                "error": str(e)
            }
        
        # Determine status based on risk score
        risk_score = analysis["risk"]
        is_dangerous = (
            (analysis["ml_score"] > 0.98 and analysis["risk"] > 0.45) 
            or analysis["risk"] > 0.55
        )
        
        # Build response
        response_data = {
            "status": "blocked" if is_dangerous else "approved",
            "prompt": prompt,
            "analysis": {
                "risk": analysis["risk"],
                "ml_score": analysis["ml_score"],
                "lexical_risk": analysis["lexical_risk"],
                "benign_offset": analysis["benign_offset"],
                "adaptive_phrases": analysis["adaptive_phrases"]
            },
            "analysisTime": round((time.time() - start_time) * 1000, 2)
        }
        
        # Add Vigil analysis if available
        if vigil_result:
            if vigil_result.get('unavailable'):
                # Add mock/demo Vigil data for demonstration purposes
                response_data["vigil_analysis"] = {
                    "scanners": {
                        "similarity": {
                            "scanner": "similarity",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "transformer": {
                            "scanner": "transformer",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "yara": {
                            "scanner": "yara",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "sentiment": {
                            "scanner": "sentiment",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "relevance": {
                            "scanner": "relevance",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "canary": {
                            "scanner": "canary",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        }
                    },
                    "detections": [],
                    "aggregated_risk": round(risk_score * 0.3, 3),  # Scale down main risk for demo
                    "risk_indicators": [],
                    "demo_mode": True,
                    "message": vigil_result.get("message", "Vigil-LLM demo mode")
                }
            else:
                response_data["vigil_analysis"] = {
                    "scanners": vigil_result.get("scanners", {}),
                    "detections": vigil_result.get("detections", []),
                    "aggregated_risk": vigil_result.get("aggregated_risk", 0.0),
                    "risk_indicators": vigil_result.get("risk_indicators", [])
                }
        
        if is_dangerous:
            # Blocked prompt - include sanitized alternative
            response_data["blockReason"] = (
                "Our security analysis detected patterns commonly associated with prompt injection attacks. "
                "The request appears to attempt to override system instructions or manipulate the AI's behavior."
            )
            
            # Use safe_generate_with_sanitization to get automatic sanitization
            logger.info("🔄 Generating sanitized alternative for blocked prompt...")
            enhanced_result = safe_generate_with_sanitization(prompt)
            
            if enhanced_result.get("sanitization"):
                sanitization = enhanced_result["sanitization"]
                response_data["sanitizedPrompt"] = {
                    "text": sanitization["sanitized_prompt"],
                    "notes": sanitization["sanitization_notes"],
                    "timeMs": sanitization["sanitization_time_ms"],
                    "issuesAddressed": sanitization.get("issues_addressed", [])
                }
                logger.info(f"✅ Sanitized alternative generated: {sanitization['sanitized_prompt'][:60]}...")
            else:
                # Fallback if sanitization fails
                response_data["sanitizedPrompt"] = {
                    "text": "Can you help me understand how to ask questions safely and effectively?",
                    "notes": "Automatic sanitization unavailable. This is a safe general question.",
                    "fallback": True
                }
                logger.warning("⚠️ Sanitization failed, using fallback")
            
            logger.warning(f"Prompt blocked: risk={risk_score}")
        else:
            # Approved - generate response
            logger.info(f"Prompt approved: risk={risk_score}")
            try:
                llm_response = call_llm(prompt)
                
                # Check output for leaks
                output_leak = output_risk(llm_response)
                if output_leak > 0.4:
                    response_data["response"] = (
                        "⚠️ Response withheld due to potential policy or system information leakage."
                    )
                else:
                    response_data["response"] = llm_response
            except Exception as e:
                logger.error(f"LLM call failed: {str(e)}")
                response_data["response"] = (
                    "I encountered an issue while processing your request. "
                    "Please try again or rephrase your question."
                )
        
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# File Analysis Endpoint (PDF/DOCX to Text)
# ==========================================
@app.route("/api/analyze/file", methods=["POST"])
def analyze_file():
    """
    Analyze an uploaded PDF/DOCX/TXT file by extracting text and
    running the standard risk assessment.

    Request: multipart/form-data with "file"
    Response: risk assessment and file metadata
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        uploads = request.files.getlist("file")
        uploads = [u for u in uploads if u and u.filename]
        if not uploads:
            return jsonify({"error": "No file selected"}), 400

        user_text = (request.form.get("text") or "").strip()

        extracted_texts = []
        file_names = []
        input_types = set()

        for upload in uploads:
            file_bytes = upload.read()
            if not file_bytes:
                continue

            if len(file_bytes) > MAX_UPLOAD_SIZE:
                return jsonify({"error": f"File too large (max {MAX_UPLOAD_SIZE // (1024 * 1024)}MB)"}), 400

            file_ext = os.path.splitext(upload.filename)[1].lower()
            if file_ext == ".pdf":
                extracted_text = extract_text_from_pdf_bytes(file_bytes)
                input_type = "pdf"
            elif file_ext == ".docx":
                extracted_text = extract_text_from_docx_bytes(file_bytes)
                input_type = "document"
            elif file_ext in [".txt", ".md", ".csv"]:
                extracted_text = extract_text_from_plaintext_bytes(file_bytes)
                input_type = "document"
            elif file_ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp", ".gif"]:
                try:
                    extracted_text = extract_text_from_image_bytes(file_bytes)
                    input_type = "image"
                except ValueError as e:
                    logger.warning(f"Image OCR failed for {upload.filename}: {e}")
                    return jsonify({"error": f"Could not extract text from image: {str(e)}"}), 400
            else:
                return jsonify({"error": "Unsupported file type. Upload PDF, DOCX, TXT, or Image (PNG, JPG, JPEG, BMP, TIFF, WebP, GIF)."}), 400

            if extracted_text:
                extracted_texts.append(extracted_text)
                file_names.append(upload.filename)
                input_types.add(input_type)

        if not extracted_texts and not user_text:
            return jsonify({"error": "No readable text found in the uploaded files"}), 400

        combined_text_parts = []
        if user_text:
            combined_text_parts.append(user_text)
        if extracted_texts:
            combined_text_parts.append("\n\n".join(extracted_texts))
        combined_text = _clean_extracted_text("\n\n".join(combined_text_parts))

        if not combined_text:
            return jsonify({"error": "No readable text found in input"}), 400

        start_time = time.time()
        analysis = final_risk(combined_text)

        # Run Vigil-LLM scanner on extracted/combined text
        vigil_result = None
        try:
            scanner = asyncio.run(get_vigil_scanner())
            if scanner:
                vigil_result = asyncio.run(scanner.scan_prompt(combined_text))
                logger.info(f"Vigil scan complete (file): {vigil_result.get('aggregated_risk', 0)}")
            else:
                vigil_result = {
                    "unavailable": True,
                    "message": "Vigil-LLM scanner not available (vigil-llm package not installed)"
                }
        except Exception as e:
            logger.warning(f"Vigil scan failed (file): {e}")
            vigil_result = {
                "unavailable": True,
                "error": str(e)
            }

        is_dangerous = (
            (analysis["ml_score"] > 0.98 and analysis["risk"] > 0.45)
            or analysis["risk"] > 0.55
        )

        risk_score = analysis["risk"]
        response_data = {
            "status": "blocked" if is_dangerous else "approved",
            "file_names": file_names,
            "input_type": "+".join(sorted(input_types)) if input_types else "document",
            "extracted_chars": sum(len(t) for t in extracted_texts),
            "combined_text_chars": len(combined_text),
            "risk_level": score_to_level(risk_score),
            "risk_score": round(risk_score, 3),
            "analysis": {
                "risk": analysis["risk"],
                "ml_score": analysis["ml_score"],
                "lexical_risk": analysis["lexical_risk"],
                "benign_offset": analysis["benign_offset"],
                "adaptive_phrases": analysis["adaptive_phrases"],
            },
            "analysisTime": round((time.time() - start_time) * 1000, 2),
            "threats": [],
        }
        
        # Add sanitization for blocked file content
        if is_dangerous:
            logger.info("🔄 Generating sanitized alternative for blocked file content...")
            enhanced_result = safe_generate_with_sanitization(combined_text)
            
            if enhanced_result.get("sanitization"):
                sanitization = enhanced_result["sanitization"]
                response_data["sanitizedPrompt"] = {
                    "text": sanitization["sanitized_prompt"],
                    "notes": sanitization["sanitization_notes"],
                    "timeMs": sanitization["sanitization_time_ms"],
                    "issuesAddressed": sanitization.get("issues_addressed", [])
                }
                logger.info(f"✅ Sanitized alternative for file content generated")
            else:
                response_data["sanitizedPrompt"] = {
                    "text": "Can you help me understand the content in a safe and appropriate way?",
                    "notes": "Automatic sanitization unavailable. This is a safe general question.",
                    "fallback": True
                }

        if vigil_result:
            if vigil_result.get("unavailable"):
                response_data["vigil_analysis"] = {
                    "scanners": {
                        "similarity": {
                            "scanner": "similarity",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "transformer": {
                            "scanner": "transformer",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "yara": {
                            "scanner": "yara",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "sentiment": {
                            "scanner": "sentiment",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "relevance": {
                            "scanner": "relevance",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        },
                        "canary": {
                            "scanner": "canary",
                            "detected": False,
                            "confidence": 0.0,
                            "details": {"status": "demo_mode"}
                        }
                    },
                    "detections": [],
                    "aggregated_risk": round(risk_score * 0.3, 3),
                    "risk_indicators": [],
                    "demo_mode": True,
                    "message": vigil_result.get("message", "Vigil-LLM demo mode")
                }
            else:
                response_data["vigil_analysis"] = {
                    "scanners": vigil_result.get("scanners", {}),
                    "detections": vigil_result.get("detections", []),
                    "aggregated_risk": vigil_result.get("aggregated_risk", 0.0),
                    "risk_indicators": vigil_result.get("risk_indicators", [])
                }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"File analysis failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# Risk Analysis Only (Lightweight)
# ==========================================
@app.route("/api/analyze/risk", methods=["POST"])
def analyze_risk_only():
    """
    Lightweight endpoint for risk analysis without LLM response
    Useful for quick threat detection without generating content
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        
        if not prompt:
            return jsonify({"error": "Prompt cannot be empty"}), 400
        
        start_time = time.time()
        analysis = final_risk(prompt)
        
        is_dangerous = (
            (analysis["ml_score"] > 0.98 and analysis["risk"] > 0.45) 
            or analysis["risk"] > 0.55
        )
        
        return jsonify({
            "status": "blocked" if is_dangerous else "safe",
            "analysis": {
                "risk": analysis["risk"],
                "ml_score": analysis["ml_score"],
                "lexical_risk": analysis["lexical_risk"],
                "benign_offset": analysis["benign_offset"],
                "adaptive_phrases": analysis["adaptive_phrases"]
            },
            "analysisTime": round((time.time() - start_time) * 1000, 2)
        }), 200
    
    except Exception as e:
        logger.error(f"Risk analysis failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# Batch Analysis Endpoint
# ==========================================
@app.route("/api/analyze/batch", methods=["POST"])
def analyze_batch():
    """
    Analyze multiple prompts in one request
    
    Request JSON:
    {
        "prompts": ["prompt1", "prompt2", ...]
    }
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        prompts = data.get("prompts", [])
        
        if not prompts or not isinstance(prompts, list):
            return jsonify({"error": "Prompts must be a non-empty list"}), 400
        
        if len(prompts) > 10:
            return jsonify({"error": "Maximum 10 prompts per batch"}), 400
        
        results = []
        for prompt in prompts:
            if not isinstance(prompt, str) or not prompt.strip():
                results.append({"error": "Invalid prompt"})
                continue
            
            analysis = final_risk(prompt)
            is_dangerous = (
                (analysis["ml_score"] > 0.98 and analysis["risk"] > 0.45) 
                or analysis["risk"] > 0.55
            )
            
            results.append({
                "prompt": prompt,
                "status": "blocked" if is_dangerous else "safe",
                "risk": analysis["risk"]
            })
        
        return jsonify({"results": results}), 200
    
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# Error Handlers
# ==========================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ==========================================
# Main Entry Point
# ==========================================
if __name__ == "__main__":
    logger.info("Starting PromptGuard API Server...")
    logger.info("Available endpoints:")
    logger.info("  GET  /api/health")
    logger.info("  POST /api/analyze")
    logger.info("  POST /api/analyze/risk")
    logger.info("  POST /api/analyze/batch")
    logger.info("  POST /api/analyze/file")
    logger.info(f"Environment: {'development' if DEBUG else 'production'}")
    logger.info(f"Port: {PORT}")
    
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=DEBUG,
        threaded=True
    )
