from fastapi import APIRouter, HTTPException
from aiagent.aiagent.StandardAiAgent import StandardAiAgent
from app.schemas.standardAiAgent import AtandardAiAgentRequest, AtandardAiAgentResponse


router = APIRouter()


@router.get("/",
            summary="Hello World",
            description="Hello Worldです。疎通確認に使用してください。")
def home_hello_world():
    return {"message": "Hello World"}


@router.post("/aiagent",
             summary="AIエージェントを実行します",
             description="AIエージェントを実行します")
def aiagent(request: AtandardAiAgentRequest):
    agent_executor = StandardAiAgent(
        model_name=request.model_name,
        max_iterations=request.max_iterations)
    result = agent_executor.invoke(request.user_input)
    _response = {"result": result}
    return AtandardAiAgentResponse(**_response)
