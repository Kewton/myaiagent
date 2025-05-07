from core.logger import setup_logging
from mymcp.utils.chatollama import chatOllama

setup_logging()

_input = """
ドラゴンボールの作者を教えてください
/no_think
"""

print(_input)

result = chatOllama([{"role": "user", "content": _input}], "qwen3:32b-q8_0")

print(result)


"""
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:27b-it-qat",
  "prompt": "ドラゴンボールの作者を教えてください",
  "stream": false
}'

curl http://localhost:11434/api/chat -d '{
  "model": "gemma3:27b-it-qat",
  "messages": [{"role": "user", "content": "ドラゴンボールの作者を教えてください"}],
  "stream": false
}'


curl -X POST -H "Content-Type: application/json" -d '{"user_input": "ドラゴンボールの作者をメールで送信してください", "model_name": "1_hello-httpAgentFilter"}' http://localhost:3030/agent/sample
"""
