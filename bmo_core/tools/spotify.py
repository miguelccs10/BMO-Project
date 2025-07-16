# bmo_core/tools/spotify.py
# Ferramentas aprimoradas para controle do Spotify

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from langchain.tools import tool

# --- Configuração da Autenticação ---
# A autenticação agora solicita mais permissões para ler o estado da reprodução.
try:
    scope = "user-modify-playback-state,user-read-playback-state,user-read-currently-playing"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    print("✅ Conexão com a API do Spotify estabelecida.")
except Exception as e:
    print(f"❌ ERRO: Não foi possível conectar ao Spotify. Verifique as credenciais. Erro: {e}")
    sp = None

# --- Função Auxiliar ---
def get_active_device_id():
    """
    Encontra e retorna o ID do primeiro dispositivo Spotify ativo ou disponível.
    É uma função auxiliar, não uma ferramenta para o agente.
    """
    if not sp: return None
    
    try:
        devices_info = sp.devices()
        if not devices_info or not devices_info['devices']:
            print("⚠️  Aviso: Nenhum dispositivo Spotify foi encontrado na sua conta.")
            return None
        
        # Prioriza o dispositivo que já está ativo
        for device in devices_info['devices']:
            if device['is_active']:
                print(f"   Dispositivo ativo encontrado: {device['name']} (ID: {device['id']})")
                return device['id']
        
        # Se nenhum estiver ativo, pega o primeiro da lista como fallback
        first_device = devices_info['devices'][0]
        print(f"   Nenhum dispositivo ativo. Usando o primeiro disponível: {first_device['name']} (ID: {first_device['id']})")
        return first_device['id']
    except Exception as e:
        print(f"❌ Erro ao buscar dispositivos Spotify: {e}")
        return None

# --- Ferramentas para o Agente LangChain ---

@tool
def play_music_on_spotify(song_name: str, artist_name: str = None) -> str:
    """
    Busca por uma música e a toca no dispositivo Spotify mais relevante (ativo ou primeiro da lista).
    A busca é mais precisa se o nome do artista for fornecido.
    """
    if not sp: return "Não consigo me conectar ao Spotify agora."

    device_id = get_active_device_id()
    if not device_id:
        return "Não consegui encontrar um dispositivo Spotify para tocar. Por favor, abra o Spotify em um dos seus aparelhos."

    query = f"track:{song_name}"
    if artist_name:
        query += f" artist:{artist_name}"
    
    try:
        results = sp.search(q=query, type='track', limit=1)
        if not results['tracks']['items']:
            return f"Bip bop... Não encontrei a música '{song_name}'."
        
        track = results['tracks']['items'][0]
        track_uri = track['uri']
        track_name = track['name']
        artist_names = ", ".join([artist['name'] for artist in track['artists']])

        sp.start_playback(device_id=device_id, uris=[track_uri])
        return f"Tudo certo! Coloquei '{track_name}' de '{artist_names}' para tocar no Spotify!"
    except Exception as e:
        return f"Oh não! Tive um problema com o Spotify: {e}"

@tool
def control_spotify_playback(action: str) -> str:
    """
    Controla a reprodução do Spotify. As ações válidas são 'pause', 'resume' (ou 'play'), 'next' e 'previous'.
    """
    if not sp: return "Não consigo me conectar ao Spotify agora."

    device_id = get_active_device_id()
    if not device_id:
        return "Não consegui encontrar um dispositivo Spotify para controlar."

    action = action.lower().strip()
    try:
        if action == 'pause':
            sp.pause_playback(device_id=device_id)
            return "Música pausada!"
        elif action in ['resume', 'play']:
            sp.start_playback(device_id=device_id)
            return "Continuando a música!"
        elif action == 'next':
            sp.next_track(device_id=device_id)
            return "Pulei para a próxima música!"
        elif action == 'previous':
            sp.previous_track(device_id=device_id)
            return "Voltei para a música anterior!"
        else:
            return f"Não reconheci a ação '{action}'. Tente 'pause', 'resume', 'next' ou 'previous'."
    except Exception as e:
        return f"Oh não! Tive um problema ao controlar o Spotify: {e}"

@tool
def get_current_spotify_song() -> str:
    """
    Verifica e retorna a música que está tocando agora no Spotify.
    """
    if not sp: return "Não consigo me conectar ao Spotify agora."
    
    try:
        current_track = sp.current_playback()
        if current_track and current_track['is_playing']:
            item = current_track['item']
            song = item['name']
            artist = item['artists'][0]['name']
            return f"Está tocando '{song}' de '{artist}' agora mesmo!"
        else:
            return "O Spotify está em silêncio no momento."
    except Exception as e:
        return f"Oh não! Tive um problema ao checar o Spotify: {e}"