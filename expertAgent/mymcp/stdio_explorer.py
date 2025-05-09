from typing import Dict
from mymcp.googleapis.gmail.readonly import get_emails_by_keyword
from mymcp.tool.google_search_by_gemini import googleSearchAgent
from mymcp.utils.html2markdown import getMarkdown
from mcp.server.fastmcp import FastMCP
from mymcp.utils.extract_knowledge_from_text import extract_knowledge_from_text


mcp = FastMCP("explorer")


@mcp.tool()
async def gmail_search_search_tool(keywrod: str, top: int = 5) -> Dict:
    """gmailからキーワード検索した結果をtopに指定した件数文返却します。"""
    return get_emails_by_keyword(keywrod, top)


@mcp.tool()
async def google_search_tool(input_query: str) -> str:
    """Google Searchを用いて情報を取得し、結果を返す。

    Gemini APIを使用してGoogle Searchを実行し、
    検索結果から必要な情報を抽出して返却する。

    Args:
        query (str): 検索クエリ。

    Returns:
        dict: 検索結果を含む辞書。
              - result (str): Gemini APIから返されたテキストと参照されたURIから取得したHTMLをマークダウンファイル化したもの。
              - search_entry_point (List[str]): 検索結果ページへのリンクのリスト。
              - uris (List[str]): 参照されたURIのリスト。
    Examples:
        >>> google_search_tool("東京スカイツリーの高さ")
        GoogleSearchResult(
            result="東京スカイツリーの高さは634mです。",
            search_entry_point=["https://www.tokyo-skytree.jp/"],
            uris=["https://ja.wikipedia.org/wiki/東京スカイツリー"]
        )
    """
    return googleSearchAgent(input_query)


@mcp.tool()
async def getMarkdown_tool(input_url: str) -> str:
    """指定されたURLからHTMLを取得し、マークダウン形式に変換します。
    Args:
        url (str): 変換するURL。
    Returns:
        str: マークダウン形式に変換されたテキスト。
    """
    return extract_knowledge_from_text(getMarkdown(input_url))


if __name__ == "__main__":
    mcp.run(transport='stdio')
