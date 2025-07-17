# bmo_core/tools/search.py
# Ferramenta para dar ao BMO acesso à internet através da Pesquisa Google.
# Versão atualizada para usar o pacote langchain-google-community.

# --- MUDANÇA NOS IMPORTS ---
# Em vez de importar de langchain_community, importamos do novo pacote dedicado.
from langchain_google_community import GoogleSearchRun, GoogleSearchAPIWrapper

search_wrapper = GoogleSearchAPIWrapper()

google_search_tool = GoogleSearchRun(
    name="google_search",
    description="Uma ferramenta para pesquisar na internet por informações recentes, eventos atuais, notícias e fatos. Use para qualquer pergunta que você não saiba a resposta.",
    api_wrapper=search_wrapper
)

print("✅ Ferramenta de Pesquisa Google inicializada.")