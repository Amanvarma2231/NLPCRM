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

if __name__ == "__main__":
    validate_config()

    try:
        app = create_app()
    except Exception as e:
        logger.critical(f"Failed to initialize the Flask application: {e}", exc_info=True)
        sys.exit(1)

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
