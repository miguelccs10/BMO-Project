# bmo_core/tools/calendar.py 
# Versão Correta para "Desktop App"

import datetime
import os
import traceback
from langchain.tools import tool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_service():
    """
    Autentica com a API do Google Calendar usando o fluxo padrão para apps de desktop
    e retorna um objeto de serviço para interagir com a API.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # --- ESTE É O FLUXO CORRETO PARA CREDENCIAIS DE DESKTOP ---
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build('calendar', 'v3', credentials=creds)

@tool
def get_next_appointment() -> str:
    """
    Verifica e retorna o próximo compromisso na agenda principal do Google Calendar.
    """
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=1, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            return "Sua agenda está livre como um passarinho!"
        
        event = events[0]
        start_info = event['start'].get('dateTime', event['start'].get('date'))
        try:
            dt_obj = datetime.datetime.fromisoformat(start_info.replace('Z', '+00:00'))
            formatted_start = dt_obj.strftime('%d de %B às %H:%M')
        except:
            formatted_start = start_info

        return f"Seu próximo compromisso é: '{event['summary']}' em {formatted_start}."
    except Exception as e:
        print(f"❌ ERRO ao buscar evento no Google Calendar: {e}")
        traceback.print_exc()
        return f"Oh não! Tive um problema ao olhar sua agenda: {e}"