# 🧠 Prompt Engineering Guide — Streaming Implementation

## 🎯 Objective

Transition from simulated progress bars to **real-time streaming responses** in all agent workflows (`predict_agent`, `diagnostic_agent`, `charter_agent`, etc.).

Prompts and system messages should now be designed to **yield incremental updates** — reflecting what the model or API is doing step-by-step, creating a natural, conversational experience.

---

## 🧩 Key Prompt Behavior Principles

### 1. **Remove All Progress Bar or Percentage References**

❌ **BAD:**
- "Progress: 25% complete..."
- "Loading weather data..."
- "Processing... 50% done"
- "Step 3 of 12: Analyzing..."

✅ **GOOD:**
- "Fetching weather and soil data for your location..."
- "Analyzing blight risk based on temperature and humidity patterns..."
- "Comparing historical outbreaks with current conditions..."
- "Summarizing recommendations and generating final report..."

### 2. **Stream Outputs as Separate Thought Steps**

Each logical part of the workflow should produce a **self-contained output chunk** that can be rendered independently:

- **Step 1** → Weather/soil summary (complete section)
- **Step 2** → Disease risk analysis (complete section)
- **Step 3** → Recommendations + visual summary (complete section)
- **Step 4** → Tavily references (formatted and structured)

Each step should be:
- **Self-contained**: Can stand alone without context from previous steps
- **Clearly titled**: Frontend can render it with proper headers
- **Complete**: Not a fragment, but a complete thought/section

### 3. **Natural Language Communication**

The model should communicate what it's doing in natural, conversational language:

✅ **Natural:**
- "I'm analyzing the weather patterns for your field..."
- "Based on the current conditions, I'm seeing elevated risk for Late Blight..."
- "Let me check historical outbreaks in your area to compare conditions..."

❌ **Robotic:**
- "Executing analysis module..."
- "Processing data structure..."
- "Initializing risk calculation algorithm..."

---

## 🧠 Prompt Design Examples

### ❌ Bad Prompt (Monolithic Output)

```
System: "You are a disease prediction agent. Analyze weather data and generate a complete report."

User: "Predict disease risk for my crop."

Model: [Waits 15 seconds, then outputs entire report at once]
```

**Problem:** User sees nothing for 15 seconds, then everything appears at once.

---

### ✅ Good Prompt (Streaming Output)

```
System: """You are a predictive agriculture assistant. 
Analyze disease risk step-by-step and stream your findings as you complete each stage.

STREAMING INSTRUCTIONS:
1. Begin by summarizing the weather and soil data you're analyzing
2. Once analysis is complete, yield your disease risk assessment
3. Then provide recommendations
4. Finally, append structured Tavily references

Each stage should be a complete, self-contained section that can be rendered independently."""

User: "Predict disease risk for my crop."

Model: [Streams incrementally]
→ "🌦️ Analyzing current weather conditions for your field..."
→ [Weather summary appears]
→ "🧬 Evaluating disease risk patterns..."
→ [Risk assessment appears]
→ [And so on...]
```

**Result:** User sees content appearing progressively, feels engaged and informed.

---

## 🧩 Ideal Streaming Sequence (Model Behavior)

### Step-by-Step Output Structure

#### **Step 1: Weather & Field Information**
```
🌦️ Field & Weather Information

- Location: Hyderabad, India
- Elevation: 515m
- Analysis Date: Nov 10, 2025
- Forecast Window: 8 days

Current Conditions:
- Temperature: 28.1°C (avg)
- Humidity: 86% (avg)
- Precipitation: 12mm
```

#### **Step 2: Disease Risk Assessment**
```
🧬 Risk Assessment

| Disease | Risk Level | Confidence | Peak Days |
|---------|------------|------------|-----------|
| Late Blight | **HIGH (82%)** | High | Nov 10–11 |
| Early Blight | **MODERATE (46%)** | Medium | Nov 12 |

Summary:
High humidity (86%) and moderate temperatures (28°C) create ideal conditions for Late Blight development.
```

#### **Step 3: Environmental Observations**
```
🌿 Key Environmental Observations

- Soil Moisture: 0.15 m³/m³ → irrigation may be needed
- Air Quality: PM2.5 levels 32–58 µg/m³ → may enhance spore dispersal
- Cloud Cover: 14–33% during peak risk days
```

#### **Step 4: Recommendations**
```
🧪 Recommendations

Immediate Actions:
1. Apply Dimethomorph 50% WP @ 450 g/acre on Nov 12
2. Maintain humidity monitoring and irrigate to stabilize soil moisture

Preventive Measures:
- Spray Mancozeb (625ml/acre) on Nov 12
- Ensure good field drainage and destroy infected residues
```

#### **Step 5: Historical Context & Tavily References**
```
📚 Location-Specific Research & Historical Context

Historical Outbreak - November 2023:

Historical Weather Conditions:
- Temperature: 27-29°C (average)
- Humidity: 84-88%
- Rainfall: 15-20mm

The current temperature of 28°C and humidity of 86% closely match conditions during the November 2023 outbreak in Hyderabad, when temperatures averaged 27-29°C with 84-88% humidity. This similarity suggests elevated disease risk, as the pathogen thrives under these specific temperature and humidity ranges.

Risk Assessment: Current conditions mirror those of the 2023 outbreak, indicating a high probability of disease development if preventive measures are not taken immediately.

Source: [IntechOpen – Management of Late Blight](https://...)
```

---

## 🧰 Implementation Notes for Prompt Engineers

### 1. **Agent Prompt Structure**

Each agent prompt should include streaming instructions:

```python
system_prompt = """You are a predictive agriculture assistant analyzing potato disease risk.

STREAMING BEHAVIOR:
- Respond incrementally in structured, readable sections
- Stream your outputs in stages as you complete each subtask
- Each section should be complete and self-contained
- Use clear section headers (##, ###) for organization
- Communicate what you're doing in natural language

OUTPUT FORMAT:
1. Weather & Field Information (complete section)
2. Risk Assessment (complete section)
3. Environmental Observations (complete section)
4. Recommendations (complete section)
5. Historical Context & References (complete section)

Do NOT mention progress percentages or loading states.
Instead, describe what you're analyzing or doing."""
```

### 2. **Tavily Integration Prompts**

When processing Tavily results, structure the prompt to yield formatted output incrementally:

```python
tavily_formatting_prompt = """Transform raw Tavily research data into structured markdown.

STREAMING INSTRUCTIONS:
- Process and format historical context first
- Then format recommendations
- Finally format preventive measures
- Each section should be complete before moving to the next

OUTPUT STRUCTURE:
1. Historical Outbreak Analysis (with weather comparisons)
2. Management Recommendations
3. Preventive Measures
4. References (clickable links)

Format each section completely before proceeding to the next."""
```

### 3. **Avoid Monolithic Outputs**

❌ **DON'T:**
- Generate entire report, then return it all at once
- Buffer multiple sections before outputting
- Use progress indicators or loading messages

✅ **DO:**
- Yield each section as soon as it's ready
- Make each section independent and complete
- Use natural language to describe what's happening

### 4. **Markdown Formatting Best Practices**

- Use proper headers (##, ###) for section hierarchy
- Format links as clickable markdown: `[Text](URL)`
- Use bullet points for lists
- Add clear separators (---) between major sections
- Ensure all formatting is valid markdown

---

## 📋 Base System Prompt Template

### For Predictive Agent

```python
BASE_PREDICTIVE_SYSTEM_PROMPT = """You are an expert agricultural disease prediction assistant specializing in potato blight risk assessment.

STREAMING BEHAVIOR:
You analyze weather data and field conditions step-by-step, streaming your findings as you complete each stage. Each stage produces a complete, self-contained section that can be rendered independently.

ANALYSIS WORKFLOW:
1. **Weather & Field Information**: Summarize current weather conditions, location, elevation, and forecast window
2. **Risk Assessment**: Analyze disease risk for Late Blight and Early Blight with specific percentages and confidence levels
3. **Environmental Observations**: Highlight key environmental factors (soil moisture, air quality, cloud cover)
4. **Recommendations**: Provide immediate actions and preventive measures with specific fungicides and dosages
5. **Historical Context**: Compare current conditions with historical outbreaks (if available from Tavily research)

OUTPUT GUIDELINES:
- Use clear section headers (##, ###) for organization
- Write in natural, professional language (not technical jargon)
- Make each section complete and self-contained
- Include specific values (temperatures, percentages, dates)
- Format recommendations as actionable bullet points
- Include clickable source links for references

COMMUNICATION STYLE:
- Describe what you're analyzing in natural language
- Avoid progress indicators, percentages, or loading messages
- Use emoji icons (🌦️, 🧬, 🌿, 🧪, 📚) for visual hierarchy
- Write clear, grammatically correct sentences

RESPONSE FORMAT:
Stream your response in the following order, with each section complete before moving to the next:

## 🌦️ Field & Weather Information
[Complete weather summary]

## 🧬 Risk Assessment
[Complete risk analysis with table]

## 🌿 Key Environmental Observations
[Complete environmental analysis]

## 🧪 Recommendations
[Complete recommendations section]

## 📚 Location-Specific Research & Historical Context
[Complete historical context and references]"""
```

### For Diagnostic Agent

```python
BASE_DIAGNOSTIC_SYSTEM_PROMPT = """You are an expert plant pathologist specializing in potato disease diagnosis.

STREAMING BEHAVIOR:
You analyze images step-by-step, streaming your findings as you complete each stage. Each stage produces a complete, self-contained section.

ANALYSIS WORKFLOW:
1. **Disease Identification**: Analyze the image and identify the disease type
2. **Confidence & Severity**: Assess confidence level and disease severity
3. **Visual Indicators**: List specific visual features observed
4. **Treatment Recommendations**: Provide immediate treatment actions
5. **Historical Context**: Include location-specific research and historical outbreaks (if available)

OUTPUT GUIDELINES:
- Use clear section headers for organization
- Write in natural, professional language
- Make each section complete and self-contained
- Include specific treatment recommendations with dosages
- Format as actionable bullet points
- Include clickable source links for references

COMMUNICATION STYLE:
- Describe what you're observing in natural language
- Avoid progress indicators or loading messages
- Use emoji icons for visual hierarchy
- Write clear, grammatically correct sentences"""
```

---

## ✅ Expected User Experience

### Before (Progress Bar)
```
User: "What is the disease risk for my crop?"
System: [Progress bar: 0% → 15% → 30% → ... → 100%]
System: [Entire report appears at once after 15 seconds]
```

### After (Streaming)
```
User: "What is the disease risk for my crop?"
System: "🌦️ Analyzing current weather conditions for your field..."
      [Weather summary appears immediately]
System: "🧬 Evaluating disease risk patterns..."
      [Risk assessment appears]
System: "🌿 Reviewing environmental factors..."
      [Environmental observations appear]
System: "🧪 Generating recommendations..."
      [Recommendations appear]
System: "📚 Checking historical outbreaks in your area..."
      [Historical context appears]
```

**Result:** User sees content appearing progressively, feels engaged, and understands what's happening at each step.

---

## 🔧 Integration Checklist

When adapting existing prompts for streaming:

- [ ] Remove all progress bar/percentage references
- [ ] Add streaming behavior instructions to system prompt
- [ ] Structure output into independent, complete sections
- [ ] Use natural language to describe what's happening
- [ ] Ensure each section can be rendered independently
- [ ] Test that sections appear incrementally (not all at once)
- [ ] Verify markdown formatting is valid and clean
- [ ] Ensure Tavily results are formatted and streamed properly
- [ ] Check that historical weather comparisons are clear and readable

---

## 📝 Example: Converting a Non-Streaming Prompt

### Original Prompt (Non-Streaming)
```python
prompt = """Analyze the weather data and generate a complete disease risk report.
Include risk assessment, recommendations, and references.
Return the full report when complete."""
```

### Converted Prompt (Streaming)
```python
prompt = """Analyze the weather data step-by-step and stream your findings.

STREAMING INSTRUCTIONS:
1. Begin by summarizing the weather data you're analyzing
2. Once analysis is complete, yield your disease risk assessment
3. Then provide recommendations with specific actions
4. Finally, append structured historical context and references

Each section should be complete and self-contained. Use clear headers (##, ###) and natural language.
Do not mention progress or loading - just describe what you're analyzing."""
```

---

## 🎯 Key Takeaways

1. **No Progress Bars**: Remove all progress indicators, percentages, and loading messages
2. **Natural Communication**: Describe what you're doing in conversational language
3. **Incremental Output**: Stream complete sections as they're ready
4. **Self-Contained Sections**: Each section should be independent and renderable
5. **Clear Structure**: Use proper markdown headers and formatting
6. **Professional Language**: Write clear, grammatically correct sentences

---

## 📚 Additional Resources

- See `src/agents/blight_prediction_agent.py` for implementation examples
- See `src/agents/diagnostic_agent.py` for diagnostic agent streaming patterns
- See `api/main.py` for API streaming endpoint implementation
- See `frontend/app/chat/page.tsx` for frontend streaming rendering

