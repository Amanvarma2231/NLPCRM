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
try:
    contact_service.migrate_legacy_contacts()
except Exception as e:
    logger.error(f"Migration failed: {e}")

main_bp = Blueprint("main", __name__)

# Authentication Middleware
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

def _parse_json_from_llm(text):
    """Helper to extract and parse JSON from a potentially messy LLM response."""
    if not text: return None
    try:
        if isinstance(text, dict): return text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            return json.loads(text[start:end])
    except Exception as e:
        logger.error(f"JSON Parse Error: {e} | Text snippet: {text[:50]}...")
    return None

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@nlpcrm.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin@2026')
        
        if email == admin_email and password == admin_password:
            session['logged_in'] = True
            session['user_email'] = email
            return redirect(url_for('main.dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password.")
    if session.get('logged_in'):
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main_bp.app_context_processor
def inject_global_data():
    if not session.get('logged_in'):
        return {"contacts_count": 0, "admin_settings": {}}
    try:
        contacts = contact_service.get_contacts() or []
        count = len(contacts)
        settings = db_service.get_settings() or {}
        # Simple primary profile extraction
        for key, new_key in [('USER_EMAILS', 'USER_EMAIL2_PRIMARY'), ('USER_SOCIALS', 'USER_SOCIAL_PRIMARY')]:
            val = settings.get(key)
            if val:
                try:
                    parsed = json.loads(str(val))
                    if isinstance(parsed, list) and len(parsed) > 0:
                        settings[new_key] = parsed[0].get('value', '')
                except: pass
    except Exception as e:
        logger.error(f"Failed to inject global data: {e}")
        count = 0
        settings = {}
    
    # Professional fallbacks for branding
    settings.setdefault('ADMIN_NAME', 'Aman Varma')
    settings.setdefault('AVATAR_URL', '')
    
    return {"contacts_count": count, "admin_settings": settings}

@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    source_filter = request.args.get('source')
    contacts = contact_service.get_contacts() or []
    
    # Apply source filter if provided
    if source_filter:
        if source_filter == 'teams':
            filtered_contacts = [c for c in contacts if (c.get('source') or '').lower() in ['teams', 'outlook', 'microsoft']]
        else:
            filtered_contacts = [c for c in contacts if (c.get('source') or '').lower() == source_filter.lower()]
    else:
        filtered_contacts = contacts

    contacts_count = len(contacts)
    messages = whatsapp_service.fetch_messages() or []
    messages_count = len(messages)
    
    # Use filtered contacts for the feed
    recent_contacts = filtered_contacts[-8:][::-1] if filtered_contacts else []
    recent_activity = db_service.get_recent_activity(limit=5) or []
    settings = db_service.get_settings() or {}
    
    sentiment_stats = {"Positive": 0, "Negative": 0, "Neutral": 0}
    priority_stats = {"High": 0, "Medium": 0, "Low": 0}
    total_importance = 0
    important_contacts = 0
    
    for c in contacts:
        s = c.get('sentiment', 'Neutral')
        if s in sentiment_stats: sentiment_stats[s] += 1
        p = c.get('urgency') or c.get('interest', 'Low')
        if p in priority_stats: priority_stats[p] += 1
        imp = c.get('importance_score', 0)
        try:
            val = float(imp)
            total_importance += val
            if val > 7: important_contacts += 1
        except: pass
            
    avg_importance = round(total_importance / contacts_count, 1) if contacts_count > 0 else 0
    error_msg = request.args.get('error_msg')

    # Sanitize recent activity to avoid None errors in templates
    sanitized_activity = []
    for act in recent_activity:
        sanitized_activity.append([
            act[0] or 'activity',
            act[1] or 'Admin',
            act[2] or 'System',
            act[3] or 'Operation completed successfully.',
            act[4] or ''
        ])

    return render_template("dashboard.html", 
                           contacts_count=contacts_count, 
                           messages_count=messages_count, 
                           recent_contacts=recent_contacts, 
                           recent_activity=sanitized_activity,
                           settings=settings,
                           error_msg=error_msg,
                           sentiment_stats=sentiment_stats,
                           priority_stats=priority_stats,
                           avg_importance=avg_importance,
                           important_contacts=important_contacts)

@main_bp.route("/contacts")
@login_required
def contacts_list():
    try:
        contacts = contact_service.get_contacts() or []
        return render_template("contacts.html", contacts=contacts)
    except Exception as e:
        logger.error(f"Failed to render contacts_list: {e}", exc_info=True)
        return redirect(url_for('main.dashboard', error_msg="Failed to load contacts directory."))

@main_bp.route("/contacts/add", methods=["POST"])
@login_required
def add_contact():
    import json as _json
    email2_raw = request.form.get("email2", "[]")
    social_raw = request.form.get("social_media", "[]")
    try:
        email2 = _json.dumps([e for e in _json.loads(email2_raw) if isinstance(e, dict) and e.get("value")])
    except Exception:
        email2 = "[]"
    try:
        socials = _json.dumps([s for s in _json.loads(social_raw) if isinstance(s, dict) and s.get("value")])
    except Exception:
        socials = "[]"
    contact_data = {
        "name": request.form.get("name", ""),
        "email": request.form.get("email", ""),
        "phone": request.form.get("phone", ""),
        "company": request.form.get("company", ""),
        "email2": email2,
        "social_media": socials,
        "sentiment": request.form.get("sentiment", "Neutral"),
        "importance_score": request.form.get("importance_score", 0),
        "urgency": request.form.get("urgency", "Low"),
        "summary": request.form.get("summary", ""),
        "source": request.form.get("source", "Manual Input")
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
    data = request.get_json(silent=True) or {}
    emails = data.get('emails', [])
    for email in emails:
        contact_service.delete_contact(email)
    return jsonify({"success": True, "deleted": len(emails)})

@main_bp.route("/contacts/export")
@login_required
def export_contacts():
    import csv
    from io import StringIO
    from flask import make_response
    contacts = contact_service.get_contacts()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Name','Email','Phone','Company','Job Title','Source','Interest','Sentiment','Importance','Summary','Created At'])
    for c in contacts:
        cw.writerow([c.get('name',''), c.get('email',''), c.get('phone',''), c.get('company',''),
                     c.get('job_title',''), c.get('source',''), c.get('interest',''),
                     c.get('sentiment',''), c.get('importance_score',''), c.get('summary',''), c.get('created_at','')])
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=nlpcrm_contacts.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@main_bp.route("/entities")
@login_required
def entities():
    entities_data = db_service.get_entities()
    return render_template("entities.html", entities=entities_data)

@main_bp.route("/sync-all", methods=["POST"])
@login_required
def sync_all():
    results = []
    
    # 1. Pull WhatsApp (Real API Attempt)
    try:
        wa_messages = whatsapp_service.fetch_messages() or []
        for m in wa_messages:
            text = m.get('text', '')
            if len(text) > 10:
                extracted = nlp_service.extract_contact_info(text, source=m.get('source', 'WhatsApp'))
                json_data = _parse_json_from_llm(extracted)
                if json_data and (json_data.get('email') or json_data.get('phone')):
                    contact_service.add_contact(json_data)
                    results.append(json_data)
    except Exception as e:
        logger.error(f"WhatsApp Sync Error: {e}")

    # 2. Pull Gmail (Real API Attempt if Auth exists)
    if google_service.is_authenticated():
        try:
            gmail_messages = google_service.fetch_gmail_messages(max_results=5) or []
            for m in gmail_messages:
                text = m.get('text', '')
                if len(text) > 10:
                    extracted = nlp_service.extract_contact_info(text, source='Gmail')
                    json_data = _parse_json_from_llm(extracted)
                    if json_data and (json_data.get('email') or json_data.get('phone')):
                        contact_service.add_contact(json_data)
                        results.append(json_data)
        except Exception as e:
            logger.error(f"Gmail Sync Error: {e}")
    
    return jsonify({
        "success": True, 
        "synced_count": len(results),
        "gmail_active": google_service.is_authenticated()
    })

@main_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        for key, val in request.form.items():
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
    data = request.get_json(silent=True) or {}
    text = data.get('transcript') or data.get('payload', {}).get('object', {}).get('transcript', '')
    if text:
        extracted = nlp_service.extract_contact_info(text, source="Zoom")
        contact_json = _parse_json_from_llm(extracted)
        if contact_json: contact_service.add_contact(contact_json)
    return jsonify({"status": "received"}), 200

@main_bp.route("/webhooks/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == os.getenv("WHATSAPP_VERIFY_TOKEN", "nlpcrm_verify_token"):
            return request.args.get("hub.challenge"), 200
        return "Forbidden", 403
    payload = request.get_json(silent=True) or {}
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            messages = change.get("value", {}).get("messages", [])
            for msg in messages:
                text = msg.get("text", {}).get("body")
                if text:
                    extracted = nlp_service.extract_contact_info(text, source="WhatsApp Webhook")
                    contact_json = _parse_json_from_llm(extracted)
                    if contact_json: contact_service.add_contact(contact_json)
    return jsonify({"status": "received"}), 200

@main_bp.route("/webhooks/teams", methods=["POST"])
def teams_webhook():
    data = request.get_json(silent=True) or {}
    text = data.get('transcript') or data.get('message', {}).get('content', '')
    if text:
        extracted = nlp_service.extract_contact_info(text, source="Teams")
        contact_json = _parse_json_from_llm(extracted)
        if contact_json: contact_service.add_contact(contact_json)
    return jsonify({"status": "received"}), 200

# --- NEW: AI & NLP INTERACTIVE ROUTES ---

@main_bp.route("/process-text", methods=["POST"])
@login_required
def process_text():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        return jsonify({"success": False, "error": "No text provided"}), 400
    
    try:
        extracted = nlp_service.extract_contact_info(text, source="Manual Extraction")
        # Store in DB if it contains valid info
        contact_json = _parse_json_from_llm(extracted)
        if contact_json and contact_json.get('email'):
            contact_service.add_contact(contact_json)
            
        return jsonify({"success": True, "extracted": extracted})
    except Exception as e:
        logger.error(f"Manual extraction failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@main_bp.route("/ai-assistant/query", methods=["POST"])
@login_required
def ai_assistant_query():
    data = request.get_json(silent=True) or {}
    query = data.get("query")
    if not query:
        return jsonify({"success": False, "error": "No query provided"}), 400
    
    try:
        # 1. Translate query to filter or just use general analyst
        # We'll use the analyst for broad questions or specific data retrieval
        context_summary = contact_service.get_context_summary()
        answer = nlp_service.crm_chat_analyst(query, context_summary)
        
        # Also try to see if it was a search query
        search_filter_json = nlp_service.ai_query(query)
        search_filter = _parse_json_from_llm(search_filter_json) or {}
        
        results = []
        if search_filter:
            # Simple keyword matching from the filter for now
            contacts = contact_service.get_contacts()
            for c in contacts:
                match = True
                if search_filter.get('company') and search_filter['company'].lower() not in (c.get('company') or '').lower(): match = False
                if search_filter.get('interest') and search_filter['interest'] != c.get('interest'): match = False
                if search_filter.get('sentiment') and search_filter['sentiment'] != c.get('sentiment'): match = False
                if match: results.append(c)

        return jsonify({
            "success": True, 
            "answer": answer, 
            "results": results, 
            "count": len(results),
            "is_analysis": len(results) == 0
        })
    except Exception as e:
        logger.error(f"AI Assistant error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# --- NEW: DEDICATED SOURCE PAGES ---

@main_bp.route("/sources/gmail")
@login_required
def source_gmail():
    contacts = contact_service.get_contacts()
    gmail_signals = [c for c in contacts if (c.get('source') or '').lower() == 'gmail']
    messages = google_service.fetch_gmail_messages(max_results=10) if google_service.is_authenticated() else []
    
    return render_template("source_view.html", 
                           source_name="Gmail",
                           source_id="google",
                           brand_color="#ea4335",
                           signals=gmail_signals,
                           messages=messages,
                           icon="fab fa-google",
                           is_connected=google_service.is_authenticated())

@main_bp.route("/sources/whatsapp")
@login_required
def source_whatsapp():
    contacts = contact_service.get_contacts()
    wa_signals = [c for c in contacts if (c.get('source') or '').lower() == 'whatsapp']
    messages = whatsapp_service.fetch_messages() or []
    
    settings = db_service.get_settings()
    is_connected = True if settings.get('WHATSAPP_PHONE') or os.getenv("WHATSAPP_PHONE") else False
    
    return render_template("source_view.html", 
                           source_name="WhatsApp Business", 
                           source_id="whatsapp",
                           brand_color="#22c55e",
                           signals=wa_signals,
                           messages=messages,
                           icon="fab fa-whatsapp",
                           is_connected=is_connected)

@main_bp.route("/sources/outlook")
@login_required
def source_outlook():
    contacts = contact_service.get_contacts()
    outlook_signals = [c for c in contacts if (c.get('source') or '').lower() in ['outlook', 'teams', 'microsoft']]
    # Placeholder for Outlook messages as we currently use webhooks for Teams
    messages = [] 
    
    return render_template("source_view.html", 
                           source_name="Outlook / Teams", 
                           source_id="teams",
                           brand_color="#0088ff",
                           signals=outlook_signals,
                           messages=messages,
                           icon="fab fa-microsoft",
                           is_connected=True)

# --- NEW: ADDITIONAL PAGES ---

@main_bp.route("/activity")
@login_required
def activity():
    activity_data = db_service.get_recent_activity(limit=100)
    return render_template("activity.html", activity=activity_data)

@main_bp.route("/pipeline")
@login_required
def pipeline():
    contacts = contact_service.get_contacts()
    return render_template("pipeline.html", contacts=contacts)

@main_bp.route("/ai-engine")
@login_required
def ai_engine():
    return render_template("ai_engine.html")

@main_bp.route("/google-auth")
@login_required
def google_auth():
    redirect_uri = url_for('main.google_auth_callback', _external=True)
    logger.info(f"Initiating Google Auth with Redirect URI: {redirect_uri}")
    auth_url, state = google_service.get_auth_url(redirect_uri)
    session['google_auth_state'] = state
    return redirect(auth_url)

@main_bp.route("/google-auth-callback")
def google_auth_callback():
    state = session.get('google_auth_state')
    logger.info(f"Received Google Auth Callback. State in session: {'Yes' if state else 'No'}")
    if not state:
        return redirect(url_for('main.settings', error="State mismatch in Google Auth."))
    
    redirect_uri = url_for('main.google_auth_callback', _external=True)
    logger.info(f"Fetching Token with Redirect URI: {redirect_uri}")
    try:
        google_service.fetch_token(request.url, state, redirect_uri)
        return redirect(url_for('main.settings', success="Google account connected successfully!"))
    except Exception as e:
        logger.error(f"Google Auth Callback Failed: {e}")
        return redirect(url_for('main.settings', error=f"Auth failed: {str(e)}"))

# --- STATIC & SYSTEM ---

# --- DEPRECATED SYSTEM ROUTES (MOVED TO APP ROOT) ---
# Routes for favicon, manifest, and service-worker are now handled in app/__init__.py
# to ensure consistent access across all authentication states.
