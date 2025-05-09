from pydantic import BaseModel
from typing import List, Dict, Any # List, Dict, Any をインポート


# チャットメッセージの形式を表すモデル
class ChatMessage(BaseModel):
    role: str
    content: str
    # 必要であれば他のフィールド (例: name: Optional[str] = None)


class StandardAiAgentResponse(BaseModel):
    # result フィールドを ChatMessage モデルのリストとして定義
    result: List[ChatMessage]


class ExpertAiAgentRequest(BaseModel):
    user_input: str
    model_name: str | None = None


class ExpertAiAgentResponse(BaseModel):
    # result フィールドを ChatMessage モデルのリストとして定義
    result: str
    type: str | None = None
    chathistory: List[ChatMessage] | None = None


class ExpertAiAgentResponseJson(BaseModel):
    # result フィールドを ChatMessage モデルのリストとして定義
    result: dict
    type: str | None = None
    chathistory: List[ChatMessage] | None = None