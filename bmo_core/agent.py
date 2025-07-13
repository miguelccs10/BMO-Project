# bmo_core/agent.py
# Versão 2.2: Agente com ferramentas aprimoradas

import traceback
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.prompts import PromptTemplate

from . import config
# Importa as ferramentas que criamos
from .tools.spotify import play_music_on_spotify, control_spotify_playback, get_current_spotify_song
from .tools.calendar import get_next_appointment

class BMOAgent:
    def __init__(self):
        self.agent_executor = None
        try:
            self.llm = ChatGroq(
                temperature=0.2,
                model_name="llama3-70b-8192",
                groq_api_key=config.GROQ_API_KEY
            )
            
            # ATUALIZADA: Lista de ferramentas que o agente pode usar
            self.tools = [
                play_music_on_spotify,
                control_spotify_playback,
                get_current_spotify_song,
                get_next_appointment,
            ]
            
            # Puxa o prompt base do hub
            base_prompt = hub.pull("hwchase17/react")

            # Extrai o template de texto completo do prompt base
            base_template = base_prompt.template

            # Constrói o novo template, adicionando a personalidade do BMO no início
            final_template_string = config.BMO_SYSTEM_PROMPT + "\n\n" + base_template
            
            # Cria um novo PromptTemplate a partir da nossa string combinada
            prompt = PromptTemplate.from_template(final_template_string)
            
            # Cria o agente com o novo prompt
            agent = create_react_agent(self.llm, self.tools, prompt)
            
            # O AgentExecutor é o que realmente roda o agente
            self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
            
            print("✅ Agente BMO com Ferramentas Aprimoradas inicializado.")

        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar o BMOAgent com ferramentas. {e}")
            traceback.print_exc()

    def run(self, user_question: str) -> str:
        if not self.agent_executor:
            return "Desculpe, meu cérebro está offline agora."
        try:
            # O executor lida com todo o ciclo de pensamento e uso de ferramentas
            response = self.agent_executor.invoke({"input": user_question})
            return response['output']
        except Exception as e:
            print(f"❌ ERRO: Falha ao invocar o AgentExecutor. {e}")
            traceback.print_exc()
            return "Bip bop... tive um curto-circuito tentando usar minhas ferramentas."