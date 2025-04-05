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

# 2. AgentExecutor の実行準備
# ※ handle_parsing_errors と return_intermediate_steps を True に設定
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=True
)

# Gradio のチャット関数（中間出力もUIに反映）
def chat(user_input, chat_history):
    # ユーザー入力をチャット履歴に追加（OpenAI形式のdict）
    chat_history = chat_history or []
    chat_history.append({"role": "user", "content": user_input})
    
    # AgentExecutorを実行し、最終出力と中間ステップを取得
    result = agent_executor.invoke({"input": user_input})
    final_answer = result.get("output", result)
    intermediate_steps = result.get("intermediate_steps", [])
    
    # 中間ステップを文字列に整形
    # ※ intermediate_steps の構造はバージョンやエージェントによって異なる場合があるので、ここでは単純に str() で結合しています。
    intermediate_steps_str = "\n\n".join(str(step) for step in intermediate_steps)
    
    # 最終回答と中間出力（思考プロセス）を結合して表示
    full_output = f"{final_answer}\n\n---\nThought Process:\n{intermediate_steps_str}"
    chat_history.append({"role": "assistant", "content": full_output})
    
    # ユーザー入力をクリアし、更新されたチャット履歴を返す
    return "", chat_history, chat_history

# Gradio UI の構築（チャットUIはそのまま利用）
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
