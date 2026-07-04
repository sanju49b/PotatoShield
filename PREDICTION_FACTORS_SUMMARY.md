# Disease Prediction Factors - Quick Reference

## 🎯 Core Factors Used for Blight Prediction

### **Tier 1: Critical Factors** (Highest Impact)

| Factor | Data Collected | Late Blight Impact | Early Blight Impact |
|--------|---------------|-------------------|---------------------|
| **Temperature** | Min, Max, Mean, Dew Point | ⭐⭐⭐⭐⭐ Critical (8-22°C optimal) | ⭐⭐⭐⭐ High (20-30°C optimal) |
| **Relative Humidity** | Min, Max, Mean | ⭐⭐⭐⭐⭐ Critical (>85% high risk) | ⭐⭐⭐⭐ High (70-90% risk) |
| **Days After Planting** | Calculated from sowing date | ⭐⭐⭐⭐⭐ Critical (45-60 DAP highest risk) | ⭐⭐⭐⭐ High (90+ DAP risk) |
| **Hutton Criteria (UK)** | Min temp + RH hours | ⭐⭐⭐⭐⭐ Critical (when met) | N/A |

### **Tier 2: High Impact Factors**

| Factor | Data Collected | Impact |
|--------|---------------|--------|
| **Precipitation** | Daily sum, hours, probability | ⭐⭐⭐⭐ High (creates leaf wetness) |
| **Cloud Cover** | Mean, Low, Mid, High | ⭐⭐⭐⭐ High (>70% + humidity = risk) |
| **Dew Point** | Mean daily | ⭐⭐⭐⭐ High (dew formation indicator) |

### **Tier 3: Moderate Impact Factors**

| Factor | Data Collected | Impact |
|--------|---------------|--------|
| **Wind Speed** | Mean, Max, Gusts, Direction | ⭐⭐⭐ Moderate (5-15 km/h optimal for spore spread) |
| **Soil Moisture** | 0-7cm, 7-28cm, 28-100cm depth | ⭐⭐⭐ Moderate (>0.120 m³/m³ + humidity = risk) |
| **Solar Radiation** | Total, Direct, Diffuse, Sunshine hours | ⭐⭐⭐ Moderate (low = prolonged wetness) |
| **PM2.5** | Mean concentration | ⭐⭐⭐ Moderate (>50 µg/m³ + humidity = spore dispersal) |
| **UV Index** | Max daily | ⭐⭐⭐ Moderate (>7 + humidity = Early Blight risk) |

### **Tier 4: Supporting Factors**

| Factor | Data Collected | Impact |
|--------|---------------|--------|
| **Soil Temperature** | 0cm, 0-7cm, 7-28cm, 28-100cm | ⭐⭐ Low-Moderate (pathogen activity) |
| **Ozone** | Mean concentration | ⭐⭐ Low-Moderate (plant health) |
| **Air Pressure** | Surface, MSL | ⭐ Low (weather pattern indicator) |
| **Evapotranspiration** | Daily sum | ⭐ Low (moisture balance) |

## 📊 Factor Combinations That Trigger High Risk

### **Late Blight High Risk:**
1. ✅ Min temp 8-12°C + Max temp 18-22°C + RH >85% + Cloud cover >70%
2. ✅ Fog/mist + High humidity (>80%) + Moderate temps (10-20°C)
3. ✅ PM2.5 >50 µg/m³ + Humidity >85% + Wind 5-15 km/h
4. ✅ Soil moisture >0.120 m³/m³ + High humidity
5. ✅ **UK: Hutton Criteria met** (2 consecutive days: min temp >=10°C + 6+ hours RH >=90%)

### **Early Blight High Risk:**
1. ✅ Warm days (25-30°C) + Cool nights (10-15°C) + RH 70-90%
2. ✅ Dew formation (dew point ≈ min temp) + High humidity
3. ✅ High UV (>7) + Moderate humidity + Later growth stages (90+ DAP)
4. ✅ Water stress + Older leaves

## 🔍 How Each Factor is Analyzed

### **Temperature Analysis:**
- **Min Temperature**: Critical for Late Blight (8-12°C optimal)
- **Max Temperature**: Affects Early Blight (25-30°C optimal)
- **Temperature Range**: Day-night variation affects disease risk
- **Dew Point**: Close to min temp → dew formation → disease risk

### **Humidity Analysis:**
- **Mean Humidity**: Overall moisture level
- **Max Humidity**: Peak moisture periods
- **Duration**: Hours above thresholds (especially 90% for UK)
- **Combined with Temp**: Critical interaction

### **Precipitation Analysis:**
- **Daily Sum**: Total rainfall amount
- **Precipitation Hours**: Duration of wet conditions
- **Pattern**: Consecutive wet days → higher risk
- **Intensity**: Heavy rain (>25mm) vs light rain

### **Wind Analysis:**
- **Speed**: 5-15 km/h optimal for spore spread
- **Gusts**: High gusts → physical damage
- **Direction**: Affects spore movement patterns

### **Cloud Cover Analysis:**
- **Total Cover**: >70% → reduced solar → prolonged wetness
- **Low Clouds**: Most relevant for leaf wetness
- **Combined with Humidity**: High clouds + high RH → risk

### **Soil Analysis:**
- **Moisture Level**: Affects pathogen activity and plant health
- **Temperature**: Affects root health and pathogen growth
- **Depth**: Surface (0-7cm) most relevant for disease

### **Air Quality Analysis:**
- **PM2.5**: Can carry spores, enhance dispersal
- **Ozone**: Affects plant stress
- **UV Index**: Affects leaf aging and susceptibility

## 📈 Factor Priority Matrix

```
Priority 1 (Critical):     Temperature + Humidity + Growth Stage
Priority 2 (High):        Precipitation + Cloud Cover + Dew Point
Priority 3 (Moderate):    Wind + Soil Moisture + Solar + PM2.5 + UV
Priority 4 (Supporting):  Soil Temp + Ozone + Pressure + ET
```

## 🎯 Risk Calculation Logic

The AI evaluates:

1. **Individual Factor Values** → Compared against optimal ranges
2. **Factor Combinations** → Multiple factors creating favorable conditions
3. **Temporal Patterns** → Consecutive days meeting criteria
4. **Growth Stage Context** → How factors affect current stage
5. **Climate Context** → India vs UK specific thresholds
6. **Historical Patterns** → Similar to known outbreak conditions

## 📋 Complete Factor List (80+ Variables)

### Weather Variables (40+):
- Temperature (4 metrics)
- Humidity (3 metrics)
- Precipitation (4 metrics)
- Wind (4 metrics)
- Cloud Cover (4 metrics)
- Solar Radiation (4 metrics)
- Pressure (2 metrics)
- Dew Point
- Visibility
- Weather Code
- Sunshine Duration
- Evapotranspiration (2 metrics)
- Vapour Pressure Deficit
- And more...

### Soil Variables (8+):
- Soil Temperature (4 depths)
- Soil Moisture (3 depths)
- Surface Temperature

### Air Quality Variables (12+):
- PM2.5, PM10
- Ozone
- Nitrogen Dioxide
- Sulphur Dioxide
- UV Index (2 metrics)
- Aerosol Optical Depth
- Dust
- Ammonia
- AQI (European, US)

### Phenological Variables:
- Days After Planting (DAP)
- Growth Stage
- Calendar Period
- Sowing Date

## 💡 Key Insights

1. **No single factor** determines risk - **combinations** are critical
2. **Temperature + Humidity** is the most important pair
3. **Growth stage** modifies how all factors are interpreted
4. **Temporal patterns** (consecutive days) are crucial
5. **Hutton Criteria** (UK) is the highest priority when met
6. **80+ variables** are collected, but **~15 core factors** drive predictions

## 🔬 Factor Interactions

The system analyzes how factors **interact**:

- **Synergistic Effects**: Factors that amplify each other
  - Example: High humidity + Low temp + Cloud cover = High Late Blight risk
  
- **Limiting Effects**: Factors that reduce risk despite others
  - Example: High solar radiation can reduce risk even with moderate humidity
  
- **Compound Effects**: Multiple factors creating cumulative risk
  - Example: Rain + High humidity + Moderate temp + Cloud cover = Very high risk

## 📊 Data Quality & Confidence

The system also considers:
- **Data Completeness**: Missing factors reduce confidence
- **Data Consistency**: Patterns across days increase confidence
- **Weather Pattern Clarity**: Clear patterns = higher confidence
- **Historical Comparison**: Matching known outbreaks = higher confidence

