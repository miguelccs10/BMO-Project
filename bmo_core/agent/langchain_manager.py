# bmo_core/langchain_manager.py
# (Versão 3.0 - Gerenciamento de LangChain com Groq)

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from ...config import settings

class LangChainManager:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0.7,
            model_name="llama3-70b-8192",
            groq_api_key=settings.GROQ_API_KEY
        )
        
        # O prompt agora é um template do LangChain
        system_prompt = settings.BMO_SYSTEM_PROMPT
        human_prompt = "{question}"

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        
        # Cria a "cadeia" de execução: prompt -> LLM -> parser de saída
        self.chain = self.prompt | self.llm | StrOutputParser()
        print("LangChain com Groq inicializado.")

    def ask(self, question):
        return self.chain.invoke({"question": question})