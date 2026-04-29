"""
email_service.py — SMTP + POP3 email integration for NLPCRM.

Send emails via SMTP (smtplib) and fetch inbox via POP3 (poplib).
No OAuth or Google credentials required — just standard email/password/server settings.
"""

import os
import smtplib
import poplib
import email as email_lib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header

from dotenv import load_dotenv
from app.services.db_service import db_service

load_dotenv()
logger = logging.getLogger("EmailService")


class EmailService:
    """Handles email send (SMTP) and receive (POP3) using plain credentials."""

    # ------------------------------------------------------------------ #
    #  Private helpers — read config from DB first, then fall back to env  #
    # ------------------------------------------------------------------ #

    def _get_config(self):
        """Return a config dict with SMTP and POP3 settings."""
        settings = db_service.get_settings()

        def _get(key, env_key=None, default=""):
            val = settings.get(key) or (os.getenv(env_key or key, default))
            return val or default

        return {
            # SMTP (sending)
            "smtp_host":     _get("SMTP_HOST",     default="smtp.gmail.com"),
            "smtp_port":     int(_get("SMTP_PORT",  default="587")),
            "smtp_user":     _get("SMTP_USER"),
            "smtp_password": _get("SMTP_PASSWORD"),
            "smtp_use_tls":  _get("SMTP_USE_TLS",  default="true").lower() == "true",

            # POP3 (receiving)
            "pop3_host":     _get("POP3_HOST",     default="pop.gmail.com"),
            "pop3_port":     int(_get("POP3_PORT",  default="995")),
            "pop3_user":     _get("POP3_USER"),
            "pop3_password": _get("POP3_PASSWORD"),
        }

    # ------------------------------------------------------------------ #
    #  Status helpers                                                       #
    # ------------------------------------------------------------------ #

    def is_configured(self):
        """True if both SMTP and POP3 credentials are set."""
        cfg = self._get_config()
        smtp_ready = bool(cfg["smtp_user"] and cfg["smtp_password"])
        pop3_ready = bool(cfg["pop3_user"] and cfg["pop3_password"])
        return smtp_ready and pop3_ready

    def get_status(self):
        """Returns a dict describing the current configuration state."""
        cfg = self._get_config()
        return {
            "smtp_configured": bool(cfg["smtp_user"] and cfg["smtp_password"]),
            "pop3_configured": bool(cfg["pop3_user"] and cfg["pop3_password"]),
            "smtp_user": cfg["smtp_user"],
            "pop3_user": cfg["pop3_user"],
            "smtp_host": cfg["smtp_host"],
            "pop3_host": cfg["pop3_host"]
        }

    def test_smtp_connection(self):
        """Try connecting to SMTP server and authenticating. Returns (ok, message)."""
        cfg = self._get_config()
        if not cfg["smtp_user"] or not cfg["smtp_password"]:
            return False, "SMTP credentials not configured."
        try:
            if cfg["smtp_use_tls"]:
                server = smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=10)
                server.ehlo()
                server.starttls()
                server.ehlo()
            else:
                server = smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"], timeout=10)
            server.login(cfg["smtp_user"], cfg["smtp_password"])
            server.quit()
            return True, f"SMTP connection OK ({cfg['smtp_host']}:{cfg['smtp_port']})"
        except Exception as e:
            logger.error(f"SMTP test failed: {e}")
            return False, str(e)

    def test_pop3_connection(self):
        """Try connecting to POP3 server and authenticating. Returns (ok, message)."""
        cfg = self._get_config()
        if not cfg["pop3_user"] or not cfg["pop3_password"]:
            return False, "POP3 credentials not configured."
        try:
            server = poplib.POP3_SSL(cfg["pop3_host"], cfg["pop3_port"], timeout=10)
            server.user(cfg["pop3_user"])
            server.pass_(cfg["pop3_password"])
            msg_count, _ = server.stat()
            server.quit()
            return True, f"POP3 connection OK — {msg_count} message(s) on server."
        except Exception as e:
            error_str = str(e)
            if "not enabled for POP access" in error_str:
                return False, "POP3 is disabled in your Gmail settings. Please enable it in Gmail > Settings > Forwarding and POP/IMAP."
            logger.error(f"POP3 test failed: {e}")
            return False, error_str


    # ------------------------------------------------------------------ #
    #  Sending                                                              #
    # ------------------------------------------------------------------ #

    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None):
        """Send an email via SMTP. Returns (ok: bool, message: str)."""
        cfg = self._get_config()
        if not cfg["smtp_user"] or not cfg["smtp_password"]:
            return False, "SMTP not configured."

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = cfg["smtp_user"]
            msg["To"] = to_email

            msg.attach(MIMEText(body, "plain"))
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            if cfg["smtp_use_tls"]:
                server = smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"], timeout=15)
                server.ehlo()
                server.starttls()
                server.ehlo()
            else:
                server = smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"], timeout=15)

            server.login(cfg["smtp_user"], cfg["smtp_password"])
            server.sendmail(cfg["smtp_user"], to_email, msg.as_string())
            server.quit()
            logger.info(f"Email sent to {to_email} | Subject: {subject}")
            return True, f"Email sent successfully to {to_email}"
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False, str(e)

    # ------------------------------------------------------------------ #
    #  Receiving via POP3                                                   #
    # ------------------------------------------------------------------ #

    def fetch_emails(self, max_count: int = 10):
        """
        Fetch recent emails from the POP3 inbox.
        Returns a list of dicts: {id, from, subject, text, snippet, source}.
        """
        cfg = self._get_config()
        if not cfg["pop3_user"] or not cfg["pop3_password"]:
            logger.warning("POP3 credentials not configured — skipping fetch.")
            return []

        messages = []
        try:
            server = poplib.POP3_SSL(cfg["pop3_host"], cfg["pop3_port"], timeout=15)
            server.user(cfg["pop3_user"])
            server.pass_(cfg["pop3_password"])

            msg_count, _ = server.stat()
            # Fetch the last `max_count` messages (most recent are at higher indices)
            start_index = max(1, msg_count - max_count + 1)

            for i in range(msg_count, start_index - 1, -1):
                try:
                    raw_lines = server.retr(i)[1]
                    raw_bytes = b"\r\n".join(raw_lines)
                    msg = email_lib.message_from_bytes(raw_bytes)

                    # Decode subject
                    subject_parts = decode_header(msg.get("Subject", "No Subject"))
                    subject = ""
                    for part, charset in subject_parts:
                        if isinstance(part, bytes):
                            subject += part.decode(charset or "utf-8", errors="ignore")
                        else:
                            subject += part

                    from_addr = msg.get("From", "Unknown")
                    body_text = self._extract_body(msg)

                    messages.append({
                        "id": str(i),
                        "from": from_addr,
                        "subject": subject,
                        "text": body_text[:2000],
                        "snippet": body_text[:200],
                        "source": "Email (POP3)"
                    })
                except Exception as msg_error:
                    logger.warning(f"Skipping message {i}: {msg_error}")

            server.quit()
            logger.info(f"Fetched {len(messages)} emails via POP3.")
            return messages

        except Exception as e:
            error_str = str(e)
            if "not enabled for POP access" in error_str:
                logger.error("POP3 fetch failed: POP access is not enabled in Gmail settings.")
            else:
                logger.error(f"POP3 fetch failed: {e}")
            return []


    def _extract_body(self, msg) -> str:
        """Extract plain-text body from an email.Message object."""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = str(part.get("Content-Disposition", ""))
                if content_type == "text/plain" and "attachment" not in disposition:
                    charset = part.get_content_charset() or "utf-8"
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(charset, errors="ignore")
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                body = payload.decode(charset, errors="ignore")

        return body.strip()


# Singleton instance
email_service = EmailService()
