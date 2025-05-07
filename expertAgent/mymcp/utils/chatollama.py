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
