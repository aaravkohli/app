#!/usr/bin/env python3
"""
Test script to verify that different prompts return different responses
"""
import requests
import json
import time

API_URL = "http://localhost:5000/api/analyze"

test_prompts = [
    "What is artificial intelligence?",
    "Explain blockchain technology",
    "How does photosynthesis work?",
    "Tell me about quantum computing",
    "What is machine learning?",
]

def test_api(prompt):
    """Test the API with a prompt"""
    data = {"prompt": prompt}
    try:
        response = requests.post(API_URL, json=data)
        if response.ok:
            result = response.json()
            return {
                "prompt": prompt,
                "status": result.get("status"),
                "risk": result.get("analysis", {}).get("risk"),
                "response_preview": result.get("response", "N/A")[:100] if result.get("response") else "BLOCKED",
                "response_length": len(result.get("response", "")) if result.get("response") else 0,
            }
        else:
            return {
                "prompt": prompt,
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "prompt": prompt,
            "error": str(e)
        }

if __name__ == "__main__":
    print("Testing API responses for different prompts...\n")
    print("=" * 80)
    
    for prompt in test_prompts:
        result = test_api(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Status: {result.get('status', 'ERROR')}")
        print(f"Risk: {result.get('risk', 'N/A')}")
        print(f"Response Length: {result.get('response_length', 0)} chars")
        print(f"Response Preview: {result.get('response_preview', 'ERROR')}")
        if "error" in result:
            print(f"Error: {result['error']}")
        print("-" * 80)
        time.sleep(1)
    
    print("\n✅ Test complete!")
