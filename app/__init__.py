import os
from flask import Flask, jsonify, request, render_template, redirect, url_for, session
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
            'https://ui-avatars.com'
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
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return redirect(url_for('main.dashboard', error_msg="The requested page was not found."))

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"status": "error", "message": "Method Not Allowed"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}")
        if request.is_json:
            return jsonify({"status": "error", "message": "Internal Server Error"}), 500
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return render_template('dashboard.html', error_msg="A server error occurred. Please try again later."), 500
        
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({"status": "error", "message": "File too large"}), 413

    return app
