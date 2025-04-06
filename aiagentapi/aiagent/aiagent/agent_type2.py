#from dotenv import load_dotenv
from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from aiagent.tool.google_search_by_gemini import google_search_tool
from aiagent.googleapis import send_email_tool, gmail_search_search_tool
import os

## 環境変数のロード
#load_dotenv()


def creatAgentType2():
    # HubからReact用プロンプトを取得
    prompt = hub.pull("hwchase17/react")

    # LLMの初期化（例: gpt-4o-mini）
    # gemini-1.5-pro
    # gemini-2.5-pro-exp-03-25
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=os.environ["GEMINI_API_KEY"])

    # ツールリストに google_search_tool を含める
    tools = [
        google_search_tool,
        send_email_tool,
        gmail_search_search_tool
    ]

    # 1. エージェントの作成
    agent = create_react_agent(model, tools, prompt)

    # 2. AgentExecutor の実行準備（handle_parsing_errors と return_intermediate_steps を True に設定）
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        return_intermediate_steps=True
    )
    return agent_executor