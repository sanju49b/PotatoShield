# src/agents/general_chat_agent.py
from langchain_openai import ChatOpenAI
from src.state.agent_state import AgentState
from typing import Dict, Optional
import re
import os

class GeneralChatAgent:
    """
    General conversational agent that handles non-disease-related queries.
    Maintains conversation context and provides friendly, helpful responses.
    Includes multi-language translation support for Telugu, Hindi, and Tamil.
    """
    
    def __init__(self, long_memory=None):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        # Use gpt-4o-mini for translations (fast and cost-effective)
        self.translation_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        self.long_memory = long_memory
        self.enable_translations = os.getenv("ENABLE_TRANSLATIONS", "true").lower() == "true"
    
    def chat(self, state: AgentState) -> AgentState:
        """
        Generate a conversational response with full context awareness.
        Can also handle state updates like changing location or sowing date.
        Detects language preference and translates accordingly.
        """
        user_input = state["user_input"]
        user_profile = state["user_profile"]
        conversation_messages = state["conversation"].get("messages", [])
        user_id = user_profile.get("user_id")
        
        # Respect UI-selected preferred language (if provided via workflow state)
        requested_languages = []
        preferred_language = state.get("preferred_language")
        if preferred_language:
            if isinstance(preferred_language, list):
                requested_languages = preferred_language
            else:
                requested_languages = [preferred_language]
        else:
            # Detect language preference from user input when no override exists
            requested_languages = self._detect_language_preference(user_input)
        
        # Check if user has a stored language preference
        user_language_preference = user_profile.get("language_preference", None)
        
        # If no language preference detected in current input, use stored preference
        if not requested_languages and user_language_preference:
            requested_languages = user_language_preference if isinstance(user_language_preference, list) else [user_language_preference]
            print(f"[LANGUAGE] Using stored language preference: {requested_languages}")
        
        # Store detected language preference for future use in user profile
        if requested_languages and requested_languages != user_language_preference:
            user_profile["language_preference"] = requested_languages
            # Persist language preference to database if long_memory available
            if self.long_memory and hasattr(self.long_memory, 'db'):
                try:
                    user_id = user_profile.get("user_id")
                    if user_id and hasattr(self.long_memory.db, 'update_user_language_preference'):
                        self.long_memory.db.update_user_language_preference(user_id, requested_languages)
                        print(f"[LANGUAGE] Saved language preference to DB: {requested_languages}")
                except Exception as e:
                    print(f"[LANGUAGE] Could not save language preference to DB: {e}")
        
        # Check if user wants to update field information
        update_result = self._check_and_update_field(user_input, user_profile, user_id)
        
        # Build conversation history for context
        conversation_context = ""
        if conversation_messages:
            # Format last 10 messages for context
            for msg in conversation_messages[-10:]:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                conversation_context += f"{role}: {content}\n"
        
        # Get user's field info for context (after potential update)
        fields = user_profile.get('fields', [])
        field_info = ""
        field_id = None
        if fields:
            field = fields[0]
            location = field.get('location', 'Not set')
            sowing_date = field.get('sowing_date', 'Not set')
            field_id = field.get('field_id')
            field_info = f"\nUser's field information:\n- Location: {location}\n- Sowing Date: {sowing_date}"
        
        # Build prompt with full context
        update_context = ""
        if update_result:
            if update_result.get("updated"):
                update_context = f"\n[SYSTEM: Field information has been updated. {update_result.get('message', '')}]"
            elif update_result.get("needs_clarification"):
                update_context = f"\n[SYSTEM: User wants to update field information but needs clarification: {update_result.get('message', '')}]"
        
        # Add language preference context
        language_context = ""
        is_early_conversation = len(conversation_messages) <= 1  # First message or two
        if False and not requested_languages and not user_language_preference and is_early_conversation:
            # Early in conversation and no stored preference - offer language selection
            language_context = "\n[CRITICAL: The user has NO language preference set. You MUST ask them about their preferred language.\n\nAfter responding to their query, you MUST include this exact prompt:\n\n'🌐 **Language Preference**\nWould you like to receive responses in your preferred language? I can respond in:\n• English\n• తెలుగు (Telugu)\n• हिंदी (Hindi)  \n• தమிழ் (Tamil)\n\nJust tell me which language you prefer, and all future responses will be in that language! (You can also say \"English\" to continue in English)'\n\nThis is REQUIRED.]"
        
        prompt = f"""You are a friendly, helpful agricultural assistant for Potato Shield, an AI-powered potato disease management system. You help farmers with potato farming questions, general conversation, and provide context-aware responses.

CONVERSATION HISTORY:
{conversation_context if conversation_context else "No previous conversation"}

USER'S CURRENT MESSAGE: {user_input}
{field_info}
{update_context}
{language_context}

INSTRUCTIONS:
1. Be friendly, conversational, and helpful
2. Maintain context from the conversation history - reference previous messages when relevant
3. If the user asks about potato farming, agriculture, or related topics, provide helpful information
4. If the user greets you or thanks you, respond naturally and warmly
5. If the conversation is about disease prediction/diagnosis, briefly acknowledge but remind them they can use the predictive or diagnostic features
6. Keep responses concise but informative (2-4 sentences for general chat, longer if explaining concepts)
7. Use the field information if relevant to the conversation
8. If the user asks about their location or sowing date, answer directly using the field information above
9. If field information was just updated, acknowledge it naturally in your response
10. If instructed about language preference in the SYSTEM context above, you MUST include the language preference prompt EXACTLY as provided
11. If user has selected a language preference (Telugu/Hindi/Tamil), acknowledge it warmly and confirm all future responses will be in that language

Generate a natural, contextual response:"""
        
        response = self.llm.invoke(prompt)
        english_response = response.content
        
        # If no language preference and early in conversation, APPEND the language selection prompt
        # This ensures it shows even if LLM doesn't follow instructions
        # Use same variable as defined earlier
        if False and not requested_languages and not user_language_preference and is_early_conversation:
            english_response += "\n\n🌐 **Language Preference**\nWould you like to receive responses in your preferred language? I can respond in:\n• English\n• తెలుగు (Telugu)\n• हिंदी (Hindi)\n• தமிழ் (Tamil)\n\nJust tell me which language you prefer, and all future responses will be in that language!"
        
        # Determine primary language for response
        # If user has a stored language preference (not requesting new one), use it as PRIMARY
        primary_language = None
        show_english_secondary = False
        
        if user_language_preference and not requested_languages:
            # User has a stored preference - use it as primary language
            primary_language = user_language_preference if isinstance(user_language_preference, list) else [user_language_preference]
            if primary_language and primary_language[0] != "english":
                show_english_secondary = True  # Show English as reference
                print(f"[LANGUAGE] Using stored preference as primary: {primary_language}")
        elif requested_languages:
            # User just selected a language - treat as primary for next responses
            primary_language = requested_languages
            if primary_language and primary_language[0] != "english":
                show_english_secondary = True
                print(f"[LANGUAGE] Language just selected: {primary_language}")
        
        # Generate translations based on primary language
        translations = {}
        primary_response = english_response  # Default to English
        
        if self.enable_translations and primary_language and primary_language[0] != "english":
            try:
                # Generate the PRIMARY language version
                translations = self._translate_response(english_response, primary_language)
                
                # Set the PRIMARY response to the user's language
                if primary_language[0] in translations and translations[primary_language[0]]:
                    primary_response = translations[primary_language[0]]
                    # If showing English as secondary, add it to translations
                    if show_english_secondary:
                        translations["english"] = english_response
                    print(f"[LANGUAGE] Primary response set to: {primary_language[0]}")
                else:
                    # Translation failed, fall back to English
                    print(f"[LANGUAGE] Translation failed, using English")
                    primary_response = english_response
                    
            except Exception as e:
                print(f"[TRANSLATION] Error generating translations: {e}")
                # Fall back to English on error
                primary_response = english_response
                translations = {lang: None for lang in primary_language}
                translations["error"] = str(e)
        
        # Store response in state (primary language version)
        state["final_report"] = primary_response
        state["translations"] = translations
        state["requested_languages"] = primary_language if primary_language else []
        state["primary_language"] = primary_language[0] if primary_language else "english"
        state["show_english_secondary"] = show_english_secondary
        state["selected_agent"] = "general_chat"
        
        # Add language selection UI metadata if user has no preference
        state["show_language_selector"] = False
        state["available_languages"] = []
        
        # Update field info in state if it was updated
        if update_result and update_result.get("updated") and fields:
            fields[0].update(update_result.get("updates", {}))
        
        return state
    
    def _check_and_update_field(self, user_input: str, user_profile: Dict, user_id: str) -> Optional[Dict]:
        """
        Check if user wants to update field information and update it if possible.
        Returns dict with update status and message.
        """
        if not self.long_memory:
            return None
        
        user_input_lower = user_input.lower()
        fields = user_profile.get('fields', [])
        
        if not fields:
            return None
        
        field = fields[0]
        field_id = field.get('field_id')
        
        # Check for location update requests
        location_update_keywords = [
            'change location', 'update location', 'set location', 'new location',
            'change my location', 'update my location', 'set my location',
            'location is', 'location to', 'location should be', 'location will be'
        ]
        
        # Check for sowing date update requests
        dos_update_keywords = [
            'change sowing date', 'update sowing date', 'set sowing date', 'new sowing date',
            'change dos', 'update dos', 'set dos',
            'sowing date is', 'sowing date to', 'sowing date should be', 'planted on',
            'planted', 'sowed on', 'sowing on'
        ]
        
        wants_location_update = any(keyword in user_input_lower for keyword in location_update_keywords)
        wants_dos_update = any(keyword in user_input_lower for keyword in dos_update_keywords)
        
        location_to_update = None
        dos_to_update = None
        
        # Try to extract location from user input
        if wants_location_update:
            # Look for location patterns: "location is [X]", "location to [X]", "set location [X]"
            location_patterns = [
                r'location (?:is|to|should be|will be)\s+([^,\.\?\!]+)',
                r'set location\s+([^,\.\?\!]+)',
                r'change location (?:to|is)\s+([^,\.\?\!]+)',
                r'update location (?:to|is)\s+([^,\.\?\!]+)',
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    location_to_update = match.group(1).strip()
                    break
        
        # Try to extract sowing date from user input
        if wants_dos_update:
            # Look for date patterns: "sowing date is [X]", "planted on [X]", dates like "2024-01-15" or "January 15, 2024"
            date_patterns = [
                r'sowing date (?:is|to|should be|will be)\s+([^,\.\?\!]+)',
                r'planted on\s+([^,\.\?\!]+)',
                r'sowed on\s+([^,\.\?\!]+)',
                r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD format
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    dos_to_update = match.group(1).strip()
                    # Try to normalize date format
                    try:
                        from datetime import datetime
                        # Try parsing various date formats
                        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y', '%B %d, %Y', '%b %d, %Y']:
                            try:
                                date_obj = datetime.strptime(dos_to_update, fmt)
                                dos_to_update = date_obj.strftime('%Y-%m-%d')
                                break
                            except:
                                continue
                    except:
                        pass
                    break
        
        # Update if we have values
        if location_to_update or dos_to_update:
            try:
                # Use DynamoDB service to update
                if hasattr(self.long_memory, 'db') and hasattr(self.long_memory.db, 'update_field'):
                    success = self.long_memory.db.update_field(
                        field_id=field_id,
                        location=location_to_update,
                        sowing_date=dos_to_update
                    )
                    
                    if success:
                        updates = {}
                        if location_to_update:
                            updates['location'] = location_to_update
                        if dos_to_update:
                            updates['sowing_date'] = dos_to_update
                        
                        return {
                            "updated": True,
                            "message": f"Field information updated successfully.",
                            "updates": updates
                        }
                else:
                    # Fallback: try to update via long_memory if method exists
                    return {
                        "updated": False,
                        "needs_clarification": True,
                        "message": "I understood you want to update your field information, but I need a bit more detail. Could you please specify the exact location or date?"
                    }
            except Exception as e:
                print(f"Error updating field: {e}")
                return {
                    "updated": False,
                    "message": f"Sorry, I encountered an error updating your field information. Please try again."
                }
        
        # If user wants to update but we couldn't extract values
        if wants_location_update or wants_dos_update:
            return {
                "updated": False,
                "needs_clarification": True,
                "message": "I'd be happy to update your field information! Could you please provide the specific location or sowing date you'd like to set?"
            }
        
        return None
    
    def _detect_language_preference(self, user_input: str) -> list:
        """
        Detect if user wants response in a specific language.
        Returns list of requested languages.
        """
        user_input_lower = user_input.lower()
        requested_languages = []
        
        # Language detection patterns
        language_keywords = {
            "telugu": ["telugu", "telgu", "తెలుగు", "in telugu", "తెలుగులో"],
            "hindi": ["hindi", "हिंदी", "in hindi", "हिंदी में"],
            "tamil": ["tamil", "தமிழ்", "in tamil", "தமிழில்"],
            "english": ["english", "in english"]  # Also support explicit English selection
        }
        
        # Check for explicit language requests
        for lang, keywords in language_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                if lang != "english":  # Don't add English to translation list (it's default)
                    requested_languages.append(lang)
        
        # Check for phrases like "translate to", "respond in", "answer in", "I want", "prefer"
        translation_phrases = [
            r'(?:translate|respond|answer|reply|give|show|i\s+want|prefer|choose|select)\s+(?:in|to|it\s+in)?\s*(telugu|hindi|tamil)',
            r'(telugu|hindi|tamil)\s+(?:translation|version|language|please|response)',
            r'(?:also\s+in|include|both\s+in)\s+(telugu|hindi|tamil)',
            r'(?:want|need|like)\s+(?:response|answer|reply)?\s*(?:in)?\s+(telugu|hindi|tamil)',
        ]
        
        for pattern in translation_phrases:
            matches = re.findall(pattern, user_input_lower)
            for match in matches:
                lang = match.strip()
                if lang in language_keywords and lang not in requested_languages:
                    requested_languages.append(lang)
        
        # Check for simple selections like "telugu", "hindi", "tamil" as standalone words
        # This handles cases where user just clicks a language button/option
        words = user_input_lower.split()
        for word in words:
            word_clean = word.strip('.,!?;:')
            if word_clean in ["telugu", "hindi", "tamil"] and word_clean not in requested_languages:
                requested_languages.append(word_clean)
        
        # Log detected languages
        if requested_languages:
            print(f"[LANGUAGE DETECTION] User requested: {', '.join(requested_languages)}")
        
        return requested_languages
    
    def _translate_response(self, english_text: str, target_languages: list = None) -> Dict[str, str]:
        """
        Translate the English response into requested languages using OpenAI.
        Args:
            english_text: The English text to translate
            target_languages: List of language codes to translate to (e.g., ["telugu", "hindi"])
        Returns:
            Dictionary with translations for each requested language
        """
        translations = {}
        
        # Define all available languages with their native names
        all_languages = {
            "telugu": "Telugu (తెలుగు)",
            "hindi": "Hindi (हिंदी)",
            "tamil": "Tamil (தமிழ்)"
        }
        
        # If no specific languages requested, return empty dict
        if not target_languages:
            return translations
        
        # Only translate to requested languages
        languages_to_translate = {
            lang: all_languages[lang] 
            for lang in target_languages 
            if lang in all_languages
        }
        
        # Translate to each requested language
        for lang_key, lang_name in languages_to_translate.items():
            try:
                translation_prompt = f"""You are a professional translator specializing in agricultural and technical content.

Translate the following English text into {lang_name}. 

IMPORTANT GUIDELINES:
1. Maintain the same tone and formality as the original
2. Keep technical terms related to agriculture accurate
3. If a technical term has no direct translation, keep it in English with a brief explanation in {lang_name}
4. Preserve any formatting (line breaks, bullet points, etc.)
5. Make the translation natural and fluent for native speakers
6. Keep greetings and common phrases culturally appropriate

English text to translate:
{english_text}

Provide ONLY the {lang_name} translation (no explanations or notes):"""

                translation_response = self.translation_llm.invoke(translation_prompt)
                translations[lang_key] = translation_response.content.strip()
                
                print(f"[TRANSLATION] Successfully translated to {lang_key}")
                
            except Exception as e:
                print(f"[TRANSLATION] Error translating to {lang_key}: {e}")
                translations[lang_key] = None
        
        return translations

