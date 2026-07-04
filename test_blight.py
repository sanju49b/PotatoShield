"""
Test runner for Blight Prediction Agent
Run this from the project root directory
"""

import sys
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[OK] Loaded environment variables from {env_path}")
    else:
        print(f"[WARNING] .env file not found at {env_path}")
except ImportError:
    print("[WARNING] python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"[WARNING] Could not load .env file: {e}")

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run
from src.agents.blight_prediction_agent import (
    ComprehensiveBlightDataCollector,
    BlightPredictionAgent
)
import json
from datetime import datetime, timedelta

if __name__ == "__main__":
    # Step 1: Collect weather data
    print("="*70)
    print("BLIGHT PREDICTION - COMPLETE WORKFLOW")
    print("="*70)
    print("\nStep 1: Collecting weather data...")
    
    collector = ComprehensiveBlightDataCollector()
    target_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    
    weather_dataset = collector.collect_complete_dataset(
        location_name="Hyderabad",
        target_date=target_date,
        country_code="IN"
    )

    # Print weather summary
    collector.print_summary(weather_dataset)

    # Step 2: Initialize blight prediction agent
    print("\nStep 2: Initializing Blight Prediction Agent...")
    agent = BlightPredictionAgent()

    # Step 3: Create state with weather data
    state = {
        "weather_dataset": weather_dataset,  # Full dataset from collector
        "days_after_planting": 30,  # Vegetative growth stage
    }

    # Step 4: Run prediction
    print("\nStep 3: Running blight risk prediction...")
    result_state = agent.predict_blight_risk(state)

    # Step 5: Print report
    print("\n" + "="*70)
    print("BLIGHT PREDICTION REPORT")
    print("="*70)
    print(result_state["final_report"])

    # Step 6: Access structured prediction data
    prediction = result_state.get("blight_prediction", {})
    print("\n" + "="*70)
    print("STRUCTURED PREDICTION DATA (JSON)")
    print("="*70)
    print(json.dumps(prediction, indent=2))

