# bmo_server.py
import asyncio
import websockets
import os
import tempfile
from pydub import AudioSegment

# Importa nossos módulos principais
from bmo_core.ai_manager import AIManager
from bmo_core.audio_manager import AudioManager
from bmo_core.hardware_manager import HardwareManager, IS_RASPBERRY_PI
from bmo_core.display_manager import DisplayManager

# --- Inicialização dos Módulos ---
print("✅ Inicializando módulos do BMO...")
ai_manager = AIManager()

# Usa o hardware real se estiver na Pi, caso contrário, usa um Dummy.
try:
    if not IS_RASPBERRY_PI:
        raise ImportError("Não é uma Raspberry Pi, usando hardware dummy.")
    hardware_manager = HardwareManager()
    display_manager = DisplayManager()
    print("✅ Hardware real e display inicializados.")
except (ImportError, RuntimeError) as e:
    print(f"⚠️  Aviso: {e}. Usando hardware e display dummy.")
    class Dummy:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    hardware_manager = Dummy()
    display_manager = Dummy()

audio_manager = AudioManager(hardware_manager) 
print("✅ Servidor BMO pronto para receber conexões.")

# --- Lógica do Servidor WebSocket ---
async def handle_audio_connection(websocket, path):
    print(f"🔗 Cliente conectado: {websocket.remote_address}")
    try:
        async for received_data in websocket:
            print("\n--- Novo Pedido Recebido ---")
            display_manager.draw_face("listening")
            hardware_manager.led_on()

            # Cria arquivos temporários que são únicos para esta conexão
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as input_audio_file, \
                 tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_wav_file:

                input_filename = input_audio_file.name
                output_filename = output_wav_file.name
                response_audio_filename = None # Será definido depois

                try:
                    # 1. Salva o áudio recebido no arquivo temporário
                    with open(input_filename, "wb") as f:
                        f.write(received_data)
                    print(f"   Áudio salvo como '{os.path.basename(input_filename)}'")

                    # 2. Converte WebM -> WAV
                    audio = AudioSegment.from_file(input_filename)
                    audio.export(output_filename, format="wav")
                    print(f"   Áudio convertido para '{os.path.basename(output_filename)}'")

                    # 3. Transcreve o arquivo WAV
                    display_manager.draw_face("thinking")
                    print("🗣️  Transcrevendo texto...")
                    user_question = audio_manager.transcribe_from_file(output_filename)
                    
                    if user_question:
                        print(f"   Você disse: '{user_question}'")
                        
                        # 4. Obtém a resposta da IA
                        print("🧠 Pedindo resposta ao BMO (Gemini)...")
                        ai_response = ai_manager.ask(user_question)
                        print(f"   BMO respondeu: '{ai_response}'")

                        # 5. Converte a resposta em áudio para um arquivo temporário
                        display_manager.draw_face("speaking")
                        print("🎤 Gerando áudio da resposta (gTTS)...")
                        response_audio_filename = audio_manager.text_to_speech_file(ai_response) # Retorna um nome de arquivo temporário

                        # 6. Envia o áudio de volta para o cliente
                        if response_audio_filename:
                            print("⬆️  Enviando áudio da resposta para o cliente...")
                            with open(response_audio_filename, "rb") as f:
                                await websocket.send(f.read())
                            print("✅ Resposta enviada com sucesso!")
                    else:
                        print("   ⚠️ Não foi possível transcrever o áudio.")
                        # Envia uma resposta de erro em áudio
                        error_response_filename = audio_manager.text_to_speech_file("Desculpe, não entendi o que você disse.")
                        if error_response_filename:
                            with open(error_response_filename, "rb") as f:
                                await websocket.send(f.read())
                            os.remove(error_response_filename)


                finally:
                    # 7. Limpeza: Garante que todos os arquivos temporários sejam deletados
                    print("🧹 Limpando arquivos temporários...")
                    for f in [input_filename, output_filename, response_audio_filename]:
                        if f and os.path.exists(f):
                            os.remove(f)
                    
                    display_manager.draw_face("neutral")
                    hardware_manager.led_off()


    except websockets.exceptions.ConnectionClosed as e:
        print(f"👋 Cliente desconectado: {e.reason} (código: {e.code})")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado na conexão: {e}")
        import traceback
        traceback.print_exc()
    finally:
        display_manager.draw_face("neutral")
        hardware_manager.led_off()


# --- Ponto de Entrada ---
async def main():
    """Função principal para iniciar o servidor."""
    async with websockets.serve(handle_audio_connection, "0.0.0.0", 8765):
        print("🚀 Servidor WebSocket escutando em ws://0.0.0.0:8765...")
        display_manager.draw_face("neutral")
        await asyncio.Future()  # Manter rodando

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor desligado.")
    finally:
        display_manager.clear()
        hardware_manager.led_off()
