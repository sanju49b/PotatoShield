"""
Test script for multi-language translation feature in General Chat Agent

This script tests the language detection and translation functionality.
"""

import os
import sys

# Add parent directory to path to import src modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.general_chat_agent import GeneralChatAgent
from src.state.agent_state import AgentState

def test_language_detection():
    """Test the language detection feature"""
    
    agent = GeneralChatAgent()
    
    test_cases = [
        # Test case format: (input, expected_languages)
        ("Hello, how are you?", []),  # No language requested
        ("Tell me about potato farming in Telugu", ["telugu"]),
        ("Respond in Hindi please", ["hindi"]),
        ("Can you answer in Tamil?", ["tamil"]),
        ("Translate to Telugu and Hindi", ["telugu", "hindi"]),
        ("Give me the answer in hindi and tamil", ["hindi", "tamil"]),
        ("What is late blight? Also show in Telugu", ["telugu"]),
        ("How to prevent early blight? తెలుగు", ["telugu"]),
    ]
    
    print("=" * 80)
    print("TESTING LANGUAGE DETECTION")
    print("=" * 80)
    
    for user_input, expected_langs in test_cases:
        detected = agent._detect_language_preference(user_input)
        status = "✅ PASS" if set(detected) == set(expected_langs) else "❌ FAIL"
        
        print(f"\n{status}")
        print(f"Input: {user_input}")
        print(f"Expected: {expected_langs}")
        print(f"Detected: {detected}")
    
    print("\n" + "=" * 80)

def test_full_translation():
    """Test full translation workflow"""
    
    print("\n" + "=" * 80)
    print("TESTING FULL TRANSLATION WORKFLOW")
    print("=" * 80)
    
    agent = GeneralChatAgent()
    
    # Create a mock state
    state: AgentState = {
        "user_profile": {
            "user_id": "test_user",
            "username": "Test Farmer",
            "fields": [{
                "field_id": "test_field",
                "location": "Hyderabad, India",
                "sowing_date": "2024-10-01"
            }]
        },
        "conversation": {
            "session_id": "test_session",
            "messages": [],
            "current_field_id": "test_field"
        },
        "user_input": "What is potato blight? Please respond in Telugu and Hindi.",
        "input_type": "text",
        "image_data": None,
        "selected_agent": None,
        "routing_reasoning": None,
        "routing_confidence": None,
        "weather_data": None,
        "weather_dataset": None,
        "disease_prediction": None,
        "blight_prediction": None,
        "disease_identification": None,
        "final_report": None,
        "llm_judge_validation": None
    }
    
    print("\nUser Input:", state["user_input"])
    print("\nProcessing...")
    
    try:
        result_state = agent.chat(state)
        
        print("\n" + "-" * 80)
        print("ENGLISH RESPONSE:")
        print("-" * 80)
        print(result_state.get("final_report", "No response"))
        
        translations = result_state.get("translations", {})
        requested_languages = result_state.get("requested_languages", [])
        
        if requested_languages:
            print("\n" + "-" * 80)
            print(f"REQUESTED LANGUAGES: {', '.join(requested_languages)}")
            print("-" * 80)
            
            for lang in requested_languages:
                translation = translations.get(lang)
                if translation:
                    print(f"\n{lang.upper()} TRANSLATION:")
                    print(translation)
                else:
                    print(f"\n{lang.upper()}: Translation failed")
        else:
            print("\nNo translations requested.")
        
        print("\n" + "=" * 80)
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set OpenAI API key from environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set in environment")
        print("Please set it in your .env file or as an environment variable")
        sys.exit(1)
    
    # Test language detection
    test_language_detection()
    
    # Test full translation (uncomment to test with actual OpenAI API calls)
    # WARNING: This will use OpenAI API credits!
    print("\n" + "=" * 80)
    print("To test full translation with OpenAI API, uncomment the line below")
    print("WARNING: This will use OpenAI API credits!")
    print("=" * 80)
    
    # Uncomment to test:
    # test_full_translation()
