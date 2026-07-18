# BMO - Seu amiguinho VideoGame vivo!

<img src="https://static.wikia.nocookie.net/adventuretimewithfinnandjake/images/8/81/BMO.png/revision/latest?cb=20200613123757" alt="BMO" width="200">

Bem-vindo ao projeto BMO! Este é um assistente de voz pessoal, inspirado no personagem BMO de "Hora de Aventura". Ele é capaz de manter conversas e executar ferramentas com a personalidade divertida do BMO. 

**O grande diferencial desta versão é ser 100% Local-First e Multi-Device.**

## ✨ Funcionalidades

*   **100% Offline (Local-First):** O "Cérebro", a "Boca" e os "Ouvidos" do BMO rodam inteiramente no seu próprio computador, sem depender de internet.
*   **Arquitetura Multi-Device:** Roda desde PCs "Batata" sem placa de vídeo (via Ollama) até PCs Dedicados/Gamer (via AirLLM).
*   **Voz e Audição Nativas:**
    *   **STT (Ouvidos):** Usa `faster-whisper` (transcrição hiper-precisa local).
    *   **TTS (Boca):** Usa `Piper TTS` para geração de voz instantânea e de alta qualidade (offline).
    *   **Wake-Word:** Usa `OpenWakeWord` para responder apenas quando você diz "Ei, BMO".
*   **Integração com Ferramentas Clássicas (Opcional):**
    *   🎵 **Spotify:** Toca músicas, controla a reprodução.
    *   📅 **Google Calendar:** Lê compromissos.

## 🛠️ Arquitetura

O projeto utiliza uma arquitetura de Agente com Ferramentas baseada em **LangChain**, orquestrando modelos locais.

*   **LLM (O Cérebro):**
    *   **Ollama:** C++ otimizado (Quantização 4-bit) perfeito para rodar modelos como Qwen2 1.5B usando menos de 1GB de RAM.
    *   **AirLLM:** Abordagem que carrega modelos gigantes direto do SSD para PCs com muita VRAM/RAM.
*   **Roteador de Intenções:** O LangChain analisa a sua frase e decide, com base na inteligência local, se o BMO deve apenas bater papo (Conversation Chain) ou usar um módulo (Tool Chain).

## 🚀 Guia de Instalação e Configuração (Novo Modo)

Para simplificar a instalação em qualquer máquina, utilize o instalador universal interativo.

### 1. Dependências de Sistema

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio ffmpeg git python3-venv flac
```

### 2. Clonar o Projeto

```bash
git clone https://github.com/miguelccs10/BMO-Project.git
cd BMO-Project
```

### 3. Instalação Automática

```bash
./install.sh
```
*Ele perguntará:*
1. **O seu Perfil de Máquina:** Máquina Fraca (Instala o Ollama automaticamente) vs Máquina Dedicada (AirLLM).
2. **O Peso da IA:** Small (Muito rápido), Medium (Equilibrado), Large (Para PCs muito fortes).

O script criará seu `venv`, instalará o Langchain, fará o download da inteligência artificial adequada, baixará os arquivos `.onnx` e configurará o `config.yaml` sozinho.

### 4. Configuração do `.env` (Para usar Spotify e APIs web)
*Isso é opcional, caso queira que ele acesse a internet.*
Renomeie o `.env.example` para `.env` e coloque suas chaves (GROQ, SPOTIPY, GOOGLE).

### 5. Executando o BMO!

Após o `install.sh` terminar o show, ative o ambiente virtual criado e acorde o BMO:

```bash
source venv/bin/activate
python -m app.BMO
```

Fale **"Ei, BMO"**, aguarde o bip, e converse com seu amiguinho inteligente 100% offline! 🎮
