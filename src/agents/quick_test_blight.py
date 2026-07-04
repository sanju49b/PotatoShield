"""
Quick test script for Blight Prediction Agent

This is a simplified test that runs the full workflow quickly.
Use this for quick verification before running the full test suite.
"""

import os
import sys
from datetime import datetime, timedelta

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[OK] Loaded environment variables from {env_path}")
    else:
        print(f"[WARNING] .env file not found at {env_path}")
except ImportError:
    print("[WARNING] python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"[WARNING] Could not load .env file: {e}")

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.blight_prediction_agent import (
    ComprehensiveBlightDataCollector,
    BlightPredictionAgent
)


def quick_test():
    """Quick test of the blight prediction workflow"""
    print("="*70)
    print("QUICK TEST - BLIGHT PREDICTION")
    print("="*70)
    
    try:
        # Step 1: Collect data
        print("\n📥 Collecting weather data for Hyderabad...")
        collector = ComprehensiveBlightDataCollector()
        target_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        dataset = collector.collect_complete_dataset(
            location_name="Hyderabad",
            target_date=target_date,
            country_code="IN"
        )
        print("✓ Data collected")
        
        # Step 2: Run prediction
        print("\n🤖 Running blight prediction...")
        agent = BlightPredictionAgent()
        
        state = {
            "weather_dataset": dataset,
            "days_after_planting": 50  # Tuber Initiation stage
        }
        
        result_state = agent.predict_blight_risk(state)
        
        # Step 3: Show results
        if "blight_prediction" in result_state:
            prediction = result_state["blight_prediction"]
            
            if "error" in prediction:
                print(f"\n❌ Error: {prediction.get('error')}")
                print(f"   {prediction.get('user_message', '')}")
                return False
            
            print("\n✅ Prediction successful!")
            print(f"\n📊 Results:")
            print(f"   Location: {prediction.get('location', 'N/A')}")
            print(f"   Growth Stage: {prediction.get('growth_stage', 'N/A')}")
            print(f"   Late Blight Risk: {prediction.get('late_blight_risk', {}).get('risk_level', 'N/A').upper()}")
            print(f"   Early Blight Risk: {prediction.get('early_blight_risk', {}).get('risk_level', 'N/A').upper()}")
            print(f"   Disease Pressure: {prediction.get('overall_disease_pressure', 'N/A').upper()}")
            
            # Show report preview
            if "final_report" in result_state:
                print("\n" + "="*70)
                print("REPORT PREVIEW (first 500 chars):")
                print("="*70)
                print(result_state["final_report"][:500] + "...")
            
            return True
        else:
            print("\n❌ No prediction in result")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 Quick test passed!")
    else:
        print("\n⚠ Quick test failed")
    sys.exit(0 if success else 1)

