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
        
        known = {"name", "company", "job_title", "source", "interest", "email", "phone", "email2", "social_media"}
        extra = {k: v for k, v in contact_data.items() if k not in known}
        extra_json = json.dumps(extra) if extra else ""

        # --- Smart Deduplication Logic ---
        existing_id = None
        
        if primary_email:
            cursor = self._execute("SELECT contact_id FROM contact_emails WHERE email = ?", (primary_email,))
            if cursor and cursor.rowcount == -1: # SQLite rowcount is -1 for SELECT, use fetchone
                row = cursor.fetchone()
                if row: existing_id = row[0]
                
        if not existing_id and primary_phone:
            cursor = self._execute("SELECT contact_id FROM contact_phones WHERE phone = ?", (primary_phone,))
            if cursor:
                row = cursor.fetchone()
                if row: existing_id = row[0]
                
        if existing_id:
            # Merge Logic: Update empty fields
            logger.info(f"Duplicate found for {primary_email} / {primary_phone}. Merging into contact {existing_id}.")
            
            # Fetch existing to avoid overwriting good data with empty strings
            cursor = self._execute("SELECT name, company, job_title, interest FROM contacts_v2 WHERE id = ?", (existing_id,))
            if cursor:
                ex_name, ex_comp, ex_job, ex_int = cursor.fetchone()
                
                upd_name = name if name and not ex_name else ex_name
                upd_comp = company if company and not ex_comp else ex_comp
                upd_job = job_title if job_title and not ex_job else ex_job
                
                # Update Interest only if it's better/changed (Simplistic check)
                upd_int = interest if interest and interest != "New" else ex_int
                
                self._execute("""
                    UPDATE contacts_v2 
                    SET name=?, company=?, job_title=?, interest=?, updated_at=?, source=?
                    WHERE id=?
                """, (upd_name, upd_comp, upd_job, upd_int, now, source, existing_id))
            
            contact_id = existing_id
        else:
            # Insert New Contact
            res = self._execute("""
                INSERT INTO contacts_v2 (name, company, job_title, source, interest, extra, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, company, job_title, source, interest, extra_json, now, now))
            
            if not res: return False
            contact_id = res.lastrowid
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
            SELECT id, name, company, job_title, source, interest, created_at, updated_at
            FROM contacts_v2
            ORDER BY datetime(created_at) DESC
        """)
        if not cursor: return []
        
        results = []
        for row in cursor.fetchall():
            c_id, name, company, job_title, source, interest, created_at, updated_at = row
            
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
                "social_media": json.dumps(social_list)
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

contact_service = ContactService()
