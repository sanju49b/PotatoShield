# Enhanced Blight Prediction Agent - Complete Guide

## 🎯 Overview

The enhanced blight prediction agent now supports:
- **Automatic user data extraction** from profile (location, sowing date)
- **Multi-country support** (India & UK) with climate-specific configurations
- **Hutton Criteria** for UK (official blight warning system)
- **Advanced prediction logic** with detailed metric breakdowns
- **Seamless data flow** from first page through all layers

## 🌍 Climate-Specific Configurations

### India Configuration

**Growth Stages:**
- Sowing & Germination (0-15 DAP): Late Nov-Early Dec
- Vegetative Growth (15-45 DAP): Dec-Early Jan
- Tuber Initiation (45-60 DAP): January
- Tuber Bulking (60-90 DAP): Late Jan-Feb
- Maturity (90-110 DAP): Mid-Late Feb
- Harvest (110-130 DAP): Late Feb-March

**Key Features:**
- Focus on fog, dew, and monsoon patterns
- High humidity (>85%) triggers Late Blight
- Fungicides: Mancozeb, Metalaxyl, Copper oxychloride, Cymoxanil

### UK Configuration

**Growth Stages:**
- Sowing & Germination (0-20 DAP): Mid-Apr to Early May
- Vegetative Growth (21-50 DAP): May-Early Jun
- Flowering (51-75 DAP): Jun-Early Jul
- Tuber Formation (76-105 DAP): Jul-Aug
- Maturity (106-140 DAP): Aug-Sep
- Harvest (140-180 DAP): Sep-Oct

**Hutton Criteria (UK Standard):**
- **CRITICAL RISK**: Two consecutive days with:
  - Minimum temperature >= 10°C
  - At least 6 hours of relative humidity >= 90%
- When met, immediate fungicide application recommended
- This is the UK's official blight warning system

**Key Features:**
- Cool, wet summer conditions
- Fungicides: Fluazinam, Propamocarb, Mandipropamid, Cymoxanil, Fenamidone

## 🔄 Automatic Data Flow

The agent automatically extracts data from `user_profile` in the state:

```python
# Data automatically extracted:
- location: from user_profile.fields[0].location
- sowing_date: from user_profile.fields[0].sowing_date
- days_after_planting: calculated from sowing_date
- country: detected from location or weather dataset
```

**No need to ask user again!** The data flows seamlessly from the first page setup.

## 📊 Enhanced Features

### 1. Automatic User Data Extraction
```python
user_data = self._extract_user_data(state)
# Returns: location, sowing_date, days_after_planting, country, field_data
```

### 2. Country Detection
- Automatically detects UK vs India from:
  - Location string (UK cities, "UK", "United Kingdom", etc.)
  - Weather dataset country field
  - Defaults to India if unclear

### 3. Hutton Criteria Checking (UK)
```python
hutton_criteria = self._check_hutton_criteria(weather_dataset)
# Returns: met status, consecutive days, details, risk level
```

### 4. Climate-Specific Growth Stages
- Different DAP ranges for India vs UK
- Country-specific stage names and characteristics

### 5. Climate-Specific System Prompts
- India: Focus on monsoon, fog, Indian fungicides
- UK: Focus on Hutton Criteria, cool/wet conditions, UK fungicides

## 🚀 Usage Examples

### Example 1: Basic Usage (Auto-extracts from state)
```python
agent = BlightPredictionAgent()
state = {
    "user_profile": {
        "fields": [{
            "location": "Hyderabad",
            "sowing_date": "2024-11-01"
        }]
    }
}
result_state = agent.predict_blight_risk(state)
# Automatically:
# - Extracts location and sowing_date
# - Calculates DAP
# - Detects country (India)
# - Collects weather data if needed
# - Runs prediction with India-specific config
```

### Example 2: UK Location
```python
state = {
    "user_profile": {
        "fields": [{
            "location": "London, UK",
            "sowing_date": "2024-04-15"
        }]
    }
}
result_state = agent.predict_blight_risk(state)
# Automatically:
# - Detects UK
# - Checks Hutton Criteria
# - Uses UK growth stages
# - UK-specific fungicide recommendations
```

### Example 3: With Existing Weather Data
```python
state = {
    "user_profile": {
        "fields": [{
            "location": "Hyderabad",
            "sowing_date": "2024-11-01"
        }]
    },
    "weather_dataset": existing_dataset  # Optional
}
result_state = agent.predict_blight_risk(state)
# Uses existing weather data, still extracts user data for context
```

## 📋 Enhanced Output Structure

The prediction result now includes:

```json
{
    "growth_stage": "Vegetative Growth",
    "days_after_planting": 30,
    "location": "Hyderabad, India",
    "country": "India",
    "sowing_date": "2024-11-01",
    "location_from_profile": "Hyderabad",
    
    "hutton_criteria": {  // UK only
        "met": true,
        "consecutive_days": 2,
        "details": [...],
        "risk_level": "high"
    },
    
    "climate_config": {
        "country": "India",
        "growth_stage_config": {...},
        "fungicides": ["Mancozeb", "Metalaxyl", ...]
    },
    
    "late_blight_risk": {...},
    "early_blight_risk": {...},
    "overall_disease_pressure": "high",
    ...
}
```

## 🔍 Key Methods

### `_extract_user_data(state)`
Extracts location, sowing_date, and calculates DAP from user_profile.

### `_detect_country(location, state)`
Detects country from location string or weather dataset.

### `_check_hutton_criteria(weather_dataset)`
Checks UK Hutton Criteria for Late Blight risk.

### `_determine_growth_stage(dap, country)`
Returns growth stage based on DAP and country-specific ranges.

### `_get_system_prompt(country)`
Returns climate-specific system prompt (India or UK).

## 🎨 Integration with Workflow

The agent integrates seamlessly with the LangGraph workflow:

1. **User sets up field** (location + sowing_date) → Saved to `user_profile.fields`
2. **Router agent** routes to predictive agent
3. **BlightPredictionAgent** automatically:
   - Extracts location and sowing_date from profile
   - Detects country
   - Collects weather data if needed
   - Runs climate-specific prediction
   - Returns enhanced results

**No additional user prompts needed!**

## 🧪 Testing

Test with different countries:

```python
# Test India
state = {
    "user_profile": {
        "fields": [{"location": "Hyderabad", "sowing_date": "2024-11-01"}]
    }
}

# Test UK
state = {
    "user_profile": {
        "fields": [{"location": "London, UK", "sowing_date": "2024-04-15"}]
    }
}
```

## 📝 Notes

- **Backward Compatible**: Still works with manual `weather_dataset` and `days_after_planting` in state
- **Auto-Collection**: If weather_dataset missing but location provided, automatically collects weather data
- **Country Detection**: Smart detection from multiple sources, defaults to India
- **Hutton Criteria**: Only checked for UK, integrated into prediction logic
- **Climate Configs**: Stored in `INDIA_CONFIG` and `UK_CONFIG` dictionaries

## 🔮 Future Enhancements

Potential additions:
- More countries (USA, Canada, etc.)
- LLM-as-a-Judge for final validation
- Advanced metric breakdowns with confidence scores
- Historical pattern matching
- More disease types (Black Scurf, etc.)

