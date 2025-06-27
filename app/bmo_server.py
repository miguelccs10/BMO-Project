# bmo_server.py
# Arquitetura refeita com Flask para maior estabilidade.
print("--- Running BMO Server v3.0 (Flask Architecture) ---")

import os
import tempfile
import traceback
from flask import Flask, render_template_string
from flask_sock import Sock
from pydub import AudioSegment

# --- Importação dos módulos principais ---
from bmo_core.ai_manager import AIManager
from bmo_core.audio_manager import AudioManager
from bmo_core.hardware_manager import IS_RASPBERRY_PI

# --- Inicialização do Flask ---
app = Flask(__name__)
sock = Sock(app)

# --- Inicialização Condicional do Hardware ---
try:
    if not IS_RASPBERRY_PI:
        raise ImportError("Não é uma Raspberry Pi. Usando Dummies.")
    from bmo_core.hardware_manager import HardwareManager
    from bmo_core.display_manager import DisplayManager
    hardware_manager = HardwareManager()
    display_manager = DisplayManager()
    print("✅ Hardware real e display inicializados.")
except (ImportError, RuntimeError, ModuleNotFoundError) as e:
    print(f"⚠️  Aviso: {e}. Usando hardware e display dummy.")
    class Dummy:
        def __getattr__(self, name): return lambda *args, **kwargs: None
    hardware_manager = Dummy()
    display_manager = Dummy()

# --- Inicialização dos Módulos de Software ---
print("✅ Inicializando módulos do BMO...")
ai_manager = AIManager()
audio_manager = AudioManager(hardware_manager) 
print("✅ Servidor BMO pronto para receber conexões.")

# --- Rota para a Página Web ---
@app.route('/')
def index():
    """Serve o arquivo index.html."""
    try:
        with open('index.html', 'r') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return "<h1>Erro: index.html não encontrado.</h1>", 404

# --- Rota para a Conexão de Áudio WebSocket ---
@sock.route('/audio')
def handle_audio_connection(ws):
    """
    Esta função é chamada para cada cliente que se conecta ao WebSocket.
    """
    print(f"🔗 Cliente conectado via WebSocket: {ws.environ.get('REMOTE_ADDR')}")
    try:
        while True:
            received_data = ws.receive()
            if received_data is None:
                break
                
            print("\n--- Novo Pedido Recebido ---")
            display_manager.draw_face("listening"); hardware_manager.led_on()

            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as input_file, \
                 tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:

                input_filename, wav_filename, response_audio_filename = input_file.name, wav_file.name, None
                try:
                    input_file.write(received_data); input_file.flush()
                    print(f"   Áudio salvo em: '{os.path.basename(input_filename)}'")

                    audio = AudioSegment.from_file(input_filename, format="webm")
                    audio.export(wav_filename, format="wav")
                    print(f"   Áudio convertido para: '{os.path.basename(wav_filename)}'")

                    display_manager.draw_face("thinking")
                    print("🗣️  Transcrevendo texto...")
                    user_question = audio_manager.transcribe_from_file(wav_filename)
                    
                    if user_question:
                        print(f"   Você disse: '{user_question}'")
                        print("🧠 Pedindo resposta ao BMO (Gemini)...")
                        ai_response = ai_manager.ask(user_question)
                        print(f"   BMO respondeu: '{ai_response}'")

                        display_manager.draw_face("speaking")
                        print("🎤 Gerando áudio da resposta...")
                        response_audio_filename = audio_manager.text_to_speech_file(ai_response)
                        
                        if response_audio_filename:
                            print("⬆️  Enviando áudio para o cliente...")
                            with open(response_audio_filename, "rb") as f:
                                ws.send(f.read())
                            print("✅ Resposta enviada!")
                    else:
                        print("   ⚠️ Não foi possível transcrever. Enviando resposta de erro.")
                        response_audio_filename = audio_manager.text_to_speech_file("Bip bop... Não ouvi, pode repetir?")
                        if response_audio_filename:
                            with open(response_audio_filename, "rb") as f: ws.send(f.read())
                finally:
                    print("🧹 Limpando arquivos temporários...")
                    for f in [input_filename, wav_filename, response_audio_filename]:
                        if f and os.path.exists(f): os.remove(f)
                    display_manager.draw_face("neutral"); hardware_manager.led_off()

    except Exception as e:
        print(f"❌ Erro na conexão WebSocket: {e}"); traceback.print_exc()
    finally:
        print(f"👋 Cliente desconectado: {ws.environ.get('REMOTE_ADDR')}")
        display_manager.draw_face("neutral"); hardware_manager.led_off()


# --- Ponto de Entrada para Iniciar o Servidor ---
if __name__ == "__main__":
    try:
        # O Flask agora serve a aplicação. Use 'host="0.0.0.0"' para ser acessível na rede.
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Servidor desligado.")
    finally:
        if 'display_manager' in locals(): display_manager.clear()
        if 'hardware_manager' in locals(): hardware_manager.led_off()
