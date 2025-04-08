from aiagent.utils.html2markdown import getMarkdown
from aiagent.tool.generate_podcast_script import generate_podcast_script
from dotenv import load_dotenv

load_dotenv()


print(generate_podcast_script("gpt-4o-mini", getMarkdown("https://news.yahoo.co.jp/articles/031edf378bc2b3f15dc6da4ed7f09b1569fd7929")))