import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.email_service import email_service

def test_email_connections():
    print("Testing SMTP Connection...")
    ok_smtp, msg_smtp = email_service.test_smtp_connection()
    print(f"SMTP: {ok_smtp}, {msg_smtp}")

    print("\nTesting POP3 Connection...")
    ok_pop3, msg_pop3 = email_service.test_pop3_connection()
    print(f"POP3: {ok_pop3}, {msg_pop3}")

    if ok_smtp:
        print("\nSending Test Email...")
        ok_send, msg_send = email_service.send_email(
            to_email="amangurauli@gmail.com",
            subject="NLPCRM Test Email",
            body="This is a test email from NLPCRM to verify SMTP settings."
        )
        print(f"Send: {ok_send}, {msg_send}")

    if ok_pop3:
        print("\nFetching Emails...")
        emails = email_service.fetch_emails(max_count=3)
        print(f"Fetched {len(emails)} emails.")
        for i, email in enumerate(emails):
            print(f"[{i+1}] From: {email['from']}, Subject: {email['subject']}")

if __name__ == "__main__":
    test_email_connections()
