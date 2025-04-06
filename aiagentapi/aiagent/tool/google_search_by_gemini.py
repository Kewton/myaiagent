import google.generativeai as genai
from bs4 import BeautifulSoup
from langchain.tools import tool
from typing import Dict
import os


@tool
def google_search_tool(query: str) -> Dict:
    """Google検索を実行して、検索結果やリンク一覧を返します。"""
    return googleSearchAgent(query)


def googleSearchAgent(_input):
    """Google Searchを用いて情報を取得し、結果を返す。

    Gemini APIを使用してGoogle Searchを実行し、
    検索結果から必要な情報を抽出して返却する。

    Args:
        _input (str): 検索クエリ。

    Returns:
        dict: 検索結果を含む辞書。
              - result (str): Gemini APIから返されたテキスト。
              - search_entry_point (list): 検索結果ページへのリンクのリスト。
              - uris (list): 参照されたURIのリスト。

    Examples:
        >>> googleSearchAgent("東京スカイツリーの高さ")
        {
            "result": "東京スカイツリーの高さは634mです。",
            "search_entry_point": ["https://www.tokyo-skytree.jp/"],
            "uris": ["https://ja.wikipedia.org/wiki/東京スカイツリー"]
        }
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('models/gemini-1.5-pro')

    _content = f"""
    # 命令指示書
    - 要求に対し前提条件と制約条件を満たす最高の成果物を生成してください。

    # 前提条件
    - あなたは検索AIエージェントです

    # 制約条件
    - 参照したサイト情報を返却に含めること

    # 要求
    {_input}
    """

    response = model.generate_content(
        contents=_content,
        tools='google_search_retrieval')

    soup = BeautifulSoup(response._result.candidates[0].grounding_metadata.search_entry_point.rendered_content, 'html.parser')

    # リンクを抽出
    links = []
    for a in soup.find_all('a'):
        links.append(a['href'])

    uris = []
    for a in response._result.candidates[0].grounding_metadata.grounding_chunks:
        uris.append(a.web.uri)

    _result = {
        "result": response.text,
        "search_entry_point": links,
        "uris": uris
    }

    return _result