import os
import sys
import logging
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
        ("SQLITE_CLOUD_URL", "Database connectivity is required. Check your .env file."),
        ("HF_API_KEY", "HuggingFace API Key missing. AI extraction will fail."),
        ("SECRET_KEY", "Secret key not set. Sessions are not secure.")
    ]
    missing = []
    for key, msg in required_keys:
        if not os.getenv(key):
            missing.append(f"- {key}: {msg}")
    
    if missing:
        logger.error("Configuration Validation Failed:")
        for m in missing:
            logger.error(m)
        return False
    return True

if __name__ == "__main__":
    if not validate_config():
        logger.critical("Application startup aborted due to missing configuration.")
        sys.exit(1)

    try:
        app = create_app()
    except Exception as e:
        logger.critical(f"Failed to initialize the Flask application: {e}", exc_info=True)
        sys.exit(1)

    # Fetch port from environment variable for platforms like Render/Heroku
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1", "yes"]
    
    logger.info(f"Starting NLPCRM Server on port {port} (Debug: {debug_mode})")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
