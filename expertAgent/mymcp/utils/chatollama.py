import requests
from core.config import settings


def chatOllama(_messages: list, _model: str = settings.OLLAMA_DEF_SMALL_MODEL, _stream: bool = False) -> str:
    """
    Ollama APIを使用してチャットを行う関数
    Args:
        _messages (list): チャットメッセージのリスト。各メッセージは辞書形式で、"role"と"content"を含む。
        _model (str): 使用するモデルの名前。デフォルトは"gemma3:27b-it-qat"。
    """
    # APIエンドポイント（ローカル）
    url = settings.OLLAMA_URL + "/api/chat"

    # リクエストボディ
    payload = {
        "model": _model,
        "messages": _messages,
        "stream": _stream  # Trueにするとストリームレスポンスになる
    }

    # リクエスト送信
    response = requests.post(url, json=payload)

    # 結果出力
    if response.ok:
        return response.json()["message"]["content"]
    else:
        print("Error:", response.status_code, response.text)
        return "Error occurred"


def extract_knowledge_from_text(_text, _model: str = "gemma3:27b-it-q8_0"):
    _query = f"""
    # 命令指示書
    入力情報と制約条件に従って最高の成果物を日本語で生成してください。

    # 制約条件
    - ナレッジを抽出すること
    - 日本語で返却すること

    # 入力情報
    {_text}
    """

    _messages = []
    _messages.append(
        {"role": "user", "content": _query}
    )

    result = chatOllama(_messages, _model)

    print("============================")
    print("extract_knowledge_from_text:")
    print("============================")
    print(result)
    print("============================")
    print("============================")

    return result