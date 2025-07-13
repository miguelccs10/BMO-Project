# bmo_core/agent.py (Versão 2.4 - Correção de Parsing e Resposta Final)

import traceback
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.prompts import PromptTemplate

from . import config
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
            
            self.tools = [
                play_music_on_spotify,
                control_spotify_playback,
                get_current_spotify_song,
                get_next_appointment,
            ]
            
            base_prompt = hub.pull("hwchase17/react")
            base_template = base_prompt.template

            # --- MUDANÇA NO PROMPT ---
            # Adicionamos uma instrução explícita sobre a "Final Answer"
            bmo_instructions = (
                "Quando você tiver a resposta final para o usuário e não precisar mais usar ferramentas, "
                "VOCÊ DEVE usar o formato: `Action: Final Answer` e `Action Input: [sua resposta final aqui]`."
            )
            final_template_string = config.BMO_SYSTEM_PROMPT + "\n\n" + bmo_instructions + "\n\n" + base_template
            
            prompt = PromptTemplate.from_template(final_template_string)
            
            agent = create_react_agent(self.llm, self.tools, prompt)
            
            # --- MUDANÇA NO EXECUTOR ---
            # Adicionamos o handle_parsing_errors para maior robustez
            self.agent_executor = AgentExecutor(
                agent=agent, 
                tools=self.tools, 
                verbose=True,
                handle_parsing_errors=True  # <-- A SUGESTÃO DO PRÓPRIO ERRO!
            )
            
            print("✅ Agente BMO com Ferramentas (com correção de parsing) inicializado.")

        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar o BMOAgent. {e}")
            traceback.print_exc()

    def run(self, user_question: str) -> str:
        if not self.agent_executor:
            return "Desculpe, meu cérebro está offline agora."
        try:
            response = self.agent_executor.invoke({"input": user_question})
            return response['output']
        except Exception as e:
            print(f"❌ ERRO: Falha ao invocar o AgentExecutor. {e}")
            traceback.print_exc()
            return "Bip bop... tive um curto-circuito tentando usar minhas ferramentas."