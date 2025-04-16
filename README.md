## 環境構築
### 

# bk
```
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

```
uvicorn app.main:app --reload
```

```
docker-compose up --build
```


scp ./aiagentapi/token/token.json newton@192.168.11.8:/mnt/my_ssd/k3s_storage/secret/token

# token格納フォルダ
/mnt/my_ssd/k3s_storage/secret/token


server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}



location / {
    proxy_pass http://127.0.0.1:7860/;
    proxy_read_timeout 180s;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}



import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
AIAGENT_API_URI = os.getenv('AIAGENT_API_URI', "192.168.11.8")
AIAGENT_PORT = os.getenv('AIAGENT_PORT', "31953")
AIAGENT_API_PATH = os.getenv('AIAGENT_API_PATH', "/aiagent-api/v1/aiagent")

MODEL_LIST = []
if os.getenv('MODEL_LIST', "gemini-1.5-pro"):
    MODEL_LIST = [model.strip() for model in os.getenv('MODEL_LIST', "gemini-1.5-pro").split(',') if model.strip()]

# テンプレートの定義（名前と本文）
PROMPT_TEMPLATES = {
    "なし（手動入力）": "",
    "記事要約": "以下の記事を要約してください：\n\n＜ここに記事本文を貼り付けてください＞",
    "コードレビュー依頼": "以下のコードの改善点をレビューしてください：\n\n```python\n# ここにコードを貼ってください\n```",
    "マーケティング用アイデア出し": "新しいプロダクトを紹介するSNS投稿のアイデアを10個提案してください。\n\n商品名: 〇〇\n特徴: 〜〜〜",
}

# レイアウトの調整（スマホ対応）
st.set_page_config(layout="wide")

# タイトル
st.title("AIエージェントUI")

# モード選択
modelname = st.selectbox("モデルを選択してください", MODEL_LIST)
max_iterations = st.selectbox("最大イテレーション数を選択してください", range(4, 12))

# プロンプトテンプレート選択
selected_template_name = st.selectbox("テンプレートを選択してください", list(PROMPT_TEMPLATES.keys()))

# テキストエリアにテンプレート内容を初期表示（選択時のみ変更）
if "last_template" not in st.session_state:
    st.session_state.last_template = ""

if selected_template_name != st.session_state.last_template:
    st.session_state.user_input = PROMPT_TEMPLATES[selected_template_name]
    st.session_state.last_template = selected_template_name

# ユーザー入力欄
user_input = st.text_area("メッセージを入力してください", value=st.session_state.get("user_input", ""), height=100, key="user_input")

# 送信ボタン
if st.button("送信"):
    if user_input.strip():
        try:
            api_url = f"http://{AIAGENT_API_URI}:{AIAGENT_PORT}{AIAGENT_API_PATH}"
            parameters = {
                "user_input": user_input,
                "model_name": modelname,
                "max_iterations": max_iterations
            }
            response = requests.post(api_url, json=parameters)

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

# スタイルのカスタマイズ（スマホ対応）
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
