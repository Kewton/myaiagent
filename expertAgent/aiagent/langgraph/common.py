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
async def make_graph(_mcpmodule: str = "mymcp.stdioall", _graphname: str = "Tool Agent", _model: str = settings.GRAPH_AGENT_MODEL):
    if _model is None:
        _model = settings.GRAPH_AGENT_MODEL
        
    if isChatGptAPI(_model) or isChatGPT_o(_model):
        model = ChatOpenAI(model=_model)
    elif isGemini(_model):
        # gemini-2.5-flash-preview-04-17
        model = ChatGoogleGenerativeAI(model=_model)
    elif isClaude(_model):
        model = ChatAnthropic(model=_model)
    else:
        model = ChatOllama(
            model=_model,
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
