from aiagent.langchain.utils.html2markdown import getMarkdown
from aiagent.langchain.tool.generate_podcast_script import generate_podcast_script
from dotenv import load_dotenv
from aiagent.langchain.utils.html2markdown import getMarkdown
from aiagent.langchain.utils.execllm import execLlmApi

load_dotenv()


# print(getMarkdown("https://news.yahoo.co.jp/articles/031edf378bc2b3f15dc6da4ed7f09b1569fd7929"))

_messages = [
    {"role": "system", "content": "あなたは売れっ子メルマガです"},
    {"role": "user", "content": "葛飾区についてのメルマガを執筆してください。"}
]

result = execLlmApi("gemini-2.0-flash", _messages)

print(result)