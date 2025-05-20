import requests
from core.config import settings
from app.schemas.standardAiAgent import ChatMessage
from typing import List


def chatOllama(_messages: List[ChatMessage], _model: str = settings.OLLAMA_DEF_SMALL_MODEL, _stream: bool = False) -> str:
    """
    Ollama APIを使用してチャットを行う関数
    Args:
        _messages (list): チャットメッセージのリスト。各メッセージは辞書形式で、"role"と"content"を含む。
        _model (str): 使用するモデルの名前。デフォルトは"gemma3:27b-it-qat"。
    """
    # APIエンドポイント（ローカル）
    url = settings.OLLAMA_URL + "/api/chat"

    # 128000
    # 32,768

    if "gemma3" in _model:
        _num_ctx = 128000
    elif  "qwen3" in _model:
        _num_ctx = 32768
    else:
        _num_ctx = 4096

    # リクエストボディ
    payload = {
        "model": _model,
        "messages": _messages,
        "stream": _stream,  # Trueにするとストリームレスポンスになる
        "options": {
            "num_ctx": _num_ctx
        }
    }

    # リクエスト送信
    response = requests.post(url, json=payload)

    # 結果出力
    if response.ok:
        return response.json()["message"]["content"]
    else:
        print("Error:", response.status_code, response.text)
        return "Error occurred"


def chatMlx(_messages: List[ChatMessage]) -> str:
    """
    MLX APIを使用してチャットを行う関数
    Args:
        _messages (list): チャットメッセージのリスト。各メッセージは辞書形式で、"role"と"content"を含む。
        _model (str): 使用するモデルの名前。デフォルトは"gemma3:27b-it-qat"。
    """
    # APIエンドポイント（ローカル）
    url = f"{settings.MLX_LLM_SERVER_URL}/v1/chat/completions"
    HEADERS = {"Content-Type": "application/json"}

    # リクエストボディ
    payload = {
        "messages": _messages
    }

    # リクエスト送信
    response = requests.post(url, json=payload, headers=HEADERS)

    # 結果出力
    if response.ok:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("Error:", response.status_code, response.text)
        return "Error occurred"
    

def extract_knowledge_from_text(_text, _model: str = "gemma3:27b-it-qat"):
    _query = f"""
    # 命令指示書
    入力情報と制約条件を元に下記手順に従い最高の成果物を生成してください。
    
    1. 入力情報に目を通し、重要な情報が存在しない場合は、"情報なし"と返却すること
    2. 重要度が高い順に最大８つの用語を抽出し一覧化すること。
    3. 用語の意味や概念を整理すること。必要に応じてあなたの知見を付与すること。
    4. 用語同士の関係性を整理すること。
    5. 出力情報から不要な情報を削除すること。

    # 制約条件
    - 日本語で返却すること
    - 出力は RESPONSE_FORMAT に従うこと
    - 返却は JSON 形式で行い、コメントやマークダウンは含めないこと
    - 考察など独自の意見は含めないこと

    # 入力情報
    ```
    {_text}
    ```

    # RESPONSE FORMAT:
    ```json
    {{
        "用語名一覧": [
            "用語の名前",
            ・・・
            ],
        "用語の意味や概念": [
            {{
                "用語名": "用語の名前",
                "用語の説明": "用語の意味や概念や定義。必要に応じて具体例を含む",
            }},
            ・・・
            ],
        "関係性": [
            {{
                "用語1": "用語の名前",
                "用語2": "用語の名前",
                "関係性": "用語1と用語2の関係性"
            }},
            ・・・
            ]
    }}
    ```

    """

    _messages = []
    _messages.append(
        {"role": "user", "content": _query}
    )
    
    result = chatMlx(_messages)
    # if _model == "mlx-community":
    #     result = chatMlx(_messages)
    # else:
    #     result = chatOllama(_messages, _model)
    
    print("============================")
    print("extract_knowledge_from_text:")
    print("============================")
    print(result)
    print("============================")
    print("============================")

    return result