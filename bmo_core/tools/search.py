# bmo_core/tools/search.py
# Ferramenta para dar ao BMO acesso à internet através da Pesquisa Google.
# Versão atualizada para usar o pacote langchain-google-community.

# --- MUDANÇA NOS IMPORTS ---
# Em vez de importar de langchain_community, importamos do novo pacote dedicado.
from langchain_google_community import GoogleSearchRun, GoogleSearchAPIWrapper

# Lazy initialization to avoid requiring credentials at import time
_google_search_tool = None

def get_google_search_tool():
    """Get or initialize the Google Search tool."""
    global _google_search_tool
    if _google_search_tool is None:
        search_wrapper = GoogleSearchAPIWrapper()
        _google_search_tool = GoogleSearchRun(
            name="google_search",
            description="Uma ferramenta para pesquisar na internet por informações recentes, eventos atuais, notícias e fatos. Use para qualquer pergunta que você não saiba a resposta.",
            api_wrapper=search_wrapper
        )
        print("✅ Ferramenta de Pesquisa Google inicializada.")
    return _google_search_tool

# For backward compatibility, expose as google_search_tool
# But it will only be initialized when accessed
class LazySearchTool:
    def __getattr__(self, name):
        return getattr(get_google_search_tool(), name)

google_search_tool = LazySearchTool()