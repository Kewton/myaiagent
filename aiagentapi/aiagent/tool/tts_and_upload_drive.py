from aiagent.googleapis.drive import get_file_id_and_mime_type, resumable_upload, get_google_drive_file_links
from aiagent.tts.tts import tts
from aiagent.utils.file_operation import delete_file
import uuid
from langchain.tools import tool
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ValidationError
from typing import Type, Optional, Union, Dict, Any
from pathlib import Path
from aiagent.utils.generate_subject_from_text import generate_subject_from_text


class TTSUploadInput(BaseModel):
    """tts_and_upload_to_google_drive ツールの入力スキーマ"""
    input_message: str = Field(
        description="必須。音声ファイルに変換したいテキストメッセージ。"
    )

    target_folder_name: Optional[str] = Field(
        default="MyAiAgent", # デフォルト値を設定
        description="任意。Google Drive内のアップロード先フォルダ名。省略時は'MyAiAgent'になります。"
                "この名前のフォルダが存在する必要があります。"
    )


class TextToSpeechAndUploadTool(BaseTool):
    """
    テキストを音声(MP3)に変換し、Google Driveにアップロードして共有可能なリンクを返すツール。
    """
    name: str = "tts_and_upload_to_google_drive"
    description: str = (
        # AIへの指示を具体的に記述
        "ユーザーから指定されたテキストメッセージを音声ファイル（MP3形式）に変換する必要がある場合に使用します。"
        "生成された音声ファイルは、Google Driveの指定されたフォルダ（デフォルトは'MyAiAgent'）にアップロードされます。"
        "このツールは、テキストの内容を音声で共有したい、または音声ファイルをDriveに保存したい場合に特に役立ちます。"
        "実行には、事前のGoogle Drive APIへの認証と、対象フォルダへの書き込み権限が必要です。"
        "このフォーマットに従うオブジェクトの形で入力してください。"
        f"{TTSUploadInput.model_json_schema()}"
        "入力として、音声化するテキストメッセージ（input_message）は必須です。"
        "任意で、アップロード先のフォルダ名（target_folder_name）を指定できます。"
        "処理が成功すると、アップロードされた音声ファイルへのGoogle Driveウェブ表示用リンク（webViewLink）を含む成功メッセージを返します。"
        "処理中にエラーが発生した場合は、具体的なエラー内容を含むメッセージを返します。"
    )
    # 定義したPydanticモデルを入力スキーマとして指定
    args_schema: Type[BaseModel] = TTSUploadInput

    # --- 同期実行メソッド ---
    def _run(
        self,
        tool_input: Union[str, Dict[str, Any]], # 位置引数としてツール入力を受け取る
        **kwargs: Any # 将来のため、または他の引数渡しに対応するためkwargsも残す
    ) -> str:
        """ツールの本体ロジック（同期）"""
        print(f"[{self.name}] INFO: Received tool_input type: {type(tool_input)}")
        print(f"[{self.name}] INFO: Received tool_input: {tool_input}")
        # print(f"[{self.name}] INFO: Received kwargs: {kwargs}") # 必要ならkwargsも確認

        input_dict: Dict[str, Any]

        # tool_input の型を確認し、辞書形式に統一する
        if isinstance(tool_input, str):
            # もし文字列で渡された場合、それが 'input_message' であると仮定するか、
            # あるいは JSON 文字列としてパースを試みる。
            # args_schema を指定している場合、通常は辞書が期待される。
            # ここではエラーとするか、特定のキーに割り当てるか設計による。
            # 例: エラーとする場合
            # return f"エラー: ツール入力は辞書形式である必要がありますが、文字列を受け取りました: '{tool_input}'"
            # 例: input_message として扱う場合 (スキーマ違反の可能性あり)
            input_dict = {"input_message": tool_input}
            print(f"[{self.name}] WARNING: Received string input, assuming it's 'input_message'. This might be incomplete.")
        elif isinstance(tool_input, dict):
            input_dict = tool_input
        else:
            # 予期しない型の場合
            return f"エラー: ツール入力の型が不正です ({type(tool_input)})。辞書または文字列が必要です。"

        # --- Pydanticモデルで検証 ---
        try:
            parsed_input = TTSUploadInput(**input_dict)
            input_message = parsed_input.input_message
            file_name = generate_subject_from_text(input_message)
            target_folder_name = parsed_input.target_folder_name
            print(f"[{self.name}] INFO: Parsed arguments: input_message='{input_message[:30]}...', file_name='{file_name}', target_folder_name='{target_folder_name}'")
        except ValidationError as e:
            return f"エラー: ツールへの入力形式が無効です。詳細: {e}. 受け取った入力: {input_dict}"
        except Exception as e:
            return f"エラー: ツール入力の処理中に予期せぬエラーが発生しました: {e}. 受け取った入力: {input_dict}"

        """ツールの本体ロジック（同期）"""
        temp_dir = Path("./temp")
        speech_file_path: Optional[Path] = None # finally スコープで参照するため

        # 引数のデフォルト値がNoneの場合の処理 (Pydanticがデフォルト値を適用するはずだが念のため)
        if file_name is None:
            file_name = "AIエージェントからの手紙"
        if target_folder_name is None:
            target_folder_name = "MyAiAgent"

        try:
            # 0. 一時ディレクトリの確認/作成
            try:
                temp_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                return f"エラー: 一時ディレクトリ '{temp_dir}' の作成に失敗しました: {e}"

            # 一時ファイルパスの生成
            unique_filename = f"{uuid.uuid4()}.mp3"
            speech_file_path = temp_dir / unique_filename

            # 1. テキスト -> 音声ファイル (TTS)
            print(f"[{self.name}] INFO: Generating speech file at '{speech_file_path}'...")
            try:
                # tts関数がファイルパス(文字列)とテキストを引数に取ることを想定
                tts(str(speech_file_path), input_message)
                # 生成されたファイルが存在し、空でないかを確認
                if not speech_file_path.is_file() or speech_file_path.stat().st_size == 0:
                    # TTS失敗時のエラーメッセージ
                    return f"エラー: TTS処理に失敗しました。音声ファイルが生成されませんでした。Text: '{input_message[:50]}...'"
            except Exception as e:
                # TTS実行中の予期せぬエラー
                return f"エラー: 音声ファイル生成中に予期せぬエラーが発生しました: {e}"
            print(f"[{self.name}] INFO: Speech file generated successfully.")

            # 2. Google Drive アップロード先フォルダIDの取得
            print(f"[{self.name}] INFO: Searching for Google Drive folder '{target_folder_name}'...")
            folder_id: Optional[str] = None
            try:
                # 注意: get_file_id_and_mime_typeは同名フォルダ/ファイルが複数ある場合、
                # 意図しないものを返す可能性があります。より堅牢にするには、
                # mimeType='application/vnd.google-apps.folder' を条件に加えるなどの改善を検討。
                _name, folder_id, mimeType = get_file_id_and_mime_type(target_folder_name)

                if not folder_id:
                    return f"エラー: Google Drive でフォルダ '{target_folder_name}' が見つかりません。"
                if mimeType != 'application/vnd.google-apps.folder':
                    return f"エラー: Google Drive で見つかった '{target_folder_name}' はフォルダではありません (Type: {mimeType})。"
            except Exception as e:
                # フォルダ検索中のエラー
                return f"エラー: Google Drive フォルダ '{target_folder_name}' の検索中にエラーが発生しました: {e}"
            print(f"[{self.name}] INFO: Found folder ID: {folder_id}")

            # 3. Google Drive へのファイルアップロード
            drive_filename = f"{file_name}.mp3"
            print(f"[{self.name}] INFO: Uploading '{speech_file_path.name}' as '{drive_filename}' to folder '{folder_id}'...")
            uploaded_file_id: Optional[str] = None
            try:
                # resumable_upload がアップロード成功時にファイルIDを返すことを想定
                uploaded_file_id = resumable_upload(
                    save_file_name_in_drive=drive_filename,
                    upload_file_path=str(speech_file_path),
                    mime_type="audio/mpeg", # MP3の正しいMIMEタイプ
                    folder_id=folder_id
                )
                if not uploaded_file_id:
                    return f"エラー: Google Drive へのファイル '{drive_filename}' のアップロードに失敗しました（ファイルIDが返されませんでした）。"
            except Exception as e:
                # アップロード中のエラー
                return f"エラー: Google Drive へのアップロード中にエラーが発生しました: {e}"
            print(f"[{self.name}] INFO: File uploaded successfully. File ID: {uploaded_file_id}")

            # 4. アップロードされたファイルのリンク取得
            print(f"[{self.name}] INFO: Getting links for file ID '{uploaded_file_id}'...")
            try:
                link_info = get_google_drive_file_links(uploaded_file_id)
                if not link_info or not link_info.get('webViewLink'):
                    # リンク取得失敗、または webViewLink が見つからない場合
                    return f"エラー: アップロードされたファイル (ID: {uploaded_file_id}) のリンクを取得できませんでした。"

                web_view_link = link_info['webViewLink']
                print(f"[{self.name}] INFO: Successfully retrieved webViewLink: {web_view_link}")
                # 成功時の返り値 (AI に分かりやすいメッセージ形式)
                return f"音声ファイル「{drive_filename}」を Google Drive のフォルダ「{target_folder_name}」にアップロードしました。表示用リンク: {web_view_link}"

            except Exception as e:
                # リンク取得中のエラー
                return f"エラー: アップロードされたファイルのリンク取得中にエラーが発生しました (File ID: {uploaded_file_id}): {e}"

        finally:
            # 5. 一時ファイルの削除 (tryブロックの成功・失敗に関わらず実行)
            if speech_file_path and speech_file_path.exists():
                print(f"[{self.name}] INFO: Deleting temporary file '{speech_file_path}'...")
                try:
                    # delete_file 関数がファイルパス文字列を期待する場合
                    delete_file(str(speech_file_path))
                    print(f"[{self.name}] INFO: Temporary file deleted.")
                except Exception as e:
                    # 一時ファイルの削除失敗は警告に留める (主要処理ではないため)
                    print(f"[{self.name}] WARNING: Failed to delete temporary file '{speech_file_path}': {e}")


def tts_and_upload_drive(file_name, input_message):
    speech_file_path = f"./temp/{uuid.uuid4()}.mp3"

    tts(speech_file_path, input_message)

    name, id, mimeType = get_file_id_and_mime_type("MyAiAgent")

    upfileid = resumable_upload(f"{file_name}.mp3", speech_file_path, "audio/mpeg", id)

    result = get_google_drive_file_links(upfileid)

    delete_file(speech_file_path)

    return result["webViewLink"]
