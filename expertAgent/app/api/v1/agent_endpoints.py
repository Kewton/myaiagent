from fastapi import APIRouter, HTTPException
from aiagent.langgraph.sampleagent.graphagent import ainvoke_graphagent
from app.schemas.standardAiAgent import AtandardAiAgentRequest, AtandardAiAgentResponse
from datetime import datetime

router = APIRouter()


@router.get("/",
            summary="Hello World",
            description="Hello Worldです。疎通確認に使用してください。")
def home_hello_world():
    return {"message": "Hello World"}


# @router.post("/aiagent/graph",
#              summary="LangGraphのAIエージェントを実行します",
#              description="LangGraphのAIエージェントを実行します")
# async def aiagent_graph(request: AtandardAiAgentRequest):
#     try:
#         print("request.user_input")
#         _input = f"""
#         # メタ情報:
#         - 現在の時刻は「{datetime.now()}」です。

#         # 指示書
#         {request.user_input}
#         """
#         result = await ainvoke_graphagent(_input)
#         _response = {"result": result}
#         return AtandardAiAgentResponse(**_response)
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         raise HTTPException(status_code=500, detail="An internal server error occurred in the agent.")

