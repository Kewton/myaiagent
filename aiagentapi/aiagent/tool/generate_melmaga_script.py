from langchain.tools import tool
import os
from aiagent.utils.execllm import execLlmApi


PODCAST_SCRIPT_DEFAULT_MODEL = os.getenv('PODCAST_SCRIPT_DEFAULT_MODEL', "gpt-4o-mini")


@tool
def generate_melmaga_script_tool(input_info: str):
    """指定された情報とモデル名からメルマガを生成する

    指定された情報を元にLLMを活用してメルマガを生成します
    インプット情報が詳細で具体的であればあるほど良いです。
    集めた情報をそのまま入力してください。

    Args:
        input_info (str): メルマガを生成するためのインプット情報。詳細で具体的であればあるほど良いです。

    Returns:
        str: 生成したメルマガ

    """
    return generate_melmaga_script(input_info, PODCAST_SCRIPT_DEFAULT_MODEL)


def generate_melmaga_script(input_info: str, model_name: str = "gpt-4o-mini"):
    """指定された情報とモデル名からメルマガを生成する"""
    _input = f"""
    あなたは優れた編集者兼ライターです。
    以下の情報を踏まえ、30～40代のビジネスパーソンがスキマ時間で読めるメルマガを作成してください。
    1テーマ600～800文字程度で、要点を押さえながらも興味を持続させる構成を意識してください。
    見出しや箇条書きを活用し、専門的な内容でも理解しやすいように平易な言葉に言い換える工夫を加えてください。
    最終的には、読者にビジネス活用のための具体的な一歩を促すCTAを用意し、行動につなげてください。
    以下がインプットとなる情報の概要です：
    ---
    {input_info}
    ---
    出力形式は、件名、導入、本文（見出しあり）、まとめ・CTA、フッター情報（任意）の順にしてください。
    文章全体のトーンはビジネス視点を中心に、親しみやすさと専門性のバランスを考慮してください。
    """

    _messages = [
        {"role": "system", "content": "あなたは優れた編集者兼ライターです"},
        {"role": "user", "content": _input}
    ]

    return execLlmApi(model_name, _messages)
