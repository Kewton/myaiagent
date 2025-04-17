import streamlit as st
import requests
import os
from dotenv import load_dotenv


load_dotenv()
AIAGENT_API_URI = os.getenv('AIAGENT_API_URI', "192.168.11.8")
AIAGENT_PORT = os.getenv('AIAGENT_PORT', "31953")
AIAGENT_API_PATH = os.getenv('AIAGENT_API_PATH', "/aiagent-api/v1/aiagent")
AIAGENT_API_PATH_1_1 = os.getenv('AIAGENT_API_PATH_1_1', "/aiagent-api/v1_1/aiagent")

MODEL_LIST = []
if os.getenv('MODEL_LIST', "gemini-1.5-pro"):
    # 1. カンマ(,)で文字列を分割する -> ['server1...', 'server2...', ' 192...', ' server3... ']
    # 2. 各要素の前後の空白を strip() で除去する -> ['server1...', 'server2...', '192...', 'server3...']
    # 3. 空文字列になった要素を除去する (例: ",," のような場合)
    MODEL_LIST = [model.strip() for model in os.getenv('MODEL_LIST', "gemini-1.5-pro").split(',') if model.strip()]

# テンプレートの定義（名前と本文）
PROMPT_TEMPLATES = {
    "なし（手動入力）": "",
    "メルマガ生成（URL指定）": "以下の記事からメルマガを生成してメール送信してください。：\n\n# 記事",
    "メルマガ生成（キーワード指定）": "以下のキーワード毎に関係する記事を検索し、取得したURIをもとにURLの一覧を作成し、このURLの記事をもとにメルマガを生成してメール送信してください。：\n\n# キーワード",
    "ポッドキャスト生成": "以下の記事とその他情報からポッドキャストを生成してGoogleDriveにアップし、ポッドキャストの台本とリンクをメール送信してください：\n\n# 記事\n\n\n\n# その他情報",
    "ADK": "",
    "graph": "",
}

# レイアウトの調整（スマホ対応）
st.set_page_config(layout="wide")

# タイトル
st.title("AIエージェント")

# モード選択
modelname = st.selectbox("モデルを選択してください", MODEL_LIST)
max_iterations = st.selectbox("最大イテレーション数を選択してください", range(6, 15))
thought_process_Flg = st.selectbox("思考プロセスを出力しますか？", [False, True])

# プロンプトテンプレート選択
selected_template_name = st.selectbox("処理モードを選択してください", list(PROMPT_TEMPLATES.keys()))

# テキストエリアにテンプレート内容を初期表示（選択時のみ変更）
if "last_template" not in st.session_state:
    st.session_state.last_template = ""

if selected_template_name != st.session_state.last_template:
    # st.session_state.user_input = PROMPT_TEMPLATES[selected_template_name]
    st.session_state.last_template = selected_template_name

# 入力フィールド
user_input = st.text_area(
    "メッセージを入力してください",
    value=st.session_state.get("user_input", ""),
    height=250,
    key="user_input"
)


# 送信ボタン
if st.button("送信"):
    if user_input.strip():
        try:
            # APIにリクエストを送信
            if selected_template_name == "ADK":
                api_url = f"http://{AIAGENT_API_URI}:{AIAGENT_PORT}{AIAGENT_API_PATH_1_1}/adk"
            elif selected_template_name == "graph":
                api_url = f"http://{AIAGENT_API_URI}:{AIAGENT_PORT}{AIAGENT_API_PATH_1_1}/graph"
            else:
                api_url = f"http://{AIAGENT_API_URI}:{AIAGENT_PORT}{AIAGENT_API_PATH}"

            _user_input = PROMPT_TEMPLATES[selected_template_name] + user_input
            parameters = {
                "user_input": _user_input,
                "model_name": modelname,
                "max_iterations": max_iterations,
                "thought_process_Flg": thought_process_Flg
            }
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
