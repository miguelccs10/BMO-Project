# bmo_server.py
# Versão 3.1: Upgrade do cérebro para LangChain + Groq

print("--- Running BMO Server v3.1 (Flask + LangChain/Groq) ---")

import os
import tempfile
import traceback
from flask import Flask, render_template_string
from flask_sock import Sock
from pydub import AudioSegment

# --- Importação dos módulos principais ---
# MUDANÇA: Importamos o BMOAgent em vez do AIManager
from bmo_core.agent import BMOAgent 
from bmo_core.audio_manager import AudioManager
from bmo_core.hardware_manager import IS_RASPBERRY_PI

# --- Inicialização do Flask ---
app = Flask(__name__)
sock = Sock(app)

# --- Inicialização Condicional do Hardware (Nenhuma mudança aqui) ---
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
# MUDANÇA: Instanciamos o BMOAgent em vez do AIManager
bmo_agent = BMOAgent() 
audio_manager = AudioManager(hardware_manager) 
print("✅ Servidor BMO pronto para receber conexões.")

# --- Rota para a Página Web (Nenhuma mudança aqui) ---
@app.route('/')
def index():
    """Serve o arquivo index.html."""
    try:
        # Apontando para a pasta 'web' como discutido
        with open('web/index.html', 'r') as f:
            return render_template_string(f.read())
    except FileNotFoundError:
        return "<h1>Erro: web/index.html não encontrado.</h1>", 404

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

            # --- Gerenciamento de Arquivos Temporários (Versão Robusta) ---
            # Criamos os nomes dos arquivos temporários primeiro
            input_file_obj = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
            wav_file_obj = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            
            input_filename = input_file_obj.name
            wav_filename = wav_file_obj.name
            response_audio_filename = None

            try:
                # Escreve os dados recebidos e FECHA o arquivo explicitamente
                input_file_obj.write(received_data)
                input_file_obj.close() # <-- Fecha o arquivo para liberar o bloqueio
                print(f"   Áudio salvo em: '{os.path.basename(input_filename)}'")

                # Pydub/FFmpeg agora pode acessar o arquivo sem bloqueios
                audio = AudioSegment.from_file(input_filename, format="webm")
                
                # Exporta para WAV e o arquivo é fechado automaticamente
                audio.export(wav_filename, format="wav")
                wav_file_obj.close() # Garantia extra
                print(f"   Áudio convertido para: '{os.path.basename(wav_filename)}'")

                display_manager.draw_face("thinking")
                print("🗣️  Transcrevendo texto...")
                user_question = audio_manager.transcribe_from_file(wav_filename)
                
                if user_question:
                    # ... (resto da sua lógica de IA, que já está perfeita)
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
                    # ... (sua lógica de erro de transcrição)
                    print("   ⚠️ Não foi possível transcrever. Enviando resposta de erro.")
                    response_audio_filename = audio_manager.text_to_speech_file("Bip bop... Não ouvi, pode repetir?")
                    if response_audio_filename:
                        with open(response_audio_filename, "rb") as f: ws.send(f.read())

            finally:
                # Bloco de limpeza final
                print("🧹 Limpando arquivos temporários...")
                for f in [input_filename, wav_filename, response_audio_filename]:
                    if f and os.path.exists(f):
                        try:
                            os.remove(f)
                        except PermissionError:
                            # Se mesmo assim der erro (raro agora), apenas avisa e continua
                            print(f"   ⚠️ Não foi possível remover o arquivo {os.path.basename(f)}, ele pode estar bloqueado.")
                display_manager.draw_face("neutral"); hardware_manager.led_off()

    except Exception as e:
        print(f"❌ Erro na conexão WebSocket: {e}"); traceback.print_exc()
    finally:
        print(f"👋 Cliente desconectado: {ws.environ.get('REMOTE_ADDR')}")
        display_manager.draw_face("neutral"); hardware_manager.led_off()


# --- Ponto de Entrada para Iniciar o Servidor (Nenhuma mudança aqui) ---
if __name__ == "__main__":
    try:
        # Use 'waitress' ou 'gunicorn' em produção em vez do servidor de dev do Flask
        # Para desenvolvimento, app.run() está ótimo.
        print("🚀 Iniciando servidor Flask na porta 5000...")
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Servidor desligado.")
    finally:
        # Usamos 'globals()' para verificar se as variáveis foram definidas
        if 'display_manager' in globals(): display_manager.clear()
        if 'hardware_manager' in globals(): hardware_manager.led_off()