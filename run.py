import os
import sys
import logging
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

from app import create_app

# Configure robust production logging
log_file = 'app.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding='utf-8')
    ]
)
logger = logging.getLogger('NLPCRM_Server')

import threading
import time

def background_intelligence_loop(app):
    """Periodically triggers the sync-all intelligence loop."""
    with app.app_context():
        from app.services.email_service import email_service
        from app.services.whatsapp_service import whatsapp_service
        from app.services.nlp_service import nlp_service
        from app.services.contact_service import contact_service
        from app.services.db_service import db_service
        
        logger.info("Background Intelligence Worker: INITIALIZED")
        
        while True:
            try:
                # 1. Pull WhatsApp
                wa_messages = whatsapp_service.fetch_messages() or []
                for m in wa_messages:
                    text = m.get('text', '')
                    if len(text) > 10:
                        extracted = nlp_service.extract_contact_info(text, source=m.get('source', 'Live WhatsApp'))
                        # Robust extraction
                        import json
                        try:
                            start = extracted.find('{')
                            end = extracted.rfind('}') + 1
                            if start != -1 and end != -1:
                                contact_data = json.loads(extracted[start:end])
                                if contact_data.get('name') or contact_data.get('email'):
                                    contact_service.add_contact(contact_data)
                                    logger.info(f"LIVE SIGNAL: Extracted lead {contact_data.get('name')}")
                        except: pass

                # 2. Pull Email
                if email_service.is_configured():
                    inbox = email_service.fetch_emails(max_count=5) or []
                    for m in inbox:
                        text = m.get('text', '')
                        extracted = nlp_service.extract_contact_info(text, source=f'Live Email ({m.get("from")})')
                        try:
                            start = extracted.find('{')
                            end = extracted.rfind('}') + 1
                            if start != -1 and end != -1:
                                contact_data = json.loads(extracted[start:end])
                                if contact_data.get('name'):
                                    contact_service.add_contact(contact_data)
                        except: pass

            except Exception as e:
                logger.error(f"Background worker error: {e}")
            
            # Wait for 10 minutes before next sweep
            time.sleep(600) 

def validate_config():
    """Ensure critical environment variables are present before starting."""
    required_keys = [
        ("HF_API_KEY", "HuggingFace API Key missing. AI extraction will fail."),
        ("SECRET_KEY", "Secret key not set. Sessions are not secure.")
    ]
    missing = []
    for key, msg in required_keys:
        if not os.getenv(key):
            missing.append(f"- {key}: {msg}")
    
    # SQLite Cloud is optional (falls back to local)
    if not os.getenv("SQLITE_CLOUD_URL"):
        logger.warning("SQLITE_CLOUD_URL not set. System will use local nlpcrm.db.")
    
    if missing:
        logger.warning("Configuration Validation Warning:")
        for m in missing:
            logger.warning(m)
        logger.warning("System will start, but some features (AI/Sessions) may be limited.")
    return True

validate_config()
try:
    app = create_app()
    # Start Background Intelligence Worker (only if it's the main process or configured to run in gunicorn)
    # Note: running background threads in gunicorn requires care, but we will start it here.
    worker_thread = threading.Thread(target=background_intelligence_loop, args=(app,), daemon=True)
    worker_thread.start()
except Exception as e:
    logger.critical(f"Failed to initialize the Flask application: {e}", exc_info=True)
    sys.exit(1)

if __name__ == "__main__":
    # Fetch port from environment variable, default to 5000 (Flask standard)
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1", "yes"]
    
    logger.info("="*60)
    logger.info("🚀 NLPCRM v3.1 - Neural Intelligence Platform")
    logger.info("="*60)
    logger.info(f"Server: http://localhost:{port}")
    logger.info(f"Debug Mode: {debug_mode}")
    logger.info(f"Environment: {'Development' if debug_mode else 'Production'}")
    logger.info("="*60)
    
    try:
        app.run(host="0.0.0.0", port=port, debug=debug_mode, threaded=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 Server shutdown requested by user")
    except Exception as e:
        logger.critical(f"Server crashed: {e}", exc_info=True)
        sys.exit(1)
