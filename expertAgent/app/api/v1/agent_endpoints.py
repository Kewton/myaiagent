from fastapi import APIRouter, HTTPException
from aiagent.langgraph.sampleagent.graphagent import ainvoke_graphagent
from aiagent.langgraph.utilityaiagents.jsonOutput_agent import jsonOutputagent
from aiagent.langgraph.utilityaiagents.explorer_agent import exploreragent
from app.schemas.standardAiAgent import ExpertAiAgentRequest, ExpertAiAgentResponse, ExpertAiAgentResponseJson
from datetime import datetime

router = APIRouter()


@router.get("/",
            summary="Hello World",
            description="Hello Worldです。疎通確認に使用してください。")
def home_hello_world():
    return {"message": "Hello World"}


@router.post("/aiagent/sample",
             summary="LangGraphのAIエージェントを実行します",
             description="LangGraphのAIエージェントを実行します")
async def aiagent_graph(request: ExpertAiAgentRequest):
    try:
        _input = f"""
        # メタ情報:
        - 現在の時刻は「{datetime.now()}」です。

        # 指示書
        {request.user_input}
        """
        print(f"request.user_input:{_input}")
        chat_history, aiMessage = await ainvoke_graphagent(_input)
        _response = {
            "result": aiMessage,
            "type": "sample",
            "chathistory": chat_history
        }
        return ExpertAiAgentResponse(**_response)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred in the agent.")


@router.post("/aiagent/utility/{agent_name}",
             summary="LangGraphのAIエージェントを実行します",
             description="LangGraphのAIエージェントを実行します")
async def myaiagents(request: ExpertAiAgentRequest, agent_name: str):
    try:
        _input = f"""
        # メタ情報:
        - 現在の時刻は「{datetime.now()}」です。

        # 指示書
        {request.user_input}
        """

        if "jsonoutput" in agent_name:
            print(f"request.user_input:{_input}")
            parsed_json = await jsonOutputagent(_input)
            _response = {
                "result": parsed_json,
                "type": "jsonOutput"
            }
            return ExpertAiAgentResponseJson(**_response)
        elif "explorer" in agent_name:
            print(f"request.user_input:{_input}")
            result = await exploreragent(_input)
            _response = {
                "result": result,
                "type": "explorer"
            }
            return ExpertAiAgentResponse(**_response)
        return {"message": "No matching agent found."}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred in the agent.")