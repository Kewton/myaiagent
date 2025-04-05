import gradio as gr
from aiagent.agent_type1 import creatAgentType1

agent_executor = creatAgentType1()


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
