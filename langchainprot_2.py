from dotenv import load_dotenv
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.agents import AgentExecutor, create_react_agent
from tool.google_search_by_gemini import google_search_tool


load_dotenv()


prompt = hub.pull("hwchase17/react")

model = ChatOpenAI(model="gpt-4o-mini")

tools = [google_search_tool]

#1 エージェントの作成
agent = create_react_agent(model, tools, prompt)

#2 エージェントの実行準備
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

response = agent_executor.invoke({"input": [HumanMessage(content="株式会社Elithの住所を教えてください。最新の公式情報として公開されているものを教えてください。")]})

print(response)