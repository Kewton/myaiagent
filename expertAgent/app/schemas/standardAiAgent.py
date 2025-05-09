from pydantic import BaseModel
from typing import List, Literal


# チャットメッセージの形式を表すモデル
class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


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