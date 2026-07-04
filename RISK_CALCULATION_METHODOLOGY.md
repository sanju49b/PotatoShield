# Potato Blight Risk Calculation Methodology

## Overview

The Potato Shield predictive algorithm uses a **deterministic, sliding-window approach** to calculate disease risk percentages for Late Blight and Early Blight. This ensures consistent, reproducible results based on weather data analysis.

---

## 1. Algorithm Architecture

### 1.1 Two-Stage Approach

1. **Deterministic Risk Calculation**: Uses mathematical formulas based on weather parameters
2. **AI Contextual Analysis**: Provides recommendations and contextual insights (does NOT affect risk percentages)

### 1.2 Key Principles

- **Deterministic**: Same weather data always produces same risk percentage
- **Sliding Window**: Each day's risk considers surrounding days for context
- **Weighted Factors**: Different weather parameters have different importance
- **Country-Specific**: Different thresholds for India vs UK conditions

---

## 2. Sliding Window Implementation

### 2.1 Window Structure

For each day `i` in the forecast:
- **Window Size**: 7 days total
- **Window Range**: `[i - 3, i + 3]` (3 days before + current day + 3 days after)
- **Boundary Handling**: 
  - At start: `window_start = max(0, i - 3)`
  - At end: `window_end = min(len(dates) - 1, i + 3)`

### 2.2 Weighting Strategy

- **Current Day Weight**: 40% (primary importance)
- **Surrounding Days Weight**: 60% shared equally among other days in window
- **Purpose**: Balances immediate conditions with trend context

### 2.3 Effective Values Calculation

For each weather parameter:
```
effective_value = current_day_value (if available)
                OR window_average (if current day missing)
```

Window averages are calculated as:
- Simple average for: temp_min, temp_max, humidity_min, humidity_max, wind, cloud
- Weighted average for: temp_mean, humidity_mean (current day 40%, others 60%)
- Sum for: precipitation (total in window)

---

## 3. Late Blight Risk Calculation

### 3.1 Formula Structure

```
Late Blight Risk = (Temperature Risk × 0.25) + 
                   (Humidity Risk × 0.35) + 
                   (Precipitation Risk × 0.20) + 
                   (Wind Risk × 0.10) + 
                   (Cloud Cover Risk × 0.10)
```

**Total Weight**: 1.0 (100%)

### 3.2 Temperature Factor (25% weight)

**Optimal Range**: 10-20°C (min temp 8-12°C, max temp 18-22°C)

| Temperature Range | Risk Score | Rationale |
|------------------|------------|-----------|
| 10-20°C | 20 | Low risk - optimal pathogen activity range |
| 8-10°C or 20-25°C | 40 | Moderate risk - slightly outside optimal |
| 5-8°C or 25-30°C | 60 | Higher risk - suboptimal conditions |
| <5°C or >30°C | 30 | Lower risk - pathogen less active |

**Fallback**: If mean temp unavailable, uses `(temp_min + temp_max) / 2`

### 3.3 Humidity Factor (35% weight - MOST IMPORTANT)

**Critical Threshold**: RH ≥90% for extended periods

| Humidity Range | Risk Score | Rationale |
|---------------|------------|-----------|
| ≥90% | 90 | Very high risk - spore germination enabled |
| ≥85% | 70 | High risk - favorable for disease |
| ≥80% | 50 | Moderate risk |
| ≥70% | 30 | Low risk |
| <70% | 15 | Very low risk |

**Fallback**: If mean unavailable, uses `humidity_max` (conservative estimate)

### 3.4 Precipitation Factor (20% weight)

**Impact**: Rain increases disease spread and creates favorable conditions

| Precipitation | Risk Score | Rationale |
|--------------|------------|-----------|
| ≥10mm | 80 | High risk - heavy rain spreads spores |
| ≥5mm | 60 | Moderate risk |
| ≥2mm | 40 | Low-moderate risk |
| >0mm | 25 | Low risk - light rain |
| 0mm | 10 | Very low risk - no rain |

### 3.5 Wind Factor (10% weight)

**Principle**: Low wind = higher risk (spores don't disperse)

| Wind Speed | Risk Score | Rationale |
|-----------|------------|-----------|
| <5 km/h | 70 | High risk - spores remain in canopy |
| <10 km/h | 50 | Moderate risk |
| <15 km/h | 30 | Lower risk - moderate dispersal |
| ≥15 km/h | 15 | Very low risk - high wind disperses spores |

### 3.6 Cloud Cover Factor (10% weight)

**Impact**: High clouds = prolonged humidity = higher risk

| Cloud Cover | Risk Score | Rationale |
|------------|------------|-----------|
| ≥80% | 60 | High risk - overcast conditions |
| ≥60% | 40 | Moderate risk |
| ≥40% | 25 | Low risk |
| <40% | 10 | Very low risk - clear skies allow drying |

### 3.7 Minimum Visibility

If calculated risk > 0 but < 5%, it's set to 5% to ensure visibility.

---

## 4. Early Blight Risk Calculation

### 4.1 Formula Structure

```
Early Blight Risk = (Temperature Risk × 0.30) + 
                    (Humidity Risk × 0.25) + 
                    (Precipitation Risk × 0.25) + 
                    (Wind Risk × 0.10) + 
                    (Cloud Cover Risk × 0.10)
```

**Total Weight**: 1.0 (100%)

### 4.2 Temperature Factor (30% weight)

**Optimal Range**: 20-25°C (warm days + cool nights)

| Temperature Range | Risk Score | Rationale |
|------------------|------------|-----------|
| 20-25°C | 60 | Optimal for Early Blight |
| 18-20°C or 25-28°C | 50 | Good conditions |
| 15-18°C or 28-30°C | 40 | Moderate |
| <15°C or >30°C | 20 | Too cold or hot |

**Special Case**: If min/max available, checks for warm days + cool nights:
- Ideal: avg 20-25°C AND day-night difference ≥8°C → Risk = 70

### 4.3 Humidity Factor (25% weight)

**Optimal Range**: 70-90% (moderate humidity)

| Humidity Range | Risk Score | Rationale |
|---------------|------------|-----------|
| 80-90% | 70 | Optimal range |
| 70-80% | 55 | Good conditions |
| 60-70% | 40 | Moderate |
| ≥90% | 50 | Too high (more Late Blight) |
| <60% | 25 | Too low |

### 4.4 Precipitation Factor (25% weight)

**Optimal Range**: 5-15mm (moderate rain)

| Precipitation | Risk Score | Rationale |
|--------------|------------|-----------|
| 5-15mm | 65 | Optimal |
| 2-5mm or 15-20mm | 50 | Good |
| >20mm | 40 | Too much rain |
| >0mm | 35 | Light rain |
| 0mm | 20 | No rain |

### 4.5 Wind Factor (10% weight)

| Wind Speed | Risk Score | Rationale |
|-----------|------------|-----------|
| <8 km/h | 55 | Low wind helps |
| <15 km/h | 40 | Moderate |
| ≥15 km/h | 25 | High wind disperses |

### 4.6 Cloud Cover Factor (10% weight)

| Cloud Cover | Risk Score | Rationale |
|------------|------------|-----------|
| 50-70% | 50 | Moderate clouds optimal |
| 40-50% or 70-80% | 40 | Good |
| ≥80% | 30 | Too overcast (Late Blight) |
| <40% | 25 | Clear skies |

---

## 5. Overall Risk Percentage Calculation

### 5.1 Per-Day Risk Calculation

For each day `i`:
1. Collect weather data for window `[i-3, i+3]`
2. Calculate effective values (current day + window context)
3. Calculate Late Blight risk using formula
4. Calculate Early Blight risk using formula
5. Store both values

### 5.2 Weighted Average Across Days

After calculating risk for all days:

```
weights = [0.5 + (i / total_days) * 0.5 for i in range(total_days)]
```

This creates a linear weighting where:
- First day: weight = 0.5
- Last day: weight = 1.0
- **Recent days weighted more heavily**

Final percentages:
```
weighted_late_blight = sum(lb_risk[i] * weights[i]) / sum(weights)
weighted_early_blight = sum(eb_risk[i] * weights[i]) / sum(weights)
```

### 5.3 Risk Level Classification

**Late Blight:**
- **High**: ≥70%
- **Medium**: 40-69%
- **Low**: 20-39%
- **None**: <20%

**Early Blight:**
- **High**: ≥70%
- **Medium**: 40-69%
- **Low**: 20-39%
- **None**: <20%

---

## 6. Crop Growth Stage Detection

### 6.1 Days After Planting (DAP) Calculation

```
DAP = (Current Date - Sowing Date).days
```

If sowing date not provided, defaults to 30 days.

### 6.2 Growth Stage Determination

**India:**
- 0-15 DAP: Sowing & Germination
- 16-45 DAP: Vegetative Growth
- 46-60 DAP: Tuber Initiation
- 61-90 DAP: Tuber Bulking
- 91-110 DAP: Maturity & Senescence
- >110 DAP: Harvest & Storage

**UK:**
- 0-20 DAP: Sowing & Germination
- 21-50 DAP: Vegetative Growth
- 51-75 DAP: Flowering
- 76-105 DAP: Tuber Formation
- 106-140 DAP: Maturity
- >140 DAP: Harvest

### 6.3 Growth Stage Impact

Growth stage is used for:
- Contextual risk assessment (some stages more susceptible)
- AI recommendations (stage-specific advice)
- Display in dashboard

**Note**: Growth stage does NOT directly modify risk percentages (those are purely weather-based).

---

## 7. Risk Timeline Generation

### 7.1 Daily Risk Scores

For chart visualization, each day gets its own risk score calculated using the sliding window approach.

### 7.2 Overall Risk Calculation

```
Overall Risk = (Late Blight Risk × 0.7) + (Early Blight Risk × 0.3)
```

Late Blight weighted more heavily as it's more serious.

---

## 8. Key Features

### 8.1 Deterministic Results

- Same weather data → Same risk percentage
- No randomness or AI variability in risk scores
- Reproducible across runs

### 8.2 Context-Aware

- Sliding window considers trends, not just single day
- Recent days weighted more heavily
- Handles missing data gracefully

### 8.3 Scientifically-Based

- Thresholds based on epidemiological research
- Different weights reflect relative importance
- Country-specific considerations (India vs UK)

### 8.4 Transparent

- All calculations are explicit
- Risk factor contributions visible
- Methodology documented

---

## 9. Example Calculation

### Input Data (Day 5):
- Temperature: 15°C (mean), 12°C (min), 18°C (max)
- Humidity: 88% (mean), 75% (min), 95% (max)
- Precipitation: 8mm
- Wind: 6 km/h
- Cloud Cover: 75%

### Late Blight Calculation:

1. **Temperature**: 15°C → Risk = 20 (optimal range) → 20 × 0.25 = **5.0**
2. **Humidity**: 88% → Risk = 70 (high) → 70 × 0.35 = **24.5**
3. **Precipitation**: 8mm → Risk = 60 (moderate) → 60 × 0.20 = **12.0**
4. **Wind**: 6 km/h → Risk = 50 (moderate) → 50 × 0.10 = **5.0**
5. **Cloud Cover**: 75% → Risk = 40 (moderate) → 40 × 0.10 = **4.0**

**Total Late Blight Risk**: 5.0 + 24.5 + 12.0 + 5.0 + 4.0 = **50.5%**

### Early Blight Calculation:

1. **Temperature**: 15°C → Risk = 40 (moderate) → 40 × 0.30 = **12.0**
2. **Humidity**: 88% → Risk = 50 (too high) → 50 × 0.25 = **12.5**
3. **Precipitation**: 8mm → Risk = 50 (good) → 50 × 0.25 = **12.5**
4. **Wind**: 6 km/h → Risk = 55 (low wind) → 55 × 0.10 = **5.5**
5. **Cloud Cover**: 75% → Risk = 40 (good) → 40 × 0.10 = **4.0**

**Total Early Blight Risk**: 12.0 + 12.5 + 12.5 + 5.5 + 4.0 = **46.5%**

---

## 10. Implementation Notes

### 10.1 Data Sources

- Weather data from Open-Meteo API
- Daily aggregates from hourly data
- 8-day forecast window (4 days past + 3 days future)

### 10.2 Missing Data Handling

- Uses window averages if current day data missing
- Falls back to min/max if mean unavailable
- Conservative estimates (e.g., uses max humidity if mean missing)

### 10.3 Performance

- O(n × w) complexity where n = days, w = window size
- Efficient: single pass through data
- Cached calculations for chart generation

---

## 11. Future Enhancements

Potential improvements:
1. Hourly risk calculations (currently daily)
2. Machine learning model integration
3. Historical pattern matching
4. Regional calibration factors
5. Real-time sensor data integration

---

## 12. References

- Late Blight thresholds: Fry & Goodwin (1997), Zwankhuizen et al. (1998)
- Early Blight thresholds: Rotem (1994), Shitenberg (2010)
- UK Hutton Criteria: Hutton et al. (2004)
- Indian potato growing conditions: ICAR research publications

---

**Last Updated**: January 2025  
**Version**: 2.0 (Sliding Window Implementation)

