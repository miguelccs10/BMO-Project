# bmo_core/tools/search.py
# Ferramenta para dar ao BMO acesso à internet através da Pesquisa Google.

from langchain_community.tools import GoogleSearchRun
from langchain_community.utilities import GoogleSearchAPIWrapper

#"wrapper" da API, que lida com a comunicação.
search_wrapper = GoogleSearchAPIWrapper()

#ferramenta que o agente LangChain usará.
# O nome e a descrição são CRUCIAIS para que o agente saiba QUANDO usar esta ferramenta.
google_search_tool = GoogleSearchRun(
    name="google_search",
    description="Uma ferramenta para pesquisar na internet por informações recentes, eventos atuais, notícias e fatos. Use para qualquer pergunta que você não saiba a resposta.",
    api_wrapper=search_wrapper
)