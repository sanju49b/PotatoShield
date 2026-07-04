"""
Test script for Blight Prediction Agent

This script tests:
1. ComprehensiveBlightDataCollector - Data collection functionality
2. BlightPredictionAgent - Prediction functionality
3. Full workflow integration

Run this script to verify everything is working correctly.
"""

import os
import sys
import json
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

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.blight_prediction_agent import (
    ComprehensiveBlightDataCollector,
    BlightPredictionAgent
)


def test_data_collector():
    """Test the ComprehensiveBlightDataCollector"""
    print("\n" + "="*70)
    print("TEST 1: DATA COLLECTOR")
    print("="*70)
    
    try:
        collector = ComprehensiveBlightDataCollector()
        print("✓ Collector initialized successfully")
        
        # Test location lookup
        print("\n📍 Testing location lookup...")
        location = collector.get_location_coordinates("Hyderabad", "IN")
        print(f"✓ Found location: {location['city']}, {location['country']}")
        print(f"  Coordinates: {location['latitude']}, {location['longitude']}")
        print(f"  Elevation: {location['elevation']}m")
        
        # Test data collection
        print("\n📊 Testing data collection...")
        target_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        print(f"  Target date: {target_date}")
        
        dataset = collector.collect_complete_dataset(
            location_name="Hyderabad",
            target_date=target_date,
            country_code="IN"
        )
        
        # Validate dataset structure
        assert "location" in dataset, "Missing location in dataset"
        assert "target_date" in dataset, "Missing target_date in dataset"
        assert "daily_weather" in dataset, "Missing daily_weather in dataset"
        assert "daily_air_quality" in dataset, "Missing daily_air_quality in dataset"
        assert "metadata" in dataset, "Missing metadata in dataset"
        
        print("✓ Dataset structure is valid")
        
        # Check data quality
        daily_weather = dataset["daily_weather"]
        if "date" in daily_weather and len(daily_weather["date"]) > 0:
            print(f"✓ Collected {len(daily_weather['date'])} days of weather data")
        else:
            print("⚠ Warning: No daily weather dates found")
        
        # Print summary
        print("\n📋 Dataset Summary:")
        collector.print_summary(dataset)
        
        return True, dataset
        
    except Exception as e:
        print(f"❌ Error in data collector test: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_prediction_agent_with_mock_data():
    """Test the BlightPredictionAgent with mock data"""
    print("\n" + "="*70)
    print("TEST 2: PREDICTION AGENT (MOCK DATA)")
    print("="*70)
    
    try:
        agent = BlightPredictionAgent()
        print("✓ Agent initialized successfully")
        
        # Create mock weather dataset
        mock_dataset = {
            "location": {
                "city": "Hyderabad",
                "country": "India",
                "latitude": 17.3850,
                "longitude": 78.4867,
                "elevation": 500
            },
            "target_date": "2025-11-10",
            "daily_weather": {
                "date": ["2025-11-06", "2025-11-07", "2025-11-08", "2025-11-09", 
                        "2025-11-10", "2025-11-11", "2025-11-12", "2025-11-13"],
                "temperature_2m_mean": [24.5, 25.0, 24.8, 25.2, 24.0, 23.5, 24.2, 25.5],
                "temperature_2m_min": [18.0, 19.0, 18.5, 19.2, 17.5, 17.0, 18.0, 19.5],
                "temperature_2m_max": [30.0, 31.0, 30.5, 31.2, 29.5, 29.0, 30.0, 31.5],
                "relative_humidity_2m_mean": [75, 80, 85, 90, 88, 82, 78, 75],
                "relative_humidity_2m_min": [60, 65, 70, 75, 73, 68, 65, 60],
                "relative_humidity_2m_max": [90, 95, 100, 100, 98, 95, 90, 90],
                "dew_point_2m_mean": [18.0, 19.5, 20.0, 21.0, 20.5, 19.0, 18.5, 18.0],
                "precipitation_sum": [0, 2.5, 5.0, 8.0, 12.0, 5.5, 2.0, 0],
                "wind_speed_10m_mean": [8.0, 10.0, 12.0, 15.0, 18.0, 12.5, 10.0, 8.5],
                "wind_speed_10m_max": [15.0, 18.0, 20.0, 25.0, 28.0, 20.0, 18.0, 16.0],
                "cloud_cover_mean": [40, 60, 80, 90, 95, 85, 70, 50],
                "shortwave_radiation_sum": [15000, 12000, 8000, 5000, 3000, 7000, 10000, 14000],
                "soil_temperature_0_to_7cm_mean": [22.0, 22.5, 23.0, 23.5, 23.0, 22.5, 22.0, 22.5],
                "soil_moisture_0_to_7cm_mean": [0.15, 0.16, 0.18, 0.20, 0.22, 0.19, 0.17, 0.15]
            },
            "daily_air_quality": {
                "date": ["2025-11-06", "2025-11-07", "2025-11-08", "2025-11-09", 
                        "2025-11-10", "2025-11-11", "2025-11-12", "2025-11-13"],
                "pm2_5_mean": [45, 50, 55, 60, 65, 58, 52, 48],
                "ozone_mean": [80, 85, 90, 95, 100, 92, 88, 82],
                "uv_index_max": [6, 5, 4, 3, 2, 4, 5, 6]
            },
            "metadata": {
                "total_days": 8,
                "expected_days": 8
            }
        }
        
        state = {
            "weather_dataset": mock_dataset,
            "days_after_planting": 45  # Tuber Initiation stage
        }
        
        print("\n🤖 Running prediction with mock data...")
        result_state = agent.predict_blight_risk(state)
        
        # Validate results
        if "blight_prediction" in result_state:
            prediction = result_state["blight_prediction"]
            
            if "error" in prediction:
                print(f"⚠ Prediction returned error: {prediction.get('error')}")
                print(f"  Message: {prediction.get('user_message', 'N/A')}")
                return False, None
            
            # Check required fields
            required_fields = ["late_blight_risk", "early_blight_risk", "overall_disease_pressure"]
            for field in required_fields:
                if field not in prediction:
                    print(f"⚠ Missing field: {field}")
                else:
                    print(f"✓ Found field: {field}")
            
            print("\n📊 Prediction Results:")
            print(f"  Growth Stage: {prediction.get('growth_stage', 'N/A')}")
            print(f"  Late Blight Risk: {prediction.get('late_blight_risk', {}).get('risk_level', 'N/A')}")
            print(f"  Early Blight Risk: {prediction.get('early_blight_risk', {}).get('risk_level', 'N/A')}")
            print(f"  Overall Disease Pressure: {prediction.get('overall_disease_pressure', 'N/A')}")
            
            return True, result_state
        else:
            print("❌ No prediction in result state")
            return False, None
            
    except Exception as e:
        print(f"❌ Error in prediction agent test: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_full_workflow():
    """Test the complete workflow from data collection to prediction"""
    print("\n" + "="*70)
    print("TEST 3: FULL WORKFLOW INTEGRATION")
    print("="*70)
    
    try:
        # Step 1: Collect data
        print("\n📥 Step 1: Collecting weather data...")
        collector = ComprehensiveBlightDataCollector()
        target_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        
        dataset = collector.collect_complete_dataset(
            location_name="Hyderabad",
            target_date=target_date,
            country_code="IN"
        )
        print("✓ Data collection complete")
        
        # Step 2: Run prediction
        print("\n🤖 Step 2: Running blight prediction...")
        agent = BlightPredictionAgent()
        
        state = {
            "weather_dataset": dataset,
            "days_after_planting": 50  # Tuber Initiation stage
        }
        
        result_state = agent.predict_blight_risk(state)
        
        # Step 3: Validate results
        print("\n✅ Step 3: Validating results...")
        if "blight_prediction" in result_state:
            prediction = result_state["blight_prediction"]
            
            if "error" in prediction:
                print(f"❌ Prediction failed: {prediction.get('error')}")
                print(f"  Message: {prediction.get('user_message', 'N/A')}")
                return False
            
            print("✓ Prediction completed successfully")
            print(f"\n📋 Summary:")
            print(f"  Location: {prediction.get('location', 'N/A')}")
            print(f"  Growth Stage: {prediction.get('growth_stage', 'N/A')}")
            print(f"  Late Blight: {prediction.get('late_blight_risk', {}).get('risk_level', 'N/A')}")
            print(f"  Early Blight: {prediction.get('early_blight_risk', {}).get('risk_level', 'N/A')}")
            print(f"  Disease Pressure: {prediction.get('overall_disease_pressure', 'N/A')}")
            
            # Print full report
            if "final_report" in result_state:
                print("\n" + "="*70)
                print("FULL REPORT")
                print("="*70)
                print(result_state["final_report"])
            
            return True
        else:
            print("❌ No prediction in result")
            return False
            
    except Exception as e:
        print(f"❌ Error in full workflow test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_streaming():
    """Test the streaming prediction method"""
    print("\n" + "="*70)
    print("TEST 4: STREAMING PREDICTION")
    print("="*70)
    
    try:
        agent = BlightPredictionAgent()
        
        # Create minimal mock dataset for streaming test
        mock_dataset = {
            "location": {
                "city": "Hyderabad",
                "country": "India",
                "elevation": 500
            },
            "target_date": "2025-11-10",
            "daily_weather": {
                "date": ["2025-11-10"],
                "temperature_2m_mean": [24.0],
                "temperature_2m_min": [17.5],
                "temperature_2m_max": [29.5],
                "relative_humidity_2m_mean": [88],
                "relative_humidity_2m_min": [73],
                "relative_humidity_2m_max": [98],
                "precipitation_sum": [12.0],
                "wind_speed_10m_mean": [18.0],
                "wind_speed_10m_max": [28.0],
                "cloud_cover_mean": [95],
                "shortwave_radiation_sum": [3000],
                "soil_temperature_0_to_7cm_mean": [23.0],
                "soil_moisture_0_to_7cm_mean": [0.22]
            },
            "daily_air_quality": {
                "date": ["2025-11-10"],
                "pm2_5_mean": [65],
                "ozone_mean": [100],
                "uv_index_max": [2]
            },
            "metadata": {
                "total_days": 1
            }
        }
        
        state = {
            "weather_dataset": mock_dataset,
            "days_after_planting": 45
        }
        
        print("🔄 Testing streaming prediction...")
        updates = []
        for update in agent.predict_blight_risk_streaming(state):
            updates.append(update)
            update_type = update.get("type", "unknown")
            message = update.get("message", "")
            stage = update.get("stage", "")
            
            if update_type == "status":
                print(f"  [{stage}] {message}")
            elif update_type == "result":
                print("✓ Streaming completed successfully")
                data = update.get("data", {})
                print(f"  Risk Level: {data.get('late_blight_risk', {}).get('risk_level', 'N/A')}")
                return True
            elif update_type == "error":
                print(f"❌ Streaming error: {message}")
                return False
        
        print("⚠ No result received from streaming")
        return False
        
    except Exception as e:
        print(f"❌ Error in streaming test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n" + "="*70)
    print("TEST 5: ERROR HANDLING")
    print("="*70)
    
    try:
        agent = BlightPredictionAgent()
        
        # Test 1: Missing weather dataset
        print("\n🧪 Test 5.1: Missing weather dataset...")
        state = {"days_after_planting": 30}
        result = agent.predict_blight_risk(state)
        
        if "blight_prediction" in result and "error" in result["blight_prediction"]:
            print("✓ Correctly handled missing dataset")
        else:
            print("⚠ Should have returned error for missing dataset")
        
        # Test 2: Invalid location
        print("\n🧪 Test 5.2: Invalid location...")
        collector = ComprehensiveBlightDataCollector()
        try:
            location = collector.get_location_coordinates("InvalidCityXYZ123", "IN")
            print("⚠ Should have raised error for invalid location")
        except ValueError as e:
            print(f"✓ Correctly raised error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in error handling test: {e}")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("BLIGHT PREDICTION AGENT - TEST SUITE")
    print("="*70)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run tests
    results["data_collector"] = test_data_collector()[0]
    results["prediction_mock"] = test_prediction_agent_with_mock_data()[0]
    results["full_workflow"] = test_full_workflow()
    results["streaming"] = test_streaming()
    results["error_handling"] = test_error_handling()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:20s}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

