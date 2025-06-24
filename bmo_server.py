# bmo_server.py
import asyncio
import websockets
import os
from bmo_core.ai_manager import AIManager
from bmo_core.audio_manager import AudioManager
import speech_recognition as sr # Importar para usar a exceção

# Classe falsa para simular hardware, já que a Pi será "headless"
class DummyHardware:
    def led_on(self): pass
    def led_off(self): pass
    def led_blink(self, duration=0.5): pass

# --- Inicialização dos Módulos ---
print("Inicializando módulos do BMO...")
ai_manager = AIManager()
audio_manager = AudioManager(DummyHardware()) 
print("Servidor BMO pronto para receber conexões.")

async def handle_audio(websocket, path):
    """Função executada para cada cliente (celular) que se conecta."""
    print(f"Cliente conectado: {websocket.remote_address}")
    try:
        while True:
            # 1. Espera e recebe o áudio do celular
            audio_bytes = await websocket.recv()
            print(f"Áudio recebido ({len(audio_bytes)} bytes).")

            temp_audio_file = "temp_question.wav"
            with open(temp_audio_file, "wb") as f:
                f.write(audio_bytes)

            # 2. Usa os módulos para processar o áudio
            print("Transcrevendo áudio...")
            user_question = audio_manager.transcribe_from_file(temp_audio_file)
            
            if user_question:
                print(f"Pergunta: '{user_question}'")
                print("Pedindo resposta ao Gemini...")
                ai_response = ai_manager.ask(user_question)
                print(f"Resposta da IA: '{ai_response}'")

                # Converte a resposta em um arquivo de áudio
                response_audio_file = audio_manager.text_to_speech_file(ai_response)

                # 3. Envia o áudio da resposta de volta para o celular
                print("Enviando áudio da resposta...")
                with open(response_audio_file, "rb") as f:
                    await websocket.send(f.read())
                print("Resposta enviada com sucesso!")

                os.remove(response_audio_file)
            else:
                print("Não foi possível transcrever o áudio, nenhuma ação tomada.")
            
            os.remove(temp_audio_file)

    except websockets.exceptions.ConnectionClosed:
        print(f"Cliente desconectado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# --- Ponto de Entrada do Servidor ---
if __name__ == "__main__":
    # O endereço "0.0.0.0" permite que qualquer dispositivo na sua rede se conecte
    start_server = websockets.serve(handle_audio, "0.0.0.0", 8765)
    print("Servidor WebSocket escutando na porta 8765...")
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()