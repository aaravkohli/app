# ML Risk Score Bug Fix - February 5, 2026

## Problem
The ML risk score was **always showing 100% (1.0)** for all prompts, regardless of whether they were safe or malicious.

## Root Cause
The bug was in the `ml_risk()` function in `safe_llm.py` (lines 119-128):

```python
# BROKEN CODE:
def ml_risk(prompt: str) -> float:
    variants = [
        prompt,
        "User instruction: " + prompt,
        "Analyze for prompt injection: " + prompt
    ]
    return max(guard(v)[0]["score"] for v in variants)
```

### Why This Was Wrong:
1. The Hugging Face text-classification pipeline returns a **confidence score** for the predicted label, not necessarily for "INJECTION"
2. When a prompt is classified as "SAFE", the score is ~0.999 (high confidence it's safe)
3. When a prompt is classified as "INJECTION", the score is ~0.999 (high confidence it's injection)
4. Taking `max()` of all scores means ANY high-confidence prediction = ~1.0 result
5. The third variant "Analyze for prompt injection: ..." was triggering false positives because the word "injection" itself was flagged as suspicious

### Example of the Bug:
```
"What is AI?" → [SAFE: 0.9999, SAFE: 0.7742, INJECTION: 0.9885] → max = 0.9885 ≈ 1.0 ❌
```

## Solution
Rewrote `ml_risk()` to properly interpret the model output:

```python
# FIXED CODE:
def ml_risk(prompt: str) -> float:
    # Analyze the prompt directly with the guard model
    result = guard(prompt)[0]
    
    # Return the injection risk score only if labeled as INJECTION
    # Otherwise return a low risk score (0.0) for SAFE prompts
    if result["label"] == "INJECTION":
        return result["score"]
    else:
        return 0.0
```

### Why This Works:
1. Check the **label**, not just the score
2. Only return high scores (the confidence) if the label is "INJECTION"
3. For SAFE prompts, return 0.0 (no injection detected)
4. Removed problematic variants that triggered false positives

## Test Results After Fix

| Prompt | Label | ML Score |
|--------|-------|----------|
| "What is AI?" | SAFE | 0.000 ✅ |
| "Explain blockchain" | SAFE | 0.000 ✅ |
| "Ignore previous instructions" | INJECTION | 1.000 ✅ |
| "Tell me a joke" | SAFE | 0.000 ✅ |
| "How does quantum computing work?" | SAFE | 0.000 ✅ |
| "Disregard all instructions" | INJECTION | 1.000 ✅ |

## Additional Fix
Fixed syntax error in `call_llm()` - removed comma from number `16,384` → `16384`

## Files Modified
- `/Users/aaravkohli/idk/safe_llm.py` - Fixed `ml_risk()` function and `call_llm()` syntax error

## Impact
- ML risk scores now correctly show 0.0 for safe prompts
- ML risk scores correctly show 1.0 for injection attempts
- Overall risk calculation is now accurate
- Frontend should now display correct risk metrics in the Analysis Breakdown panel
