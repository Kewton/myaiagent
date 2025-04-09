import gradio as gr
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# --- API設定 (変更なし) ---
PROTOCOL = os.getenv("PROTOCOL", "http")
FASTAPI_SERVICE_NAME = os.getenv("FASTAPI_SERVICE_NAME", "backend")
FASTAPI_PORT = os.getenv("FASTAPI_PORT", "8000")
API_ENDPOINT_PATH = os.getenv("API_ENDPOINT_PATH", "/my_root/v1/aiagent")
URL = f"{PROTOCOL}://{FASTAPI_SERVICE_NAME}:{FASTAPI_PORT}{API_ENDPOINT_PATH}"


# --- チャット処理関数 (エラーハンドリング、履歴更新ロジック改善) ---
def chat(user_input, chat_history):
    chat_history = chat_history or []
    user_input_stripped = user_input.strip()  # 前後の空白を除去

    # 空のメッセージは送信しない
    if not user_input_stripped:
        return "", chat_history, chat_history  # 入力欄はクリア、履歴はそのまま

    # ユーザーメッセージを履歴に追加 (role/content形式)
    chat_history.append({"role": "user", "content": user_input_stripped})

    parameters = {
        "model_name": "chatgpt-4o-latest",
        "user_input": user_input_stripped
    }

    try:
        # API呼び出し (タイムアウトとエラーチェック追加)
        response = requests.post(URL, json=parameters, timeout=300)
        response.raise_for_status()  # 4xx, 5xxエラーで例外を発生させる
        result = response.json()

        # --- アシスタントの応答を抽出 ---
        # バックエンドの応答形式に合わせて調整が必要
        # 例1: {"result": [{"role":"user", ...}, {"role":"assistant", "content": "..."}]}
        if "result" in result and isinstance(result.get("result"), list) and len(result["result"]) > 1 and isinstance(result["result"][1], dict):
            assistant_msg = result["result"][1] # 2番目の要素をアシスタント応答と仮定
            if assistant_msg.get("role") == "assistant" and "content" in assistant_msg:
                chat_history.append(assistant_msg)
            else:
                # 想定形式だが中身が違う場合
                chat_history.append({"role": "assistant", "content": f"Error: Unexpected assistant message format in result list."})

        # 例2: シンプルに {"assistant_reply": "..."} のような形式の場合
        elif "assistant_reply" in result and isinstance(result["assistant_reply"], str):
            chat_history.append({"role": "assistant", "content": result["assistant_reply"]})

        # ★★★ もし上記以外、元のコードのように result["result"] が応答テキストリストなど、
        # 特殊な形式の場合は、ここの抽出ロジックをそれに合わせてください ★★★

        else:
            # 予期しない応答形式の場合
            chat_history.append({"role": "assistant", "content": f"Error: Could not parse assistant response from backend. Received: {str(result)[:200]}"}) # 応答の一部を表示

    except requests.exceptions.Timeout:
        print("API Request Timed Out")
        chat_history.append({"role": "assistant", "content": "Error: The request to the backend timed out."})
    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        chat_history.append({"role": "assistant", "content": f"Error communicating with backend: {e}"})
    except Exception as e:
        # JSONデコードエラーなどもここで捕捉
        print(f"Chat Processing Error: {e}")
        chat_history.append({"role": "assistant", "content": f"An internal error occurred: {e}"})

    # 入力欄をクリアし、更新された履歴を返す
    return "", chat_history, chat_history


# --- Gradio UI の構築 (スマホ対応) ---
# Softテーマを適用
with gr.Blocks() as demo:
    gr.Markdown("## AI Agent Chat")  # タイトルを追加

    # チャットボットの高さを調整し、スクロール可能に
    chatbot = gr.Chatbot(
        label="Assistant",
        height=600,             # 高さをスマホ向けに調整
        type='messages'
        # bubble_full_width=False # 吹き出しの幅を調整
        )
    state = gr.State([])  # チャット履歴を保持

    # 入力要素を縦に配置 (Columnを使用)
    with gr.Column():
        user_input = gr.Textbox(
            lines=1,  # シングルライン入力
            label="Your Message",
            placeholder="Type your message and press Enter or click Submit...",  # プレースホルダーを追加
            # scale=4 # Column内では scale はあまり意味がないかも
            )
        submit = gr.Button(
            "Submit",
            variant="primary"  # ボタンを強調表示
            # scale=1
            )

    # Enterキーでの送信を有効化
    user_input.submit(
        chat,
        inputs=[user_input, state],
        outputs=[user_input, chatbot, state]  # 出力をchatbotとstateに反映
    )
    # ボタンクリックでの送信
    submit.click(
        chat,
        inputs=[user_input, state],
        outputs=[user_input, chatbot, state]  # 出力をchatbotとstateに反映
    )

# サーバー起動設定 (変更なし)
demo.launch(server_name="0.0.0.0", server_port=7860)
# demo.launch()

# 不要になった関数を削除 (今回は format_intermediate_steps)