from dotenv import load_dotenv
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_react_agent
from tool.google_search_by_gemini import google_search_tool
import gradio as gr

# 環境変数のロード
load_dotenv()

# HubからReact用プロンプトを取得
prompt = hub.pull("hwchase17/react")

# LLMの初期化（例: gpt-4o-mini）
model = ChatOpenAI(model="gpt-4o-mini")

# ツールリストに google_search_tool を含める
tools = [google_search_tool]

# 1. エージェントの作成
agent = create_react_agent(model, tools, prompt)

# 2. AgentExecutor の実行準備（verbose=Trueで詳細ログ出力）
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True  # 追加
)

# Gradioのチャット関数（内部で agent_executor.invoke() を利用）
def chat(user_input, chat_history):
    # ユーザーの入力をチャット履歴に追加（OpenAIスタイルのdict形式）
    chat_history = chat_history or []
    chat_history.append({"role": "user", "content": user_input})
    
    # agent_executor.invoke() により、内部ロジックでエージェントを実行
    result = agent_executor.invoke({"input": user_input})
    # 結果は辞書形式で返るので、"output"キーがあればそこから取得
    response = result.get("output", result)
    
    # エージェントの返答を履歴に追加
    chat_history.append({"role": "assistant", "content": response})
    
    # ユーザー入力をクリアし、更新されたチャット履歴を返す
    return "", chat_history, chat_history

# Gradio UIの構築（チャットUIはそのまま利用）
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="Assistant", height=800, type="messages")
    state = gr.State([])
    with gr.Row():
        user_input = gr.Textbox(lines=1, label="Chat Message")
        submit = gr.Button("Submit")
    submit.click(
        chat,
        inputs=[user_input, state],
        outputs=[user_input, chatbot, state]
    )

demo.launch()
