import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from flask import current_app

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/calendar.readonly']

class GoogleService:
    def __init__(self):
        self.creds = None
        self._load_creds()

    def _load_creds(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

    def is_authenticated(self):
        return self.creds and self.creds.valid

    def get_flow(self, redirect_uri=None):
        client_config = {
            "web": {
                "client_id": current_app.config.get('GOOGLE_CLIENT_ID'),
                "client_secret": current_app.config.get('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        return flow

    def get_auth_url(self, redirect_uri):
        flow = self.get_flow(redirect_uri=redirect_uri)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url, state

    def fetch_token(self, authorization_response, state, redirect_uri):
        flow = self.get_flow(redirect_uri=redirect_uri)
        flow.fetch_token(authorization_response=authorization_response)
        self.creds = flow.credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(self.creds, token)
        return self.creds

    def fetch_gmail_messages(self, query="is:unread", max_results=5):
        if not self.creds: 
            return []
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            detailed_messages = []
            for msg in messages:
                m = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                headers = m.get('payload', {}).get('headers', [])
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                # Extract body
                body = ""
                payload = m.get('payload', {})
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            import base64
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                elif 'body' in payload and payload['body'].get('data'):
                    import base64
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
                
                if not body:
                    body = m.get('snippet', '')

                detailed_messages.append({
                    'id': m['id'],
                    'from': from_email,
                    'text': body,
                    'snippet': m.get('snippet', ''),
                    'source': 'gmail'
                })
            return detailed_messages
        except Exception as e:
            print(f"Gmail fetch error: {e}")
            return []

    def fetch_calendar_events(self, max_results=10):
        if not self.creds: return []
        service = build('calendar', 'v3', credentials=self.creds)
        events_result = service.events().list(calendarId='primary', maxResults=max_results).execute()
        return events_result.get('items', [])

google_service = GoogleService()
