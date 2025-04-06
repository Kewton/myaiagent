from aiagent.googleapis.googleapi_services import get_googleapis_service
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
import base64

SERVICE_NAME = "gmail"


def send_email(to_email, subject, body):
    try:
        print("-- send mail start --")
        service = get_googleapis_service(SERVICE_NAME)

        # MIMEメッセージを作成
        message = MIMEMultipart()
        message['To'] = to_email
        message['From'] = "me"
        message['Subject'] = subject
        
        body_processed = body.replace('\\n', '\n')

        # メール本文を設定
        msg_body = MIMEText(body_processed, "plain", "utf-8")
        message.attach(msg_body)

        # メッセージをbase64エンコード
        raw_msg = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        message_body = {"raw": raw_msg}

        # メールを送信
        service.users().messages().send(userId="me", body=message_body).execute()

        return True
    except RefreshError as e:
        print(f"Error refreshing the token: {e}")
        # `stderr`ではなく、エラーメッセージを取得
        print(f"Error details: {e.args}")
        return False
    except HttpError as e:
        print(f"Standard HttpError: {e.stderr}")
        return False
    except Exception as e:
        print(f"Exception occuerd: {e}")
        return False