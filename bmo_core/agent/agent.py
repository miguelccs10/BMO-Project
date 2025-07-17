# bmo_core/agent.py (Versão 6.0 - Arquitetura de Agente Único e Robusto)

import traceback
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from ...config import settings
from ..tools.spotify import play_music_on_spotify, control_spotify_playback, get_current_spotify_song
from ..tools.calendar import get_next_appointment

class BMOAgent:
    def __init__(self):
        self.agent_with_chat_history = None
        self.session_histories = {} 
        try:
            # --- LLM ---
            # Usamos uma temperatura média para equilibrar criatividade e precisão.
            llm = ChatGroq(temperature=0.7, model_name="llama3-70b-8192", groq_api_key=settings.GROQ_API_KEY)
            
            # --- FERRAMENTAS ---
            # A lista de habilidades que o BMO pode usar.
            tools = [play_music_on_spotify, control_spotify_playback, get_current_spotify_song, get_next_appointment]

            # --- PROMPT DO AGENTE ---
            # Este é o único prompt necessário. Ele instrui o agente sobre sua personalidade,
            # como usar as ferramentas e como lidar com o histórico da conversa.
            # O placeholder 'agent_scratchpad' é usado internamente pelo agente para seus pensamentos.
            prompt = ChatPromptTemplate.from_messages([
                ("system", settings.BMO_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])

            # --- CRIAÇÃO DO AGENTE ---
            # Usamos o `create_openai_tools_agent`. Ele é o padrão da indústria para agentes
            # que precisam decidir entre conversar e usar ferramentas. Ele lida com o roteamento implicitamente.
            agent = create_openai_tools_agent(llm, tools, prompt)
            
            # --- EXECUTOR DO AGENTE ---
            # O AgentExecutor envolve o agente e as ferramentas, criando o ciclo de execução.
            agent_executor = AgentExecutor(
                agent=agent, 
                tools=tools, 
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5 # Prevenção contra loops infinitos
            )

            # --- ESTRUTURA FINAL COM MEMÓRIA ---
            # Envolvemos o executor do agente com o gerenciador de memória.
            # Esta é a cadeia final e completa.
            self.agent_with_chat_history = RunnableWithMessageHistory(
                agent_executor,
                lambda session_id: self.session_histories.get(session_id, ChatMessageHistory()),
                input_messages_key="input",
                history_messages_key="chat_history", # Garante que a chave correta seja usada
            )
            print("✅ Agente BMO com Arquitetura de Ferramentas e Memória inicializado.")

        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar o BMOAgent. {e}"); traceback.print_exc()

    def run(self, user_question: str, session_id: str = "default_session") -> str:
        if not self.agent_with_chat_history: return "Desculpe, meu cérebro está com um parafuso solto."
        try:
            # Cria um histórico para a sessão se for a primeira vez.
            if session_id not in self.session_histories:
                self.session_histories[session_id] = ChatMessageHistory()

            # Invoca a cadeia com a pergunta. A memória é gerenciada automaticamente.
            response = self.agent_with_chat_history.invoke(
                {"input": user_question},
                config={"configurable": {"session_id": session_id}}
            )
            
            # A saída do AgentExecutor estará sempre na chave 'output'.
            return response.get('output', 'Bip bop... algo deu errado na minha resposta final.')
        except Exception as e:
            print(f"❌ ERRO: Falha ao invocar a cadeia principal. {e}"); traceback.print_exc()
            return "Bip bop... tive um grande curto-circuito cerebral."