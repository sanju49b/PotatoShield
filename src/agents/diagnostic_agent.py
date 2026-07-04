# src/agents/diagnostic_agent.py
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import base64
import json
import os
from typing import Dict, Any, Optional, Generator, List
from PIL import Image
import io
from datetime import datetime
from src.state.agent_state import AgentState

# Import Tavily for enhanced recommendations
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("[WARNING] Tavily not installed. Install with: pip install tavily-python")

class DiagnosticAgent:
    """
    Image-based disease identification agent using GPT-4V
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=700
        )
    
    def _search_tavily(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Search Tavily for disease recommendations and historical data.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        if not TAVILY_AVAILABLE:
            return []
        
        try:
            tavily_api_key = os.getenv("TAVILY_API_KEY")
            if not tavily_api_key:
                return []
            
            client = TavilyClient(api_key=tavily_api_key)
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )
            return response.get("results", [])
        except Exception as e:
            print(f"[WARNING] Tavily search failed: {e}")
            return []
    
    def _refine_tavily_results(self, raw_results: List[Dict], category: str) -> List[Dict]:
        """
        Process raw Tavily search results through LLM to make them human-readable,
        grammatically correct, and professionally formatted.
        
        Args:
            raw_results: List of raw Tavily search results
            category: Category of results ("historical_context", "recommendations", "preventive_measures")
            
        Returns:
            List of refined results with cleaned content
        """
        if not raw_results:
            return []
        
        try:
            # Prepare raw content for LLM processing
            raw_content = []
            for i, result in enumerate(raw_results, 1):
                title = result.get("title", f"Result {i}")
                content = result.get("content", "")
                url = result.get("url", "")
                raw_content.append(f"Result {i}:\nTitle: {title}\nContent: {content}\nURL: {url}")
            
            raw_text = "\n\n---\n\n".join(raw_content)
            
            # Create prompt for LLM to refine the content
            system_prompt = """You are an expert agricultural content editor specializing in plant disease management. 
Your task is to refine raw research data into clear, professional, and grammatically correct recommendations.

STREAMING BEHAVIOR:
Process and refine content step-by-step. Do not mention progress, loading, or percentages. Instead, communicate naturally like "Refining research recommendations..." or "Formatting treatment guidelines...". Stream your outputs in stages, with each section being complete and self-contained.

CRITICAL CLEANING RULES:
- REMOVE ALL markdown headers: #, ##, ###, ####, etc. - convert them to plain text or remove entirely
- REMOVE ALL references to AI services: "ChatGPT", "OpenAI", "ChatOpenAI", "chatopen ai", "AI assistant", "AI model", etc.
- REMOVE ALL markdown formatting: **bold**, *italic*, `code`, etc. - convert to plain text
- REMOVE ALL markdown list markers if they appear in content: -, *, 1., etc. (keep the content, just remove the markers)
- PRESERVE location-specific data: dates, locations, weather conditions, historical outbreaks
- PRESERVE actionable recommendations: fungicide names, dosages, application rates, treatment methods
- Format as clear, readable paragraphs WITHOUT markdown
- Use plain text only - no markdown syntax whatsoever

Guidelines:
- Remove technical jargon, copyright notices, citation formats, and metadata
- Improve grammar and sentence structure
- Make content concise and actionable
- Maintain scientific accuracy
- Use professional agricultural terminology
- Format as clear, readable paragraphs (NO markdown)
- Preserve key information (dates, locations, specific recommendations)
- Remove redundant information and formatting artifacts
- Do NOT mention progress percentages, loading states, or step counters
- Do NOT mention AI tools, models, or services"""
            
            user_prompt = f"""Please refine the following {category} research data about potato disease management. 
Make it human-readable, grammatically correct, and professionally formatted.

RAW RESEARCH DATA:
{raw_text}

Please provide refined versions of each result. For each result, provide:
1. A clear, professional title (extract meaningful title from content or URL)
2. A well-written, grammatically correct summary (2-4 sentences) that highlights key insights
3. Key actionable points if applicable (extract specific recommendations, fungicides, dosages, dates)
4. Source name (extract meaningful source name from URL domain, e.g., "IntechOpen", "Academia.edu", "NACL Industries")

Format your response as JSON:
{{
    "refined_results": [
        {{
            "title": "Refined professional title",
            "summary": "Clear, grammatically correct summary paragraph with key insights",
            "key_points": ["Specific actionable point 1", "Specific actionable point 2", "Specific actionable point 3"],
            "source_name": "Extracted source name from URL",
            "url": "original_url"
        }}
    ]
}}

Important:
- Extract source names from URLs (e.g., "intechopen.com" → "IntechOpen", "academia.edu" → "Academia.edu")
- Preserve specific technical details (fungicide names, dosages, dates, locations)
- Remove copyright notices, citation formats, and metadata
- Make summaries concise but informative

Respond ONLY with valid JSON - no additional text."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm.invoke(messages)
            result_text = response.content.strip()
            
            # Debug: Log raw response
            print(f"[TAVILY_DEBUG] Raw LLM response length: {len(result_text)} chars")
            print(f"[TAVILY_DEBUG] Raw response preview: {result_text[:200]}...")
            
            # Parse JSON response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Additional cleaning: Remove any remaining markdown or AI references
            import re
            # Remove markdown headers
            result_text = re.sub(r'^#+\s*', '', result_text, flags=re.MULTILINE)
            # Remove AI service references
            result_text = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model|generated by|created by AI)\b', '', result_text, flags=re.IGNORECASE)
            
            parsed = json.loads(result_text)
            refined_results = parsed.get("refined_results", [])
            
            # Debug: Log refined results
            print(f"[TAVILY_DEBUG] Refined {len(refined_results)} results for category: {category}")
            
            # Post-process: Clean each refined result
            for refined in refined_results:
                # Remove markdown from title
                if refined.get("title"):
                    refined["title"] = re.sub(r'^#+\s*', '', refined["title"]).strip()
                    refined["title"] = re.sub(r'\*\*(.*?)\*\*', r'\1', refined["title"])  # Remove bold
                    refined["title"] = re.sub(r'\*(.*?)\*', r'\1', refined["title"])  # Remove italic
                
                # Remove markdown from summary
                if refined.get("summary"):
                    refined["summary"] = re.sub(r'^#+\s*', '', refined["summary"], flags=re.MULTILINE)
                    refined["summary"] = re.sub(r'\*\*(.*?)\*\*', r'\1', refined["summary"])  # Remove bold
                    refined["summary"] = re.sub(r'\*(.*?)\*', r'\1', refined["summary"])  # Remove italic
                    refined["summary"] = re.sub(r'`(.*?)`', r'\1', refined["summary"])  # Remove code
                    # Remove AI references
                    refined["summary"] = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model)\b', '', refined["summary"], flags=re.IGNORECASE)
                    refined["summary"] = refined["summary"].strip()
                
                # Clean key points
                if refined.get("key_points"):
                    cleaned_points = []
                    for point in refined["key_points"]:
                        cleaned = re.sub(r'^#+\s*', '', point)
                        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
                        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
                        cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)
                        cleaned = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model)\b', '', cleaned, flags=re.IGNORECASE)
                        cleaned = cleaned.strip()
                        if cleaned:  # Only add non-empty points
                            cleaned_points.append(cleaned)
                    refined["key_points"] = cleaned_points
            
            # Merge with original URLs and metadata, extract source names
            for i, refined in enumerate(refined_results):
                if i < len(raw_results):
                    original_url = raw_results[i].get("url", "")
                    refined["original_url"] = original_url
                    # Keep original URL as primary
                    if not refined.get("url"):
                        refined["url"] = original_url
                    
                    # Extract source name from URL if not provided
                    if not refined.get("source_name") and original_url:
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(original_url)
                            domain = parsed.netloc.replace("www.", "")
                            # Extract meaningful name (e.g., "intechopen.com" → "IntechOpen")
                            if domain:
                                parts = domain.split(".")
                                if len(parts) > 0:
                                    source_name = parts[0].capitalize()
                                    # Handle special cases
                                    if "academia" in domain:
                                        source_name = "Academia.edu"
                                    elif "intechopen" in domain:
                                        source_name = "IntechOpen"
                                    elif "mdpi" in domain:
                                        source_name = "MDPI"
                                    elif "pmc" in domain or "ncbi" in domain:
                                        source_name = "PubMed Central"
                                    refined["source_name"] = source_name
                        except Exception:
                            pass
            
            return refined_results
            
        except Exception as e:
            print(f"[WARNING] Failed to refine Tavily results: {e}")
            # Return original results if refinement fails
            return raw_results
    
    def _get_tavily_recommendations(self, disease_name: str, location: str = None, country: str = None) -> Dict[str, Any]:
        """
        Get comprehensive Tavily recommendations for a diagnosed disease.
        Results are processed through LLM to make them human-readable and professional.
        Uses location-specific site filters for better quality results.
        Searches for recent outbreaks with dates and weather conditions.
        
        Args:
            disease_name: Name of the disease (e.g., "Early Blight", "Late Blight")
            location: Optional location name for location-specific recommendations
            country: Optional country name for site filtering
            
        Returns:
            Dict with recommendations, historical_context, and preventive_measures (all refined)
        """
        tavily_data = {
            "recommendations": [],
            "historical_context": [],
            "preventive_measures": []
        }
        
        if not TAVILY_AVAILABLE or disease_name in ["Healthy", "Unclear/Poor Image"]:
            return tavily_data
        
        try:
            # Build location-specific query with site filters if country provided
            location_suffix = f" {location}" if location else ""
            site_filter = ""
            if country:
                if country == "India":
                    site_filter = " site:.gov.in OR site:.edu OR site:.org"
                elif country == "UK":
                    site_filter = " site:.gov.uk OR site:.ac.uk OR site:.org.uk"
            
            # Search for treatment recommendations
            rec_query = f"{disease_name} potato treatment management recommendations{location_suffix}{site_filter}"
            rec_results = self._search_tavily(rec_query, max_results=3)
            if rec_results:
                # Refine through LLM
                tavily_data["recommendations"] = self._refine_tavily_results(rec_results, "recommendations")
            
            # Search for RECENT outbreaks with dates and weather (if location provided)
            if location:
                # Use multiple queries to find recent outbreaks
                history_queries = [
                    f"potato {disease_name} outbreak {location}{' ' + country if country else ''} 2024 2023 2022 recent occurrence date weather conditions temperature humidity{site_filter}",
                    f"{disease_name} potato epidemic {location}{' ' + country if country else ''} recent years outbreak date temperature rainfall{site_filter}",
                    f"potato {disease_name} {location}{' ' + country if country else ''} last outbreak when date weather conditions similar{site_filter}"
                ]
                
                all_history_results = []
                for query in history_queries:
                    results = self._search_tavily(query, max_results=2)
                    all_history_results.extend(results)
                    if len(all_history_results) >= 5:  # Get top 5 most relevant
                        break
                
                if all_history_results:
                    # Use enhanced refinement that extracts weather and compares
                    tavily_data["historical_context"] = self._refine_tavily_results_enhanced(
                        all_history_results, location, country
                    )
            
            # Search for preventive measures
            preventive_query = f"{disease_name} potato prevention preventive measures{location_suffix}{site_filter}"
            preventive_results = self._search_tavily(preventive_query, max_results=2)
            if preventive_results:
                # Refine through LLM
                tavily_data["preventive_measures"] = self._refine_tavily_results(preventive_results, "preventive_measures")
                
        except Exception as e:
            print(f"[WARNING] Tavily recommendation search failed: {e}")
            import traceback
            traceback.print_exc()
        
        return tavily_data
    
    def _refine_tavily_results_enhanced(self, raw_results: List[Dict], location: str, country: str) -> List[Dict]:
        """
        Enhanced refinement that extracts outbreak dates and weather conditions.
        Similar to blight_prediction_agent but without current weather comparison.
        """
        if not raw_results:
            return []
        
        try:
            # Prepare raw content for LLM processing
            raw_content = []
            for i, result in enumerate(raw_results, 1):
                title = result.get("title", f"Result {i}")
                content = result.get("content", "")
                url = result.get("url", "")
                raw_content.append(f"Result {i}:\nTitle: {title}\nContent: {content}\nURL: {url}")
            
            raw_text = "\n\n---\n\n".join(raw_content)
            
            system_prompt = """You are an expert agricultural analyst specializing in plant disease outbreaks.
Your task is to extract historical outbreak information, identify weather conditions during those outbreaks, and present them clearly.

STREAMING BEHAVIOR:
Process historical data step-by-step and communicate what you're doing naturally. Do not mention progress, loading, or percentages. Instead, describe what you're analyzing in conversational language like "Extracting historical outbreak dates..." or "Comparing weather conditions...". Stream your outputs in stages, with each section being complete and self-contained.

Guidelines:
- Extract specific dates (year, month, season) from historical outbreaks
- Identify weather conditions mentioned (temperature, humidity, rainfall, etc.)
- Generate clear, professional sentences
- Remove technical jargon and make content readable
- Use professional agricultural terminology
- Do NOT mention progress percentages, loading states, or step counters"""
            
            user_prompt = f"""Analyze the following research data about historical {location}, {country} potato disease outbreaks.
Extract outbreak dates and weather conditions during outbreaks.

RAW RESEARCH DATA:
{raw_text}

For each historical outbreak found, provide:
1. **Outbreak Date**: Specific date, year, or season if mentioned
2. **Historical Weather Conditions**: Temperature, humidity, rainfall during the outbreak
3. **Summary**: Clear, professional sentences summarizing the outbreak

Format your response as JSON:
{{
    "refined_results": [
        {{
            "title": "Clear title describing the outbreak",
            "outbreak_date": "Date or year of outbreak (e.g., 'November 2023', '2022', 'Winter 2021')",
            "historical_weather": {{
                "temperature": "Temperature range or average during outbreak",
                "humidity": "Humidity levels during outbreak",
                "rainfall": "Rainfall amounts during outbreak"
            }},
            "summary": "2-3 clear, professional sentences summarizing the outbreak and its conditions",
            "key_points": ["Key point 1", "Key point 2"],
            "source_name": "Extracted source name from URL",
            "url": "original_url"
        }}
    ]
}}

Important:
- Extract dates and weather conditions accurately
- Write clear, professional sentences (not technical jargon)
- Focus on the MOST RECENT outbreaks first

Respond ONLY with valid JSON - no additional text."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm.invoke(messages)
            result_text = response.content.strip()
            
            # Parse JSON response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(result_text)
            refined_results = parsed.get("refined_results", [])
            
            # Merge with original URLs and extract source names
            for i, refined in enumerate(refined_results):
                if i < len(raw_results):
                    original_url = raw_results[i].get("url", "")
                    refined["original_url"] = original_url
                    if not refined.get("url"):
                        refined["url"] = original_url
                    
                    # Extract source name from URL if not provided
                    if not refined.get("source_name") and original_url:
                        try:
                            from urllib.parse import urlparse
                            parsed_url = urlparse(original_url)
                            domain = parsed_url.netloc.replace("www.", "")
                            if domain:
                                parts = domain.split(".")
                                if len(parts) > 0:
                                    source_name = parts[0].capitalize()
                                    if "academia" in domain:
                                        source_name = "Academia.edu"
                                    elif "intechopen" in domain:
                                        source_name = "IntechOpen"
                                    elif "mdpi" in domain:
                                        source_name = "MDPI"
                                    elif "pmc" in domain or "ncbi" in domain:
                                        source_name = "PubMed Central"
                                    refined["source_name"] = source_name
                        except Exception:
                            pass
            
            return refined_results
            
        except Exception as e:
            print(f"[WARNING] Failed to refine Tavily results with enhanced extraction: {e}")
            import traceback
            traceback.print_exc()
            # Return basic refined results if enhanced extraction fails
            return self._refine_tavily_results(raw_results, "historical_context")
    
    def _format_tavily_section(self, tavily_data: Dict[str, Any], disease_name: str, location: str = None, country: str = None) -> str:
        """
        Format Tavily data into a well-structured, readable markdown section using OpenAI.
        Creates a professional report with proper hierarchy, clickable links, and clear sections.
        
        Args:
            tavily_data: Dict with Tavily results
            disease_name: Name of the diagnosed disease
            location: Optional location name
            country: Optional country name
            
        Returns:
            Formatted markdown string with structured Tavily recommendations
        """
        if not tavily_data or not any(tavily_data.values()):
            return ""
        
        try:
            # Prepare raw content for OpenAI formatting
            raw_content = {
                "disease": disease_name,
                "historical_context": tavily_data.get("historical_context", []),
                "recommendations": tavily_data.get("recommendations", []),
                "preventive_measures": tavily_data.get("preventive_measures", [])
            }
            raw_content_text = json.dumps(raw_content, indent=2)
            
            # Create comprehensive formatting prompt
            system_prompt = """You are an expert agricultural report writer specializing in plant disease management.
Your task is to transform raw research data into a well-structured, professional markdown report.

STREAMING BEHAVIOR:
Process and format each section completely before moving to the next. Do not mention progress, loading, or percentages. Instead, communicate naturally like "Formatting historical outbreak data..." or "Structuring treatment recommendations...". Stream your outputs in stages, with each section being complete and self-contained.

CRITICAL FORMATTING RULES:
- START your response directly with "## 📚 Location-Specific Research & Treatment References" - do NOT include any headers before this
- Do NOT include headers like "## 🌿 Key Environmental Observations" or any other headers before the main Location-Specific header
- Do NOT mention AI services: "ChatGPT", "OpenAI", "ChatOpenAI", "chatopen ai", "AI assistant", "AI model", etc.
- Do NOT include duplicate "Location-Specific Research" headers - only include it once at the start
- PRESERVE location-specific data: dates, locations, weather conditions, historical outbreaks
- PRESERVE actionable recommendations: fungicide names, dosages, application rates, treatment methods

Guidelines:
- Create clear hierarchical structure with proper markdown headers (##, ###) - but ONLY after the main header
- Format links as clickable markdown: [Link Text](URL)
- Extract and label source domains (e.g., "IntechOpen", "Academia.edu", "NACL Industries")
- Remove redundancy while preserving all critical technical details
- Highlight actionable recommendations with clear formatting
- Use bullet points and numbered lists for readability
- Maintain scientific accuracy and terminology
- Group related information logically
- Add emoji icons for visual hierarchy (🧬, 🌿, 🧪, 📚)
- Ensure all links are properly formatted and clickable
- Do NOT mention progress percentages, loading states, or step counters
- Do NOT mention AI tools, models, or services"""
            
            location_context = f"{location}, {country}" if location and country else (location or country or "General")
            
            user_prompt = f"""Transform the following raw Tavily research data into a well-structured markdown section for a potato disease diagnostic report.

CONTEXT:
- Disease: {disease_name}
- Location: {location_context}

RAW TAVILY DATA (JSON):
{raw_content_text}

Create a structured markdown section titled "📚 Location-Specific Research & Treatment References" that includes:

1. **Historical Outbreak Analysis** (if available):
   - For each historical outbreak, clearly state:
     * **Outbreak Date**: When it occurred (e.g., "November 2023", "Winter 2022")
     * **Historical Weather Conditions**: Temperature, humidity, rainfall during the outbreak
     * **Summary**: Clear, professional sentences summarizing the outbreak and its conditions
   - Write in clear, professional sentences (not bullet points for the descriptions)
   - Highlight the most recent outbreaks first
   - Make sentences flow naturally and be grammatically correct

2. **Treatment & Management Recommendations**:
   - Actionable treatment recommendations
   - Specific fungicides/products if mentioned
   - Application methods and timing
   - Dosage information if available

3. **Preventive Measures**:
   - Cultural practices to prevent recurrence
   - Preventive treatments
   - Field management tips

4. **References** (as clickable links):
   - Format as: [Source Name – Article Title](URL)
   - Extract meaningful source names from URLs
   - List all sources at the end

Requirements:
- Use proper markdown formatting (##, ###, **bold**, *italic*)
- Make ALL links clickable markdown format: [Text](URL)
- Remove copyright notices, citation metadata, redundant text
- Keep technical details but make them concise
- Use bullet points for lists
- Add clear section separators (---)
- Ensure professional, readable formatting

Respond ONLY with the formatted markdown section - no additional text or explanations."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm.invoke(messages)
            formatted_section = response.content.strip()
            
            # Debug: Log raw formatted section
            print(f"[TAVILY_DEBUG] Raw formatted section length: {len(formatted_section)} chars")
            print(f"[TAVILY_DEBUG] Raw formatted preview: {formatted_section[:300]}...")
            
            # Clean up any markdown code blocks if present
            if formatted_section.startswith("```"):
                if "```markdown" in formatted_section:
                    formatted_section = formatted_section.split("```markdown")[1].split("```")[0].strip()
                elif "```" in formatted_section:
                    formatted_section = formatted_section.split("```")[1].split("```")[0].strip()
            
            # Post-process: Remove unwanted markdown headers at the start and AI references
            import re
            
            # Remove leading markdown headers (but keep section headers inside)
            # Only remove if they're at the very start of the document
            formatted_section = re.sub(r'^#+\s*📚\s*Location-Specific', '## 📚 Location-Specific', formatted_section, flags=re.MULTILINE)
            formatted_section = re.sub(r'^#+\s*Location-Specific', '## 📚 Location-Specific', formatted_section, flags=re.MULTILINE)
            
            # Remove duplicate section headers
            # Count occurrences of "Location-Specific Research"
            location_header_count = len(re.findall(r'##\s*📚\s*Location-Specific', formatted_section, re.IGNORECASE))
            if location_header_count > 1:
                print(f"[TAVILY_DEBUG] Found {location_header_count} duplicate Location-Specific headers, removing duplicates")
                # Keep only the first occurrence
                parts = re.split(r'##\s*📚\s*Location-Specific', formatted_section, flags=re.IGNORECASE)
                if len(parts) > 1:
                    formatted_section = '## 📚 Location-Specific Research & Treatment References' + parts[1]
            
            # Remove AI service references
            formatted_section = re.sub(r'\b(ChatGPT|OpenAI|ChatOpenAI|chatopen ai|AI assistant|AI model|generated by|created by AI|powered by AI)\b', '', formatted_section, flags=re.IGNORECASE)
            
            # Remove standalone markdown headers that shouldn't be there (like "## 🌿 Key Environmental Observations" if it appears)
            # But preserve legitimate section headers
            # This is tricky - we want to keep section structure but remove unwanted headers
            
            # Clean up extra whitespace
            formatted_section = re.sub(r'\n{3,}', '\n\n', formatted_section)
            formatted_section = formatted_section.strip()
            
            # Debug: Log cleaned section
            print(f"[TAVILY_DEBUG] Cleaned formatted section length: {len(formatted_section)} chars")
            print(f"[TAVILY_DEBUG] Cleaned formatted preview: {formatted_section[:300]}...")
            
            return formatted_section
            
        except Exception as e:
            print(f"[WARNING] Failed to format Tavily section: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to basic formatting
            return self._format_tavily_section_fallback(tavily_data, disease_name)
    
    def _format_tavily_section_fallback(self, tavily_data: Dict[str, Any], disease_name: str) -> str:
        """
        Fallback formatting if OpenAI formatting fails.
        Creates basic structured output with clickable markdown links.
        """
        if not tavily_data:
            return ""
        
        section = "\n## 📚 Location-Specific Research & Treatment References\n\n"
        
        # Historical Context with Weather Data
        if tavily_data.get("historical_context"):
            section += "### Historical Outbreak Analysis\n\n"
            for hist in tavily_data["historical_context"]:
                title = hist.get("title", "Historical Data")
                outbreak_date = hist.get("outbreak_date", "")
                historical_weather = hist.get("historical_weather", {})
                summary = hist.get("summary", hist.get("content", ""))
                url = hist.get("url") or hist.get("original_url", "")
                source_name = hist.get("source_name", "")
                
                # Format outbreak with date
                if outbreak_date:
                    section += f"**Historical Outbreak - {outbreak_date}:**\n\n"
                
                # Historical weather conditions
                if historical_weather:
                    section += "**Historical Weather Conditions:**\n"
                    if historical_weather.get("temperature"):
                        section += f"- Temperature: {historical_weather.get('temperature')}\n"
                    if historical_weather.get("humidity"):
                        section += f"- Humidity: {historical_weather.get('humidity')}\n"
                    if historical_weather.get("rainfall"):
                        section += f"- Rainfall: {historical_weather.get('rainfall')}\n"
                    section += "\n"
                
                # Summary (clear sentences)
                if summary:
                    section += f"{summary}\n\n"
                
                # Source link
                if url:
                    if source_name:
                        link_text = f"{source_name} – {title}"
                    else:
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(url).netloc.replace("www.", "")
                            link_text = domain if domain else title
                        except:
                            link_text = title
                    section += f"Source: [{link_text}]({url})\n\n"
                
                section += "---\n\n"
        
        # Recommendations
        if tavily_data.get("recommendations"):
            section += "### Treatment & Management Recommendations\n\n"
            for rec in tavily_data["recommendations"]:
                title = rec.get("title", "Recommendation")
                summary = rec.get("summary", rec.get("content", ""))
                url = rec.get("url") or rec.get("original_url", "")
                source_name = rec.get("source_name", "")
                
                if summary:
                    section += f"- {summary}\n"
                if url:
                    if source_name:
                        link_text = f"{source_name} – {title}"
                    else:
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(url).netloc.replace("www.", "")
                            link_text = domain if domain else title
                        except:
                            link_text = title
                    section += f"  Source: [{link_text}]({url})\n"
            section += "\n"
        
        # Preventive Measures
        if tavily_data.get("preventive_measures"):
            section += "### Preventive Measures\n\n"
            for prev in tavily_data["preventive_measures"]:
                title = prev.get("title", "Prevention")
                summary = prev.get("summary", prev.get("content", ""))
                url = prev.get("url") or prev.get("original_url", "")
                source_name = prev.get("source_name", "")
                
                if summary:
                    section += f"- {summary}\n"
                if url:
                    if source_name:
                        link_text = f"{source_name} – {title}"
                    else:
                        try:
                            from urllib.parse import urlparse
                            domain = urlparse(url).netloc.replace("www.", "")
                            link_text = domain if domain else title
                        except:
                            link_text = title
                    section += f"  Source: [{link_text}]({url})\n"
            section += "\n"
        
        return section
    
    def identify_disease(self, state: AgentState) -> AgentState:
        """
        Analyze potato leaf image to identify diseases.
        Handles images from camera or file uploads.
        """
        image_data = state.get("image_data")
        
        if not image_data:
            state["disease_identification"] = {
                "error": "No image data provided",
                "user_message": "Please upload an image of a potato leaf."
            }
            state["final_report"] = "I need an image to diagnose potato diseases. Please upload a photo of your potato plant."
            return state
        
        # Convert image_data (bytes) to base64 string
        if isinstance(image_data, bytes):
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        elif isinstance(image_data, str):
            # Handle if already base64 or data URL
            if image_data.startswith('data:image'):
                image_base64 = image_data.split(',')[1]
            else:
                image_base64 = image_data
        else:
            state["disease_identification"] = {
                "error": "Invalid image format",
                "user_message": "Unable to process image. Please try again."
            }
            state["final_report"] = "I couldn't process the image. Please try uploading a different image."
            return state
        
        print("🌐 Processing uploaded image...")
        
        # Decode and validate base64 image
        try:
            image_bytes = base64.b64decode(image_base64)
            print(f"✅ Decoded image: {len(image_bytes)} bytes ({len(image_bytes) / 1024:.1f} KB)")
        except Exception as e:
            state["disease_identification"] = {
                "error": f"Invalid image data: {str(e)}",
                "user_message": "The uploaded file appears to be corrupted. Please try uploading again."
            }
            state["final_report"] = "The image file appears to be corrupted. Please try uploading again."
            return state
        
        # Validate and optimize image
        try:
            img = Image.open(io.BytesIO(image_bytes))
            
            # Get image info
            original_format = img.format
            original_size = img.size
            original_mode = img.mode
            
            print(f"📊 Original: {original_format}, {original_size}, {original_mode}")
            
            # Check if image is valid
            if original_size[0] < 100 or original_size[1] < 100:
                state["disease_identification"] = {
                    "error": "Image too small",
                    "user_message": "Please upload a larger image (at least 100x100 pixels) for accurate analysis."
                }
                state["final_report"] = "The image is too small. Please upload a larger image (at least 100x100 pixels) for accurate analysis."
                return state
            
            # Auto-fix orientation from EXIF (common with mobile uploads)
            try:
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
                print("✅ Fixed orientation from EXIF")
            except Exception:
                pass
            
            # Optimize image size for API
            MAX_SIZE = 2000  # Good balance between quality and API limits
            if max(img.size) > MAX_SIZE:
                ratio = MAX_SIZE / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"🔄 Resized: {original_size} → {new_size}")
            
            # Convert to RGB (handles PNG with transparency, CMYK, etc.)
            if img.mode not in ('RGB', 'L'):
                # Preserve transparency by adding white background
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                else:
                    img = img.convert('RGB')
                print(f"🔄 Converted to RGB")
            
            # Re-encode as optimized JPEG
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=90, optimize=True)
            optimized_bytes = buffer.getvalue()
            optimized_base64 = base64.b64encode(optimized_bytes).decode('utf-8')
            
            compression_ratio = (1 - len(optimized_bytes) / len(image_bytes)) * 100
            print(f"✅ Optimized: {len(optimized_bytes) / 1024:.1f} KB (saved {compression_ratio:.1f}%)")
            
        except Exception as e:
            state["disease_identification"] = {
                "error": f"Image processing failed: {str(e)}",
                "user_message": "Unable to process this image file. Please ensure it's a valid image format (JPG, PNG, etc.)."
            }
            state["final_report"] = f"Unable to process this image file. Please ensure it's a valid image format (JPG, PNG, etc.)."
            return state
        
        # Professional prompt optimized for web uploads
        system_prompt = """You are an expert plant pathologist specializing in potato disease diagnosis. 
You analyze images uploaded by farmers and gardeners to help them identify and treat potato leaf diseases.

STREAMING BEHAVIOR:
Analyze the image step-by-step and communicate what you're doing naturally. Do not mention progress, loading, or percentages. Instead, describe what you're observing in conversational language like "Analyzing the image for disease symptoms..." or "Identifying disease characteristics...". Stream your outputs in stages as you complete each subtask, with each section being complete and self-contained.

**Your Analysis Process:**

1. **Examine the image carefully** for:
   - Leaf color and uniformity
   - Presence of spots, lesions, or discoloration
   - Pattern and distribution of symptoms
   - Overall leaf health

2. **Classify into ONE category**:
   - **"Early Blight"** 
     • Dark brown/black spots with concentric rings (bull's-eye/target pattern)
     • Yellow halo around spots
     • Usually starts on older, lower leaves
     • Spots may have dry, papery texture
   
   - **"Late Blight"**
     • Irregular water-soaked lesions
     • Brown to purplish-black spots
     • White fuzzy mold on leaf undersides (in humid conditions)
     • Rapid spread, can affect entire plant
     • May see greasy or wet appearance
   
   - **"Healthy"**
     • Uniform green color
     • No spots, lesions, or abnormal discoloration
     • Good leaf structure and texture
   
   - **"Unclear/Poor Image"**
     • Image too blurry, dark, or distant to diagnose
     • Leaf not clearly visible
     • Need better photo

3. **Respond in this EXACT JSON format**:

{
    "disease_type": "Early Blight" | "Late Blight" | "Healthy" | "Unclear/Poor Image",
    "confidence": "high" | "medium" | "low",
    "confidence_percentage": 85,
    "summary": "Clear description of what you observe in the image",
    "key_visual_indicators": [
        "Specific feature 1 you can see",
        "Specific feature 2 you can see"
    ],
    "severity": "none" | "mild" | "moderate" | "severe",
    "recommendations": "Specific actionable advice for the user",
    "requires_better_photo": false,
    "photo_improvement_tips": "Optional: how to take a better photo if needed"
}

**Important Guidelines:**
- Be honest about image quality - if you can't see clearly, say so
- Provide specific observations, not generic descriptions
- Give practical, actionable recommendations
- If uncertain, explain what additional information would help
- Consider that users may be beginners - explain in accessible language"""

        user_prompt = """Please analyze this potato leaf image and provide a detailed disease assessment.
Focus on specific visual features you can observe.

Respond ONLY with valid JSON in the exact format specified - no additional text."""

        # Prepare API messages
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{optimized_base64}",
                            "detail": "high"  # Use high detail for accurate diagnosis
                        }
                    }
                ]
            }
        ]
        
        # Call OpenAI API
        try:
            print("🤖 Analyzing image with AI...")
            response = self.llm.invoke(messages)
            result_text = response.content.strip()
            print(f"✅ Analysis complete")
            
            # Parse JSON response
            try:
                # Clean up response (remove markdown if present)
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()
                
                result = json.loads(result_text)
                
                # Add metadata for frontend
                result["analysis_timestamp"] = datetime.now().isoformat()
                result["image_dimensions"] = f"{img.size[0]}x{img.size[1]}"
                result["model_version"] = "gpt-4o-mini"
                
                # Ensure all expected fields exist
                required_fields = ["disease_type", "confidence", "summary", "recommendations"]
                for field in required_fields:
                    if field not in result:
                        result[field] = "Not available"
                
                # Get Tavily recommendations if disease is identified
                disease_type = result.get('disease_type', '')
                tavily_data = {}
                if disease_type and disease_type not in ["Healthy", "Unclear/Poor Image"]:
                    # Try to get location and country from state if available
                    location = None
                    country = None
                    user_profile = state.get("user_profile", {})
                    if user_profile:
                        fields = user_profile.get("fields", [])
                        if fields:
                            # Use first field's location directly (same as streaming version)
                            current_field = fields[0]
                            location = current_field.get("location", "")
                            # Detect country from location
                            if location:
                                location_lower = location.lower()
                                if any(indicator in location_lower for indicator in ["uk", "united kingdom", "britain", "england", "scotland", "wales"]):
                                    country = "UK"
                                else:
                                    country = "India"
                    
                    print(f"[INFO] Fetching Tavily recommendations for {disease_type}...")
                    tavily_data = self._get_tavily_recommendations(disease_type, location, country)
                    result["tavily_data"] = tavily_data
                
                # Store in state
                state["disease_identification"] = result
                
                # Generate user-friendly report
                report = f"🔍 **Disease Analysis Complete**\n\n"
                report += f"**Disease Type:** {result.get('disease_type', 'Unknown')}\n"
                report += f"**Confidence:** {result.get('confidence_percentage', result.get('confidence', 'N/A'))}% ({result.get('confidence', 'medium')})\n"
                report += f"**Severity:** {result.get('severity', 'unknown').title()}\n\n"
                report += f"**Summary:**\n{result.get('summary', 'No summary available')}\n\n"
                
                if result.get('key_visual_indicators'):
                    report += f"**Key Visual Indicators:**\n"
                    for indicator in result['key_visual_indicators']:
                        report += f"• {indicator}\n"
                    report += "\n"
                
                # Base recommendations from AI
                report += f"**Recommendations:**\n{result.get('recommendations', 'No recommendations available')}\n"
                
                # Add Tavily-enhanced recommendations with structured formatting
                if tavily_data and any(tavily_data.values()):
                    # Use OpenAI to format Tavily section into structured markdown
                    tavily_section = self._format_tavily_section(
                        tavily_data=tavily_data,
                        disease_name=disease_type,
                        location=location,
                        country=country
                    )
                    
                    if tavily_section:
                        report += "\n\n" + tavily_section + "\n"
                    else:
                        # Fallback formatting
                        report += "\n\n## 📚 Location-Specific Research & Treatment References\n\n"
                        report += f"*Research-based recommendations for {disease_type} are available.*\n\n"
                
                if result.get('requires_better_photo'):
                    report += f"\n**Note:** {result.get('photo_improvement_tips', 'A better photo would help improve diagnosis accuracy.')}\n"
                
                state["final_report"] = report
                
                # Note: Character-by-character streaming will be handled in the streaming method
                
                return state
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error: {e}")
                print(f"Raw response: {result_text[:200]}...")
                
                # Graceful fallback
                state["disease_identification"] = {
                    "disease_type": "Analysis Incomplete",
                    "confidence": "low",
                    "summary": result_text,
                    "recommendations": "Please try uploading the image again.",
                    "error_note": "Response format error",
                    "raw_response": result_text[:500]
                }
                state["final_report"] = f"I analyzed the image but encountered an issue formatting the response. Here's what I found:\n\n{result_text[:500]}"
                return state
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ API Error: {error_msg}")
            
            # User-friendly error messages
            if "rate_limit" in error_msg.lower():
                user_message = "Too many requests. Please wait a moment and try again."
            elif "invalid_api_key" in error_msg.lower():
                user_message = "Service configuration error. Please contact support."
            elif "timeout" in error_msg.lower():
                user_message = "Analysis timed out. Please try again."
            else:
                user_message = "Unable to analyze image. Please try again."
            
            state["disease_identification"] = {
                "error": error_msg,
                "user_message": user_message,
                "retry_allowed": True
            }
            state["final_report"] = user_message
            return state
    
    def identify_disease_streaming(self, state: AgentState) -> Generator[Dict[str, Any], None, None]:
        """
        Stream disease identification with natural language status updates.
        Yields status updates for frontend streaming without progress bars or percentages.
        """
        yield {"type": "status", "message": "Processing uploaded image...", "stage": "image_processing"}
        
        # Process image (same as above but yield updates)
        image_data = state.get("image_data")
        if not image_data:
            yield {"type": "error", "message": "No image data provided"}
            return
        
        # Convert and optimize image
        try:
            if isinstance(image_data, bytes):
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            elif isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    image_base64 = image_data.split(',')[1]
                else:
                    image_base64 = image_data
            else:
                yield {"type": "error", "message": "Invalid image format"}
                return
            
            yield {"type": "status", "message": "Preparing image for analysis...", "stage": "image_optimization"}
            
            image_bytes = base64.b64decode(image_base64)
            img = Image.open(io.BytesIO(image_bytes))
            
            # Optimize
            MAX_SIZE = 2000
            if max(img.size) > MAX_SIZE:
                ratio = MAX_SIZE / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            if img.mode not in ('RGB', 'L'):
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                else:
                    img = img.convert('RGB')
            
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=90, optimize=True)
            optimized_bytes = buffer.getvalue()
            optimized_base64 = base64.b64encode(optimized_bytes).decode('utf-8')
            
            yield {"type": "status", "message": "Analyzing the image for disease symptoms...", "stage": "ai_analysis"}
            
            # Stream engaging message during AI analysis (non-streaming operation)
            from src.utils.streaming_helpers import stream_engaging_message
            for msg_event in stream_engaging_message(
                "ai_analysis",
                "analyzing image with AI vision",
                {},
                delay=0.015
            ):
                yield msg_event
            
            # Call AI
            system_prompt = """You are an expert plant pathologist specializing in potato disease diagnosis.

STREAMING BEHAVIOR:
Analyze the image step-by-step and communicate what you're doing naturally. Do not mention progress, loading, or percentages. Instead, describe what you're observing in conversational language like "Analyzing the image for disease symptoms..." or "Identifying disease characteristics...". Stream your outputs in stages as you complete each subtask, with each section being complete and self-contained. 
Analyze the image and respond in JSON format:
{
    "disease_type": "Early Blight" | "Late Blight" | "Healthy" | "Unclear/Poor Image",
    "confidence": "high" | "medium" | "low",
    "confidence_percentage": 85,
    "summary": "Description",
    "key_visual_indicators": ["feature1", "feature2"],
    "severity": "none" | "mild" | "moderate" | "severe",
    "recommendations": "Actionable advice"
}"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this potato leaf image. Respond ONLY with valid JSON."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{optimized_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            
            response = self.llm.invoke(messages)
            result_text = response.content.strip()
            
            # Parse JSON
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            result["analysis_timestamp"] = datetime.now().isoformat()
            result["image_dimensions"] = f"{img.size[0]}x{img.size[1]}"
            
            # Get disease name for Tavily search
            disease_type = result.get("disease_type", "")
            
            # If disease identified, fetch Tavily recommendations
            if disease_type and disease_type not in ["Healthy", "Unclear/Poor Image"]:
                yield {"type": "status", "message": "Gathering location-specific treatment recommendations...", "stage": "tavily_search"}
                
                # Stream engaging message during Tavily search
                for msg_event in stream_engaging_message(
                    "tavily_search",
                    "searching treatment recommendations",
                    {"disease": disease_type},
                    delay=0.015
                ):
                    yield msg_event
                
                # Get location from state if available
                user_profile = state.get("user_profile", {})
                fields = user_profile.get("fields", [])
                location = None
                country = None
                if fields:
                    current_field = fields[0]
                    location = current_field.get("location", "")
                    # Detect country from location
                    if location:
                        location_lower = location.lower()
                        if any(indicator in location_lower for indicator in ["uk", "united kingdom", "britain", "england", "scotland", "wales"]):
                            country = "UK"
                        else:
                            country = "India"
                
                tavily_data = self._get_tavily_recommendations(disease_type, location, country)
                
                if tavily_data and any(tavily_data.values()):
                    yield {"type": "status", "message": "Formatting treatment recommendations and historical context...", "stage": "formatting_recommendations"}
                    
                    # Format Tavily section
                    tavily_section = self._format_tavily_section(tavily_data, disease_type, location, country)
                    if tavily_section:
                        result["tavily_recommendations"] = tavily_section
                        # Stream Tavily section character-by-character
                        from src.utils.streaming_helpers import stream_text_character_by_character
                        for char_event in stream_text_character_by_character(tavily_section, chunk_size=2, delay=0.01, event_type="stream_char"):
                            yield char_event
            
            # Generate final report
            report = f"🔍 **Disease Analysis Complete**\n\n"
            report += f"**Disease Type:** {result.get('disease_type', 'Unknown')}\n"
            report += f"**Confidence:** {result.get('confidence_percentage', result.get('confidence', 'N/A'))}% ({result.get('confidence', 'medium')})\n"
            report += f"**Severity:** {result.get('severity', 'unknown').title()}\n\n"
            report += f"**Summary:**\n{result.get('summary', 'No summary available')}\n\n"
            
            if result.get('key_visual_indicators'):
                report += f"**Key Visual Indicators:**\n"
                for indicator in result['key_visual_indicators']:
                    report += f"• {indicator}\n"
                report += "\n"
            
            report += f"**Recommendations:**\n{result.get('recommendations', 'No recommendations available')}\n"
            
            # Stream final report character-by-character
            from src.utils.streaming_helpers import stream_text_character_by_character
            yield {"type": "status", "message": "Generating comprehensive diagnosis report...", "stage": "final_report"}
            for char_event in stream_text_character_by_character(report, chunk_size=2, delay=0.01, event_type="stream_char"):
                yield char_event
            
            yield {"type": "status", "message": "Diagnosis complete!", "stage": "complete"}
            yield {"type": "result", "data": result, "report": report}
            
        except Exception as e:
            yield {"type": "error", "message": str(e)}
