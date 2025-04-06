from aiagent.aiagent.agent_type2 import creatAgentType2

agent_executor = creatAgentType2()
user_input = """
2025/4/7の葛飾区の天気予報を調べてベール送信してください
"""
result = agent_executor.invoke({"input": user_input})
final_answer = result.get("output", result)
print("======")
print(final_answer)