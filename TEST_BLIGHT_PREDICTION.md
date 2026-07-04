# Testing Blight Prediction Agent

## Quick Start

### Prerequisites
1. **OpenAI API Key**: Set your OpenAI API key as an environment variable
   ```powershell
   # Windows PowerShell
   $env:OPENAI_API_KEY="your-api-key-here"
   
   # Or set it permanently in your system environment variables
   ```

2. **Python Dependencies**: Make sure you have all required packages installed
   ```bash
   pip install langchain-openai requests
   ```

## Testing Methods

### Method 1: Quick Test (Recommended)
Run the simple test script from the project root:

```powershell
python test_blight.py
```

This will:
1. Collect weather data for Hyderabad
2. Run blight prediction
3. Display the results

### Method 2: Full Test Suite
Run the comprehensive test suite:

```powershell
python src/agents/test_blight_prediction.py
```

This runs multiple tests:
- Data collector test
- Prediction agent test (with mock data)
- Full workflow integration test
- Streaming test
- Error handling test

### Method 3: Interactive Notebook
Open the Jupyter notebook for interactive testing:

```powershell
jupyter notebook src/agents/testing.ipynb
```

### Method 4: Direct Execution
Run the main file directly (includes example usage):

```powershell
python src/agents/blight_prediction_agent.py
```

## Expected Output

When running successfully, you should see:

1. **Data Collection Phase**:
   - Location coordinates lookup
   - Historical weather data fetch
   - Forecast weather data fetch
   - Air quality data fetch
   - Daily data aggregation

2. **Prediction Phase**:
   - Weather data analysis
   - AI-based blight risk assessment
   - Risk level determination (Late Blight & Early Blight)
   - Actionable recommendations

3. **Results**:
   - Full text report
   - Structured JSON data with risk percentages
   - Peak risk days
   - Immediate actions and preventive recommendations

## Example Output

```
[INFO] Analyzing weather data for Hyderabad, India...
[INFO] Days After Planting: 30 (Vegetative Growth)
[INFO] Target Date: 2025-11-13
[INFO] Analyzing weather patterns with AI...
[OK] Analysis complete

BLIGHT PREDICTION REPORT
======================================================================
Location: Hyderabad, India
Growth Stage: Vegetative Growth (30 DAP)
Late Blight Risk: MEDIUM (45%)
Early Blight Risk: LOW (20%)
...
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src'"
**Solution**: Run from the project root directory, not from `src/agents/`

### Issue: "OpenAIError: api_key must be set"
**Solution**: Set your OpenAI API key:
```powershell
$env:OPENAI_API_KEY="sk-..."
```

### Issue: "UnicodeEncodeError"
**Solution**: Already fixed! All Unicode characters have been replaced with ASCII-safe alternatives.

### Issue: Network/API Errors
**Solution**: 
- Check your internet connection
- Verify Open-Meteo API is accessible
- Check if OpenAI API is accessible

## Customizing Tests

### Change Location
Edit `test_blight.py`:
```python
weather_dataset = collector.collect_complete_dataset(
    location_name="YourCity",  # Change this
    target_date=target_date,
    country_code="IN"  # Change country code if needed
)
```

### Change Growth Stage
Edit the `days_after_planting` value:
```python
state = {
    "weather_dataset": weather_dataset,
    "days_after_planting": 50,  # Change this (0-130)
}
```

Growth stages:
- 0-15 DAP: Sowing & Germination
- 15-45 DAP: Vegetative Growth
- 45-60 DAP: Tuber Initiation
- 60-90 DAP: Tuber Bulking
- 90-110 DAP: Maturity & Senescence
- 110+ DAP: Harvest & Storage

## Files Created

- `test_blight.py` - Quick test script (project root)
- `src/agents/test_blight_prediction.py` - Full test suite
- `src/agents/quick_test_blight.py` - Minimal test
- `src/agents/testing.ipynb` - Interactive notebook

## Success Criteria

✅ Test passes if:
1. Data collection completes without errors
2. Weather data is successfully fetched and aggregated
3. Blight prediction returns valid JSON structure
4. Report is generated with risk levels and recommendations

## Next Steps

After testing, you can:
1. Integrate into your main workflow
2. Use the streaming method for real-time updates
3. Customize the system prompt for different regions
4. Add more test cases for edge scenarios

