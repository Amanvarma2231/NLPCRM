import os
import sys
import logging
from app import create_app

# Configure robust production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('NLPCRM_Server')

try:
    app = create_app()
except Exception as e:
    logger.critical(f"Failed to initialize the Flask application: {e}", exc_info=True)
    sys.exit(1)

if __name__ == "__main__":
    # Fetch port from environment variable for platforms like Render/Heroku
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1", "yes"]
    
    logger.info(f"Starting NLPCRM Server on port {port} (Debug: {debug_mode})")
    
    # In production, this should be run via Gunicorn instead of app.run()
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
