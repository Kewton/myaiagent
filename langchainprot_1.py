from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from tool.google_search_by_gemini import google_search_tool
from langchain.agents import initialize_agent, AgentType


load_dotenv()

tools = [google_search_tool]

agent = initialize_agent(
    tools=tools,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

response = agent.invoke({
    "input": "2025年4月6日の葛飾区の天気予報を調べ、3歳の子連れ向けの1日のプランを考えてください。"
})
print(response)


#result = google_search_tool.invoke({"query": "東京スカイツリーの高さ"})
#print(result)



#result = model.invoke([HumanMessage(content="熊童子について教えてください。")])
#print(result.content)

#from tool.google_search_by_gemini import googleSearchAgent
#print(googleSearchAgent("葛飾区の明日の天気は？"))