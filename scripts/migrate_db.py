import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.db_service import db_service

def migrate():
    print("Connecting to DB...")
    if not db_service._connect():
        print("Failed to connect.")
        return

    cursor = db_service._conn.cursor()
    cursor.execute("PRAGMA table_info(contacts)")
    columns = [row[1] for row in cursor.fetchall()]

    print(f"Current columns: {columns}")

    columns_to_add = {
        "email2": "TEXT",
        "social_media": "TEXT",
        "interest": "TEXT",
        "extra": "TEXT"
    }

    for col, col_type in columns_to_add.items():
        if col not in columns:
            print(f"Adding column {col}...")
            try:
                cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col} {col_type}")
                print(f"Added column {col}")
            except Exception as e:
                print(f"Failed to add {col}: {e}")
        else:
            print(f"Column {col} already exists.")

    db_service._conn.commit()
    print("Migration finished!")

if __name__ == "__main__":
    migrate()
