# Disease Prediction Factors - Complete List

## 📊 Overview

The blight prediction agent uses **multiple environmental and biological factors** to assess disease risk. These factors are collected from weather APIs and analyzed using AI to predict Late Blight and Early Blight risks.

## 🌡️ Primary Weather Factors

### 1. **Temperature** (Critical Factor)
**Data Collected:**
- `temperature_2m_mean` - Average air temperature at 2m height
- `temperature_2m_min` - Minimum daily temperature
- `temperature_2m_max` - Maximum daily temperature
- `dew_point_2m_mean` - Dew point temperature (indicates moisture capacity)

**How It's Used:**
- **Late Blight**: Optimal range 8-22°C (especially 10-20°C for UK)
- **Early Blight**: Optimal range 20-30°C (warm days)
- Temperature deviation from optimal ranges affects risk
- Dew point close to min temp → dew formation → disease risk

**Risk Indicators:**
- Min temp 8-12°C + Max temp 18-22°C → High Late Blight risk
- Warm days (25-30°C) + Cool nights (10-15°C) → Early Blight risk
- Temp <7°C or >28°C → Low risk (too cold/hot for pathogens)

### 2. **Relative Humidity** (Critical Factor)
**Data Collected:**
- `relative_humidity_2m_mean` - Average relative humidity
- `relative_humidity_2m_min` - Minimum daily humidity
- `relative_humidity_2m_max` - Maximum daily humidity

**How It's Used:**
- **Late Blight**: RH >85% for extended periods → High risk
- **Early Blight**: RH 70-90% → Moderate to high risk
- **Hutton Criteria (UK)**: 6+ hours of RH >=90% → Critical risk
- High humidity enables spore germination and disease spread

**Risk Indicators:**
- RH >90% for 6+ hours (UK Hutton Criteria) → Immediate action
- RH >85% + cool temps → Late Blight risk
- RH 75-85% + moderate temps → Medium risk
- RH <70% → Low risk

### 3. **Precipitation & Rainfall** (High Impact)
**Data Collected:**
- `precipitation_sum` - Total daily precipitation (mm)
- `rain_sum` - Total rainfall
- `precipitation_hours` - Hours with precipitation
- `precipitation_probability_max` - Maximum probability of rain

**How It's Used:**
- Heavy rain (>25mm/day) → Disease spread risk
- Prolonged wet periods → Leaf wetness → Pathogen activity
- Light rain (<5mm/day) + overcast → Medium risk
- No rain + dry conditions → Lower risk

**Risk Indicators:**
- >25mm/day → High risk (disease spread)
- 2+ consecutive wet days → Prolonged humidity risk
- <5mm/day + overcast → Medium risk
- No rain → Lower risk

### 4. **Wind Speed & Direction** (Moderate Impact)
**Data Collected:**
- `wind_speed_10m_mean` - Average wind speed at 10m
- `wind_speed_10m_max` - Maximum wind speed
- `wind_gusts_10m_max` - Maximum wind gusts
- `wind_direction_10m_dominant` - Dominant wind direction

**How It's Used:**
- Wind speed 5-15 km/h → Optimal for spore dispersal
- High winds (>30 km/h) → Physical damage + spore spread
- Low wind (<5 km/h) → Stagnant conditions → Higher humidity

**Risk Indicators:**
- 5-15 km/h → Optimal spore spread (moderate risk)
- >30 km/h → High spore spread + physical damage
- <5 km/h → Stagnant air → Higher humidity risk

### 5. **Cloud Cover** (Moderate Impact)
**Data Collected:**
- `cloud_cover_mean` - Average cloud cover percentage
- `cloud_cover_low` - Low-level clouds
- `cloud_cover_mid` - Mid-level clouds
- `cloud_cover_high` - High-level clouds

**How It's Used:**
- High cloud cover (>70%) → Reduced solar radiation → Prolonged leaf wetness
- Cloud cover >50% + high humidity → Medium to high risk
- Low cloud cover (<30%) → Sunny conditions → Lower risk

**Risk Indicators:**
- >70% cloud cover + RH >80% → High Late Blight risk
- 50-70% cloud cover + moderate humidity → Medium risk
- <30% cloud cover → Lower risk (sunny conditions)

### 6. **Solar Radiation** (Moderate Impact)
**Data Collected:**
- `shortwave_radiation_sum` - Total solar radiation (Wh/m²)
- `direct_radiation` - Direct solar radiation
- `diffuse_radiation` - Diffuse solar radiation
- `sunshine_duration` - Hours of sunshine

**How It's Used:**
- Low solar radiation → Prolonged leaf wetness → Disease risk
- High solar radiation → Dries leaves → Lower risk
- UV radiation affects Early Blight (high UV + humidity → risk)

**Risk Indicators:**
- Low solar radiation + high humidity → High risk
- High solar radiation → Lower risk (dries conditions)

## 🌱 Soil Factors

### 7. **Soil Temperature** (Moderate Impact)
**Data Collected:**
- `soil_temperature_0cm` - Surface soil temperature
- `soil_temperature_0_to_7cm_mean` - Average 0-7cm depth
- `soil_temperature_7_to_28cm_mean` - Average 7-28cm depth
- `soil_temperature_28_to_100cm_mean` - Average 28-100cm depth

**How It's Used:**
- Soil temp affects pathogen activity and root health
- Optimal range varies by growth stage
- Cold soil (<8°C) → Poor emergence (UK)
- Warm soil → Pathogen activity

**Risk Indicators:**
- Soil temp in pathogen optimal range → Higher risk
- Very cold or very hot soil → Lower risk

### 8. **Soil Moisture** (Moderate Impact)
**Data Collected:**
- `soil_moisture_0_to_7cm_mean` - Average 0-7cm depth (m³/m³)
- `soil_moisture_7_to_28cm_mean` - Average 7-28cm depth
- `soil_moisture_28_to_100cm_mean` - Average 28-100cm depth

**How It's Used:**
- High soil moisture (>0.120 m³/m³) + high humidity → Late Blight risk
- Too dry → Plant stress → Early Blight risk
- Optimal moisture → Healthy plants → Lower disease susceptibility

**Risk Indicators:**
- >0.120 m³/m³ + high humidity → High risk
- <0.080 m³/m³ → Plant stress → Moderate risk
- Optimal range (0.100-0.120 m³/m³) → Lower risk

## 🌍 Air Quality Factors

### 9. **PM2.5 (Particulate Matter)** (Moderate Impact)
**Data Collected:**
- `pm2_5_mean` - Average PM2.5 concentration (µg/m³)

**How It's Used:**
- High PM2.5 (>50 µg/m³) + humidity >85% → Enhanced spore dispersal
- PM2.5 30-50 µg/m³ → Moderate impact
- Low PM2.5 (<30 µg/m³) → Minimal impact

**Risk Indicators:**
- >50 µg/m³ + high humidity → High risk (spore dispersal)
- 30-50 µg/m³ → Moderate risk
- <30 µg/m³ → Low risk

### 10. **Ozone** (Low-Moderate Impact)
**Data Collected:**
- `ozone_mean` - Average ozone concentration (µg/m³)

**How It's Used:**
- High ozone can affect plant health
- Indirect impact on disease susceptibility
- Combined with other factors

### 11. **UV Index** (Moderate Impact for Early Blight)
**Data Collected:**
- `uv_index_max` - Maximum UV index
- `uv_index_clear_sky_max` - Maximum clear sky UV

**How It's Used:**
- High UV (>7) + moderate humidity → Early Blight risk
- UV affects leaf aging and susceptibility
- Lower UV → Less stress → Lower risk

**Risk Indicators:**
- UV >7 + RH 70-90% → Early Blight risk
- Moderate UV (4-7) → Moderate risk
- Low UV (<4) → Lower risk

## 📅 Temporal & Phenological Factors

### 12. **Days After Planting (DAP)** (Critical Factor)
**How It's Used:**
- Determines growth stage
- Different stages have different susceptibility
- Critical periods:
  - **Tuber Initiation (45-60 DAP)**: Highest Late Blight risk
  - **Flowering (51-75 DAP)**: High risk period (UK)
  - **Maturity (90+ DAP)**: Early Blight risk increases

**Risk by Stage:**
- Sowing & Germination: Low risk (soil-borne diseases)
- Vegetative Growth: Moderate risk (foliar diseases start)
- Tuber Initiation/Flowering: **HIGHEST RISK** (critical period)
- Tuber Bulking: High risk (disease spread)
- Maturity: Moderate risk (Early Blight)
- Harvest: Low risk (but storage diseases)

### 13. **Growth Stage** (Critical Factor)
**How It's Used:**
- Each stage has specific ideal conditions
- Susceptibility varies by stage
- Stage-specific risk factors applied

### 14. **Calendar Period / Season** (Context Factor)
**How It's Used:**
- India: Nov-March (winter crop)
- UK: Apr-Oct (summer crop)
- Seasonal patterns affect disease pressure
- Monsoon/fog patterns (India)
- Cool/wet summers (UK)

## 🔬 Advanced Factors (UK-Specific)

### 15. **Hutton Criteria** (UK Critical Factor)
**Criteria:**
- Two consecutive days with:
  - Minimum temperature >= 10°C
  - At least 6 hours of relative humidity >= 90%

**How It's Used:**
- Official UK blight warning system
- When met → Immediate fungicide application recommended
- Highest priority factor for UK predictions

## 📈 Factor Interactions & Combinations

### High-Risk Combinations:

1. **Late Blight (High Risk):**
   - Min temp 8-12°C + Max temp 18-22°C + RH >85% + Cloud cover >70%
   - Fog/mist + High humidity + Moderate temps
   - PM2.5 >50 + Humidity >85% + Wind 5-15 km/h
   - Soil moisture >0.120 + High humidity
   - **UK**: Hutton Criteria met

2. **Early Blight (High Risk):**
   - Warm days (25-30°C) + Cool nights (10-15°C) + RH 70-90%
   - Dew formation (dew point ≈ min temp) + High humidity
   - High UV (>7) + Moderate humidity + Later growth stages
   - Water stress periods + Older leaves

3. **Medium Risk:**
   - RH 75-85% + Cloudy (>50%) + Temps 18-25°C
   - Light rain (<5mm) + Overcast + Moderate humidity
   - PM2.5 30-50 + Moderate humidity

4. **Low Risk:**
   - RH <70% + Sunny (cloud cover <30%) + Dry
   - Temp >28°C or <7°C
   - Very low humidity + High solar radiation

## 🎯 Factor Priority & Weighting

While the current implementation uses AI to analyze all factors holistically, the relative importance is:

### **Critical Factors (Highest Weight):**
1. **Temperature** (especially min temp for Late Blight)
2. **Relative Humidity** (especially >85% for Late Blight)
3. **Days After Planting / Growth Stage** (determines susceptibility)
4. **Hutton Criteria** (UK - highest priority when met)

### **High Impact Factors:**
5. **Precipitation / Rainfall** (creates leaf wetness)
6. **Cloud Cover** (affects solar radiation and leaf wetness)
7. **Dew Point** (indicates dew formation potential)

### **Moderate Impact Factors:**
8. **Wind Speed** (spore dispersal)
9. **Soil Moisture** (pathogen activity)
10. **Solar Radiation** (dries conditions)
11. **PM2.5** (spore dispersal enhancement)
12. **UV Index** (Early Blight)

### **Supporting Factors:**
13. **Soil Temperature** (pathogen activity)
14. **Ozone** (plant health)
15. **Air Pressure** (weather patterns)
16. **Evapotranspiration** (moisture balance)

## 📊 Data Collection Summary

**Total Variables Collected:**
- **40+ hourly weather variables**
- **20+ daily aggregated variables**
- **12+ air quality variables**
- **8+ soil variables**

**Key Metrics Analyzed:**
- Temperature: Min, Max, Mean, Dew Point
- Humidity: Min, Max, Mean
- Precipitation: Sum, Hours, Probability
- Wind: Mean, Max, Gusts, Direction
- Cloud Cover: Mean, Low, Mid, High
- Solar: Total, Direct, Diffuse, Sunshine Duration
- Soil: Temperature (4 depths), Moisture (3 depths)
- Air Quality: PM2.5, Ozone, UV Index

## 🔍 How Factors Are Analyzed

1. **Daily Analysis**: Each day in the 8-day window is analyzed individually
2. **Factor Combination**: Multiple factors are evaluated together (not isolated)
3. **Temporal Patterns**: Trends over the 8-day period are considered
4. **Growth Stage Context**: Factors are interpreted based on current growth stage
5. **Climate Context**: India vs UK conditions affect factor interpretation
6. **Historical Patterns**: Similar conditions to known outbreaks are considered

## 💡 Key Insights

- **No single factor** determines risk - it's the **combination** that matters
- **Temperature + Humidity** is the most critical combination
- **Growth stage** modifies how factors are interpreted
- **Hutton Criteria** (UK) overrides other factors when met
- **Temporal patterns** (consecutive days) are critical
- **Soil conditions** affect pathogen activity and plant health
- **Air quality** can enhance spore dispersal

## 🎯 Risk Calculation Logic

The AI analyzes:
1. **Individual factor values** against optimal ranges
2. **Factor combinations** that create disease-favorable conditions
3. **Temporal patterns** (consecutive days meeting criteria)
4. **Growth stage susceptibility** modifiers
5. **Climate-specific thresholds** (India vs UK)
6. **Historical outbreak patterns** matching current conditions

The final risk assessment considers all these factors holistically to provide a comprehensive prediction.

