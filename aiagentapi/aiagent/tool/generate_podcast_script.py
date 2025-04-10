from openai import OpenAI
from pydantic import BaseModel, Field # Pydanticをインポート
from aiagent.tool.tts_and_upload_drive import tts_and_upload_drive
from aiagent.utils.generate_subject_from_text import generate_subject_from_text
from langchain.tools import tool
import os
from aiagent.utils.execllm import execLlmApi


PODCAST_SCRIPT_DEFAULT_MODEL = os.getenv('PODCAST_SCRIPT_DEFAULT_MODEL', "gpt-4o-mini")

class PodcastScriptInput(BaseModel):
    """ポッドキャスト台本生成ツールの入力"""
    topic_details: str = Field(description="ポッドキャストのトピックや含めたいキーポイントに関する詳細な指示や情報。")
    model_name: str = Field(default=PODCAST_SCRIPT_DEFAULT_MODEL, description="台本生成に使用するOpenAIモデル名。") # ★ 要確認: デフォルトモデル名


class PodcastMp3Input(BaseModel):
    """ポッドキャストMP3生成・アップロードツールの入力"""
    topic_details: str = Field(description="ポッドキャストのトピックや含めたいキーポイントに関する詳細な指示や情報。")
    model_name: str = Field(default=PODCAST_SCRIPT_DEFAULT_MODEL, description="台本生成に使用するOpenAIモデル名。") # ★ 要確認: デフォルトモデル名
    subject_max_length: int = Field(default=25, description="生成する件名の最大文字数。")


# --- 改良されたLangChainツール ---

@tool(args_schema=PodcastScriptInput) # Pydanticモデルを入力スキーマとして指定
def generate_podcast_script_tool(topic_details: str, model_name: str = PODCAST_SCRIPT_DEFAULT_MODEL) -> str:
    """
    与えられたトピック詳細情報からポッドキャストの台本を生成します。

    Args:
        topic_details (str): ポッドキャストのトピック、キーポイント、構成案などの詳細情報。
        model_name (str): 台本生成に使用するOpenAIモデル名 (デフォルト: gpt-4o)。

    Returns:
        str: 生成されたポッドキャスト台本テキスト。
    """
    # 引数名を Pydantic モデルのフィールド名に合わせる
    # (toolデコレータが args_schema を使うと、Agentは辞書形式で渡すことが多い)
    # Agent が kwargs 形式で渡すことを想定し、直接引数で受け取るように修正
    print(f"Generating script with model: {model_name}") # デバッグ用
    script = generate_podcast_script(model_name=model_name, input_info=topic_details)
    return script

@tool(args_schema=PodcastMp3Input) # Pydanticモデルを入力スキーマとして指定
def generate_podcast_mp3_and_upload_tool(topic_details: str, model_name: str = PODCAST_SCRIPT_DEFAULT_MODEL, subject_max_length: int = 25) -> str:
    """
    与えられたトピック詳細情報からポッドキャスト台本を生成し、
    その内容から件名を生成、テキストをMP3音声に変換してGoogle Driveにアップロードします。

    Args:
        topic_details (str): ポッドキャストのトピック、キーポイント、構成案などの詳細情報。
        model_name (str): 台本生成に使用するOpenAIモデル名 (デフォルト: gpt-4o)。
        subject_max_length (int): 生成する件名の最大文字数 (デフォルト: 25)。

    Returns:
        str: Google Driveへのアップロード結果を示すメッセージまたはファイルURL。
    """
    print(f"Generating script for MP3 with model: {model_name}") # デバッグ用
    # 1. 台本生成
    script = generate_podcast_script(model_name=model_name, input_info=topic_details)

    if not script or not isinstance(script, str) or len(script.strip()) == 0:
        return "エラー: 台本の生成に失敗したか、内容が空です。"

    print(f"Script generated, length: {len(script)}") # デバッグ用

    # 2. 件名生成
    subject = generate_subject_from_text(script, subject_max_length)
    print(f"Subject generated: {subject}") # デバッグ用

    # 3. 音声化とアップロード
    try:
        upload_result = tts_and_upload_drive(subject, script)
        print(f"TTS and upload result: {upload_result}") # デバッグ用
        return upload_result
    except Exception as e:
        print(f"Error during TTS/Upload: {e}") # エラーログ
        return f"エラー: 音声化またはアップロード中に問題が発生しました - {e}"


def generate_podcast_script(input_info: str, model_name: str = "gpt-4o-mini"): # model_name を引数に追加
    """指定された情報とモデル名からポッドキャスト台本を生成する"""
    client = OpenAI()

    _input = f"""
    あなたは、複数の情報源からのデータを統合してポッドキャスト台本を作成するツールです。
    以下の入力情報と指示に基づいて、指定されたトピックに関する一貫性のある台本テキストのみを出力してください。
    なお、AIにより音声化することを想定した改行としてください。

    # 1. 入力情報ソース
    {input_info}

    # 2. ポッドキャストパラメータ
    * **tone:** 深掘り討論

    # 3. 出力指示
    **台本構成:** 抽出・統合した情報に基づき、導入（トピックと情報源の概要説明）、本編（キーポイントの議論・展開）、結論（まとめ、考察）を含む一貫性のある台本を作成します。
    
    # 生成開始
    """

    _messages = [
        {"role": "system", "content": "あなたは世界一のポッドキャスターです"},
        {"role": "user", "content": _input}
    ]

    return execLlmApi(model_name, _messages)

    #response = client.chat.completions.create(
    #    model=model_name,
    #    messages=_messages
    #)
    #return response.choices[0].message.content