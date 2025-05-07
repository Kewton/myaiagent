# graph.py
from contextlib import asynccontextmanager
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages.tool import ToolMessage
import asyncio
import json
from core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from aiagent.langgraph.util import isChatGptAPI, isGemini, isChatGPT_o, isClaude
from langchain_ollama import ChatOllama
from langchain_anthropic import ChatAnthropic


# Make the graph with MCP context
@asynccontextmanager
async def make_graph():
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
                "args": ["-m", "mymcp.stdioall"],
                "transport": "stdio",
            }
        }
    )

    async with mcp_client:
        mcp_tools = mcp_client.get_tools()
        print(f"Available tools: {[tool.name for tool in mcp_tools]}")
        graph = create_react_agent(model, mcp_client.get_tools())

        # graph = graph_builder.compile()
        graph.name = "Tool Agent"

        yield graph


# Run the graph with question
async def ainvoke_graphagent(query):
    chat_history = []
    chat_history.append({"role": "user", "content": query})
    async with make_graph() as graph:
        result = await graph.ainvoke({"messages": query})
        # 1. 'messages' キーでメッセージリストを取得
        message_list = result.get('messages', [])  # .get() を使うとキーが存在しない場合もエラーにならない

        # 2. リストが空でないことを確認し、最後のメッセージを取得
        final_output = {}
        humanMessage = ""
        aiMessage = ""
        toolMessages = []
        for message in message_list:
            print("~~~~")
            if isinstance(message, AIMessage):
                aiMessage = message.content
            elif isinstance(message, HumanMessage):
                humanMessage = message.content
            elif isinstance(message, ToolMessage):
                print("ToDo: ToolMessage")
            else:
                print("Unknown message type:", type(message))
                print(message)

        final_output = {
            "humanMessage": humanMessage,
            "aiMessage": aiMessage,
            "toolMessages": toolMessages
        }
        
        chat_history.append({"role": "assistant", "content": aiMessage})
        return chat_history, aiMessage
