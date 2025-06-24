# bmo_server.py
import asyncio
import websockets
import os
from pydub import AudioSegment

# Importa nossos módulos principais
from bmo_core.ai_manager import AIManager
from bmo_core.audio_manager import AudioManager

# --- Classes Dummy para Hardware Inexistente ---
class DummyHardware:
    def led_on(self): pass
    def led_off(self): pass

# --- Inicialização dos Módulos ---
print("✅ Inicializando módulos do BMO...")
ai_manager = AIManager()
audio_manager = AudioManager(DummyHardware()) 
print("✅ Servidor BMO pronto para receber conexões.")

# --- Lógica do Servidor WebSocket ---
async def handle_audio_connection(websocket, path):
    print(f"🔗 Cliente conectado: {websocket.remote_address}")
    try:
        async for received_data in websocket:
            print("\n--- Novo Pedido Recebido ---")
            print("▶️ Recebendo áudio do cliente...")
            
            input_audio_file = "received_audio.webm"
            output_wav_file = "processed_audio.wav"
            
            try:
                # 1. Salva o áudio recebido do navegador
                with open(input_audio_file, "wb") as f:
                    f.write(received_data)
                print(f"   Áudio salvo como '{input_audio_file}'")

                # 2. CONVERSÃO CRÍTICA: WebM -> WAV
                # Usa pydub para converter o áudio para um formato que o SpeechRecognition entende
                audio = AudioSegment.from_file(input_audio_file)
                audio.export(output_wav_file, format="wav")
                print(f"   Áudio convertido para '{output_wav_file}'")

                # 3. Transcreve o arquivo WAV
                print("🗣️  Transcrevendo texto...")
                user_question = audio_manager.transcribe_from_file(output_wav_file)
                
                if user_question:
                    print(f"   Você disse: '{user_question}'")
                    
                    # 4. Obtém a resposta da IA
                    print("🧠 Pedindo resposta ao BMO (Gemini)...")
                    ai_response = ai_manager.ask(user_question)
                    print(f"   BMO respondeu: '{ai_response}'")

                    # 5. Converte a resposta em áudio
                    print("🎤 Gerando áudio da resposta (gTTS)...")
                    response_audio_file = audio_manager.text_to_speech_file(ai_response)

                    # 6. Envia o áudio de volta para o cliente
                    if response_audio_file:
                        print("⬆️  Enviando áudio da resposta para o cliente...")
                        with open(response_audio_file, "rb") as f:
                            await websocket.send(f.read())
                        print("✅ Resposta enviada com sucesso!")
                else:
                    print("   ⚠️ Não foi possível transcrever o áudio.")

            finally:
                # 7. Limpeza: Garante que todos os arquivos temporários sejam deletados
                print("🧹 Limpando arquivos temporários...")
                for f in [input_audio_file, output_wav_file, "response.mp3"]:
                    if os.path.exists(f):
                        os.remove(f)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"👋 Cliente desconectado: {e.reason} (código: {e.code})")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado na conexão: {e}")

# --- Ponto de Entrada ---
async def main():
    """Função principal para iniciar o servidor."""
    # O websockets.serve já retorna um objeto de servidor que podemos esperar.
    async with websockets.serve(handle_audio_connection, "0.0.0.0", 8765):
        print("🚀 Servidor WebSocket escutando em ws://0.0.0.0:8765...")
        # A linha abaixo manterá o servidor rodando para sempre.
        await asyncio.Future()  

if __name__ == "__main__":
    try:
        # asyncio.run() gerencia o loop de eventos automaticamente.
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor desligado.")