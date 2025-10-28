# BMO - Seu amiguinho VideoGame vivo!

<img src="https://static.wikia.nocookie.net/adventuretimewithfinnandjake/images/8/81/BMO.png/revision/latest?cb=20200613123757" alt="BMO" width="200">

Bem-vindo ao projeto BMO! Este é um assistente de voz pessoal, inspirado no personagem BMO de "Hora de Aventura", construído com uma arquitetura de IA moderna. Ele é capaz de manter conversas, ter memória contextual e interagir com serviços externos como Spotify e Google Calendar, tudo isso com a personalidade divertida e amigável do BMO.

## ✨ Funcionalidades

*   **Personalidade Customizável:** Equipado com a personalidade do BMO, facilmente configurável.
*   **Cérebro de IA Rápido:** Utiliza modelos de linguagem de ponta (LLaMA 3) através da API de baixa latência da Groq.
*   **Memória de Conversa:** Lembra do contexto de interações anteriores dentro da mesma sessão de execução.
*   **Ativação por Voz (Wake-Word):** Usa um modelo `OpenWakeWord` treinado para responder ao comando "Ei, BMO".
*   **Integração com Ferramentas:**
    *   🎵 **Spotify:** Toca músicas, controla a reprodução (pausa, play, próxima) e informa o que está tocando.
    *   📅 **Google Calendar:** Lê seus próximos compromissos.
    *   🌐 **Google Search:** Acessa a internet em tempo real para responder a perguntas sobre eventos atuais e fatos recentes.
*   **Voz e Audição de Alta Qualidade:**
    *   **STT (Voz para Texto):** Transcrição de alta precisão com o modelo Whisper-Large-v3.
    *   **TTS (Texto para Voz):** Geração de voz rápida e de alta qualidade com a API do Google Cloud Text-to-Speech.

## 🛠️ Arquitetura

O projeto utiliza uma arquitetura de Agente com Ferramentas baseada em LangChain, orquestrando múltiplos serviços para criar uma experiência de conversação fluida.

*   **Interface (Cliente):** Um aplicativo web simples (`HTML/JS`) para desenvolvimento ou o `bmo.py` para operação autônoma com microfone.
*   **Servidor:** Uma aplicação Flask que gerencia a lógica e a comunicação via WebSockets (para o cliente web) ou roda localmente (no `bmo.py`).
*   **Orquestração de IA:** LangChain.
*   **LLM:** Groq (LLaMA 3 70B).
*   **Wake-Word:** OpenWakeWord (modelo treinado customizado).

## 🧠 O Cérebro do BMO: A Arquitetura LangChain

O coração do BMO é construído sobre o framework **LangChain**, que orquestra a interação entre o modelo de linguagem (LLM), a memória e as ferramentas. A arquitetura foi projetada para ser modular e inteligente, utilizando um sistema de **Roteador de Intenções**.

O fluxo de processamento de uma pergunta é o seguinte:

![Diagrama de Fluxo do LangChain](https://i.imgur.com/your-diagram-url.png) <!-- Sugestão: Crie um diagrama de fluxo simples para ilustrar isso! -->

### 1. O Roteador (O Recepcionista)

Quando uma pergunta chega, ela não é enviada diretamente para o agente principal. Primeiro, ela passa por uma **Cadeia de Roteamento** (`router_chain`).

*   **Tecnologia:** `ChatGroq` (com `temperature=0` para ser preciso) + `with_structured_output`.
*   **Função:** O roteador tem uma única e crucial tarefa: classificar a intenção do usuário. Ele é instruído a analisar a pergunta e o histórico da conversa e a decidir se a requisição é:
    1.  **`"ferramentas"`:** Se a pergunta envolve uma ação específica (tocar música, checar agenda, pesquisar na web).
    2.  **`"conversa"`:** Se a pergunta é uma saudação, uma pergunta geral ou uma continuação de um tópico anterior que não requer uma ferramenta.
*   **Saída:** Para garantir a robustez, o roteador é forçado a retornar sua decisão em um formato JSON estruturado (ex: `{"destination": "ferramentas"}`).

### 2. Os "Departamentos" (As Cadeias de Destino)

Com base na decisão do roteador, a pergunta é encaminhada para um de dois "departamentos" especializados:

#### a) A Cadeia de Conversa (`conversation_chain`)

*   **Ativada quando:** O roteador decide `"conversa"`.
*   **Componentes:**
    *   **Prompt:** Um `ChatPromptTemplate` que combina a personalidade do BMO (`BMO_SYSTEM_PROMPT`), o histórico da conversa (`chat_history`) e a pergunta atual (`input`).
    *   **LLM:** `ChatGroq` com uma temperatura mais alta (ex: `0.7`) para permitir respostas mais criativas e naturais.
    *   **Parser:** Um `StrOutputParser` simples, pois a saída esperada é apenas o texto da resposta.
*   **Função:** Lida com toda a interação que não requer ações externas, mantendo o fluxo da conversa.

#### b) O Agente de Ferramentas (`tool_agent_chain`)

*   **Ativado quando:** O roteador decide `"ferramentas"`.
*   **Componentes:**
    *   **Agente:** `create_openai_tools_agent`. Este é um agente moderno projetado para "Tool Calling". Ele permite que o LLM identifique qual ferramenta usar e com quais argumentos, formatando sua decisão em uma estrutura JSON.
    *   **Prompt:** Utiliza um template do `LangChain Hub` (`hwchase17/openai-tools-agent`), que é um prompt testado e otimizado para este tipo de agente. Nós injetamos a personalidade do BMO neste prompt.
    *   **Executor:** Um `AgentExecutor` que gerencia o ciclo de execução do agente:
        1.  O LLM "pensa" e decide chamar uma ferramenta.
        2.  O executor pausa, executa a função Python correspondente (ex: `play_music_on_spotify`).
        3.  O resultado da função (a "Observação") é retornado ao LLM.
        4.  O LLM usa essa observação para formular a resposta final para o usuário.
    *   **Segurança:** O executor é configurado com `max_iterations=5` para prevenir loops infinitos caso o agente fique "preso" tentando usar uma ferramenta repetidamente.

### 3. A Memória Compartilhada

A mágica da conversa contínua é gerenciada pelo `RunnableWithMessageHistory`.

*   **Tecnologia:** `ChatMessageHistory` para armazenamento em memória e `RunnableWithMessageHistory` para orquestração.
*   **Função:** Ele "envolve" toda a nossa cadeia de roteamento. Antes de cada execução, ele automaticamente:
    1.  Busca o histórico da sessão atual.
    2.  Injeta o histórico na chave `chat_history` do dicionário de entrada.
    3.  Executa a cadeia principal (roteador -> cadeia de destino).
    4.  Pega a pergunta atual e a resposta final e as salva de volta no histórico da sessão.
*   **Resultado:** Tanto o Roteador quanto as cadeias de Conversa e de Ferramentas sempre têm acesso ao contexto mais recente, permitindo que o BMO entenda perguntas de acompanhamento como "E qual a população de lá?".

Esta arquitetura garante que o BMO seja não apenas reativo, mas também contextual e capaz, decidindo de forma inteligente a melhor maneira de responder a cada interação.```

Este texto detalha de forma clara, mas técnica, como o "cérebro" do BMO funciona. Ele serve como uma excelente documentação e também como uma forma de mostrar a complexidade e a sofisticação do trabalho que você realizou.

## 🚀 Guia de Instalação e Configuração

Siga estes passos para colocar o BMO para funcionar no seu sistema (testado em Windows e Linux/Raspberry Pi OS).

### 1. Pré-requisitos: Configuração das APIs Externas

Antes de instalar o projeto, você precisa obter chaves de API para os serviços que o BMO utiliza.

#### a) Google Cloud (Text-to-Speech, Calendar, Search)

Você precisará de três conjuntos de credenciais do [Google Cloud Console](https://console.cloud.google.com/).

1.  **Crie um Projeto:** Se ainda não tiver um, crie um novo projeto no Google Cloud.
2.  **Habilite as APIs:** No seu projeto, vá para "APIs & Services" -> "Library" e habilite as seguintes APIs:
    *   `Cloud Text-to-Speech API`
    *   `Google Calendar API`
    *   `Custom Search API`
3.  **Crie a Credencial ADC (para TTS e Search):**
    *   Instale a [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) no seu computador.
    *   Autentique-se executando no seu terminal: `gcloud auth application-default login`.
    *   Vincule o projeto: `gcloud auth application-default set-quota-project SEU_PROJECT_ID`.
    *   **Importante:** Copie o arquivo `application_default_credentials.json` gerado para a pasta `credentials/` do seu projeto e renomeie-o para `google_adc_credentials.json`.
4.  **Crie a Credencial OAuth (para Calendar):**
    *   Em "APIs & Services" -> "Credentials", clique em "+ CREATE CREDENTIALS" -> "OAuth client ID".
    *   Selecione "Desktop app".
    *   Após criar, baixe o arquivo JSON. Renomeie-o para `credentials.json` e coloque na pasta `credentials/` do seu projeto.
5.  **Configure a Custom Search API:**
    *   Vá para a [Máquina de Pesquisa Programável](https://programmablesearchengine.google.com/).
    *   Crie uma nova máquina de pesquisa, ative a opção "Pesquisar em toda a Web".
    *   Copie o **ID da máquina de pesquisa (Search engine ID)**.

#### b) Spotify

1.  Vá para o [Dashboard de Desenvolvedor do Spotify](https://developer.spotify.com/dashboard/).
2.  Crie um novo App.
3.  Copie o **Client ID** e o **Client Secret**.
4.  Em "Settings", adicione `http://127.0.0.1:9090` como um "Redirect URI".

#### c) Groq

1.  Vá para [console.groq.com](https://console.groq.com/keys).
2.  Crie uma conta e gere uma nova **API Key**.

### 2. Configuração do Arquivo `.env`

Na raiz do projeto, crie um arquivo chamado `.env` (você pode copiar o `.env.example`) e preencha com todas as chaves obtidas:

```ini
# Chave da API da Groq
GROQ_API_KEY="gsk_..."

# Chaves da API do Spotify
SPOTIPY_CLIENT_ID="..."
SPOTIPY_CLIENT_SECRET="..."

# Chaves para a Pesquisa Google
GOOGLE_API_KEY="AIzaSy..." # Sua chave de API geral do Google Cloud
GOOGLE_CSE_ID="..."      # O ID da sua máquina de pesquisa (CX ID)
```

### 3. Instalação do Ambiente

#### a) Dependências do Sistema (Linux/Raspberry Pi)

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio ffmpeg git python3-venv flac
```

#### b) Clonar o Projeto

```bash
git clone https://github.com/SeuUsuario/BMO-Project.git
cd BMO-Project
```

#### c) Configurar o Ambiente Virtual e Instalar Dependências

```bash
# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente (Linux/macOS)
source venv/bin/activate
# ou (Windows)
# .\venv\Scripts\activate

# Instale as bibliotecas Python
pip install -r requirements/pc.txt # ou pi.txt na Raspberry Pi
```

#### d) Baixar Modelos OpenWakeWord

Execute o script de setup para baixar os modelos base necessários.

```bash
python setup_oww.py
```

### 4. Executando o BMO

Com o ambiente virtual ativado, inicie o BMO:

```bash
python bmo.py
```

**Primeira Execução (Autenticação):**
Na primeira vez que você usar as ferramentas do Spotify e do Google Calendar, o programa irá pausar e pedir para você seguir um fluxo de autenticação no navegador. Siga as instruções no terminal para autorizar o acesso. Arquivos de token (`credentials/token.json` para Google Calendar, `.cache` para Spotify) serão criados automaticamente para futuras execuções.

