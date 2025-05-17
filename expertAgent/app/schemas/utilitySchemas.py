from pydantic import BaseModel
from typing import List, Literal


class UtilityRequest(BaseModel):
    user_input: str


class UtilityResponse(BaseModel):
    # result フィールドを ChatMessage モデルのリストとして定義
    result: str