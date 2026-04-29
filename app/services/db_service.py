import os
import json
import sqlitecloud
import sqlite3
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
            logger.warning("SQLITE_CLOUD_URL not configured. Using local SQLite.")
            return self._connect_local()
            
        try:
            logger.info(f"Connecting to SQLite Cloud...")
            # Set a 5-second timeout for the initial connection to avoid hangs
            self._conn = sqlitecloud.connect(SQLITE_CLOUD_URL)
            self._setup_tables()
            self._connected = True
            return True
        except Exception as e:
            msg = str(e)
            if "timeout" in msg.lower() or "connection" in msg.lower() or "paused" in msg.lower():
                logger.warning(f"SQLite Cloud connection issue: {e}. Falling back to local DB.")
            else:
                logger.warning(f"SQLite Cloud failed: {e}. Falling back...")
            return self._connect_local()

    def _connect_local(self):
        try:
            self._conn = sqlite3.connect("nlpcrm.db", check_same_thread=False)
            self._setup_tables()
            self._connected = True
            logger.info("Connected to local SQLite.")
            return True
        except Exception as local_e:
            logger.error(f"FATAL: All database connections failed: {local_e}")
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
                sentiment TEXT,
                importance_score REAL,
                urgency TEXT,
                summary TEXT,
                extra TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Schema Patch: Add intelligence columns to contacts_v2 if they don't exist
        for col, dtype in [('sentiment', 'TEXT'), ('importance_score', 'REAL'), ('urgency', 'TEXT'), ('summary', 'TEXT')]:
            try:
                cursor.execute(f"ALTER TABLE contacts_v2 ADD COLUMN {col} {dtype}")
                logger.info(f"Schema Patch: Added {col} to contacts_v2")
            except Exception:
                pass # Already exists or table was just created with them
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
        """DEPRECATED: Use ContactService.add_contact for v2 schema support."""
        logger.warning("DBService.add_contact is deprecated. Use ContactService.add_contact instead.")
        if not self._connect(): return None
        # ... (keeping implementation for backward compatibility if needed, but steering away)

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
            cursor.execute("""
                SELECT 'activity' as type, c.name as ref, a.type as sub_type, a.description, a.timestamp 
                FROM activities_v2 a
                LEFT JOIN contacts_v2 c ON a.contact_id = c.id
                ORDER BY a.timestamp DESC
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
                FROM contacts_v2 
                WHERE company IS NOT NULL AND company != '' 
                GROUP BY company 
                ORDER BY lead_count DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"Failed to get entities: {e}")
            return []

db_service = DBService()
