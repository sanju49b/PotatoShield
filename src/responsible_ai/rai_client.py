"""
Infosys Responsible AI Toolkit Client

This module provides a Python client to interact with the Infosys RAI Toolkit APIs.
DO NOT implement custom logic - this only wraps the official toolkit endpoints.

Repository: https://github.com/Infosys/Infosys-Responsible-AI-Toolkit
"""

import requests
import yaml
import os
from typing import Dict, List, Optional
from pathlib import Path


class RAIToolkitClient:
    """
    Client for Infosys Responsible AI Toolkit APIs.
    
    This client connects to the RAI Backend service and calls the official
    Infosys RAI Toolkit endpoints for:
    - ModerationLayer (comprehensive checks)
    - Hallucination Detection
    - Privacy (PII detection)
    - Safety (toxicity, prompt injection)
    - Fairness (bias detection)
    - Explainability (CoT, ThoT, token importance)
    """
    
    def __init__(self, config_path: str = "config/rai_config.yaml"):
        """
        Initialize RAI Toolkit client.
        
        Args:
            config_path: Path to RAI configuration file
        """
        self.config = self._load_config(config_path)
        rai_config = self.config.get("responsible_ai", {})
        
        # Backend configuration
        backend_config = rai_config.get("backend", {})
        self.base_url = backend_config.get("endpoint", "http://localhost:5555")
        self.api_key = os.getenv("RAI_API_KEY", backend_config.get("api_key", ""))
        self.timeout = backend_config.get("timeout", 30)
        # FORCE ENABLE RAI - Always enabled regardless of config
        self.enabled = True
        print("[RAI] RAI Toolkit FORCED ENABLED - Validation will always be attempted")
        
        # Module endpoints - use .get() with defaults to avoid KeyError
        moderation_config = rai_config.get("moderation_layer", {})
        self.moderation_url = moderation_config.get("endpoint", f"{self.base_url}/rai/v1/moderations")
        
        safety_config = rai_config.get("safety", {})
        self.safety_url = safety_config.get("endpoint", self.moderation_url)
        
        privacy_config = rai_config.get("privacy", {})
        self.privacy_url = privacy_config.get("endpoint", self.moderation_url)
        
        hallucination_config = rai_config.get("hallucination", {})
        self.hallucination_url = hallucination_config.get("endpoint", self.moderation_url)
        
        fairness_config = rai_config.get("fairness", {})
        self.fairness_url = fairness_config.get("endpoint", self.moderation_url)
        
        explainability_config = rai_config.get("explainability", {})
        self.explainability_url = explainability_config.get("endpoint", self.moderation_url)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load RAI configuration from YAML file."""
        # Try multiple possible paths
        possible_paths = [
            Path(config_path),  # Relative to current working directory
            Path(__file__).parent.parent.parent / config_path,  # Relative to project root
            Path(__file__).parent.parent.parent.parent / config_path,  # If running from api/
        ]
        
        config_file = None
        for path in possible_paths:
            if path.exists():
                config_file = path
                break
        
        if not config_file:
            print(f"[RAI] Config file not found. Tried: {possible_paths}")
            # Use default configuration with all required keys
            return {
                "responsible_ai": {
                    "enabled": False,
                    "backend": {"endpoint": "http://localhost:5555"},
                    "moderation_layer": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "safety": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "privacy": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "hallucination": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "fairness": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "explainability": {"endpoint": "http://localhost:5555/rai/v1/moderations"}
                }
            }
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                print(f"[RAI] Loaded config from: {config_file}")
                return config
        except Exception as e:
            print(f"[RAI] Error loading config: {e}")
            # Return default config
            return {
                "responsible_ai": {
                    "enabled": False,
                    "backend": {"endpoint": "http://localhost:5555"},
                    "moderation_layer": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "safety": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "privacy": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "hallucination": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "fairness": {"endpoint": "http://localhost:5555/rai/v1/moderations"},
                    "explainability": {"endpoint": "http://localhost:5555/rai/v1/moderations"}
                }
            }
    
    def _parse_moderation_result(self, result: Dict) -> bool:
        """
        Parse RAI moderation result to determine if input is safe.
        
        Args:
            result: Raw RAI moderation response
            
        Returns:
            True if all checks passed, False otherwise
        """
        try:
            if not result or "ModerationResults" not in result:
                return True
            
            mod_results = result["ModerationResults"]
            
            # Check each moderation result
            checks = [
                "PromptInjectionCheck",
                "JailbreakCheck",
                "ToxicityCheck",
                "ProfanityCheck",
                "PrivacyCheck"
            ]
            
            for check in checks:
                if check in mod_results:
                    check_result = mod_results[check]
                    if isinstance(check_result, dict) and check_result.get("result") == "FAILED":
                        return False
                    elif isinstance(check_result, list):
                        for item in check_result:
                            if isinstance(item, dict) and item.get("result") == "FAILED":
                                return False
            
            return True
        except Exception as e:
            print(f"[RAI] Error parsing moderation result: {e}")
            return True  # Fail open
    
    def check_input_moderation(self, user_input: str, context: Dict = None) -> Dict:
        """
        Call RAI ModerationLayer API to check user input.
        
        This is the main entry point that runs comprehensive checks:
        - Safety (toxicity, profanity, prompt injection)
        - Privacy (PII detection)
        - Restricted topics
        
        Args:
            user_input: User's message
            context: Optional context (user_id, session_id)
            
        Returns:
            Dict from RAI Toolkit with validation results
        """
        # RAI is ALWAYS enabled - always attempt validation
        # If service unavailable, fail open gracefully
        
        try:
            # Official RAI Toolkit API structure
            payload = {
                "Prompt": user_input,
                "ModerationChecks": [
                    "PromptInjection",
                    "JailBreak",
                    "Toxicity",
                    "Piidetct",
                    "Profanity"
                ],
                "ModerationCheckThresholds": {
                    "PromptInjectionThreshold": {"PromptInjectionThreshold": "0.85"},
                    "JailBreakThreshold": {"JailBreakThreshold": "0.80"},
                    "ToxicityThreshold": {
                        "ToxicityThreshold": "0.50",
                        "SevereToxicityThreshold": "0.50",
                        "ObsceneThreshold": "0.50",
                        "ThreatThreshold": "0.50",
                        "InsultThreshold": "0.50",
                        "IdentityAttackThreshold": "0.50",
                        "SexualExplicitThreshold": "0.50"
                    },
                    "ProfanityThreshold": {"ProfanityThreshold": "0"},
                    "PiientitiesConfiguredToDetect": ["PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON", "LOCATION"],
                    "PiientitiesConfiguredToBlock": ["PHONE_NUMBER", "EMAIL_ADDRESS"]
                },
                "userid": context.get("user_id", "anonymous") if context else "anonymous",
                "translate": "no",
                "EmojiModeration": "no"
            }
            
            # Don't send Authorization header - RAI service doesn't require it for local use
            response = requests.post(
                self.moderation_url,  # Use base URL directly (already includes /rai/v1/moderations)
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse RAI response and convert to simpler format
                is_safe = self._parse_moderation_result(result)
                
                # Extract violations and sanitized text
                violations = []
                sanitized_text = user_input  # Default to original input
                
                mod_results = result.get("ModerationResults", {})
                
                # Check for Privacy violations and get anonymized text
                privacy_check = mod_results.get("PrivacyCheck", {})
                if isinstance(privacy_check, dict):
                    if privacy_check.get("result") == "FAILED":
                        violations.append("Privacy violation: PII detected")
                    # Check for masked/anonymized text
                    masked_text = privacy_check.get("maskedText") or privacy_check.get("anonymizedText")
                    if masked_text:
                        sanitized_text = masked_text
                
                # Check for other violations
                if mod_results.get("PromptInjectionCheck", {}).get("result") == "FAILED":
                    violations.append("Prompt injection detected")
                if mod_results.get("JailbreakCheck", {}).get("result") == "FAILED":
                    violations.append("Jailbreak attempt detected")
                if mod_results.get("ToxicityCheck", {}).get("result") == "FAILED":
                    violations.append("Toxic content detected")
                if mod_results.get("ProfanityCheck", {}).get("result") == "FAILED":
                    violations.append("Profanity detected")
                
                return {
                    "is_safe": is_safe,
                    "sanitized_text": sanitized_text,
                    "violations": violations,
                    "rai_result": result
                }
            else:
                print(f"[RAI] Input moderation check failed: {response.status_code}")
                return {"is_safe": True, "sanitized_text": user_input, "violations": [], "error": "rai_service_unavailable"}
                
        except requests.exceptions.RequestException as e:
            print(f"[RAI] Request error during input moderation: {e}")
            return {"is_safe": True, "error": str(e)}
    
    def check_output_moderation(self, ai_output: str, source_data: Dict = None) -> Dict:
        """
        Call RAI ModerationLayer API to check AI output.
        
        Validates AI responses for:
        - Safety (toxic content) - uses ToxicityPopup endpoint
        - Hallucination (factual consistency with source data) - uses Hallucination_Check endpoint
        
        Note: This method combines multiple RAI checks for comprehensive output validation.
        
        Args:
            ai_output: AI-generated response
            source_data: Ground truth data (weather dataset, user profile)
            
        Returns:
            Dict with validation results including is_safe flag
        """
        # RAI is ALWAYS enabled - always attempt validation
        
        validation_results = {
            "is_safe": True,
            "safety_check": {},
            "hallucination_check": {}
        }
        
        try:
            # 1. Safety Check (Toxicity) - use ToxicityPopup endpoint
            safety_payload = {
                "text": ai_output,
                "ToxicityThreshold": {
                    "ToxicityThreshold": "0.50",
                    "SevereToxicityThreshold": "0.50",
                    "ObsceneThreshold": "0.50",
                    "ThreatThreshold": "0.50",
                    "InsultThreshold": "0.50",
                    "IdentityAttackThreshold": "0.50",
                    "SexualExplicitThreshold": "0.50"
                }
            }
            
            safety_response = requests.post(
                f"{self.moderation_url}/ToxicityPopup",
                json=safety_payload,
                timeout=self.timeout
            )
            
            if safety_response.status_code == 200:
                safety_result = safety_response.json()
                validation_results["safety_check"] = safety_result
                # Parse toxicity response
                toxicity_data = safety_result.get("toxicity", [{}])[0] if "toxicity" in safety_result else {}
                is_safe = toxicity_data.get("status", "PASSED") == "PASSED"
                if not is_safe:
                    validation_results["is_safe"] = False
            else:
                print(f"[RAI] Output safety check failed: {safety_response.status_code}")
            
            # 2. Hallucination Check (if source data available)
            if source_data:
                hallucination_result = self.detect_hallucination(
                    ai_response=ai_output,
                    ground_truth=source_data,
                    domain="agriculture"
                )
                validation_results["hallucination_check"] = hallucination_result
                if hallucination_result.get("hallucination_detected", False):
                    # Only mark as unsafe if hallucination score is very low (< 0.5)
                    if hallucination_result.get("hallucination_score", 1.0) < 0.5:
                        validation_results["is_safe"] = False
            
            return validation_results
                
        except requests.exceptions.RequestException as e:
            print(f"[RAI] Request error during output moderation: {e}")
            return {"is_safe": True, "error": str(e)}
    
    def detect_hallucination(
        self, 
        ai_response: str, 
        ground_truth: Dict,
        domain: str = "agriculture"
    ) -> Dict:
        """
        Call RAI Hallucination Detection API.
        
        Verifies that AI response is grounded in source data.
        Critical for disease predictions and treatment recommendations.
        
        Args:
            ai_response: AI-generated text
            ground_truth: Source data (weather dataset, field data)
            domain: Domain context
            
        Returns:
            Dict with hallucination score and details
        """
        # RAI is ALWAYS enabled - always attempt validation
        
        try:
            # Convert ground_truth to source array format
            source_arr = []
            if isinstance(ground_truth, dict):
                # Flatten ground truth into text sources
                import json
                source_arr = [json.dumps(ground_truth, indent=2)]
            elif isinstance(ground_truth, list):
                source_arr = ground_truth
            
            payload = {
                "prompt": f"Domain: {domain}",
                "response": ai_response,
                "sourcearr": source_arr
            }
            
            # Don't send Authorization header
            response = requests.post(
                f"{self.moderation_url}/Hallucination_Check",  # Correct endpoint path
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse the response
                hallucination_score = result.get("similarityScore", 1.0)
                return {
                    "hallucination_detected": hallucination_score < 0.7,  # Below 0.7 = hallucination
                    "hallucination_score": hallucination_score,
                    "rai_result": result
                }
            else:
                print(f"[RAI] Hallucination detection failed: {response.status_code}")
                return {"hallucination_detected": False, "error": "rai_service_unavailable"}
                
        except requests.exceptions.RequestException as e:
            print(f"[RAI] Request error during hallucination detection: {e}")
            return {"hallucination_detected": False, "error": str(e)}
    
    def detect_pii(self, text: str, anonymize: bool = True) -> Dict:
        """
        Call RAI Privacy API to detect and anonymize PII.
        
        Ensures compliance with DPDP Act 2023 (India) and UK GDPR.
        
        Args:
            text: Text to check for PII
            anonymize: Whether to anonymize detected PII
            
        Returns:
            Dict with PII detection results and anonymized text
        """
        # RAI is ALWAYS enabled - always attempt validation
        
        try:
            payload = {
                "text": text,
                "PiientitiesConfiguredToDetect": ["PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON", "LOCATION", "AADHAAR"],
                "PiientitiesConfiguredToBlock": ["PHONE_NUMBER", "EMAIL_ADDRESS", "AADHAAR"],
                "EmojiModeration": "no"
            }
            
            # Don't send Authorization header
            response = requests.post(
                f"{self.moderation_url}/PrivacyPopup",  # Correct endpoint path
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse RAI privacy response
                entities_recognised = result.get("entitiesRecognised", [])
                has_pii = len(entities_recognised) > 0
                anonymized_text = result.get("maskedText", text)
                
                return {
                    "has_pii": has_pii,
                    "pii_types": [entity.get("entity_group", "") for entity in entities_recognised],
                    "anonymized_text": anonymized_text,
                    "rai_result": result
                }
            else:
                print(f"[RAI] PII detection failed: {response.status_code}")
                return {"has_pii": False, "anonymized_text": text, "error": "rai_service_unavailable"}
                
        except requests.exceptions.RequestException as e:
            print(f"[RAI] Request error during PII detection: {e}")
            return {"has_pii": False, "anonymized_text": text, "error": str(e)}
    
    def check_safety(self, text: str, check_type: str = "input") -> Dict:
        """
        Call RAI Safety API to check for toxic content and security threats.
        
        Args:
            text: Text to check
            check_type: "input" or "output"
            
        Returns:
            Dict with safety assessment
        """
        # RAI is ALWAYS enabled - always attempt validation
        
        try:
            payload = {
                "text": text,
                "ToxicityThreshold": {
                    "ToxicityThreshold": "0.50",
                    "SevereToxicityThreshold": "0.50",
                    "ObsceneThreshold": "0.50",
                    "ThreatThreshold": "0.50",
                    "InsultThreshold": "0.50",
                    "IdentityAttackThreshold": "0.50",
                    "SexualExplicitThreshold": "0.50"
                }
            }
            
            # Don't send Authorization header
            response = requests.post(
                f"{self.moderation_url}/ToxicityPopup",  # Correct endpoint path
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse toxicity response
                toxicity_data = result.get("toxicity", [{}])[0] if "toxicity" in result else {}
                is_safe = toxicity_data.get("status", "PASSED") == "PASSED"
                toxicity_score = float(toxicity_data.get("toxicity", {}).get("score", 0.0)) if "toxicity" in toxicity_data else 0.0
                
                return {
                    "is_safe": is_safe,
                    "toxicity_score": toxicity_score,
                    "rai_result": result
                }
            else:
                print(f"[RAI] Safety check failed: {response.status_code}")
                return {"is_safe": True, "error": "rai_service_unavailable"}
                
        except requests.exceptions.RequestException as e:
            print(f"[RAI] Request error during safety check: {e}")
            return {"is_safe": True, "error": str(e)}
    
    def check_fairness(
        self, 
        predictions: List[Dict],
        demographic_slices: Dict,
        protected_attributes: List[str] = None
    ) -> Dict:
        """
        Call RAI Fairness API to check for bias across demographics.
        
        NOTE: Fairness checks require the separate responsible-ai-fairness module
        from the RAI Toolkit, which is not part of the ModerationLayer service.
        This method currently returns a placeholder response.
        
        Args:
            predictions: List of prediction results
            demographic_slices: Dict mapping demographics to predictions
            protected_attributes: Attributes to check (country, region, farm_size)
            
        Returns:
            Dict with fairness metrics
        """
        # RAI is ALWAYS enabled - always attempt validation
        
        # TODO: Integrate with responsible-ai-fairness module when available
        print("[RAI] Fairness check requires separate fairness module (not implemented yet)")
        
        # Return placeholder response
        return {
            "is_fair": True,
            "disparate_impact_ratio": 1.0,
            "bias_detected": False,
            "note": "Fairness check requires responsible-ai-fairness module",
            "error": "fairness_module_not_configured"
        }
    
    def generate_explanation(
        self, 
        prediction: Dict,
        method: str = "chain_of_thought"
    ) -> Dict:
        """
        Call RAI Explainability API to generate explanations.
        
        Methods:
        - "chain_of_thought" (CoT)
        - "thread_of_thought" (ThoT)
        - "chain_of_verification" (CoVe)
        
        Args:
            prediction: Prediction result to explain
            method: Explainability method to use
            
        Returns:
            Dict with explanation
        """
        # RAI is ALWAYS enabled - always attempt validation
        
        try:
            # Format prediction as a prompt for explanation
            prediction_text = str(prediction)
            
            # Map method to endpoint
            endpoint_map = {
                "chain_of_thought": "/openaiCOT",
                "thread_of_thought": "/openaiTHOT",
                "chain_of_verification": "/COV"
            }
            
            endpoint = endpoint_map.get(method, "/openaiCOT")
            
            payload = {
                "Prompt": f"Explain this prediction: {prediction_text}",
                "ModerationChecks": [],  # No moderation checks for explanations
                "ModerationCheckThresholds": {},
                "model_name": "gpt-4o-mini"  # Required field for explainability endpoints
            }
            
            # Don't send Authorization header
            response = requests.post(
                f"{self.moderation_url}{endpoint}",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                explanation = result.get("response", result.get("output", "Explanation generated"))
                return {
                    "explanation": explanation,
                    "method": method,
                    "rai_result": result
                }
            else:
                print(f"[RAI] Explainability generation failed: {response.status_code}")
                return {"explanation": "Explanation unavailable", "error": "rai_service_unavailable"}
                
        except requests.exceptions.RequestException as e:
            print(f"[RAI] Request error during explanation generation: {e}")
            return {"explanation": "Explanation unavailable", "error": str(e)}
    
    def log_audit_event(self, event_type: str, data: Dict) -> bool:
        """
        Log governance and audit events to RAI Telemetry.
        
        Args:
            event_type: Type of event (prediction, validation, violation)
            data: Event data
            
        Returns:
            bool indicating success
        """
        if not self.enabled or not self.config["responsible_ai"]["governance"]["audit_logging"]:
            return False
        
        try:
            payload = {
                "event_type": event_type,
                "timestamp": data.get("timestamp"),
                "data": data
            }
            
            response = requests.post(
                f"{self.base_url}/api/governance/log-event",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            print(f"[RAI] Audit logging failed: {e}")
            return False


# Global RAI client instance
_rai_client = None

def get_rai_client() -> RAIToolkitClient:
    """Get or create global RAI client instance."""
    global _rai_client
    if _rai_client is None:
        _rai_client = RAIToolkitClient()
    return _rai_client
