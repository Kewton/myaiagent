from aiagentapi.aiagent.aiagent.StandardAiAgent import StandardAiAgent

user_input = """
2025/4/7の葛飾区の天気予報を調べてベール送信してください
"""

#agent_executor = creatAgentType2()
#result = agent_executor.invoke({"input": user_input})
#final_answer = result.get("output", result)
#print("======")
#print(final_answer)

_agenttype2 = StandardAiAgent(model_name="gpt-4o-mini", max_iterations=3, verbose=False)
print(_agenttype2.invoke(user_input))
print("~~~~~~~~~")
print(_agenttype2.exeid)
print("~~~~~~~~~")
print(_agenttype2.chat_history)
