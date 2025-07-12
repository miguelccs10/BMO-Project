# bmo_core/tools/spotify.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from langchain.tools import tool

# Configuração da autenticação
# O Spotipy vai ler as variáveis de ambiente (SPOTIPY_...) automaticamente
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-modify-playback-state,user-read-playback-state"))

@tool
def play_spotify_song(song_name: str, artist_name: str = None) -> str:
    """
    Toca uma música no Spotify. Se o nome do artista for fornecido, a busca será mais precisa.
    """
    query = song_name
    if artist_name:
        query += f" artist:{artist_name}"
    
    try:
        results = sp.search(q=query, type='track', limit=1)
        if not results['tracks']['items']:
            return f"Bip bop... Não encontrei a música '{song_name}'."
        
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(uris=[track_uri])
        return f"Tudo certo! Coloquei '{song_name}' para tocar no Spotify!"
    except Exception as e:
        return f"Oh não! Tive um problema com o Spotify: {e}"

@tool
def get_current_spotify_song() -> str:
    """
    Verifica e retorna a música que está tocando agora no Spotify.
    """
    try:
        current_track = sp.current_playback()
        if current_track and current_track['is_playing']:
            item = current_track['item']
            song = item['name']
            artist = item['artists'][0]['name']
            return f"Está tocando '{song}' de '{artist}' agora mesmo, Finn!"
        else:
            return "O Spotify está em silêncio no momento, bip bop."
    except Exception as e:
        return f"Oh não! Tive um problema ao checar o Spotify: {e}"