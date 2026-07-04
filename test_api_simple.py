import requests
import json

# Test 1: Main moderation endpoint
print("Testing main moderation endpoint...")
payload = {
    "Prompt": "What is the weather like today?",
    "ModerationChecks": ["Toxicity", "Piidetct"],
    "ModerationCheckThresholds": {
        "ToxicityThreshold": {
            "ToxicityThreshold": "0.50",
            "SevereToxicityThreshold": "0.50",
            "ObsceneThreshold": "0.50",
            "ThreatThreshold": "0.50",
            "InsultThreshold": "0.50",
            "IdentityAttackThreshold": "0.50",
            "SexualExplicitThreshold": "0.50"
        },
        "PiientitiesConfiguredToDetect": ["PHONE_NUMBER", "EMAIL_ADDRESS"],
        "PiientitiesConfiguredToBlock": ["PHONE_NUMBER", "EMAIL_ADDRESS"]
    },
    "userid": "test_user",
    "translate": "no",
    "EmojiModeration": "no"
}

try:
    response = requests.post(
        "http://localhost:5555/rai/v1/moderations",
        json=payload,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

# Test 2: Toxicity Popup
print("\n\nTesting Toxicity Popup...")
payload2 = {
    "text": "This is a test message",
    "ToxicityThreshold": {
        "ToxicityThreshold": "0.50",
        "SevereToxicityThreshold": "0.50",
        "ObsceneThreshold": "0.50",
        "ThreatThreshold": "0.50",
        "InsultThreshold": "0.50",
        "IdentityAttackThreshold": "0.50",
        "SexualExplicitThreshold": "0.50"
    }
}

try:
    response = requests.post(
        "http://localhost:5555/rai/v1/moderations/ToxicityPopup",
        json=payload2,
        timeout=30
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
