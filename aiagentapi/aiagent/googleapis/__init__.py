from langchain.tools import tool
from typing import Dict
from aiagent.googleapis.gmail.readonly import get_emails_by_keyword
from aiagent.googleapis.gmail.send import send_email
import os


@tool
def gmail_search_search_tool(keywrod: str, top: int = 5) -> Dict:
    """gmailからキーワード検索した結果をtopに指定した件数文返却します。"""
    return get_emails_by_keyword(keywrod, top)


@tool
def send_email_tool(body: str, subject: str = "AIエージェントからの手紙") -> str:
    """
    メール送信します。subjectには件名を、bodyには本文を指定します。
    """
    return send_email(os.getenv("MAIL_TO"), subject, body)
