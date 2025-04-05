from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langgraph.graph.state import AgentState
from langchain.agents import Tool
from langchain.tools import tool
from tool.google_search_by_gemini import google_search_tool


load_dotenv()

tools = [google_search_tool]

# 2. LLMの準備（OpenAIのChatモデルなど）
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. ReActエージェント作成
agent_node = create_react_agent(llm, tools)

# 4. LangGraphでステートマシンを構築
graph = StateGraph(AgentState)

# agentをノードとして追加
graph.add_node("agent", agent_node)

# 開始→エージェント→終了 という1ステップ構成
graph.set_entry_point("agent")
graph.set_finish_point("agent")

# グラフをビルド
app = graph.compile()

# 5. 実行
response = app.invoke({"input": "2025年4月6日の葛飾区の天気予報を調べ、3歳の子連れ向けの1日のプランを考えてください。"})
print(response["messages"][-1].content)  # 最後の出力のみ表示
