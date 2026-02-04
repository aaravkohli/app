#!/usr/bin/env python3
"""
API Server for PromptGuard - Secure AI Gateway
Exposes safe_llm backend as REST API for frontend consumption
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from safe_llm import safe_generate, final_risk, call_llm, output_risk
import time
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for production
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

# Get environment configuration
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("FLASK_ENV") == "development"

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
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        
        if not prompt:
            return jsonify({"error": "Prompt cannot be empty"}), 400
        
        if len(prompt) > 2000:
            return jsonify({"error": "Prompt exceeds 2000 character limit"}), 400
        
        # Start timer
        start_time = time.time()
        
        # Analyze prompt
        logger.info(f"Analyzing prompt: {prompt[:50]}...")
        analysis = final_risk(prompt)
        
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
        
        if is_dangerous:
            # Blocked prompt
            response_data["blockReason"] = (
                "Our security analysis detected patterns commonly associated with prompt injection attacks. "
                "The request appears to attempt to override system instructions or manipulate the AI's behavior."
            )
            response_data["suggestedRewrite"] = (
                "Could you rephrase your question without asking the AI to ignore its guidelines?"
            )
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
    logger.info(f"Environment: {'development' if DEBUG else 'production'}")
    logger.info(f"Port: {PORT}")
    
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=DEBUG,
        threaded=True
    )
