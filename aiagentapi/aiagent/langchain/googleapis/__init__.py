from langchain.tools import tool
from typing import Dict
from aiagent.langchain.googleapis.gmail.readonly import get_emails_by_keyword
from aiagent.langchain.googleapis.gmail.send import send_email
import os
from typing import Type, Optional, Union, Dict, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ValidationError
from aiagent.langchain.utils.generate_subject_from_text import generate_subject_from_text


@tool
def gmail_search_search_tool(keywrod: str, top: int = 5) -> Dict:
    """gmailからキーワード検索した結果をtopに指定した件数文返却します。"""
    return get_emails_by_keyword(keywrod, top)


@tool
def send_email_tool(body: str) -> str:
    """gmailサービスを利用してメール送信する

    入力したメールの本文から件名を自動生成し事前に設定した宛先にメールを送信し、
    結果を示すメッセージを返します。

    Args:
        body: メールの本文。

    Returns:
        str: 成功時は成功メッセージ、失敗時はエラーメッセージ。
    """
    subject = generate_subject_from_text(body)
    return send_email(os.getenv("MAIL_TO"), subject, body)


class SendEmailInput(BaseModel):
    """send_email_to_fixed_address ツールの入力スキーマ"""
    body: str = Field(description="必須。送信するメールの本文。")


class SendEmailTool(BaseTool):
    """固定アドレスへのメール送信ツール"""
    name: str = "send_email_to_fixed_address" # 名前をより具体的に変更
    description: str = (
        "入力内容を本文として設定し事前に設定された特定のメールアドレスにメールを送信します。"
        "なお、入力内容をもとに件名を自動で設定するので、件名の指定は不要です。"
        "このフォーマットに従うオブジェクトの形で入力してください。"
        f"{SendEmailInput.model_json_schema()}"
        "処理の成功または失敗を示すメッセージを返します。"
    )
    args_schema: Type[BaseModel] = SendEmailInput

    def _run(
        self,
        tool_input: Union[str, Dict[str, Any]], # 位置引数としてツール入力を受け取る
        **kwargs: Any # 他の引数渡しにも対応できるようkwargsも残す
    ) -> str:
        """ツールの同期実行ロジック"""
        print(f"[{self.name}] INFO: Received tool_input type: {type(tool_input)}")
        print(f"[{self.name}] INFO: Received tool_input: {tool_input}")

        input_dict: Dict[str, Any]

        print(tool_input)
        # tool_input の型を確認し、辞書形式に統一する
        if isinstance(tool_input, str):
            # 文字列で渡された場合、必須の 'body' として扱う (スキーマとは異なる可能性があるため注意)
            input_dict = {"body": tool_input}
            print(f"[{self.name}] WARNING: Received string input, assuming it's 'body'. Optional 'subject' might be missing.")
        elif isinstance(tool_input, dict):
            input_dict = tool_input
        else:
            # 予期しない型の場合はエラーメッセージを返す
            return f"エラー: ツール入力の型が不正です ({type(tool_input)})。辞書または文字列が必要です。"

        # --- Pydanticモデルで検証 ---
        try:
            # input_dict を使って Pydantic モデルを検証・初期化
            # これにより、必須フィールドの存在確認、型チェック、デフォルト値の適用が行われる
            parsed_input = SendEmailInput(**input_dict)
            print(parsed_input)
            body = parsed_input.body
            subject = generate_subject_from_text(body)

            print(f"[{self.name}] INFO: Parsed arguments: subject='{subject}', body='{body[:50]}...'")
        except ValidationError as e:
            # 検証エラーの場合、AIに分かりやすいエラーメッセージを返す
            return f"エラー: メール送信ツールへの入力形式が無効です。詳細: {e}. 受け取った入力: {input_dict}"
        except Exception as e:
            # その他のエラー
            return f"エラー: ツール入力の処理中に予期せぬエラーが発生しました: {e}. 受け取った入力: {input_dict}"

        """ツールの同期実行ロジック"""
        # 環境変数から送信先を取得
        to_email = os.getenv("MAIL_TO")
        if not to_email:
            return "エラー: 送信先メールアドレスが環境変数 'MAIL_TO' に設定されていません。"

        # subjectがNoneの場合のデフォルト値適用 (Pydanticが適用するはずだが念のため)
        if subject is None:
            subject = "AIエージェントからの手紙"

        print(f"[{self.name}] INFO: Attempting to send email via internal function...")
        # 改善された send_email 関数を呼び出し、結果メッセージを受け取る
        result_message = send_email(to_email, subject, body)
        print(f"[{self.name}] INFO: send_email function returned: {result_message}")
        return result_message  # 結果メッセージをそのまま返す