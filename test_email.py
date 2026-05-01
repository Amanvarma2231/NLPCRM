"""
NLPCRM Email Service Test
Tests SMTP (sending) and POP3 (receiving) functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_smtp():
    """Test SMTP email sending"""
    print("\n" + "="*60)
    print("  Testing SMTP (Email Sending)")
    print("="*60)
    
    from app.services.email_service import email_service
    
    # Check configuration
    print("\n[1/3] Checking SMTP Configuration...")
    config = email_service._get_config()
    print(f"   Host: {config['smtp_host']}")
    print(f"   Port: {config['smtp_port']}")
    print(f"   User: {config['smtp_user']}")
    print(f"   TLS: {config['smtp_use_tls']}")
    
    # Test connection
    print("\n[2/3] Testing SMTP Connection...")
    ok, msg = email_service.test_smtp_connection()
    if ok:
        print(f"   [OK] {msg}")
    else:
        print(f"   [FAIL] {msg}")
        return False
    
    # Send test email
    print("\n[3/3] Sending Test Email...")
    to_email = input("   Enter recipient email (or press Enter to skip): ").strip()
    
    if to_email:
        subject = "NLPCRM Test Email"
        body = """Hello!

This is a test email from NLPCRM v3.1.

If you received this, your SMTP configuration is working perfectly!

Best regards,
NLPCRM System"""
        
        ok, msg = email_service.send_email(to_email, subject, body)
        if ok:
            print(f"   [OK] {msg}")
        else:
            print(f"   [FAIL] {msg}")
            return False
    else:
        print("   [SKIP] Test email sending skipped")
    
    return True

def test_pop3():
    """Test POP3 email receiving"""
    print("\n" + "="*60)
    print("  Testing POP3 (Email Receiving)")
    print("="*60)
    
    from app.services.email_service import email_service
    
    # Check configuration
    print("\n[1/3] Checking POP3 Configuration...")
    config = email_service._get_config()
    print(f"   Host: {config['pop3_host']}")
    print(f"   Port: {config['pop3_port']}")
    print(f"   User: {config['pop3_user']}")
    
    # Test connection
    print("\n[2/3] Testing POP3 Connection...")
    ok, msg = email_service.test_pop3_connection()
    if ok:
        print(f"   [OK] {msg}")
    else:
        print(f"   [FAIL] {msg}")
        print("\n   NOTE: If POP3 is disabled, enable it in Gmail:")
        print("   1. Go to Gmail Settings")
        print("   2. Click 'Forwarding and POP/IMAP'")
        print("   3. Enable POP for all mail")
        return False
    
    # Fetch emails
    print("\n[3/3] Fetching Recent Emails...")
    try:
        messages = email_service.fetch_emails(max_count=5)
        print(f"   [OK] Found {len(messages)} messages")
        
        if messages:
            print("\n   Recent Messages:")
            for i, msg in enumerate(messages[:3], 1):
                print(f"\n   {i}. From: {msg.get('from', 'Unknown')}")
                print(f"      Subject: {msg.get('subject', 'No Subject')}")
                print(f"      Snippet: {msg.get('snippet', '')[:80]}...")
        else:
            print("   [INFO] No messages in inbox")
        
        return True
    except Exception as e:
        print(f"   [FAIL] Error fetching emails: {e}")
        return False

def test_ai_extraction():
    """Test AI extraction from email"""
    print("\n" + "="*60)
    print("  Testing AI Lead Extraction from Email")
    print("="*60)
    
    from app.services.email_service import email_service
    from app.services.nlp_service import nlp_service
    import json
    
    print("\n[1/2] Fetching Latest Email...")
    try:
        messages = email_service.fetch_emails(max_count=1)
        if not messages:
            print("   [SKIP] No emails to process")
            return True
        
        msg = messages[0]
        print(f"   From: {msg.get('from')}")
        print(f"   Subject: {msg.get('subject')}")
        
        print("\n[2/2] Extracting Contact Information...")
        text = msg.get('text', '')
        if len(text) > 10:
            extracted = nlp_service.extract_contact_info(text, source='Email')
            print(f"   [OK] Extraction complete")
            print(f"\n   Extracted Data:")
            
            # Try to parse JSON
            try:
                start = extracted.find('{')
                end = extracted.rfind('}') + 1
                if start != -1 and end != -1:
                    data = json.loads(extracted[start:end])
                    for key, value in data.items():
                        if value:
                            print(f"      {key}: {value}")
            except:
                print(f"      {extracted[:200]}...")
        else:
            print("   [SKIP] Email too short for extraction")
        
        return True
    except Exception as e:
        print(f"   [FAIL] Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  NLPCRM Email Service Test Suite")
    print("="*60)
    
    # Test SMTP
    smtp_ok = test_smtp()
    
    # Test POP3
    pop3_ok = test_pop3()
    
    # Test AI Extraction
    if pop3_ok:
        ai_ok = test_ai_extraction()
    else:
        ai_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    print(f"  SMTP (Sending): {'[OK]' if smtp_ok else '[FAIL]'}")
    print(f"  POP3 (Receiving): {'[OK]' if pop3_ok else '[FAIL]'}")
    print(f"  AI Extraction: {'[OK]' if ai_ok else '[SKIP]'}")
    print("="*60)
    
    if smtp_ok and pop3_ok:
        print("\n[SUCCESS] Email service is fully functional!")
        print("\nYou can now:")
        print("  1. Send emails from NLPCRM")
        print("  2. Receive and analyze emails")
        print("  3. Extract leads automatically")
    else:
        print("\n[WARNING] Some tests failed. Check configuration.")
    
    print("\n")
    return smtp_ok and pop3_ok

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
