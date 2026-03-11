import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WhatsAppService")
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

class WhatsAppService:
    def __init__(self):
        self.api_key = WHATSAPP_API_KEY
        self.phone_id = WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v19.0/{self.phone_id}/messages" if self.phone_id else ""

    def send_message(self, phone, message):
        """Sends a WhatsApp message using Meta Graph API."""
        if not self.api_key or not self.phone_id:
            logger.warning("WhatsApp API Key or Phone ID missing. Cannot send message.")
            return {"error": "Credentials missing"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {
                "body": message
            }
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            return response.json()
        except Exception as e:
            logger.error(f"WhatsApp Send Error: {e}")
            return {"status": "error", "message": str(e)}

    def fetch_messages(self, phone=None):
        # We always return mock data for demonstration purposes so the
        # user can test the AI Extraction engine from the dashboard's Sync button.
        # Real integration happens via Webhooks.
        return [
            {
                "from": "+91 9999999999", 
                "text": "Hi team, this is Rohan Sharma from Apex Logistics. We are urgently looking to upgrade our CRM system for 50 agents before next quarter. I want to schedule a demo ASAP. You can reach my direct line at 98765-43210 or email me at r.sharma@apexlogistics.in. Is Thursday 2PM IST open?", 
                "status": "received",
                "source": "WhatsApp API"
            },
            {
                "from": "+1 555-0198", 
                "text": "Hey, reaching out regarding a potential tech partnership. I'm Sarah Jenkins, VP of Engineering at CloudScale. We don't have an immediate timeline, just exploring options for now. email: sarah.j@cloudscale.io", 
                "status": "received",
                "source": "WhatsApp API"
            }
        ]

    def set_credentials(self, api_key, phone_id):
        self.api_key = api_key
        self.phone_id = phone_id
        self.base_url = f"https://graph.facebook.com/v19.0/{self.phone_id}/messages"

whatsapp_service = WhatsAppService()
