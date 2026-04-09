import os
import pickle
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("GoogleService")

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")


class GoogleService:
    def __init__(self):
        self.creds = None
        self._load_creds()

    def _load_creds(self):
        try:
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as f:
                    self.creds = pickle.load(f)
        except Exception as e:
            logger.warning(f"Could not load token: {e}")
            self.creds = None

    def is_authenticated(self):
        return bool(self.creds and getattr(self.creds, 'valid', False))

    def is_configured(self):
        return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

    def _get_flow(self, redirect_uri):
        from google_auth_oauthlib.flow import Flow
        client_config = {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        return Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri)

    def get_auth_url(self, redirect_uri):
        flow = self._get_flow(redirect_uri)
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='select_account'
        )
        return auth_url, state

    def fetch_token(self, authorization_response, state, redirect_uri):
        flow = self._get_flow(redirect_uri)
        flow.fetch_token(authorization_response=authorization_response)
        self.creds = flow.credentials
        with open('token.pickle', 'wb') as f:
            pickle.dump(self.creds, f)
        return self.creds

    def get_user_info(self):
        """Get logged-in Google user's email and name."""
        if not self.is_authenticated():
            return None
        try:
            from googleapiclient.discovery import build
            service = build('oauth2', 'v2', credentials=self.creds)
            info = service.userinfo().get().execute()
            return {
                'email': info.get('email', ''),
                'name': info.get('name', ''),
                'picture': info.get('picture', '')
            }
        except Exception as e:
            logger.error(f"get_user_info error: {e}")
            return None

    def fetch_gmail_messages(self, query="is:unread", max_results=5):
        if not self.is_authenticated():
            return []
        try:
            from googleapiclient.discovery import build
            import base64
            service = build('gmail', 'v1', credentials=self.creds)
            results = service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            messages = results.get('messages', [])
            detailed = []
            for msg in messages:
                m = service.users().messages().get(
                    userId='me', id=msg['id'], format='full'
                ).execute()
                headers = m.get('payload', {}).get('headers', [])
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
                body = ''
                payload = m.get('payload', {})
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain' and part.get('body', {}).get('data'):
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                            break
                elif payload.get('body', {}).get('data'):
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                if not body:
                    body = m.get('snippet', '')
                detailed.append({
                    'id': m['id'],
                    'from': from_email,
                    'text': body[:2000],
                    'snippet': m.get('snippet', ''),
                    'source': 'Gmail'
                })
            return detailed
        except Exception as e:
            logger.error(f"Gmail fetch error: {e}")
            return []


google_service = GoogleService()
