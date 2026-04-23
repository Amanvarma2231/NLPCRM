
import sys
import os

# Add the project root to sys.path to allow importing from 'app'
sys.path.append(os.getcwd())

from app.services.email_service import email_service

def test_connections():
    print("--- Testing SMTP Connection ---")
    smtp_ok, smtp_msg = email_service.test_smtp_connection()
    print(f"SMTP Status: {'SUCCESS' if smtp_ok else 'FAILED'}")
    print(f"Message: {smtp_msg}")

    print("\n--- Testing POP3 Connection ---")
    pop3_ok, pop3_msg = email_service.test_pop3_connection()
    print(f"POP3 Status: {'SUCCESS' if pop3_ok else 'FAILED'}")
    print(f"Message: {pop3_msg}")

    if smtp_ok and pop3_ok:
        print("\nAll email systems are operational!")
    else:
        print("\nOne or more email systems failed. Check your credentials in .env or Settings.")

if __name__ == "__main__":
    test_connections()
