from fastapi import APIRouter, HTTPException
from mymcp.tool.tts_and_upload_drive import tts_and_upload_drive
from mymcp.utils.generate_subject_from_text import generate_subject_from_text
from mymcp.googleapis.gmail.send import send_email
from core.config import settings
from app.schemas.utilitySchemas import UtilityRequest, UtilityResponse


router = APIRouter()


@router.post("/utility/tts_and_upload_drive",
             summary="",
             description="")
async def tts_and_upload_drive_api(request: UtilityRequest):
    """
    テキストの台本をインプットに音声合成を行い音声ファイル(.mp3)を生成しGoogle Driveにアップロードします。
    アップロードしたファイルへのURLリンクを返却します。

    Args:
        user_input (str): 音声合成するテキストメッセージ。

    Returns:
        str: アップロード結果を示すメッセージまたはファイルURリンク
    """
    try:
        # タイトル生成
        title = generate_subject_from_text(request.user_input, max_length=40)

        print(f"Generated title: {title}")

        # 音声合成とGoogle Driveへのアップロード
        result = tts_and_upload_drive(request.user_input, title)

        body = f"""
        
        音声合成とGoogle Driveへのアップロードが完了しました。
        
        # アップロード結果:
        {result}
        ---

        # 台本:
        {request.user_input}
        """

        # メール送信
        send_email(settings.MAIL_TO, title, body)

        return UtilityResponse(result=result)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred in the utility.")