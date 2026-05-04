import logging
from app.services.nlp_service import nlp_service
from app.services.contact_service import contact_service

logger = logging.getLogger("SocialService")

class SocialService:
    def __init__(self):
        self.sources = ["LinkedIn", "Twitter", "Facebook", "Instagram", "Generic Social"]

    def scan_social_content(self, text, source_platform="LinkedIn"):
        """
        Processes raw text from social media platforms to extract leads.
        Includes basic URL detection to tag leads from specific profiles.
        """
        if not text or len(text.strip()) < 10:
            return {"success": False, "error": "Content too short for reliable extraction."}

        logger.info(f"Scanning social content from {source_platform}...")
        
        # Check if the text is just a URL (simple heuristic)
        if text.startswith("http") and " " not in text:
            # In a real scenario, we'd scrape here. For now, we tag it for manual follow-up.
            logger.info(f"URL detected: {text}. Tagging for discovery.")
            # We'll still try to pass it to NLP in case it can extract something from the URL structure
            # but usually it needs content.
        
        try:
            # Use NLP service to extract structured data
            extracted_json_str = nlp_service.extract_contact_info(text, source=source_platform)
            
            import json
            try:
                # Use regex or clean helper from nlp_service if it was public, 
                # but here we'll just do a robust parse
                start = extracted_json_str.find('{')
                end = extracted_json_str.rfind('}') + 1
                if start != -1 and end != -1:
                    contact_data = json.loads(extracted_json_str[start:end])
                else:
                    contact_data = json.loads(extracted_json_str)
            except Exception as e:
                logger.error(f"Failed to parse AI output: {e}")
                return {"success": False, "error": "AI could not structure this social data."}

            # If we found a name or at least an email/phone, save it
            if contact_data.get("name") or contact_data.get("email") or contact_data.get("phone"):
                # Ensure source platform is captured
                contact_data["source"] = source_platform
                if text.startswith("http"):
                    contact_data["summary"] = f"Profile Link: {text}\n{contact_data.get('summary', '')}"
                
                contact_service.add_contact(contact_data)
                return {"success": True, "data": contact_data}
            
            return {"success": False, "error": "No lead signatures found in this social text."}

        except Exception as e:
            logger.error(f"Social Scan Error: {e}")
            return {"success": False, "error": str(e)}

    def bulk_scan(self, contents, platform="LinkedIn"):
        """Scans a list of text blocks or profiles."""
        results = []
        for item in contents:
            results.append(self.scan_social_content(item, source_platform=platform))
        return results

social_service = SocialService()
