"""
BMO Agent Executor
Builds and exports the LangChain agent with memory and intelligent routing.
Refactored to use YAML-based configuration following best practices.
"""

import traceback
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub
from pydantic import BaseModel, Field

# --- Imports from new configuration system ---
from config.config_manager import get_config
from bmo_core.agent.memory import wrap_with_memory
from bmo_core.tools.spotify import (
    play_music_on_spotify,
    control_spotify_playback,
    get_current_spotify_song
)
from bmo_core.tools.calendar import get_next_appointment
from bmo_core.tools.search import google_search_tool


class RouteQuery(BaseModel):
    """Model for router output validation."""
    destination: str = Field(
        description="O destino para rotear a pergunta. Pode ser 'ferramentas' ou 'conversa'."
    )


class BMOAgent:
    """
    BMO LangChain Agent with intelligent routing between conversation and tools.

    This agent uses a three-tier architecture:
    1. Router: Decides between conversation and tool usage
    2. Conversation Chain: Handles general conversation
    3. Tool Agent Chain: Handles tool-based actions (Spotify, Calendar, Search)

    All chains share the same conversation memory for context awareness.
    """

    def __init__(self):
        """Initialize the BMO agent with configuration from YAML."""
        self.config = get_config()
        self.agent_with_chat_history: Optional[object] = None

        try:
            self._build_agent()
            print("✅ Agente BMO inicializado com sucesso.")
        except Exception as e:
            print(f"❌ ERRO: Falha ao inicializar o BMOAgent. {e}")
            traceback.print_exc()

    def _build_agent(self):
        """Build the agent with all components."""
        # --- LLM Configuration ---
        llm_config = self.config.config.llm
        groq_api_key = self.config.get_api_key("groq")

        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        # Create LLMs with different temperatures for different purposes
        router_llm = ChatGroq(
            temperature=llm_config.temperatures.router,
            model_name=llm_config.model_name,
            groq_api_key=groq_api_key
        )

        agent_llm = ChatGroq(
            temperature=llm_config.temperatures.agent,
            model_name=llm_config.model_name,
            groq_api_key=groq_api_key
        )

        # --- Conversation Chain ---
        conv_prompt = ChatPromptTemplate.from_messages([
            ("system", self.config.get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        conversation_chain = conv_prompt | agent_llm | StrOutputParser()

        # --- Tool Agent Chain ---
        # Load tools conditionally based on configuration
        tools = []

        if self.config.is_tool_enabled("spotify"):
            tools.extend([
                play_music_on_spotify,
                control_spotify_playback,
                get_current_spotify_song
            ])
            print("   ✓ Spotify tools carregadas")
        else:
            print("   ⊗ Spotify tools desabilitadas")

        if self.config.is_tool_enabled("google_calendar"):
            tools.append(get_next_appointment)
            print("   ✓ Google Calendar tool carregada")
        else:
            print("   ⊗ Google Calendar tool desabilitada")

        if self.config.is_tool_enabled("google_search"):
            tools.append(google_search_tool)
            print("   ✓ Google Search tool carregada")
        else:
            print("   ⊗ Google Search tool desabilitada")

        if not tools:
            print("   ⚠️  AVISO: Nenhuma ferramenta habilitada! O agente funcionará apenas no modo conversação.")

        # Load the standard OpenAI tools agent prompt from LangChain Hub
        agent_prompt = hub.pull("hwchase17/openai-tools-agent")
        agent = create_openai_tools_agent(agent_llm, tools, agent_prompt)

        tool_agent_chain = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=llm_config.agent.verbose,
            handle_parsing_errors=llm_config.agent.handle_parsing_errors,
            max_iterations=llm_config.agent.max_iterations
        )

        # --- Structured Router ---
        router_prompt = ChatPromptTemplate.from_template(
            self.config.get_router_template()
        )
        structured_router = router_llm.with_structured_output(RouteQuery)
        router_chain = router_prompt | structured_router

        # --- Main Chain with Routing Logic ---
        def route(info):
            """Route to appropriate chain based on router decision."""
            destination = info["destination"].destination.lower()
            if "ferramentas" in destination:
                return tool_agent_chain
            else:
                return conversation_chain

        # Build the full chain with routing
        full_chain = RunnablePassthrough.assign(
            destination=lambda x: router_chain.invoke({
                "input": x["input"],
                "chat_history": x["chat_history"]
            })
        ) | RunnableLambda(lambda x: route(x).invoke(x))

        # --- Add Memory Management ---
        self.agent_with_chat_history = wrap_with_memory(full_chain)

    def run(self, user_question: str, session_id: str = "default_session") -> str:
        """
        Execute the agent with a user question.

        Args:
            user_question: The user's input text
            session_id: Session identifier for conversation memory

        Returns:
            The agent's response as a string
        """
        if not self.agent_with_chat_history:
            return self.config.prompts.errors["brain_error"]

        try:
            # Invoke the agent with memory management
            response = self.agent_with_chat_history.invoke(
                {"input": user_question},
                config={"configurable": {"session_id": session_id}}
            )

            # Handle both dict (from agent) and string (from conversation) responses
            if isinstance(response, dict):
                return response.get('output', self.config.prompts.errors["parsing_error"])
            return response

        except Exception as e:
            print(f"❌ ERRO: Falha ao invocar a cadeia principal. {e}")
            traceback.print_exc()
            return self.config.prompts.errors["agent_error"]
