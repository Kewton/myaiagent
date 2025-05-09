from langchain_core.messages import AIMessage
from aiagent.langgraph.common import make_graph


async def exploreragent(query: str) -> str:
    async with make_graph("mymcp.stdio_explorer") as graph:
        result = await graph.ainvoke({"messages": query})
        for message in result.get('messages', []):
            if isinstance(message, AIMessage):
                return message.content
        return ""
