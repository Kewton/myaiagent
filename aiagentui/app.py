import streamlit as st
import requests
import os
from dotenv import load_dotenv


load_dotenv()
AIAGENT_API_URI = os.getenv('AIAGENT_API_URI', "192.168.11.8")
AIAGENT_PORT = os.getenv('AIAGENT_PORT', "31953")
AIAGENT_API_PATH = os.getenv('AIAGENT_API_PATH', "/aiagent-api/v1/aiagent")

# レイアウトの調整（スマホ対応）
st.set_page_config(layout="wide")

# タイトル
st.title("AIエージェントUI")

# モード選択
modelname = st.selectbox("モデルを選択してください", ["gemini-1.5-pro", "gpt-4o-mini"])
max_iterations = st.selectbox("最大試行回数を選択してください", range(1, 10))

# 入力フィールド
user_input = st.text_area("メッセージを入力してください", height=100)


# 送信ボタン
if st.button("送信"):
    if user_input.strip():
        try:
            # APIにリクエストを送信
            api_url = f"http://{AIAGENT_API_URI}:{AIAGENT_PORT}{AIAGENT_API_PATH}"
            parameters = {
                "user_input": user_input,
                "model_name": modelname,
                "max_iterations": max_iterations
            }
            print(api_url)
            print(parameters)
            response = requests.post(api_url, json=parameters)
            
            # レスポンスの処理
            if response.status_code == 200:
                result = response.json()
                st.subheader("自身の入力")
                st.write(result["result"][0]["content"])
                st.subheader("AIエージェントの回答")
                st.write(result["result"][1]["content"])

            else:
                st.error(f"エラー: {response.status_code}")
        except Exception as e:
            st.error(f"リクエスト中にエラーが発生しました: {e}")
    else:
        st.warning("メッセージを入力してください")

# スタイルのカスタマイズ（スマホ対応のデザイン調整）
st.markdown("""
    <style>
        textarea {
            font-size: 18px;
        }
        button {
            font-size: 20px;
            width: 100%;
        }
        .stButton button {
            width: 100%;
            height: 50px;
            font-size: 20px;
        }
    </style>
    """, unsafe_allow_html=True)