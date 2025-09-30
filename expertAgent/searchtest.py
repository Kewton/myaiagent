import http.client
import json
from mymcp.utils.html2markdown import getMarkdown
from mymcp.utils.chatollama import extract_knowledge_from_text
import concurrent.futures
from core.config import settings
import time


def google_search(_query):
    start_time = time.time()  # 開始時刻
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": _query,
        "location": "Japan",
        "gl": "jp",
        "hl": "ja",
        "num": 5
    })
    headers = {
        'X-API-KEY': settings.SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    #print(data.decode("utf-8"))

    #print("===================================")

    jsondata = json.loads(data.decode("utf-8"))
    #print(jsondata)

    # 指定キーを存在する場合のみ削除
    for key in ["searchParameters", "images", "relatedSearches", "credits"]:
        jsondata.pop(key, None)
        

    # print("===================================")
    # # with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    # #     futures = [executor.submit(get_entry_summary, a) for a in jsondata['organic']]
    # #     results = [f.result() for f in concurrent.futures.as_completed(futures)]

    end_time = time.time()  # 終了時刻
    print(f"google_search 実行時間: {end_time - start_time:.2f} 秒")
    return jsondata


def get_entry_summary(_organic):
    print(f"start {_organic['title']}")
    title = _organic['title']
    link = _organic['link']
    md = getMarkdown(link, False)
    print(md)
    kl = extract_knowledge_from_text(md, "mlx-community")
    return {
        "title": title,
        "link": link,
        "knowledge": kl
    }


if __name__ == "__main__":
    # results = google_search(_query="LLM")
    # print(f"results: {results}")
    # """
    # """
    # # # 例: 結果を表示
    # for r in results:
    #     print(r)

    md = getMarkdown("https://www3.nhk.or.jp/news/html/20250505/k10014797341000.html", False)
    print(md["result"])