"""
Simple Email Test - SMTP Only
Tests email sending without POP3/IMAP complications
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_smtp_only():
    """Test SMTP email sending only"""
    print("\n" + "="*60)
    print("  NLPCRM - Simple Email Test (SMTP Only)")
    print("="*60)
    
    from app.services.email_service import email_service
    
    # Check configuration
    print("\n[1/2] Checking SMTP Configuration...")
    config = email_service._get_config()
    print(f"   Host: {config['smtp_host']}")
    print(f"   Port: {config['smtp_port']}")
    print(f"   User: {config['smtp_user']}")
    print(f"   TLS: {config['smtp_use_tls']}")
    
    # Test connection
    print("\n[2/2] Testing SMTP Connection...")
    ok, msg = email_service.test_smtp_connection()
    if ok:
        print(f"   [OK] {msg}")
        print("\n" + "="*60)
        print("  SUCCESS! Email service is working!")
        print("="*60)
        print("\n  You can now:")
        print("    1. Send emails from NLPCRM")
        print("    2. Start the application: python run.py")
        print("    3. Access: http://localhost:5000")
        print("\n")
        return True
    else:
        print(f"   [FAIL] {msg}")
        print("\n" + "="*60)
        print("  ERROR! Check your email credentials")
        print("="*60)
        print("\n  Fix:")
        print("    1. Check SMTP_USER and SMTP_PASSWORD in .env")
        print("    2. Use App Password (not regular password)")
        print("    3. Enable 2-Step Verification in Google Account")
        print("\n")
        return False

if __name__ == "__main__":
    sys.exit(0 if test_smtp_only() else 1)
