# from aiagent.langchain.googleapis.drive import get_file_id_and_mime_type, upload_file


# name, id, mimeType = get_file_id_and_mime_type("MyAiAgent")

# print(upload_file("README.md", "./README.md", "text/plain", id))
import asyncio
from core.logger import setup_logging

setup_logging()

from mymcp.tool.google_search_by_gemini import googleSearchAgent


_input = "東京スカイツリーの高さ"

result = googleSearchAgent(_input)
print(result)