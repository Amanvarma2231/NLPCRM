import os
import logging
import json
from functools import wraps
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, send_from_directory, current_app

from app.services.db_service import db_service
from app.services.nlp_service import nlp_service
from app.services.gmail_service import google_service
from app.services.whatsapp_service import whatsapp_service
from app.services.contact_service import contact_service

logger = logging.getLogger("MainRoutes")

# Auto-migrate legacy contacts on load
contact_service.migrate_legacy_contacts()

main_bp = Blueprint("main", __name__)

# Authentication Middleware
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Consistent with login.html expectations (email + password)
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@nlpcrm.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin@2026')
        
        if email == admin_email and password == admin_password:
            session['logged_in'] = True
            session['user_email'] = email
            return redirect(url_for('main.dashboard'))
        else:
            logger.warning(f"Failed login attempt for email: {email}")
            return render_template('login.html', error="Invalid email or password.")
            
    # If already logged in, skip to dashboard
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))
        
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main_bp.app_context_processor
def inject_global_data():
    # Skip DB calls if user is not logged in (e.g. on login page)
    if not session.get('logged_in'):
        return {"contacts_count": 0, "admin_settings": {}}
    try:
        contacts = contact_service.get_contacts()
        count = len(contacts) if contacts else 0
        settings = db_service.get_settings() or {}
        
        # Parse profile arrays for clearer display in base.html
        for key, new_key in [('USER_EMAILS', 'USER_EMAIL2_PRIMARY'), ('USER_SOCIALS', 'USER_SOCIAL_PRIMARY')]:
            val = settings.get(key)
            if val:
                try:
                    parsed = json.loads(str(val))
                    if isinstance(parsed, list) and len(parsed) > 0:
                        settings[new_key] = parsed[0].get('value', '')
                except (json.JSONDecodeError, TypeError, AttributeError):
                    pass

    except Exception as e:
        logger.error(f"Failed to inject global data: {e}")
        count = 0
        settings = {}
    return {"contacts_count": count, "admin_settings": settings}

@main_bp.route("/dashboard")
def dashboard_redirect():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(current_app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception:
        return '', 404

@main_bp.route('/manifest.json')
def manifest():
    try:
        return send_from_directory(current_app.static_folder, 'manifest.json', mimetype='application/manifest+json')
    except Exception as e:
        logger.error(f"Error serving manifest: {e}")
        return jsonify({"error": "Manifest not found"}), 404

@main_bp.route('/service-worker.js')
def service_worker():
    try:
        response = send_from_directory(current_app.static_folder, 'service-worker.js', mimetype='application/javascript')
        response.headers['Service-Worker-Allowed'] = '/'
        return response
    except Exception as e:
        logger.error(f"Error serving service worker: {e}")
        return jsonify({"error": "Service worker not found"}), 404

@main_bp.route('/google-auth')
@login_required
def google_auth():
    redirect_uri = url_for('main.google_auth_callback', _external=True)
    authorization_url, state = google_service.get_auth_url(redirect_uri)
    session['google_oauth_state'] = state
    return redirect(authorization_url)

@main_bp.route('/google-auth/callback')
@login_required
def google_auth_callback():
    state = session.get('google_oauth_state')
    if not state:
        return redirect(url_for('main.settings', error="Invalid OAuth state"))
    
    redirect_uri = url_for('main.google_auth_callback', _external=True)
    try:
        # Pass the full request URL as the authorization_response
        google_service.fetch_token(
            authorization_response=request.url,
            state=state,
            redirect_uri=redirect_uri
        )
        return redirect(url_for('main.settings', message="Google account synced successfully!"))
    except Exception as e:
        logger.error(f"Google OAuth Error: {e}")
        return redirect(url_for('main.settings', error=f"Google authentication failed: {str(e)}"))

@main_bp.route("/test-whatsapp")
@login_required
def test_whatsapp():
    logger.info("Testing WhatsApp connectivity...")
    result = whatsapp_service.send_message("916306572504", "Hello Aman 🚀 WhatsApp connected with CRM")
    return jsonify({"status": "sent", "response": result})

@main_bp.route("/pipeline")
@login_required
def pipeline():
    contacts = contact_service.get_contacts()
    return render_template("pipeline.html", contacts=contacts)

@main_bp.route("/ai-engine")
@login_required
def ai_engine():
    return render_template("ai_engine.html")

@main_bp.route("/ai-assistant/query", methods=["POST"])
@login_required
def ai_assistant_query():
    data = request.get_json(silent=True) or {}
    user_query = data.get("query", "")
    
    if not user_query:
        return jsonify({"error": "Missing query"}), 400
        
    # 1. Translate NL to Filter
    filter_json = nlp_service.ai_query(user_query)
    try:
        filters = json.loads(filter_json)
    except Exception:
        filters = {}
        
    # 2. Get all contacts and apply filter
    all_contacts = contact_service.get_contacts()
    results = []
    
    interest_filter = filters.get("interest")
    source_filter = filters.get("source")
    company_filter = filters.get("company", "").lower()
    search_text = filters.get("search_text", "").lower()
    
    for c in all_contacts:
        match = True
        if interest_filter and c.get("interest") != interest_filter: match = False
        if source_filter and c.get("source") != source_filter: match = False
        if company_filter and company_filter not in c.get("company", "").lower(): match = False
        if search_text:
            text_pool = f"{c.get('name', '')} {c.get('job_title', '')}".lower()
            if search_text not in text_pool: match = False
            
        if match:
            results.append(c)
            
    return jsonify({
        "success": True,
        "filters_applied": filters,
        "results": results[:10], # Limit to top 10 for chat
        "count": len(results)
    })

@main_bp.route("/entities")
@login_required
def entities():
    entities_data = db_service.get_entities()
    return render_template("entities.html", entities=entities_data)

@main_bp.route("/activity")
@login_required
def activity():
    act_logs = db_service.get_recent_activity(limit=100)
    return render_template("activity.html", activity=act_logs)

@main_bp.route("/")
@login_required
def dashboard():
    contacts = contact_service.get_contacts() or []
    contacts_count = len(contacts)
    messages = whatsapp_service.fetch_messages() or []
    messages_count = len(messages)
    recent_contacts = contacts[-5:] if contacts else []
    recent_activity = db_service.get_recent_activity(limit=5) or []
    settings = db_service.get_settings() or {}
    
    error_msg = request.args.get('error_msg')
    
    return render_template("dashboard.html", 
                           contacts_count=contacts_count, 
                           messages_count=messages_count, 
                           recent_contacts=recent_contacts, 
                           recent_activity=recent_activity,
                           settings=settings,
                           error_msg=error_msg)

@main_bp.route("/contacts")
@login_required
def contacts_list():
    try:
        logger.info("Accessing contacts_list route")
        contacts = contact_service.get_contacts()
        logger.info(f"Retrieved {len(contacts) if contacts else 0} contacts")
        return render_template("contacts.html", contacts=contacts)
    except Exception as e:
        logger.error(f"Error in contacts_list: {e}", exc_info=True)
        return render_template("dashboard.html", error_msg="Error loading contacts."), 500

@main_bp.route("/contacts/export")
@login_required
def export_contacts():
    import csv
    from io import StringIO
    from flask import make_response
    
    contacts = contact_service.get_contacts()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Name', 'Email', 'Phone', 'Company', 'Job Title', 'Source', 'Interest', 'Created At'])
    
    for c in contacts:
        cw.writerow([
            c.get('name', ''),
            c.get('email', ''),
            c.get('phone', ''),
            c.get('company', ''),
            c.get('job_title', ''),
            c.get('source', ''),
            c.get('interest', ''),
            c.get('created_at', '')
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=contacts.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@main_bp.route("/contacts/add", methods=["POST"])
@login_required
def add_contact():
    email2_raw = request.form.get("email2", "[]")
    social_media_raw = request.form.get("social_media", "[]")
    
    try:
        email2_data = json.loads(email2_raw) if email2_raw else []
        if not isinstance(email2_data, list): email2_data = []
        valid_emails = [{"label": str(e.get("label", "")).strip(), "value": str(e.get("value", "")).strip()} for e in email2_data if isinstance(e, dict) and e.get("value")]
        email2_parsed = json.dumps(valid_emails)
    except Exception:
        email2_parsed = "[]"
        
    try:
        social_data = json.loads(social_media_raw) if social_media_raw else []
        if not isinstance(social_data, list): social_data = []
        valid_socials = [{"label": str(s.get("label", "")).strip(), "value": str(s.get("value", "")).strip()} for s in social_data if isinstance(s, dict) and s.get("value")]
        social_media_parsed = json.dumps(valid_socials)
    except Exception:
        social_media_parsed = "[]"

    contact_data = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "phone": request.form.get("phone"),
        "email2": email2_parsed,
        "social_media": social_media_parsed,
        "company": request.form.get("company")
    }
    contact_service.add_contact(contact_data)
    return redirect(url_for("main.contacts_list"))

@main_bp.route("/contacts/delete/<email>", methods=["POST"])
@login_required
def delete_contact(email):
    contact_service.delete_contact(email)
    return redirect(url_for("main.contacts_list"))

@main_bp.route("/contacts/batch-delete", methods=["POST"])
@login_required
def batch_delete_contacts():
    data = request.get_json(silent=True)
    if data and 'emails' in data:
        for email in data['emails']:
            contact_service.delete_contact(email)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "No emails provided"}), 400

@main_bp.route("/sync-all", methods=["POST"])
@login_required
def sync_all():
    # 1. Fetch from WhatsApp
    wa_messages = whatsapp_service.fetch_messages() or []
    
    # 2. Fetch from Gmail
    gmail_messages = google_service.fetch_gmail_messages() or []
    
    # Combine sources
    all_data = []
    for m in wa_messages:
        all_data.append({'text': m.get('text', ''), 'source': 'whatsapp'})
    for m in gmail_messages:
        all_data.append({'text': m.get('snippet', ''), 'source': 'gmail'})
        
    results = []
    for item in all_data:
        text = item['text']
        if len(text) > 15:
            extracted = nlp_service.extract_contact_info(text, source=item['source'])
            try:
                start = extracted.find('{')
                end = extracted.rfind('}') + 1
                if start != -1 and end != -1:
                    contact_json = json.loads(extracted[start:end])
                    if contact_json.get('email'):
                        # Set source automatically if omitted
                        if 'source' not in contact_json or not contact_json['source']:
                            contact_json['source'] = item['source'].capitalize()
                            
                        contact_service.add_contact(contact_json)
                        db_service.add_interaction(
                            contact_json.get('email'), 
                            f"{item['source']}_sync", 
                            text
                        )
                        results.append(contact_json)
                else:
                    logger.warning(f"No JSON found in extraction result: {extracted}")
            except Exception as e:
                snippet = str(text)[:50] if text else "None"
                logger.error(f"Sync parsing failed for text: {snippet}... Error: {e}")
                
    return jsonify({
        "success": True, 
        "synced_count": len(results),
        "total_checked": len(all_data)
    })

@main_bp.route("/process-text", methods=["POST"])
@login_required
def process_text():
    data = request.get_json(silent=True)
    if not data or not data.get("text"):
        return jsonify({"status": "error", "message": "No text provided"}), 400
        
    source = data.get("source", "Manual Input")
    extracted = nlp_service.extract_contact_info(data.get("text"), source=source)
    return jsonify({"success": True, "extracted": extracted})

@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        config_data = request.form.to_dict()
        for key, val in config_data.items():
            if key != 'csrf_token':
                db_service.save_setting(key, val)
        return redirect(url_for('main.settings'))
    
    current_settings = db_service.get_settings()
    google_auth_status = google_service.is_authenticated()
    return render_template("settings.html", settings=current_settings, google_auth_status=google_auth_status)

@main_bp.route("/integrations")
@login_required
def integrations():
    settings = db_service.get_settings()
    return render_template("integrations.html", settings=settings)

@main_bp.route("/webhooks/zoom", methods=["POST"])
def zoom_webhook():
    payload = request.get_json(silent=True) or {}
    text = str(payload)
    if text and payload:
        try:
            extracted = nlp_service.extract_contact_info(text)
            start = extracted.find('{')
            end = extracted.rfind('}')
            if start != -1 and end != -1:
                contact_json = json.loads(extracted[start:end+1])
                if contact_json.get('email'):
                    contact_service.add_contact(contact_json)
                    db_service.add_interaction(contact_json.get('email'), 'zoom_meeting', 'Zoom Transcript Processed')
        except Exception as e:
            logger.error(f"Zoom webhook failed: {e}")
            return jsonify({"status": "error", "message": "Failed to process"}), 500
    return jsonify({"status": "received"}), 200

@main_bp.route("/webhooks/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        # Meta Webhook verification
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "nlpcrm_verify_token")
        
        if mode == "subscribe" and token == verify_token:
            logger.info("WhatsApp Webhook verified successfully!")
            return challenge, 200
        return "Verification failed", 403

    # POST - Handle incoming message
    payload = request.get_json(silent=True) or {}
    logger.info(f"WhatsApp Webhook Payload: {json.dumps(payload)}")
    
    # Simple parsing logic for WhatsApp Cloud API JSON structure
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    text = msg.get("text", {}).get("body")
                    sender_phone = msg.get("from")
                    
                    if text:
                        # Process with AI
                        extracted = nlp_service.extract_contact_info(text, source="WhatsApp API")
                        start = extracted.find('{')
                        end = extracted.rfind('}') + 1
                        
                        if start != -1 and end != -1:
                            contact_json = json.loads(extracted[start:end])
                            # Ensure phone is set from the sender if not extracted or empty
                            if not contact_json.get("phone"):
                                contact_json["phone"] = sender_phone
                            
                            contact_json["source"] = "WhatsApp Webhook"
                            contact_service.add_contact(contact_json)
                            
                            # Log Interaction
                            if contact_json.get("email"):
                                db_service.add_interaction(contact_json["email"], "whatsapp_msg", text)
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        
    return jsonify({"status": "received"}), 200

@main_bp.route("/webhooks/teams", methods=["POST"])
def teams_webhook():
    payload = request.get_json(silent=True) or {}
    text = str(payload)
    if text and payload:
        try:
            extracted = nlp_service.extract_contact_info(text)
            start = extracted.find('{')
            end = extracted.rfind('}')
            if start != -1 and end != -1:
                contact_json = json.loads(extracted[start:end+1])
                if contact_json.get('email'):
                    contact_service.add_contact(contact_json)
                    db_service.add_interaction(contact_json.get('email'), 'teams_meeting', 'Teams Transcript Processed')
        except Exception as e:
            logger.error(f"Teams webhook failed: {e}")
            return jsonify({"status": "error", "message": "Failed to process"}), 500
    return jsonify({"status": "received"}), 200
