from contextlib import asynccontextmanager
from aiagent.langgraph.util import isChatGptAPI, isGemini, isChatGPT_o, isClaude
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from core.config import settings


# Make the graph with MCP context
@asynccontextmanager
async def make_graph(_mcpmodule: str = "mymcp.stdioall", _graphname: str = "Tool Agent"):
    if isChatGptAPI(settings.GRAPH_AGENT_MODEL) or isChatGPT_o(settings.GRAPH_AGENT_MODEL):
        model = ChatOpenAI(model=settings.GRAPH_AGENT_MODEL)
    elif isGemini(settings.GRAPH_AGENT_MODEL):
        # gemini-2.5-flash-preview-04-17
        model = ChatGoogleGenerativeAI(model=settings.GRAPH_AGENT_MODEL)
    elif isClaude(settings.GRAPH_AGENT_MODEL):
        model = ChatAnthropic(model=settings.GRAPH_AGENT_MODEL)
    else:
        model = ChatOllama(
            model=settings.GRAPH_AGENT_MODEL,
            base_url=settings.OLLAMA_URL,
        )

    mcp_client = MultiServerMCPClient(
        {
            "my-mcp-tool": {
                "command": "python",
                "args": ["-m", _mcpmodule],
                "transport": "stdio",
            }
        }
    )

    async with mcp_client:
        mcp_tools = mcp_client.get_tools()
        print(f"Available tools: {[tool.name for tool in mcp_tools]}")
        graph = create_react_agent(model, mcp_client.get_tools())

        # graph = graph_builder.compile()
        graph.name = _graphname

        yield graph
