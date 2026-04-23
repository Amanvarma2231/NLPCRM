import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.email_service import email_service
from app.services.db_service import db_service

def verify_directly():
    print("Loading .env...")
    load_dotenv()
    
    print(f"SMTP User: {os.getenv('SMTP_USER')}")
    # We won't print the password for safety, but check if it exists
    print(f"SMTP Password exists: {bool(os.getenv('SMTP_PASSWORD'))}")
    
    print("\nTesting SMTP Connection...")
    smtp_ok, smtp_msg = email_service.test_smtp_connection()
    print(f"SMTP Result: {'SUCCESS' if smtp_ok else 'FAILED'}")
    print(f"Message: {smtp_msg}")
    
    print("\nTesting POP3 Connection...")
    pop3_ok, pop3_msg = email_service.test_pop3_connection()
    print(f"POP3 Result: {'SUCCESS' if pop3_ok else 'FAILED'}")
    print(f"Message: {pop3_msg}")

if __name__ == "__main__":
    verify_directly()
