import sys
import os
import json
import logging

# Set up logging to avoid noise
logging.basicConfig(level=logging.ERROR)

# Add current dir to path to import app services
sys.path.append(os.getcwd())

def validate_system():
    print("--- NLPCRM Backend Validation ---")
    
    # 1. Database Check
    print("[1/3] Checking CRM Database...")
    try:
        from app.services.db_service import db_service
        if db_service._connect():
            print("  - Connection: OK")
            cursor = db_service._conn.cursor()
            cursor.execute("SELECT count(*) FROM contacts_v2")
            count = cursor.fetchone()[0]
            print(f"  - Leads Index: OK ({count} leads found)")
        else:
            print("  - Connection: FAILED")
    except Exception as e:
        print(f"  - DB Error: {e}")

    # 2. AI Intelligence (NLP) Check
    print("[2/3] Checking AI Intelligence (HuggingFace)...")
    try:
        from app.services.nlp_service import nlp_service
        test_text = "I am Amit from Tech-Solutions. We need a CRM. email: amit@tech.com"
        result_json = nlp_service.extract_contact_info(test_text, "System Test")
        result = json.loads(result_json)
        
        if result.get("name") or result.get("email"):
            print(f"  - AI Extraction: OK (Identified {result.get('name')})")
        else:
            print(f"  - AI Extraction: WARNING (Returned empty/error result: {result})")
    except Exception as e:
        print(f"  - AI Error: {e}")

    # 3. Connection Configuration Check
    print("[3/3] Checking Connection Configs...")
    from app.services.gmail_service import google_service
    from app.services.whatsapp_service import whatsapp_service
    
    print(f"  - Gmail Setup: {'READY' if google_service.is_configured() else 'INCOMPLETE'}")
    print(f"  - WhatsApp Setup: {'READY' if whatsapp_service.api_key and whatsapp_service.phone_id else 'INCOMPLETE'}")

if __name__ == "__main__":
    validate_system()
