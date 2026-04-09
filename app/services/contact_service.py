import json
import logging
import datetime
from app.services.db_service import db_service

logger = logging.getLogger("ContactService")

class ContactService:
    def _execute(self, query, params=()):
        if not db_service._connect(): return None
        try:
            cursor = db_service._conn.cursor()
            cursor.execute(query, params)
            db_service._conn.commit()
            return cursor
        except Exception as e:
            logger.error(f"DB Error: {e} - Query: {query}")
            return None

    def migrate_legacy_contacts(self):
        """Migrate from old contacts table to contacts_v2 if needed"""
        if not db_service._connect(): return
        
        # Check if we already migrated
        cursor = self._execute("SELECT count(*) FROM contacts_v2")
        if cursor and cursor.fetchone()[0] > 0:
            return
            
        logger.info("Starting migration of legacy contacts to v2 schema...")
        legacy_cursor = self._execute("SELECT id, email, name, phone, email2, social_media, company, interest, extra, created_at FROM contacts")
        if not legacy_cursor: return
        
        legacy_contacts = legacy_cursor.fetchall()
        for row in legacy_contacts:
            c_id, email, name, phone, email2, social_media, company, interest, extra, created_at = row
            
            # Insert into v2
            res = self._execute("""
                INSERT INTO contacts_v2 (name, company, source, interest, extra, created_at, updated_at) 
                VALUES (?, ?, 'Legacy', ?, ?, ?, ?)
            """, (name, company, interest, extra, created_at, created_at))
            
            if not res: continue
            new_id = res.lastrowid
            
            # Insert Primary Email
            if email:
                self._execute("INSERT INTO contact_emails (contact_id, label, email, is_primary) VALUES (?, 'Primary', ?, 1)", (new_id, email))
            
            # Insert Extra Emails
            try:
                if email2 and email2 != "[]":
                    extra_em = json.loads(email2)
                    for e in extra_em:
                        self._execute("INSERT INTO contact_emails (contact_id, label, email, is_primary) VALUES (?, ?, ?, 0)", (new_id, e.get("label", "Other"), e.get("value")))
            except Exception: pass
            
            # Insert Primary Phone
            if phone:
                self._execute("INSERT INTO contact_phones (contact_id, label, phone, is_primary) VALUES (?, 'Primary', ?, 1)", (new_id, phone))
                
            # Insert Socials
            try:
                if social_media and social_media != "[]":
                    socials = json.loads(social_media)
                    for s in socials:
                        self._execute("INSERT INTO contact_socials (contact_id, platform, url_handle) VALUES (?, ?, ?)", (new_id, s.get("label", "Platform"), s.get("value")))
            except Exception: pass
            
        logger.info(f"Successfully migrated {len(legacy_contacts)} contacts to v2 schema.")

    def add_contact(self, contact_data):
        """Add or Update a contact cleanly using the v2 schema with Smart Deduplication"""
        now = datetime.datetime.now().isoformat()
        
        name = contact_data.get("name", "")
        company = contact_data.get("company", "")
        job_title = contact_data.get("job_title", "")
        source = contact_data.get("source", "Manual")
        interest = contact_data.get("interest", "New")
        
        primary_email = contact_data.get("email", "").strip()
        primary_phone = contact_data.get("phone", "").strip()
        
        sentiment = contact_data.get("sentiment", "Neutral")
        importance_score = contact_data.get("importance_score", 0)
        urgency = contact_data.get("urgency", "Low")
        summary = contact_data.get("summary", "")
        
        known = {"name", "company", "job_title", "source", "interest", "email", "phone", "email2", "social_media", "sentiment", "importance_score", "urgency", "summary"}
        extra = {k: v for k, v in contact_data.items() if k not in known}
        extra_json = json.dumps(extra) if extra else ""

        # --- Smart Deduplication & Merging Logic ---
        existing_id = None
        
        # Check by Email
        if primary_email:
            cursor = self._execute("SELECT contact_id FROM contact_emails WHERE email = ?", (primary_email,))
            if cursor:
                row = cursor.fetchone()
                if row: existing_id = row[0]
                
        # Check by Phone if Email didn't match
        if not existing_id and primary_phone:
            cursor = self._execute("SELECT contact_id FROM contact_phones WHERE phone = ?", (primary_phone,))
            if cursor:
                row = cursor.fetchone()
                if row: existing_id = row[0]
                
        if existing_id:
            logger.info(f"Existing entity found (ID: {existing_id}). Merging incoming intelligence from {source}.")
            
            cursor = self._execute("SELECT name, company, job_title, interest, sentiment, importance_score, urgency, summary, source FROM contacts_v2 WHERE id = ?", (existing_id,))
            if cursor:
                row = cursor.fetchone()
                if row:
                    ex_name, ex_comp, ex_job, ex_int, ex_sent, ex_imp, ex_urg, ex_sum, ex_src = row
                    
                    # Merge Strategy: Prefer new data if existing is empty
                    upd_name = name if name and (not ex_name or len(ex_name) < 2) else ex_name
                    upd_comp = company if company and (not ex_comp or len(ex_comp) < 2) else ex_comp
                    upd_job = job_title if job_title and not ex_job else ex_job
                    
                    # Sentiment/Priority: Upgrade if new is more significant
                    upd_sent = sentiment if sentiment and sentiment != "Neutral" else ex_sent
                    upd_urg = urgency if urgency and urgency != "Low" else ex_urg
                    
                    try:
                        new_score = float(importance_score or 0)
                        old_score = float(ex_imp or 0)
                        upd_imp = max(new_score, old_score)
                    except: upd_imp = ex_imp
                    
                    # Summary: Append if different
                    upd_sum = ex_sum
                    if summary and summary not in (ex_sum or ""):
                        upd_sum = f"{ex_sum}\n---\n{summary}" if ex_sum else summary
                        
                    # Source Tracking
                    upd_src = ex_src
                    if source and source not in (ex_src or ""):
                        upd_src = f"{ex_src}, {source}" if ex_src else source
                        
                    self._execute("""
                        UPDATE contacts_v2 
                        SET name=?, company=?, job_title=?, updated_at=?, source=?, sentiment=?, importance_score=?, urgency=?, summary=?
                        WHERE id=?
                    """, (upd_name, upd_comp, upd_job, now, upd_src[:200] if upd_src else upd_src, upd_sent, upd_imp, upd_urg, (upd_sum or '')[:1000], existing_id))
            contact_id = existing_id
        else:
            # Insert New Contact
            res = self._execute("""
                INSERT INTO contacts_v2 (name, company, job_title, source, interest, extra, created_at, updated_at, sentiment, importance_score, urgency, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, company, job_title, source, interest, extra_json, now, now, sentiment, importance_score, urgency, summary))
            if not res: return False
            contact_id = res.lastrowid
        
        # Emails
        if primary_email:
            check = self._execute("SELECT id FROM contact_emails WHERE contact_id=? AND email=?", (contact_id, primary_email))
            if check and not check.fetchone():
                self._execute("INSERT INTO contact_emails (contact_id, label, email, is_primary) VALUES (?, 'Primary', ?, 1)", (contact_id, primary_email))
            
        email2 = contact_data.get("email2", "[]")
        try:
            extra_em = json.loads(email2)
            for e in extra_em:
                if e.get("value"):
                    check = self._execute("SELECT id FROM contact_emails WHERE contact_id=? AND email=?", (contact_id, e.get("value")))
                    if check and not check.fetchone():
                         self._execute("INSERT INTO contact_emails (contact_id, label, email, is_primary) VALUES (?, ?, ?, 0)", (contact_id, e.get("label", "Other"), e.get("value")))
        except Exception: pass

        # Phones
        if primary_phone:
            check = self._execute("SELECT id FROM contact_phones WHERE contact_id=? AND phone=?", (contact_id, primary_phone))
            if check and not check.fetchone():
                self._execute("INSERT INTO contact_phones (contact_id, label, phone, is_primary) VALUES (?, 'Primary', ?, 1)", (contact_id, primary_phone))

        # Socials
        social_media = contact_data.get("social_media", "[]")
        try:
            socials = json.loads(social_media)
            for s in socials:
                if s.get("value"):
                    self._execute("INSERT INTO contact_socials (contact_id, platform, url_handle) VALUES (?, ?, ?)", (contact_id, s.get("label", "Social"), s.get("value")))
        except Exception: pass
        
        # Action Log
        if existing_id:
            self.log_activity(contact_id, "contact_updated", f"Contact automatically merged with new data from {source}")
        else:
            self.log_activity(contact_id, "contact_created", f"Contact added via {source}")
        return True

    def get_contacts(self):
        """Retrieve all contacts mapped back to the structured format required by the UI"""
        cursor = self._execute("""
            SELECT id, name, company, job_title, source, interest, created_at, updated_at, sentiment, importance_score, urgency, summary
            FROM contacts_v2
            ORDER BY datetime(created_at) DESC
        """)
        if not cursor: return []
        
        results = []
        for row in cursor.fetchall():
            c_id, name, company, job_title, source, interest, created_at, updated_at, sentiment, importance_score, urgency, summary = row
            
            # Fetch associative data
            emails_cur = self._execute("SELECT label, email, is_primary FROM contact_emails WHERE contact_id = ?", (c_id,))
            emails = emails_cur.fetchall() if emails_cur else []
            primary_email = next((e[1] for e in emails if e[2]), (emails[0][1] if emails else ""))
            extra_emails = [{"label": e[0], "value": e[1]} for e in emails if not e[2]]
            
            phones_cur = self._execute("SELECT label, phone, is_primary FROM contact_phones WHERE contact_id = ?", (c_id,))
            phones = phones_cur.fetchall() if phones_cur else []
            primary_phone = next((p[1] for p in phones if p[2]), (phones[0][1] if phones else ""))
            
            socials_cur = self._execute("SELECT platform, url_handle FROM contact_socials WHERE contact_id = ?", (c_id,))
            socials = socials_cur.fetchall() if socials_cur else []
            social_list = [{"label": s[0], "value": s[1]} for s in socials]

            results.append({
                "id": c_id,
                "name": name,
                "company": company,
                "job_title": job_title,
                "source": source,
                "interest": interest,
                "created_at": created_at,
                "email": primary_email,
                "phone": primary_phone,
                "email2": json.dumps(extra_emails),
                "social_media": json.dumps(social_list),
                "sentiment": sentiment,
                "importance_score": importance_score,
                "urgency": urgency,
                "summary": summary
            })
        return results

    def delete_contact(self, email):
        """Delete by primary email"""
        # First find the contact_id for the given email
        cursor = self._execute("SELECT contact_id FROM contact_emails WHERE email = ? AND is_primary = 1", (email,))
        if cursor:
            row = cursor.fetchone()
            if row:
                c_id = row[0]
                self._execute("DELETE FROM contacts_v2 WHERE id = ?", (c_id,))
                return True
        return False
        
    def log_activity(self, contact_id, activity_type, description):
        now = datetime.datetime.now().isoformat()
        self._execute("""
            INSERT INTO activities_v2 (contact_id, type, description, timestamp)
            VALUES (?, ?, ?, ?)
        """, (contact_id, activity_type, description, now))

    def get_context_summary(self):
        """Returns a string summary of all contacts for AI context."""
        contacts = self.get_contacts()
        if not contacts:
            return "No contacts found in the database."
        
        total = len(contacts)
        sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}
        interest_counts = {"High": 0, "Medium": 0, "Low": 0, "Support": 0, "New": 0}
        companies = set()
        
        for c in contacts:
            s = c.get('sentiment', 'Neutral')
            if s in sentiment_counts: sentiment_counts[s] += 1
            i = c.get('interest', 'New')
            if i in interest_counts: interest_counts[i] += 1
            if c.get('company'): companies.add(c.get('company'))
            
        summary = f"Total Leads: {total} in CRM.\n"
        summary += f"Sentiment Profile: {sentiment_counts['Positive']} Positive, {sentiment_counts['Negative']} Negative, {sentiment_counts['Neutral']} Neutral.\n"
        summary += f"Interest Profile: {interest_counts['High']} High, {interest_counts['Medium']} Medium, {interest_counts['Low']} Low.\n"
        summary += f"Organizations Represented: {len(companies)} companies.\n"
        
        # Add snippets of top 5 high impact leads
        high_impact = [c for c in contacts if float(c.get('importance_score') or 0) >= 8][:5]
        if high_impact:
            summary += "Top High Impact Leads:\n"
            for c in high_impact:
                summary += f"- {c.get('name')} ({c.get('company')}): Score {c.get('importance_score')}. Summary: {c.get('summary')}\n"
        
        return summary

contact_service = ContactService()
