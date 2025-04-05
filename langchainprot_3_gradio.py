from dotenv import load_dotenv
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.agents import AgentExecutor, create_react_agent
from tool.google_search_by_gemini import google_search_tool
import gradio as gr
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai.output_parsers.tools import PydanticToolsParser
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from gradio import ChatMessage
from langchain_core.messages import AIMessage, HumanMessage
from tool.google_search_by_gemini import google_search_tool


load_dotenv()


llm = ChatOpenAI(model="gpt-4o-mini")


# ツール入力形式の定義
class ActionItem(BaseModel):
    action_name: str = Field(description="アクション名")
    action_description: str = Field(description="アクションの詳細")


class Plan(BaseModel):
    """アクションプランを格納する"""

    problem: str = Field(description="問題の説明")
    actions: list[ActionItem] = Field(description="実行すべきアクションリスト")


class ActionResult(BaseModel):
    """実行時の考えと結果を格納する"""

    thoughts: str = Field(description="検討内容")
    result: str = Field(description="結果")


ACTION_PROMPT = """\
問題をアクションプランに分解して解いています。
これまでのアクションの結果と、次に行うべきアクションを示すので、実際にアクションを実行してその結果を報告してください。
# 問題
{problem}
# アクションプラン
{action_items}
# これまでのアクションの結果
{action_results}
# 次のアクション
{next_action}
"""

llm_action = llm.bind_tools([ActionResult], tool_choice="ActionResult")
action_parser = PydanticToolsParser(tools=[ActionResult], first_tool_only=True)
plan_parser = PydanticToolsParser(tools=[Plan], first_tool_only=True)

action_prompt = PromptTemplate.from_template(ACTION_PROMPT)
action_runnable = action_prompt | llm_action | action_parser


# プランに含まれるアクションを実行するループ
def action_loop(action_plan: Plan):
    problem = action_plan.problem
    actions = action_plan.actions

    action_items = "\n".join(["* " + action.action_name for action in actions])
    action_results = []
    action_results_str = ""
    for _, action in enumerate(actions):
        next_action = f"* {action.action_name}  \n{action.action_description}"
        response = action_runnable.invoke(
            dict(
                problem=problem,
                action_items=action_items,
                action_results=action_results_str,
                next_action=next_action,
            )
        )
        action_results.append(response)
        action_results_str += f"* {action.action_name}  \n{response.result}\n"
        yield (
            response.thoughts,
            response.result,
        )  # 変更ポイント: 途中結果を yield で返す


PLAN_AND_SOLVE_PROMPT = """\
ユーザの質問が複雑な場合は、アクションプランを作成し、その後に1つずつ実行する Plan-and-Solve 形式をとります。
これが必要と判断した場合は、Plan ツールによってアクションプランを保存してください。
"""
system_prompt = SystemMessage(PLAN_AND_SOLVE_PROMPT)
chat_prompt = ChatPromptTemplate.from_messages(
    [system_prompt, MessagesPlaceholder(variable_name="history")]
)

llm_plan = llm.bind_tools(tools=[Plan])
planning_runnable = chat_prompt | llm_plan  # route を削除


def chat(prompt, messages, history):
    # 描画用の履歴をアップデート
    messages.append(ChatMessage(role="user", content=prompt))
    # LangChain 用の履歴をアップデート
    history.append(HumanMessage(content=prompt))
    # プランまたは返答を作成
    response = planning_runnable.invoke(dict(history=history))
    if response.response_metadata["finish_reason"] != "tool_calls":
        # タスクが簡単な場合はプランを作らずに返す
        messages.append(ChatMessage(role="assistant", content=response.content))
        history.append(AIMessage(content=response.content))
        yield "", messages, history
    else:
        # アクションプランを抽出
        action_plan = plan_parser.invoke(response)

        # アクション名を表示
        action_items = "\n".join(
            ["* " + action.action_name for action in action_plan.actions]
        )
        messages.append(
            ChatMessage(
                role="assistant",
                content=action_items,
                metadata={"title": "実行されるアクション"},
            )
        )
        # プランの段階で一度描画する
        yield "", messages, history

        # アクションプランを実行
        action_results_str = ""
        for i, (thoughts, result) in enumerate(action_loop(action_plan)):
            action_name = action_plan.actions[i].action_name
            action_results_str += f"* {action_name}  \n{result}\n"
            text = f"## {action_name}\n### 思考過程\n{thoughts}\n### 結果\n{result}"
            messages.append(ChatMessage(role="assistant", content=text))
            # 実行結果を描画する
            yield "", messages, history

        history.append(AIMessage(content=action_results_str))
        # LangChain 用の履歴を更新する
        yield "", messages, history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="Assistant", type="messages", height=800)
    history = gr.State([])
    with gr.Row():
        with gr.Column(scale=9):
            user_input = gr.Textbox(lines=1, label="Chat Message")
        with gr.Column(scale=1):
            submit = gr.Button("Submit")
            clear = gr.ClearButton([user_input, chatbot, history])
    submit.click(
        chat,
        inputs=[user_input, chatbot, history],
        outputs=[user_input, chatbot, history],
    )
demo.launch(height=1000)