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
    try:
        agent_executor = StandardAiAgent(
            model_name=request.model_name,
            max_iterations=request.max_iterations)
        result = agent_executor.invoke(request.user_input)
        _response = {"result": result}
        return AtandardAiAgentResponse(**_response)

    # StandardAiAgent.invoke が投げる可能性のあるカスタム例外をキャッチ
    # except AgentExecutionError as e: # 例：カスタム例外
    #     raise HTTPException(status_code=500, detail=f"AI Agent execution failed: {e}")
    except Exception as e:
        # 予期せぬエラー全般をキャッチ
        # 本番環境では、より詳細なログ記録やエラー報告を行うべき
        print(f"An unexpected error occurred: {e}") # ログ出力
        raise HTTPException(status_code=500, detail="An internal server error occurred in the agent.")