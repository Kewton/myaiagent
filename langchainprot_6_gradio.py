import gradio as gr
from aiagent.agent_type1 import creatAgentType1

agent_executor = creatAgentType1()


def format_intermediate_steps(intermediate_steps):
    log = ""
    for step_index, (action, tool_result) in enumerate(intermediate_steps): # enumerate を使うとデバッグしやすい
        log += f"\n--- Step {step_index + 1} ---"
        log += f"\nAction: {action.log.strip()}" # actionも整形する場合

        # tool_result の型を確認して処理を分岐
        observation_str = ""
        if isinstance(tool_result, str):
            # tool_resultが文字列の場合
            observation_str = tool_result.strip()
        elif isinstance(tool_result, dict):
            # tool_resultが辞書の場合 (想定していた元の処理に近い)
            # getのデフォルト値は空文字列ではなくNoneの方が区別しやすいかも
            result_value = tool_result.get("result")
            if isinstance(result_value, str):
                 observation_str = result_value.strip()
            elif result_value is not None:
                 # resultキーの値が文字列でない場合の処理 (例: オブジェクトを文字列化)
                 observation_str = str(result_value)
            else:
                 # resultキーが存在しない場合の処理 (辞書全体を文字列化など)
                 observation_str = str(tool_result) # もしくは "" や エラーメッセージ
        elif isinstance(tool_result, list):
            # ★★★ tool_resultがリストの場合の処理 ★★★
            # リストの各要素を文字列にして結合する例
            observation_str = ", ".join(str(item) for item in tool_result)
            # もしくは他の適切な表現方法で文字列化する
            # observation_str = f"List results: {tool_result}"
        else:
            # その他の型の場合 (None など)
            observation_str = str(tool_result) # とりあえず文字列化

        log += f"\nObservation: {observation_str}"

    return log.strip() # 最終的なログの前後空白を削除


# Gradio のチャット関数（中間出力も整形してUIに反映）
def chat(user_input, chat_history):
    chat_history = chat_history or []
    # ユーザーの入力を履歴に追加（OpenAI形式の dict）
    chat_history.append({"role": "user", "content": user_input})
    
    # agent_executor を実行して、最終出力と中間ステップを取得
    result = agent_executor.invoke({"input": user_input})
    final_answer = result.get("output", result)
    intermediate_steps = result.get("intermediate_steps", [])
    
    # 中間ステップを整形
    formatted_steps = format_intermediate_steps(intermediate_steps)
    
    # 最終回答と中間出力（思考プロセス）を結合
    full_output = f"Final Answer:\n{final_answer}\n\n---\nThought Process:\n{formatted_steps}"
    chat_history.append({"role": "assistant", "content": full_output})
    
    # ユーザー入力をクリアして、更新されたチャット履歴を返す
    return "", chat_history, chat_history

# Gradio UI の構築（UIはそのままで内部ロジックのみ変更）
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
