import requests
import json

print("=" * 70)
print("Testing RAI Main Moderation Endpoint (No Auth)")
print("=" * 70)

# Test with comprehensive moderation checks
payload = {
    "Prompt": "My phone number is 9876543210 and my email is test@example.com",
    "ModerationChecks": [
        "PromptInjection",
        "JailBreak", 
        "Toxicity",
        "Piidetct",
        "Profanity"
    ],
    "ModerationCheckThresholds": {
        "PromptInjectionThreshold": {"PromptInjectionThreshold": "0.85"},
        "JailBreakThreshold": {"JailBreakThreshold": "0.80"},
        "ToxicityThreshold": {
            "ToxicityThreshold": "0.50",
            "SevereToxicityThreshold": "0.50",
            "ObsceneThreshold": "0.50",
            "ThreatThreshold": "0.50",
            "InsultThreshold": "0.50",
            "IdentityAttackThreshold": "0.50",
            "SexualExplicitThreshold": "0.50"
        },
        "ProfanityThreshold": {"ProfanityThreshold": "0"},
        "PiientitiesConfiguredToDetect": ["PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON", "LOCATION"],
        "PiientitiesConfiguredToBlock": ["PHONE_NUMBER", "EMAIL_ADDRESS"]
    },
    "userid": "test_user",
    "translate": "no",
    "EmojiModeration": "no"
}

try:
    print("\nSending request WITHOUT Authorization header...")
    response = requests.post(
        "http://localhost:5555/rai/v1/moderations",
        json=payload,
        timeout=60  # Longer timeout for first request
    )
    
    print(f"\n✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n📊 Response Summary:")
        print(f"   - Keys in response: {list(result.keys())}")
        
        if "ModerationResults" in result:
            mod_results = result["ModerationResults"]
            print(f"\n📋 Moderation Results:")
            for check_name, check_result in mod_results.items():
                if isinstance(check_result, dict):
                    status = check_result.get("result", "N/A")
                    print(f"   - {check_name}: {status}")
                elif isinstance(check_result, list) and len(check_result) > 0:
                    status = check_result[0].get("result", "N/A") if isinstance(check_result[0], dict) else "N/A"
                    print(f"   - {check_name}: {status}")
        
        print(f"\n🔍 Full Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"\n❌ Error Response:")
        print(response.text)
        
except requests.exceptions.Timeout:
    print("\n⏱️  Request timed out - RAI service might be processing slowly")
except Exception as e:
    print(f"\n💥 Exception: {type(e).__name__}: {e}")
