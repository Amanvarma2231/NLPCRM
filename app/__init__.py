import os
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, send_from_directory
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from dotenv import load_dotenv
from .routes.main import main_bp

load_dotenv()

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    # 1. Basic Middleware & Security
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    CORS(app)
    app.secret_key = os.getenv("SECRET_KEY", "super-secret-key-change-me-in-production")
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    
    # Initialize CSRF Protection
    csrf.init_app(app)
    
    # Exempt webhook routes from CSRF
    @app.after_request
    def exempt_webhooks(response):
        return response
    
    with app.app_context():
        from app.routes.main import zoom_webhook, whatsapp_webhook, teams_webhook
        csrf.exempt(zoom_webhook)
        csrf.exempt(whatsapp_webhook)
        csrf.exempt(teams_webhook)
    
    # Content Security Policy for Talisman
    csp = {
        'default-src': [
            '\'self\'',
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net'
        ],
        'style-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'https://fonts.googleapis.com',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net'
        ],
        'font-src': [
            '\'self\'',
            'https://fonts.gstatic.com',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net'
        ],
        'img-src': [
            '\'self\'',
            'data:',
            'https://ui-avatars.com',
            'https://*.ui-avatars.com',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net'
        ],
        'script-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'https://cdnjs.cloudflare.com',
            'https://cdn.jsdelivr.net'
        ]
    }
    Talisman(app, content_security_policy=csp, force_https=False)

    # 2. Register Blueprints
    app.register_blueprint(main_bp)
    
    # 3. Global Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        if request.is_json:
            return jsonify({"status": "error", "message": "Bad Request", "details": str(error)}), 400
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return render_template('dashboard.html', error_msg="Bad Request: Please check your input."), 400

    @app.errorhandler(401)
    def unauthorized(error):
        if request.is_json:
            return jsonify({"status": "error", "message": "Unauthorized Access"}), 401
        return redirect(url_for('main.login', error="Unauthorized access. Please login."))

    @app.errorhandler(404)
    def handle_404(error):
        if request.is_json:
            return jsonify({"status": "error", "message": "Resource not found"}), 404
            
        # Do not redirect to login for static assets or system files
        path = request.path.lower()
        if any(path.startswith(prefix) for prefix in ['/static/', '/api/']) or any(path.endswith(ext) for ext in ['.js', '.css', '.png', '.jpg', '.ico', '.json', '.svg', '.webmanifest', '.txt', '.pdf']):
            return "404 Not Found", 404
            
        return render_template('404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"status": "error", "message": "Method Not Allowed"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Critical System Error: {error}", exc_info=True)
        if request.is_json:
            return jsonify({"status": "error", "message": "Internal Server Error"}), 500
        return render_template('500.html'), 500
        
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"status": "error", "message": "File too large"}), 413

    # --- System Asset Routes (Directly on App to bypass Blueprint auth) ---
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.abspath(app.static_folder), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/manifest.json')
    def manifest():
        return send_from_directory(os.path.abspath(app.static_folder), 'manifest.json', mimetype='application/manifest+json')

    @app.route('/service-worker.js')
    def service_worker():
        return send_from_directory(os.path.abspath(app.static_folder), 'service-worker.js', mimetype='application/javascript')

    return app
