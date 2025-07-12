# bmo_core/agent.py (Versão 2.3 - Sem importação circular)

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.prompts import PromptTemplate

from . import config
# Importa as ferramentas que criamos
from .tools.spotify import play_spotify_song, get_current_spotify_song
from .tools.calendar import get_next_appointment

# REMOVEMOS a linha "from bmo_core.agent import BMOAgent" daqui.

class BMOAgent:
    def __init__(self):
        try:
            self.llm = ChatGroq(
                temperature=0.2,
                model_name="llama3-70b-8192",
                groq_api_key=config.GROQ_API_KEY
            )
            
            self.tools = [
                play_spotify_song,
                get_current_spotify_song,
                get_next_appointment,
            ]
            
            # --- MANIPULAÇÃO CORRETA DO PROMPT ---
            base_prompt = hub.pull("hwchase17/react")
            base_template = base_prompt.template
            bmo_personality_prompt = config.BMO_SYSTEM_PROMPT
            final_template_string = bmo_personality_prompt + "\n\n" + base_template
            prompt = PromptTemplate.from_template(final_template_string)
            agent = create_react_agent(self.llm, self.tools, prompt)
            
            self.agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
            
            print("✅ Agente BMO com Ferramentas (Spotify, Calendar) inicializado.")
        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar o BMOAgent com ferramentas. {e}")
            self.agent_executor = None

    def run(self, user_question: str) -> str:
        if not self.agent_executor:
            return "Desculpe, meu cérebro está offline agora."
        try:
            response = self.agent_executor.invoke({"input": user_question})
            return response['output']
        except Exception as e:
            print(f"❌ ERRO: Falha ao invocar o AgentExecutor. {e}")
            return "Bip bop... tive um curto-circuito tentando usar minhas ferramentas."