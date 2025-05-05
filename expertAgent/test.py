import asyncio
from aiagent.langgraph.sampleagent.graphagent import ainvoke_graphagent
from core.logger import setup_logging

setup_logging()

_input = """
今日は2025/5//5です。
今日の葛飾区の天気を教えてください。
メール送信してください。
"""

print(_input)

result = asyncio.run(ainvoke_graphagent(_input))

print(result)