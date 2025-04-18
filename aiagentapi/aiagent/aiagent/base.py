import uuid
from abc import ABC, abstractmethod
from langchain.agents import AgentExecutor


class AiAgentBase(ABC):
    def __init__(self):
        self.exeid = uuid.uuid4()
        self.myaiagent = self.createAgentExecutor()
        self.chat_history = []
        return

    @abstractmethod
    def createAgentExecutor(self) -> AgentExecutor:
        """サブクラスで AgentExecutor を生成して返す"""
        pass

    def invoke(self, user_input, thoughtProcessFlg=True):
        """エージェントを実行し、最終的な出力を返す"""
        if not self.myaiagent:
            raise RuntimeError("AgentExecutor has not been initialized.")
        try:
            # AgentExecutorのinvokeメソッドは辞書を返すことが多い
            self.chat_history.append({"role": "user", "content": user_input})
            result = self.myaiagent.invoke({"input": user_input})
            # final_answer = result.get("output", result)
            final_answer = result.get("output", str(result) if isinstance(result, dict) else result)
            intermediate_steps = result.get("intermediate_steps", [])
            
            print("--------------------------")
            print("--- Intermediate Steps ---")
            print("--------------------------")
            for action, observation in intermediate_steps:
                # action は AgentAction オブジェクト
                print(f"Action Tool: {action.tool}")
                print(f"Action Input: {action.tool_input}")
                # action.log には Action に至る思考プロセスが含まれることが多い
                #print(f"Action Log: \n{action.log}")
                #print(f"Observation: {observation}\n") # ツールの実行結果
            print("--------------------------") 
            print("--------------------------")

            # 中間ステップを整形
            formatted_steps = self.format_intermediate_steps(intermediate_steps)
            
            # 最終回答と中間出力（思考プロセス）を結合
            if thoughtProcessFlg:
                full_output = f"Final Answer:\n{final_answer}\n\n---\nThought Process:\n{formatted_steps}"
            else:
                full_output = final_answer
            self.chat_history.append({"role": "assistant", "content": full_output})
            return self.chat_history
        except Exception as e:
            print(f"Error during agent invocation (ID: {self.exeid}): {e}")
            # エラー時の挙動を決める (エラーメッセージを返す、例外を再raiseするなど)
            return f"An error occurred during execution: {e}"

    def format_intermediate_steps(self, intermediate_steps):
        log = ""
        for step_index, (action, tool_result) in enumerate(intermediate_steps):  # enumerate を使うとデバッグしやすい
            log += f"\n--- Step {step_index + 1} ---"
            log += f"\nAction: {action.log.strip()}"  # actionも整形する場合

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
                observation_str = str(tool_result)  # とりあえず文字列化

            log += f"\nObservation: {observation_str}"

        return log.strip()  # 最終的なログの前後空白を削除