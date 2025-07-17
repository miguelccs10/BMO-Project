# bmo_core/agent/memory.py
# Configura e gerencia o armazenamento do histórico de conversas.

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Um dicionário simples em memória para armazenar o histórico de cada sessão.
# Em uma aplicação de produção maior, isso poderia ser substituído por um
# banco de dados como Redis para persistir as conversas.
SESSION_HISTORIES = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    """
    Busca o histórico de uma sessão específica ou cria um novo se não existir.
    """
    if session_id not in SESSION_HISTORIES:
        SESSION_HISTORIES[session_id] = ChatMessageHistory()
    return SESSION_HISTORIES[session_id]

def wrap_with_memory(runnable):
    """
    Envolve uma cadeia (runnable) do LangChain com o gerenciador de memória.
    Isso adiciona a capacidade de lembrar do histórico da conversa.
    """
    return RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="output" # Garante que a chave de saída seja consistente
    )