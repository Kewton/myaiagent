from aiagent.googleapis.drive import get_file_id_and_mime_type, resumable_upload, get_google_drive_file_links
from aiagent.tts.tts import tts
import uuid


def tts_and_upload_drive():
    speech_file_path = f"./temp/{uuid.uuid4()}.mp3"
    input_message = "アンパンマンとは誰か？"

    tts(speech_file_path, input_message)

    name, id, mimeType = get_file_id_and_mime_type("MyAiAgent")

    upfileid = resumable_upload("test.mp3", speech_file_path, "audio/mpeg", id)

    print(get_google_drive_file_links(upfileid))

