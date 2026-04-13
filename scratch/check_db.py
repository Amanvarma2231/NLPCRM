import sqlite3
import os

def check_db():
    db_path = 'nlpcrm.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} does not exist.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables found: {', '.join(tables)}")
        
        required_tables = ['contacts_v2', 'contact_emails', 'contact_phones', 'activities_v2']
        missing = [t for t in required_tables if t not in tables]
        
        if missing:
            print(f"Missing tables: {', '.join(missing)}")
        else:
            print("All core CRM tables are present.")
            
        conn.close()
    except Exception as e:
        print(f"DB Check Failed: {e}")

if __name__ == "__main__":
    check_db()
