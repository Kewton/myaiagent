from mymcp.utils.execllm import execLlmApi
from core.config import settings


def extract_knowledge_from_text(_text: str, _model: str = settings.EXTRACT_KNOWLEDGE_MODEL):
    _query = f"""
    # 命令指示書
    入力情報と制約条件に従って最高の成果物を日本語で生成してください。

    # 制約条件
    - ナレッジを抽出すること
    - 日本語で返却すること

    # 入力情報
    {_text}
    """

    _messages = []
    _messages.append(
        {"role": "user", "content": _query}
    )

    result = execLlmApi(_messages, _model)

    print("============================")
    print("extract_knowledge_from_text:")
    print("============================")
    print(result)
    print("============================")
    print("============================")

    return result