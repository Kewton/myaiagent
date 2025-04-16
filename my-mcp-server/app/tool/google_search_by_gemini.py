import os
from typing import List
import google.generativeai as genai
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from app.utils.html2markdown import getMarkdown


class GoogleSearchResult(BaseModel):
    result: List[dict] = Field(..., description="Gemini APIから返されたテキストと参照されたURIから取得したHTMLをマークダウンファイル化したもの")
    search_entry_point: List[str] = Field(
        ..., description="検索結果ページへのリンクのリスト"
    )
    uris: List[str] = Field(
        ..., description="参照されたURIのリスト"
    )


def googleSearchAgent(_input: str) -> str:
    """Google Searchを用いて情報を取得し、結果を返す。

    Gemini APIを使用してGoogle Searchを実行し、
    検索結果から必要な情報を抽出して返却する。

    Args:
        _input (str): 検索クエリ。

    Returns:
        GoogleSearchResult: 検索結果を含むpydanticモデル。
              - result (str): Gemini APIから返されたテキスト。
              - search_entry_point (List[str]): 検索結果ページへのリンクのリスト。
              - uris (List[str]): 参照されたURIのリスト。

    Examples:
        >>> googleSearchAgent("東京スカイツリーの高さ")
        GoogleSearchResult(
            result="東京スカイツリーの高さは634mです。",
            search_entry_point=["https://www.tokyo-skytree.jp/"],
            uris=["https://ja.wikipedia.org/wiki/東京スカイツリー"]
        )
    """
    # APIキーの取得と設定（環境変数から取得する）
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
        tools='google_search_retrieval'
    )

    # BeautifulSoupを用いてレンダリングされたHTMLからリンクを抽出
    soup = BeautifulSoup(
        response._result.candidates[0].grounding_metadata.search_entry_point.rendered_content,
        'html.parser'
    )

    links = [a['href'] for a in soup.find_all('a') if a.has_attr('href')]

    uris = []
    markdowns = []
    for chunk in response._result.candidates[0].grounding_metadata.grounding_chunks:
        # chunk.web.uriが存在することを確認して追加
        if hasattr(chunk.web, 'uri'):
            uris.append(chunk.web.uri)

    markdowns.append({"GoogleApiResponse":response.text})
    for uri in uris:
        markdowns.append(getMarkdown(uri, False))

    # pydanticモデルで結果を生成
    result_model = GoogleSearchResult(
        result=markdowns,
        search_entry_point=links,
        uris=uris
    )

    print(result_model.json(indent=2, ensure_ascii=False))

    return result_model.model_dump_json()
