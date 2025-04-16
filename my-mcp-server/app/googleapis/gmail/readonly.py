from app.googleapis.googleapi_services import get_googleapis_service
from app.utils.html_operation import convert_html_to_markdown
import base64
from email.mime.text import MIMEText


SERVICE_NAME = "gmail"


# 件名に指定されたキーワードが含まれるメールを検索し、本文を取得する関数
def get_emails_by_keyword(subject_keyword, top=5):
    """
    指定された件名キーワードを含むメールを検索し、本文を取得します。
    件名キーワードは部分一致で検索されます。
    検索結果は最大で指定された件数まで取得されます。
    Args:
        subject_keyword (str): 検索する件名のキーワード。
        top (int): 取得するメールの最大件数。
    Returns:
        list: 検索結果のメール本文のリスト。
    """
    service = get_googleapis_service(SERVICE_NAME)
    
    # メールを検索 (件名にキーワードを含む)
    # query = f'subject:{subject_keyword}'
    query = f'{subject_keyword}'
    results = service.users().messages().list(userId='me', q=query).execute()
    
    messages = results.get('messages', [])
    if not messages:
        print(f"No emails found with subject containing '{subject_keyword}'")
        return []

    email_bodies = []
    
    cnt = 0

    # メッセージIDを使ってメールの詳細を取得し、本文を抽出
    for message in messages:
        cnt += 1
        if cnt > top:
            break
            
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        
        # メール本文のパートを探す
        body_data = None
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain': # "text/html" "text/plain"
                    body_data = part['body']['data']
                    break
        else:
            body_data = payload['body']['data']

        if body_data:
            # Base64でエンコードされたデータをデコード
            body_decoded = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('utf-8')
            email_bodies.append({"email_body": convert_html_to_markdown(body_decoded)})
        else:
            print(f"Could not extract body from email with ID {message['id']}")

    return {"result": email_bodies}