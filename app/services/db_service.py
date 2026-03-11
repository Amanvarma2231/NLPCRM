import os
import json
import sqlitecloud
import logging
import datetime
import threading
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DBService")

SQLITE_CLOUD_URL = os.getenv("SQLITE_CLOUD_URL", "")

class DBService:
    def __init__(self):
        self._local = threading.local()

    @property
    def _conn(self):
        return getattr(self._local, 'conn', None)

    @_conn.setter
    def _conn(self, value):
        self._local.conn = value

    @property
    def _connected(self):
        return getattr(self._local, 'connected', False)

    @_connected.setter
    def _connected(self, value):
        self._local.connected = value

    def _connect(self):
        if self._connected and self._conn:
            try:
                # Health check
                self._conn.execute("SELECT 1")
                return True
            except Exception as e:
                logger.warning(f"Connection lost, re-establishing... ({e})")
                self._connected = False
                self._conn = None

        if not SQLITE_CLOUD_URL or "REPLACE_WITH" in SQLITE_CLOUD_URL:
            logger.warning("SQLITE_CLOUD_URL not configured in environment variables.")
            return False
            
        try:
            logger.info(f"Attempting to connect to SQLite Cloud...")
            self._conn = sqlitecloud.connect(SQLITE_CLOUD_URL)
            self._setup_tables()
            self._connected = True
            logger.info("Successfully connected to SQLite Cloud node.")
            return True
        except Exception as e:
            logger.error(f"FATAL: SQLite Cloud connection failed. Error: {str(e)}")
            # If it's a socket error, it might be transient or network related
            if "socket" in str(e).lower():
                logger.error("Network/Socket initialization error. Please check your firewall and internet connection.")
            self._connected = False
            return False

    def _setup_tables(self):
        """Create tables if they don't exist and ensure they have necessary columns."""
        cursor = self._conn.cursor()
        
        # Contacts table with created_at
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                name TEXT,
                phone TEXT,
                email2 TEXT,
                social_media TEXT,
                company TEXT,
                interest TEXT,
                extra TEXT,
                created_at TEXT
            )
        """)
        
        # New v2 schema tables for proper CRM structure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                company TEXT,
                job_title TEXT,
                source TEXT,
                interest TEXT,
                extra TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                label TEXT,
                email TEXT,
                is_primary BOOLEAN,
                FOREIGN KEY(contact_id) REFERENCES contacts_v2(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_phones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                label TEXT,
                phone TEXT,
                is_primary BOOLEAN,
                FOREIGN KEY(contact_id) REFERENCES contacts_v2(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_socials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                platform TEXT,
                url_handle TEXT,
                FOREIGN KEY(contact_id) REFERENCES contacts_v2(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                type TEXT,
                description TEXT,
                timestamp TEXT,
                FOREIGN KEY(contact_id) REFERENCES contacts_v2(id) ON DELETE CASCADE
            )
        """)
        
        # Interactions table with timestamp
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_email TEXT,
                type TEXT,
                content TEXT,
                timestamp TEXT
            )
        """)
        
        cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                summary TEXT,
                timestamp TEXT
            )
        """)
        
        # Migrations/Patch: Check if created_at exists in contacts
        try:
            cursor.execute("SELECT created_at FROM contacts LIMIT 1")
        except Exception:
            logger.info("Adding created_at column to contacts table")
            cursor.execute("ALTER TABLE contacts ADD COLUMN created_at TEXT")
            
        self._conn.commit()

    def add_contact(self, contact_data):
        if not self._connect(): return None
        try:
            cursor = self._conn.cursor()
            email = contact_data.get("email", "").strip()
            if not email: return False
            
            name = contact_data.get("name", "")
            phone = contact_data.get("phone", "")
            email2 = contact_data.get("email2", "[]")
            social_media = contact_data.get("social_media", "[]")
            company = contact_data.get("company", "")
            interest = contact_data.get("interest", "")
            
            known = {"email", "name", "phone", "email2", "social_media", "company", "interest", "created_at"}
            extra = {k: v for k, v in contact_data.items() if k not in known}
            extra_json = json.dumps(extra) if extra else ""
            
            now = datetime.datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO contacts (email, name, phone, email2, social_media, company, interest, extra, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    name=excluded.name,
                    phone=excluded.phone,
                    email2=excluded.email2,
                    social_media=excluded.social_media,
                    company=excluded.company,
                    interest=excluded.interest,
                    extra=excluded.extra
            """, (email, name, phone, email2, social_media, company, interest, extra_json, now))
            self._conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to add contact: {e}")
            return False

    def get_contacts(self):
        if not self._connect(): return []
        try:
            cursor = self._conn.cursor()
            # Use specific columns to avoid index confusion
            cursor.execute("SELECT email, name, phone, email2, social_media, company, interest, extra, created_at FROM contacts")
            rows = cursor.fetchall()
            contacts = []
            for row in rows:
                try:
                    # Defensive mapping to avoid index errors if SQLite Cloud returns rows differently
                    c = {
                        "email": row[0],
                        "name": row[1],
                        "phone": row[2],
                        "email2": row[3],
                        "social_media": row[4],
                        "company": row[5],
                        "interest": row[6],
                        "extra": row[7],
                        "created_at": row[8]
                    }
                    
                    # Merge extra data if it exists and is valid JSON
                    if c.get("extra"):
                        try:
                            extra_data = json.loads(c["extra"])
                            if isinstance(extra_data, dict):
                                c.update(extra_data)
                        except (json.JSONDecodeError, TypeError):
                            logger.warning(f"Failed to parse extra JSON for {c['email']}")
                    
                    contacts.append(c)
                except Exception as row_error:
                    logger.error(f"Error processing contact row: {row_error}")
                    continue
                    
            return contacts
        except Exception as e:
            logger.error(f"Failed to get contacts: {e}", exc_info=True)
            return []

    def save_setting(self, key, value):
        if not self._connect(): return
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, value))
            self._conn.commit()
        except Exception as e:
            logger.error(f"Failed to save setting: {e}")

    def get_settings(self):
        if not self._connect(): return {}
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            return {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"Failed to get settings: {e}")
            return {}

    def delete_contact(self, email):
        if not self._connect(): return False
        try:
            cursor = self._conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE email = ?", (email,))
            cursor.execute("DELETE FROM interactions WHERE contact_email = ?", (email,))
            self._conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete contact: {e}")
            return False

    def add_interaction(self, contact_email, type, content):
        if not self._connect(): return
        try:
            timestamp = datetime.datetime.now().isoformat()
            cursor = self._conn.cursor()
            cursor.execute("""
                INSERT INTO interactions (contact_email, type, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (contact_email, type, content, timestamp))
            self._conn.commit()
        except Exception as e:
            logger.error(f"Failed to add interaction: {e}")

    def get_recent_activity(self, limit=100):
        if not self._connect(): return []
        try:
            cursor = self._conn.cursor()
            # Consistent sorting by timestamp
            cursor.execute("""
                SELECT 'interaction' as type, contact_email, type as sub_type, content, timestamp 
                FROM interactions 
                UNION ALL
                SELECT 'new_contact' as type, email, 'SYSTEM' as sub_type, name || ' was added to CRM', created_at as timestamp
                FROM contacts
                WHERE created_at IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return []

    def get_entities(self):
        if not self._connect(): return []
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                SELECT company, COUNT(*) as lead_count 
                FROM contacts 
                WHERE company IS NOT NULL AND company != '' 
                GROUP BY company 
                ORDER BY lead_count DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get entities: {e}")
            return []

db_service = DBService()
