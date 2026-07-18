"""
bmo_server.py
Flask server with WebSocket support for web-based BMO interaction.
Refactored to use YAML-based configuration following best practices.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path
from flask import Flask, render_template_string
from flask_sock import Sock
from pydub import AudioSegment
from simple_websocket.errors import ConnectionClosed

# --- Setup paths before local imports ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Local imports
from config.config_manager import get_config
from bmo_core.agent.agent_executor import BMOAgent
from bmo_core.services.audio_manager import AudioManager
from bmo_core.services.hardware_manager import HardwareManager
from bmo_core.services.display_manager import DisplayManager

# Load configuration
config = get_config()

print(f"--- Running BMO Server v{config.BMO_VERSION} (Flask Dev Mode) ---")

# --- Initialize Flask ---
app = Flask(__name__)
sock = Sock(app)

# --- Initialize BMO Modules ---
print("✅ Inicializando módulos do BMO...")
hardware_manager = HardwareManager()
display_manager = DisplayManager()
bmo_agent = BMOAgent()
audio_manager = AudioManager(hardware_manager)
print("✅ Servidor BMO pronto para receber conexões.")


@app.route('/')
def index():
    """Serve the main web interface."""
    web_folder_path = config.get_path('web_folder')
    index_file = web_folder_path / 'index.html'

    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return f"<h1>Erro: {index_file} não encontrado.</h1>", 404


@sock.route('/audio')
def handle_audio_connection(ws):
    """
    Handle WebSocket audio connection.
    Receives audio from browser, processes with BMO agent, sends back TTS response.
    """
    print(f"🔗 Cliente conectado via WebSocket: {ws.environ.get('REMOTE_ADDR')}")
    display_manager.draw_face("happy")

    try:
        while ws.connected:
            received_data = ws.receive()
            if received_data is None:
                break

            print("\n--- Novo Pedido Recebido ---")
            display_manager.draw_face("listening")
            hardware_manager.led_on()

            input_filename, wav_filename, response_audio_filename = None, None, None

            try:
                # Save received WebM audio
                with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as input_file:
                    input_filename = input_file.name
                    input_file.write(received_data)

                # Convert to WAV
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
                    wav_filename = wav_file.name

                audio = AudioSegment.from_file(input_filename, format="webm")
                audio.export(wav_filename, format="wav")

                # Transcribe
                display_manager.draw_face("thinking")
                user_question = audio_manager.transcribe_from_file(wav_filename)

                if user_question:
                    print(f"   Você disse: '{user_question}'")
                    print("🧠 Pedindo resposta ao BMO...")

                    # Process with agent (no session_id = new session each connection)
                    ai_response = bmo_agent.run(user_question)
                    print(f"   BMO respondeu: '{ai_response}'")

                    # Generate TTS
                    display_manager.draw_face("speaking")
                    response_audio_filename = audio_manager.text_to_speech_file(ai_response)

                    # Send response back
                    if response_audio_filename:
                        print("⬆️  Enviando áudio para o cliente...")
                        with open(response_audio_filename, "rb") as f:
                            ws.send(f.read())
                        print("✅ Resposta enviada!")
                else:
                    print("   ⚠️ Não foi possível transcrever. Enviando resposta de erro.")
                    error_msg = config.prompts.responses["audio_system_offline"]
                    response_audio_filename = audio_manager.text_to_speech_file(error_msg)
                    if response_audio_filename:
                        with open(response_audio_filename, "rb") as f:
                            ws.send(f.read())

            except Exception as e:
                print(f"❌ Erro ao processar áudio: {e}")
                traceback.print_exc()

            finally:
                # Cleanup temp files
                print("🧹 Limpando arquivos temporários...")
                for f in [input_filename, wav_filename, response_audio_filename]:
                    if f and os.path.exists(f):
                        os.remove(f)
                display_manager.draw_face("neutral")
                hardware_manager.led_off()

    except ConnectionClosed:
        print("   Conexão fechada normalmente pelo cliente.")
    except Exception as e:
        print(f"❌ Erro inesperado na conexão WebSocket: {e}")
        traceback.print_exc()
    finally:
        print(f"👋 Cliente desconectado: {ws.environ.get('REMOTE_ADDR')}")
        display_manager.draw_face("neutral")
        hardware_manager.led_off()


def main():
    """Start the Flask development server."""
    try:
        server_config = config.config.server
        print(f"🚀 Iniciando servidor Flask em http://{server_config.host}:{server_config.port}...")
        app.run(
            host=server_config.host,
            port=server_config.port,
            debug=server_config.debug
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor desligado.")
    finally:
        if hasattr(display_manager, 'clear'):
            display_manager.clear()
        if hasattr(hardware_manager, 'cleanup'):
            hardware_manager.cleanup()


if __name__ == "__main__":
    main()
