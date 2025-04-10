from openai import OpenAI
from langchain.tools import tool
import os
from aiagent.utils.execllm import execLlmApi


PODCAST_SCRIPT_DEFAULT_MODEL = os.getenv('PODCAST_SCRIPT_DEFAULT_MODEL', "gpt-4o-mini")


@tool
def generate_melmaga_script_tool(input_info: str):  # model_name を引数に追加
    """指定された情報とモデル名からメルマガを生成する"""
    return generate_melmaga_script(input_info, PODCAST_SCRIPT_DEFAULT_MODEL)


def generate_melmaga_script(input_info: str, model_name: str = "gpt-4o-mini"):  # model_name を引数に追加
    """指定された情報とモデル名からメルマガを生成する"""
    client = OpenAI()

    _input = f"""
    あなたは、複数の情報源からのデータを統合してメルマガを作成するツールです。
    以下の入力情報と指示に基づいて、指定されたトピックに関する一貫性のある台本テキストのみを出力してください。

    # 1. 入力情報ソース
    {input_info}

    # 2. メルマガパラメータ
    * **tone:** 深掘り討論
    * **length** 特に指定がない場合は1000~2000文字程度としてください。

    # 3. 出力指示
    **台本構成:** 抽出・統合した情報に基づき、導入（トピックと情報源の概要説明）、本編（キーポイントの議論・展開）、結論（まとめ、考察）を含む一貫性のある台本を作成します。
    
    # 生成開始
    """

    _messages = [
        {"role": "system", "content": "あなたは売れっ子メルマガです"},
        {"role": "user", "content": _input}
    ]

    return execLlmApi(model_name, _messages)
#    response = client.chat.completions.create(
#        model=model_name,
#        messages=_messages
#    )
#    return response.choices[0].message.content