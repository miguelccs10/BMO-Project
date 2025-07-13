# bmo_core/agent.py (Versão 3.1.3 - Correção de Passthrough)

import traceback
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnablePassthrough # <-- Importação adicionada
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.router.llm_router import RouterOutputParser
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

from . import config
from .tools.spotify import play_music_on_spotify, control_spotify_playback, get_current_spotify_song
from .tools.calendar import get_next_appointment

class BMOAgent:
    def __init__(self):
        self.full_chain = None
        try:
            llm = ChatGroq(temperature=0.2, model_name="llama3-70b-8192", groq_api_key=config.GROQ_API_KEY)

            # --- CADEIA 1: Conversa Geral ---
            conversation_prompt = PromptTemplate.from_template(config.BMO_SYSTEM_PROMPT + "\n\nHuman: {input}\nBMO:")
            conversation_chain = conversation_prompt | llm | {"text": StrOutputParser()}

            # --- CADEIA 2: Agente de Ferramentas ---
            tools = [play_music_on_spotify, control_spotify_playback, get_current_spotify_song, get_next_appointment]
            agent_prompt = hub.pull("hwchase17/react")
            agent = create_react_agent(llm, tools, agent_prompt)
            tool_agent_chain = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

            # --- O Roteador ---
            ROUTER_TEMPLATE = """Dada a pergunta do usuário, classifique-a como 'ferramentas' ou 'conversa'.
Faça isso com base nas seguintes descrições:

'ferramentas': Bom para responder perguntas sobre música, Spotify, agenda ou calendário.
'conversa': Bom para responder a qualquer outra pergunta, saudações ou conversas gerais.

Retorne um objeto JSON com uma única chave 'destination' e o valor sendo a escolha ('ferramentas' ou 'conversa').

Pergunta do usuário:
{input}"""
            
            router_prompt = PromptTemplate.from_template(ROUTER_TEMPLATE)
            router_chain = router_prompt | llm | StrOutputParser() | json.loads

            # --- A Cadeia Principal (Corrigida com Passthrough) ---
            # Este dicionário garante que tanto o resultado do roteador quanto a entrada original sejam passados adiante.
            self.full_chain = {
                "destination": router_chain,
                "input": lambda x: x["input"] # Passa a pergunta original do usuário adiante
            } | RunnableBranch(
                (lambda x: "ferramentas" in x["destination"].get("destination", ""), tool_agent_chain),
                conversation_chain,  # Rota padrão
            )

            print("✅ Agente BMO com Arquitetura de Roteador LCEL inicializado.")

        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar o BMOAgent. {e}")
            traceback.print_exc()

    def run(self, user_question: str) -> str:
        if not self.full_chain:
            return "Desculpe, meu cérebro está offline agora."
        try:
            response = self.full_chain.invoke({"input": user_question})
            return response.get('output', response.get('text', 'Bip bop... algo deu muito errado.'))
        except Exception as e:
            print(f"❌ ERRO: Falha ao invocar a cadeia principal. {e}")
            traceback.print_exc()
            return "Bip bop... tive um grande curto-circuito cerebral."