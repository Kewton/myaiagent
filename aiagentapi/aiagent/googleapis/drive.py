from aiagent.googleapis.googleapi_services import get_googleapis_service
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io


SERVICE_NAME = "drive"


def get_folder_id(folder_name):
    service = get_googleapis_service(SERVICE_NAME)

    # フォルダを検索するためのクエリ
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    
    results = service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print(f"No folder found with the name '{folder_name}'")
        return None
    else:
        # 複数のフォルダが見つかった場合は最初のフォルダIDを返す
        folder_id = items[0]['id']
        print(f"Folder ID for '{folder_name}': {folder_id}")
        return folder_id


def list_files_in_folder_recursive(folder_id, current_path, file_list):
    """
    フォルダ内のファイルとサブフォルダを再帰的に取得しリストに格納
    """
    service = get_googleapis_service(SERVICE_NAME)
    query = f"'{folder_id}' in parents"
    results = service.files().list(
        q=query,
        pageSize=100,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()

    files = results.get('files', [])

    if not files:
        return

    # ファイルをリストに追加
    for file in files:
        # ファイルのフルパスを作成
        full_path = os.path.join(current_path, file['name'])
        
        # ファイル情報をリストに追加
        file_list.append({
            'name': file['name'],
            'id': file['id'],
            'mimeType': file['mimeType'],
            'path': full_path
        })
        
        # MIMEタイプがフォルダの場合、再帰的にサブフォルダ内のファイルを取得
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            list_files_in_folder_recursive(file['id'], full_path, file_list)


def get_file_id_and_mime_type(folder_path):
    """
    指定されたパスに基づいて、ファイルまたはフォルダのIDとmimeTypeを取得
    """
    service = get_googleapis_service(SERVICE_NAME)

    # パスを分割 (例えば "./mywork/myapp/テスト/filename.pdf" を ['mywork', 'myapp', 'テスト', 'filename.pdf'] に分割)
    folder_names = folder_path.strip("./").split('/')

    # ルートフォルダから開始 (Google Driveのルートフォルダは'root'と指定)
    parent_id = 'root'

    # 各フォルダ/ファイル名ごとにDrive APIを使用して次の階層に進む
    for name in folder_names:
        query = f"'{parent_id}' in parents and name='{name}' and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType)"
        ).execute()

        files = results.get('files', [])

        if not files:
            print(f"'{name}' not found in the specified path.")
            return None

        # 現在のフォルダ/ファイルの情報を取得
        file_info = files[0]
        parent_id = file_info['id']  # 次の階層に進むためのフォルダIDを更新

    # 最後に見つかったファイル/フォルダのIDとmimeTypeを返す
    return file_info['name'], file_info['id'], file_info['mimeType']


def download_file(file_id, destination_path):
    service = get_googleapis_service(SERVICE_NAME)
    
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")


# フォルダが存在しなければ作成し、フォルダIDを返却する関数
def get_or_create_folder(folder_path):
    service = get_googleapis_service(SERVICE_NAME)

    # パスを分割して処理 (例えば "./mywork/myapp/テスト" を ['mywork', 'myapp', 'テスト'] に分割)
    folder_names = folder_path.strip("./").split('/')

    # ルートフォルダから開始 (Google Driveのルートフォルダは'root'と指定)
    parent_id = 'root'

    # 各フォルダ名を順に処理し、フォルダが存在するか確認する
    for folder_name in folder_names:
        query = f"'{parent_id}' in parents and name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if files:
            # フォルダが存在する場合、そのフォルダIDを取得して次の階層に進む
            parent_id = files[0]['id']
        else:
            # フォルダが存在しない場合、フォルダを作成する
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]  # 親フォルダのIDを指定
            }
            folder = service.files().create(body=file_metadata, fields='id').execute()
            parent_id = folder['id']  # 作成したフォルダのIDを取得

    # 最後のフォルダIDを返す（これが最下層のフォルダ）
    return parent_id


def get_google_drive_file_links(file_id: str) -> dict | None:

    try:
        # files().get() を呼び出し、必要なフィールドを指定してファイルメタデータを取得
        service = get_googleapis_service(SERVICE_NAME)
        file_metadata = service.files().get(
            fileId=file_id,
            # fieldsパラメータで webViewLink と webContentLink をリクエスト
            fields='id, name, webViewLink, webContentLink'
        ).execute()

        # 必要な情報を含む辞書を返す
        links = {
            'id': file_metadata.get('id'),
            'name': file_metadata.get('name'),
            'webViewLink': file_metadata.get('webViewLink'),      # ウェブ表示用リンク
            'webContentLink': file_metadata.get('webContentLink') # ダウンロード/コンテンツリンク
        }
        return links

    except Exception as e:
        print(f"An error occurred while retrieving file links for ID '{file_id}': {e}")
        return None


def upload_file(file_name, file_path, mime_type, folder_id=None):
    """
	- textファイル
        'text/plain'
    - PDFファイル (.pdf):
	    mime_type = 'application/pdf'
	- MP4ファイル (.mp4):
	    mime_type = 'video/mp4'
    - mp3ファイル（.mp3）
        mime_type = 'audio/mpeg'
    - wavファイル（.wav）
        mime_type = 'audio/wav'
	- JPEGファイル (.jpg):
	    mime_type = 'image/jpeg'
	- Excelファイル (.xlsx):
	    mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    """
    service = get_googleapis_service(SERVICE_NAME)

    # フォルダIDを指定した場合にメタデータに親フォルダを設定
    if folder_id:
        file_metadata = {'name': file_name, 'parents': [folder_id]}
    else:
        file_metadata = {'name': file_name}

    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f"File ID: {file.get('id')}")
    return file.get('id')


# Resumable Uploadを実行する関数
def resumable_upload(save_file_name_in_drive, upload_file_path, mime_type, folder_id=None):
    service = get_googleapis_service(SERVICE_NAME)

    # アップロードするファイルのメタデータ
    # フォルダIDを指定した場合にメタデータに親フォルダを設定
    if folder_id:
        file_metadata = {'name': save_file_name_in_drive, 'parents': [folder_id]}
    else:
        file_metadata = {'name': save_file_name_in_drive}

    # Resumable Uploadの準備
    media = MediaFileUpload(upload_file_path, mimetype=mime_type, resumable=True)

    # アップロード開始
    request = service.files().create(body=file_metadata, media_body=media, fields='id')

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print(f"Upload Complete. File ID: {response.get('id')}")
    return response.get('id')