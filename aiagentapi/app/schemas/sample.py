from pydantic import BaseModel


class CommonResponse(BaseModel):
    receptid: str


class StatusResponse(CommonResponse):
    """
    レスポンス用
    """
    mystatus: str


class CommonReq(BaseModel):
    user: str


class StatusReq(CommonReq):
    mystatus: str
