# bmo_core/agent/agent_executor.py
# Monta e exporta o agente LangChain final com memória e roteamento.

import traceback
import json
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub
from pydantic import BaseModel, Field

# --- Imports da Nova Estrutura ---
from config import settings
from config import prompts
# A lógica de memória foi movida para o seu próprio módulo
from bmo_core.agent.memory import wrap_with_memory, get_session_history 
from bmo_core.tools.spotify import play_music_on_spotify, control_spotify_playback, get_current_spotify_song
from bmo_core.tools.calendar import get_next_appointment
from bmo_core.tools.search import google_search_tool

# Modelo de dados para a saída do roteador.
class RouteQuery(BaseModel):
    destination: str = Field(description="O destino para rotear a pergunta. Pode ser 'ferramentas' ou 'conversa'.")

class BMOAgent:
    def __init__(self):
        self.agent_with_chat_history = None
        try:
            # --- LLMs ---
            router_llm = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key=settings.GROQ_API_KEY)
            agent_llm = ChatGroq(temperature=0.7, model_name="llama3-70b-8192", groq_api_key=settings.GROQ_API_KEY)
            
            # --- CADEIA DE CONVERSA ---
            conv_prompt = ChatPromptTemplate.from_messages([
                ("system", prompts.BMO_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            conversation_chain = conv_prompt | agent_llm | StrOutputParser()

            # --- AGENTE DE FERRAMENTAS ---
            tools = [play_music_on_spotify, 
                    control_spotify_playback,
                    get_current_spotify_song,
                    get_next_appointment,
                    google_search_tool
                ]
            agent_prompt = hub.pull("hwchase17/openai-tools-agent")
            agent = create_openai_tools_agent(agent_llm, tools, agent_prompt)
            tool_agent_chain = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

            # --- ROTEADOR ESTRUTURADO ---
            router_prompt = ChatPromptTemplate.from_template(prompts.ROUTER_TEMPLATE)
            structured_router = router_llm.with_structured_output(RouteQuery)
            router_chain = router_prompt | structured_router
            
            # --- CADEIA PRINCIPAL COM ROTEAMENTO ---
            def route(info):
                if "ferramentas" in info["destination"].destination.lower():
                    return tool_agent_chain
                else:
                    return conversation_chain
            
            # O RunnablePassthrough garante que o input original seja mantido
            # para ser usado pela cadeia de destino (conversa ou ferramentas).
            full_chain = RunnablePassthrough.assign(
                destination=lambda x: router_chain.invoke({"input": x["input"], "chat_history": x["chat_history"]})
            ) | RunnableLambda(lambda x: route(x).invoke(x))

            # --- ESTRUTURA FINAL COM MEMÓRIA ---
            # Usamos a função 'wrap_with_memory' do nosso módulo de memória
            self.agent_with_chat_history = wrap_with_memory(full_chain)
            
            print("✅ Agente BMO com Arquitetura Refatorada inicializado.")

        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar o BMOAgent. {e}"); traceback.print_exc()

    def run(self, user_question: str, session_id: str = "default_session") -> str:
        """
        Executa a cadeia principal do agente com a pergunta do usuário e o ID da sessão.
        A lógica de gerenciamento de memória foi abstraída para o módulo de memória.
        """
        if not self.agent_with_chat_history: 
            return "Desculpe, meu cérebro está com um parafuso solto."
        try:
            # A invocação é simples. Passamos o input e a configuração da sessão.
            # O RunnableWithMessageHistory cuida de carregar e salvar o histórico.
            response = self.agent_with_chat_history.invoke(
                {"input": user_question},
                config={"configurable": {"session_id": session_id}}
            )

            # A saída pode ser um dicionário (do agente) ou uma string (da conversa)
            if isinstance(response, dict):
                return response.get('output', 'Bip bop... algo deu errado na resposta do agente.')
            return response
        except Exception as e:
            print(f"❌ ERRO: Falha ao invocar a cadeia principal. {e}"); traceback.print_exc()
            return "Bip bop... tive um grande curto-circuito cerebral."