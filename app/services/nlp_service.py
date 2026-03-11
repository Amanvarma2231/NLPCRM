import os
import requests
import logging
import json
import re
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("NLPService")

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")

class NLPService:
    def __init__(self):
        # Use standard Serverless Inference API for chat models
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        } if HF_API_KEY else {}
        
        self.system_prompt = """You are an elite, highly precise enterprise CRM Assistant. 
Your ONLY job is to extract business contact entities from raw text streams (like emails or chat messages) and output them strictly as a JSON object.

CRITICAL RULES:
1. ONLY return the raw JSON. Do not include markdown codeblocks (no ```json).
2. Use EXACTLY these keys:
   - "name" (Full name of contact, or "" if missing)
   - "email" (Primary email, or "" if missing)
   - "phone" (Primary phone number, or "" if missing)
   - "company" (Organization name, or "" if missing)
   - "job_title" (Their role, or "" if missing)
   - "interest" (Must be exactly one of: "High", "Medium", "Low", "Support", or "New")

If a field is not found in the text, use an empty string "". Do not guess."""

    def query_model(self, prompt, source="Unknown"):
        if not HF_API_KEY:
            logger.warning("HF_API_KEY is missing. Returning placeholder.")
            return '{"name": "API Key Missing", "email": "admin@nlpcrm.com", "interest": "New"}'
        
        # Guide the AI based on the platform it originated from
        context_prompt = f"Data Source: {source}\nMessage Body: {prompt}"
        
        payload = {
            "model": HF_MODEL,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": context_prompt}
            ],
            "parameters": {"max_tokens": 800, "temperature": 0.1, "top_p": 0.9}
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=25)
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                raw_output = result["choices"][0]["message"]["content"].strip()
                return self._clean_json_output(raw_output)
            return '{"error": "Empty AI response"}'
            
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error: {http_err} - Response: {response.text}")
            return json.dumps({"error": "API HTTP Error", "details": response.text})
        except Exception as e:
            logger.error(f"NLP processing error: {e}", exc_info=True)
            return '{"error": "Internal AI Error"}'

    def ai_query(self, user_query):
        """Translates natural language to structured search criteria"""
        system_prompt = """You are a CRM Database Assistant. Your job is to translate user questions into a JSON search filter.
Available keys for filtering:
- interest: ['High', 'Medium', 'Low', 'Support', 'New']
- source: ['Gmail', 'WhatsApp API', 'Manual']
- company: string
- search_text: string (to search in name or job_title)

Example Input: "Show me all high interest leads from WhatsApp"
Example Output: {"interest": "High", "source": "WhatsApp API"}

Example Input: "Find someone from Apex Logistics"
Example Output: {"company": "Apex Logistics"}

Output strictly a JSON object. No conversation."""
        
        try:
            payload = {
                "model": HF_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                "parameters": {"max_tokens": 150, "temperature": 0.1}
            }
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                raw_text = result["choices"][0]["message"]["content"].strip()
                return self._clean_json_output(raw_text)
            return "{}"
        except Exception as e:
            logger.error(f"AI Query error: {e}")
            return "{}"

    def _clean_json_output(self, raw_text):
        """Robustly extracts JSON even if the AI hallucinates markdown wrappers."""
        raw_text = raw_text.strip()
        
        # If it's pure JSON, return it
        if raw_text.startswith('{') and raw_text.endswith('}'):
            return raw_text
            
        # Regex to find JSON block hidden inside markdown backticks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()
            
        # Greedy fallback: find the first { and last }
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return raw_text[start_idx:end_idx+1].strip()
            
        # Absolute failure
        logger.error(f"Failed to extract JSON from AI output: {raw_text}")
        return '{"name": "Unknown Entity", "interest": "New"}'

    def extract_contact_info(self, text, source="Unknown"):
        logger.info(f"Extracting contact info from {source} (Length: {len(text)})")
        return self.query_model(text, source)

nlp_service = NLPService()
