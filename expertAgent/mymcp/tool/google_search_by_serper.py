import http.client
import json
from mymcp.utils.html2markdown import getMarkdown
from mymcp.utils.chatollama import extract_knowledge_from_text
import concurrent.futures
from typing import List, Union
from pydantic import BaseModel, Field
from mymcp.utils.html2markdown import getMarkdown
from core.config import settings
from core.logger import getlogger

logger = getlogger()


class SerperSearchResult(BaseModel):
    text: str | None = Field(..., description="")
    result: List[Union[dict, str]] = Field(..., description="")


async def google_search_by_serper_list(queries: List[str], num: int = 3) -> str:
    """Google Searchを用いて情報を取得し、結果を返す。

    Serper APIを使用してGoogle Searchを実行し、
    検索結果から必要な情報を抽出して返却する。

    Args:
        _query (str): 検索クエリ。

    Returns:
        SerperSearchResult: 検索結果を含むpydanticモデル。
            - text (str): Gemini APIから返されたテキスト。
            - result (List[dict]): 検索結果から抽出したナレッジのリスト
    """
    logger.info("google_search_by_serperを実行します")
    _serperresults = []
    for _query in queries:
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
            "q": _query,
            "location": "Japan",
            "gl": "jp",
            "hl": "ja",
            "num": num
        })
        headers = {
            'X-API-KEY': settings.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        jsondata = json.loads(data.decode("utf-8"))
        for a in jsondata['organic']:
            _serperresults.append(a)

    # 並列で実行して結果をリストで取得
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num*2) as executor:
        futures = [executor.submit(get_entry_summary, a) for a in _serperresults]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    result_model = SerperSearchResult(
        text="ok",
        result=results,
    )

    return result_model.model_dump_json()


async def get_overview_by_google_serper(queries: List[str], num: int = 3) -> str:
    """Google Searchを用いて情報を取得し、結果を返す。

    Serper APIを使用してGoogle Searchを実行し、
    検索結果から必要な情報を抽出して返却する。

    Args:
        _query (List[str]): 検索クエリのリスト

    Returns:
        SerperSearchResult: 検索結果を含むpydanticモデル。
            - text (str): Gemini APIから返されたテキスト。
            - result (List[dict]): 検索結果から抽出したナレッジのリスト
    """
    logger.info("get_overview_by_google_serperを実行します")
    _serperresults = []
    for _query in queries:
        conn = http.client.HTTPSConnection("google.serper.dev")
        payload = json.dumps({
            "q": _query,
            "location": "Japan",
            "gl": "jp",
            "hl": "ja",
            "num": num
        })
        headers = {
            'X-API-KEY': settings.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        jsondata = json.loads(data.decode("utf-8"))
        for key in ["searchParameters", "images", "relatedSearches", "credits"]:
            jsondata.pop(key, None)
        
        print(_query)
        print(jsondata)
        # for a in jsondata:
        _serperresults.append(jsondata)

    result_model = SerperSearchResult(
        text="ok",
        result=_serperresults,
    )

    print(f"result_model: {result_model}")
    return result_model.model_dump_json()


def get_entry_summary(_organic):
    print(f"start {_organic['title']}")
    title = _organic['title']
    link = _organic['link']
    md = getMarkdown(link, False)
    # print(md)
    if isinstance(md, dict):
        result_text = md.get("result", "")
    else:
        result_text = md
    if result_text.startswith("JavaScript"):
        print(f"'{title}' と '{link}' は 'JavaScript' から始まっています。")
        print(f"md: {md}")
        kl = "情報なし"
    elif md["state"] == "success":
        kl = extract_knowledge_from_text(md["result"], "mlx-community") # mlx-community, gemma3:4b
    else:
        kl = "情報取得失敗"
    return {
        "title": title,
        "link": link,
        "knowledge": kl
    }
