# app/bmo_server.py
# Versão 3.3.4: Correção de API langchain

print("--- Running BMO Server v3.3.X ---")

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tempfile
import traceback
from flask import Flask, render_template_string
from flask_sock import Sock
from pydub import AudioSegment
from simple_websocket.errors import ConnectionClosed

from bmo_core.agent.agent import BMOAgent
from bmo_core.services.audio_manager import AudioManager
from bmo_core.services.hardware_manager import HardwareManager
from bmo_core.services.display_manager import DisplayManager

app = Flask(__name__)
sock = Sock(app)

print("✅ Inicializando módulos do BMO...")
hardware_manager = HardwareManager()
display_manager = DisplayManager()
bmo_agent = BMOAgent()
audio_manager = AudioManager(hardware_manager) 
print("✅ Servidor BMO pronto para receber conexões.")

@app.route('/')
def index():
    try:
        with open('web/index.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return "<h1>Erro: web/index.html não encontrado.</h1>", 404

@sock.route('/audio')
def handle_audio_connection(ws):
    print(f"🔗 Cliente conectado via WebSocket: {ws.environ.get('REMOTE_ADDR')}")
    display_manager.draw_face("happy")
    try:
        while ws.connected:
            received_data = ws.receive()
            if received_data is None: break
            
            print("\n--- Novo Pedido Recebido ---")
            display_manager.draw_face("listening"); hardware_manager.led_on()

            input_filename, wav_filename, response_audio_filename = None, None, None
            try:
                with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as input_file:
                    input_filename = input_file.name
                    input_file.write(received_data)
                print(f"   Áudio salvo em: '{os.path.basename(input_filename)}'")
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
                    wav_filename = wav_file.name
                
                audio = AudioSegment.from_file(input_filename, format="webm")
                audio.export(wav_filename, format="wav")
                print(f"   Áudio convertido para: '{os.path.basename(wav_filename)}'")

                display_manager.draw_face("thinking")
                print("🗣️  Transcrevendo texto...")
                user_question = audio_manager.transcribe_from_file(wav_filename)
                
                if user_question:
                    print(f"   Você disse: '{user_question}'")
                    print("🧠 Pedindo resposta ao BMO (LangChain/Groq)...")
                    ai_response = bmo_agent.run(user_question)
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
                    response_audio_filename = audio_manager.text_to_speech_file("Ops... Não ouvi, pode repetir?")
                    if response_audio_filename:
                        with open(response_audio_filename, "rb") as f: ws.send(f.read())
            finally:
                print("🧹 Limpando arquivos temporários...")
                for f in [input_filename, wav_filename, response_audio_filename]:
                    if f and os.path.exists(f): os.remove(f)
                display_manager.draw_face("neutral"); hardware_manager.led_off()
    except ConnectionClosed:
        # Captura o fechamento normal da conexão e não mostra um erro feio.
        print(f"   Conexão fechada normalmente pelo cliente.")
    except Exception as e:
        # Captura todos os outros erros inesperados.
        print(f"❌ Erro inesperado na conexão WebSocket: {e}"); traceback.print_exc()
    finally:
        print(f"👋 Cliente desconectado: {ws.environ.get('REMOTE_ADDR')}")

if __name__ == "__main__":
    try:
        print("🚀 Iniciando servidor Flask na porta 5000...")
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Servidor desligado.")
    finally:
        if 'display_manager' in globals(): display_manager.clear()
        if 'hardware_manager' in globals() and hasattr(hardware_manager, 'cleanup'): hardware_manager.cleanup()