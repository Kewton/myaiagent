from langchain.tools import tool
from aiagent.utils.html2markdown import getMarkdown
from typing import Dict


@tool
def getMarkdown_tool(url: str) -> Dict:
    """指定したURLからhtmlを取得しmarkdownに変換して返します。"""
    return getMarkdown(url)
