# safe_llm.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")
genai.configure(api_key=api_key)

# Use available Gemini model
try:
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(f"Model initialization error: {e}")
    raise
from transformers import pipeline
import re
from collections import Counter


def call_llm(prompt: str) -> str:
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 16384
            }
        )
        if response and response.text:
            return response.text
        else:
            return "I couldn't generate a response. Please try again."
    except Exception as e:
        error_msg = str(e)
        print(f"LLM Error Details: {error_msg}")
        
        # Fallback response
        if "429" in error_msg or "quota" in error_msg.lower():
            raise Exception("API rate limit exceeded. Please try again in a moment.")
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            raise Exception("API authentication failed. Check your GOOGLE_API_KEY.")
        elif "404" in error_msg:
            raise Exception("Model not found. Try with a different model.")
        else:
            raise Exception(f"LLM processing failed: {error_msg}")

# =========================
# Load model (lazy loading)
# =========================
guard = None

def get_guard():
    global guard
    if guard is None:
        from transformers import pipeline
        guard = pipeline(
            "text-classification",
            model="ProtectAI/deberta-v3-base-prompt-injection-v2",
            truncation=True,
            max_length=512,
            device=-1  # CPU-safe
        )
    return guard

# =========================
# Static lexical signals
# =========================
ATTACK_PATTERNS = [
    r"ignore (all|previous|earlier) instructions",
    r"disregard .* instructions",
    r"you are now .* system",
    r"act as .* system",
    r"reveal .* system prompt",
    r"developer mode",
    r"bypass .* safety",
    r"override .* policy"
]

BENIGN_PATTERNS = [
    r"explain",
    r"summarize",
    r"translate",
    r"write a story",
    r"help me understand",
    r"what is",
    r"how does"
]

# =========================
# Adaptive memory (NO retraining)
# =========================
ADAPTIVE_ATTACK_PHRASES = Counter()
ADAPTIVE_PROMOTION_THRESHOLD = 3  # promote phrase after N hits

# =========================
# Output-side protection
# =========================
OUTPUT_LEAK_PATTERNS = [
    r"system prompt",
    r"internal policy",
    r"developer message",
    r"my instructions are",
    r"i was instructed to",
    r"openai policy",
    r"as an ai language model"
]

# =========================
# Normalization
# =========================
def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

# =========================
# Adaptive phrase extraction
# =========================
def extract_phrases(prompt: str, n=4):
    words = prompt.split()
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]

# =========================
# Intent analysis
# =========================
def lexical_attack_score(prompt: str) -> float:
    score = 0.0

    # static patterns
    for pattern in ATTACK_PATTERNS:
        if re.search(pattern, prompt):
            score += 0.25

    # adaptive phrases
    for phrase, count in ADAPTIVE_ATTACK_PHRASES.items():
        if count >= ADAPTIVE_PROMOTION_THRESHOLD and phrase in prompt:
            score += 0.2

    return min(score, 1.0)

def lexical_benign_score(prompt: str) -> float:
    score = 0.0
    for pattern in BENIGN_PATTERNS:
        if re.search(pattern, prompt):
            score += 0.15
    return min(score, 0.5)

# =========================
# ML ensemble
# =========================
def ml_risk(prompt: str) -> float:
    # Lazy load the guard model
    guard_model = get_guard()
    
    # Analyze the prompt directly with the guard model
    # The original approach was broken - it would return near-1.0 for everything
    # because the model returns high confidence scores for both SAFE and INJECTION labels
    try:
        result = guard_model(prompt)[0]
        print(f"🤖 ML Model result: Label={result['label']}, Score={result['score']:.3f}")
        
        # Return the injection risk score only if labeled as INJECTION
        # Otherwise return a low risk score (0.0) for SAFE prompts
        if result["label"] == "INJECTION":
            print(f"⚠️ ML Risk Score: {result['score']:.3f} (INJECTION)")
            return result["score"]
        else:
            print(f"✅ ML Risk Score: 0.0 (SAFE)")
            return 0.0
    except Exception as e:
        print(f"❌ ML Risk check failed: {e}")
        return 0.1  # Default to low risk on error

# =========================
# Adaptive update (online learning)
# =========================
def adaptive_update(prompt: str, risk: float):
    if risk > 0.7:
        phrases = extract_phrases(prompt)
        for p in phrases:
            ADAPTIVE_ATTACK_PHRASES[p] += 1

# =========================
# Output-side protection
# =========================
def output_risk(response: str) -> float:
    r = response.lower()
    score = 0.0
    for pattern in OUTPUT_LEAK_PATTERNS:
        if re.search(pattern, r):
            score += 0.3
    return min(score, 1.0)

def sanitize_output():
    return (
        "⚠️ Response withheld due to potential policy or system information leakage."
    )

# =========================
# Final risk reasoning
# =========================
def final_risk(prompt: str) -> dict:
    p = normalize(prompt)
    print(f"\n📊 RISK ANALYSIS START")
    print(f"   Original: {prompt[:80]}")
    print(f"   Normalized: {p[:80]}")

    lexical_risk = lexical_attack_score(p)
    benign_offset = lexical_benign_score(p)
    ml_score = ml_risk(prompt)

    print(f"   Lexical Risk: {lexical_risk:.3f}")
    print(f"   Benign Offset: {benign_offset:.3f}")
    print(f"   ML Score: {ml_score:.3f}")

    # calibrated aggregation (balanced, not paranoid)
    risk = (0.5 * ml_score) + (0.5 * lexical_risk) - benign_offset
    risk = max(min(risk, 1.0), 0.0)
    
    print(f"   Final Risk: {risk:.3f}")
    print(f"📊 RISK ANALYSIS END\n")

    return {
        "risk": round(risk, 3),
        "ml_score": round(ml_score, 3),
        "lexical_risk": round(lexical_risk, 3),
        "benign_offset": round(benign_offset, 3),
        "adaptive_phrases": len(ADAPTIVE_ATTACK_PHRASES)
    }

# =========================
# Main API
# =========================
def safe_generate(user_prompt: str) -> str:
    analysis = final_risk(user_prompt)

    # adaptive learning
    adaptive_update(normalize(user_prompt), analysis["risk"])

    # 🔐 input-side protection
    if (
        analysis["ml_score"] > 0.98
        and analysis["risk"] > 0.45
    ) or analysis["risk"] > 0.55:
        return (
            "🚨 Prompt blocked: high-confidence prompt injection detected.\n"
            f"Details: {analysis}"
        )

    # 🤖 Gemini call
    llm_response = call_llm(user_prompt)

    # 🔐 output-side protection
    if output_risk(llm_response) > 0.4:
        return sanitize_output()

    return (
        "✅ Safe response generated.\n"
        f"Details: {analysis}\n\n"
        + llm_response
    )