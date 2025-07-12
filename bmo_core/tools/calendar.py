# bmo_core/tools/calendar.py
import datetime
from langchain.tools import tool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Se o token.json existir, ele reutiliza. Se não, ele pede autenticação.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    """Autentica e retorna o objeto de serviço do Google Calendar."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

@tool
def get_next_appointment() -> str:
    """
    Verifica e retorna o próximo compromisso na agenda do Google Calendar.
    """
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indica UTC
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=1, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            return "Bip bop! Sua agenda está livre como um passarinho!"
        
        event = events[0]
        start = event['start'].get('dateTime', event['start'].get('date'))
        return f"Seu próximo compromisso é: '{event['summary']}' em {start}."
    except Exception as e:
        return f"Oh não! Tive um problema ao olhar sua agenda: {e}"