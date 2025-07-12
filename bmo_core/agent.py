# bmo_core/agent.py
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from . import config

class BMOAgent:
    def __init__(self):
        try:
            self.llm = ChatGroq(
                temperature=0.7,
                model_name="llama3-70b-8192",
                groq_api_key=config.GROQ_API_KEY
            )
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", config.BMO_SYSTEM_PROMPT),
                ("human", "{user_question}")
            ])
            self.chain = prompt_template | self.llm | StrOutputParser()
            print("✅ Agente BMO com LangChain e Groq inicializado.")
        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar o BMOAgent. {e}")
            self.chain = None

    def run(self, user_question: str) -> str:
        if not self.chain:
            return "Desculpe, meu cérebro está offline agora."
        try:
            response = self.chain.invoke({"user_question": user_question})
            return response
        except Exception as e:
            print(f"❌ ERRO: Falha ao invocar a cadeia do LangChain. {e}")
            return "Bip-bop... tive um curto-circuito tentando pensar."