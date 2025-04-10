import time
from aiagent.googleapis.googleapi_services import get_googleapis_service
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io
import pandas as pd
from googleapiclient.errors import HttpError


SERVICE_NAME = "drive"
SHEETS_SERVICE_NAME = "sheets"
SHEETS_API_VERSION = "v4"  # Sheets API v4 を使用


class SpreadsheetDB:
    """
    Google スプレッドシートを簡易データベースとして操作するクラス。
    シートが存在しない場合は自動的に作成します。
    """
    # __init__ メソッドは変更なし
    def __init__(self, spreadsheet_id):
        """
        クラスを初期化し、Sheets APIサービスを取得します。

        Args:
            spreadsheet_id (str): 操作対象のスプレッドシートID。
        """
        self.spreadsheet_id = spreadsheet_id
        try:
            self.service = get_googleapis_service(SHEETS_SERVICE_NAME) # 引数1つに修正済みと仮定
            if not self.service:
                 raise ConnectionError("Failed to get Google Sheets service object via get_googleapis_service.")
            self.sheet_api = self.service.spreadsheets()
            print(f"Google Sheets API (Spreadsheet ID: {self.spreadsheet_id}) への接続準備完了。")
        except Exception as e:
            print(f"エラー: Google Sheets APIサービスの取得に失敗しました: {e}")
            raise

    def _sheet_exists(self, sheet_name):
        """指定された名前のシートが存在するか確認する"""
        try:
            # スプレッドシート全体のメタデータを取得 (シート名のみ取得)
            sheet_metadata = self.sheet_api.get(
                spreadsheetId=self.spreadsheet_id,
                fields='sheets.properties.title' # 必要なフィールドのみに限定
            ).execute()
            sheets = sheet_metadata.get('sheets', [])
            # シート名のリストを生成
            existing_sheet_names = [sheet.get('properties', {}).get('title', '') for sheet in sheets]
            # 指定したシート名が存在するかチェック
            return sheet_name in existing_sheet_names
        except HttpError as error:
            print(f"シート存在チェック中にAPIエラーが発生しました ({sheet_name}): {error}")
            # エラー発生時は存在しないとみなすか、例外を再送出するか選択
            # ここでは False を返し、後続処理でシート作成を試みる
            return False
        except Exception as e:
            print(f"シート存在チェック中に予期せぬエラーが発生しました ({sheet_name}): {e}")
            return False

    def _create_sheet(self, sheet_name, headers=None):
        """
        新しいシートを作成し、指定されていればヘッダー行を追加する。

        Args:
            sheet_name (str): 作成するシート名。
            headers (list, optional): ヘッダー行として書き込む文字列のリスト。

        Returns:
            bool: 作成に成功した場合は True、失敗した場合は False。
        """
        print(f"シート '{sheet_name}' が存在しないため、作成します...")
        requests = [{'addSheet': {'properties': {'title': sheet_name}}}]
        body = {'requests': requests}
        try:
            response = self.sheet_api.batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            created_sheet_id = response.get('replies', [{}])[0].get('addSheet', {}).get('properties', {}).get('sheetId')
            if created_sheet_id is not None:
                 print(f"シート '{sheet_name}' (ID: {created_sheet_id}) を作成しました。")
                 # ヘッダーが指定されていれば、作成したシートの最初の行に書き込む
                 if headers and isinstance(headers, list) and len(headers) > 0:
                     print(f"ヘッダー行 {headers} を '{sheet_name}' に追加します...")
                     # ヘッダーを書き込む範囲 (A1から始まる)
                     # 列数を計算 (A, B, ..., Z, AA, AB, ...)
                     num_cols = len(headers)
                     end_column_letter = ''
                     temp_num = num_cols
                     while temp_num > 0:
                         temp_num, remainder = divmod(temp_num - 1, 26)
                         end_column_letter = chr(65 + remainder) + end_column_letter # 65は'A'のASCIIコード

                     header_range = f"A1:{end_column_letter}1"
                     # update_range を呼び出してヘッダーを書き込む
                     update_result = self.update_range(sheet_name, header_range, [headers])
                     if update_result:
                         print("ヘッダー行の追加に成功しました。")
                         return True
                     else:
                         print("警告: シートは作成されましたが、ヘッダー行の追加に失敗しました。")
                         return True # シート作成自体は成功
                 else:
                    return True # ヘッダーなしで作成成功
            else:
                print(f"エラー: シート '{sheet_name}' の作成応答からシートIDを取得できませんでした。")
                return False

        except HttpError as error:
            print(f"シート '{sheet_name}' の作成中にAPIエラーが発生しました: {error}")
            # すでに同名シートが存在する場合のエラー (400 Bad Request) などをここでハンドリングすることも可能
            # 例: if 'already exists' in str(error): return True # 既に存在する場合も成功とみなす
            return False
        except Exception as e:
            print(f"シート '{sheet_name}' の作成中に予期せぬエラーが発生しました: {e}")
            return False

    def ensure_sheet_exists(self, sheet_name, headers=None):
         """
         シートが存在するか確認し、なければ作成するヘルパーメソッド。
         シート作成に失敗した場合は RuntimeError を発生させる。

         Args:
             sheet_name (str): 確認/作成するシート名。
             headers (list, optional): 新規作成する場合のヘッダー行。
         """
         if not self._sheet_exists(sheet_name):
             if not self._create_sheet(sheet_name, headers):
                 # シート作成に失敗したら例外を発生
                 raise RuntimeError(f"シート '{sheet_name}' の作成に失敗しました。APIログを確認してください。")
             else:
                 # シート作成後、APIへの反映を待つために少し待機
                 print("シート作成/ヘッダー追加の反映待ち...")
                 time.sleep(3) # 3秒待機 (必要に応じて調整)
         return True # シートが存在する、または作成に成功した場合

    # --- 各操作メソッドを修正 ---
    # (get_data, append_rows, update_range, find_rows, clear_range)

    def get_data(self, sheet_name, range_name=None, return_dataframe=True, headers_if_create=None):
        """
        指定されたシートまたは範囲のデータを取得します。
        シートが存在しない場合は作成します (headers_if_create でヘッダー指定可)。
        """
        try:
            self.ensure_sheet_exists(sheet_name, headers=headers_if_create)
        except RuntimeError as e:
             print(f"エラー: {e}")
             return pd.DataFrame() if return_dataframe else [] # エラー時は空を返す

        # --- 以降は元の get_data の処理をベースにする ---
        target_range = f"'{sheet_name}'"
        if range_name:
            target_range = f"'{sheet_name}'!{range_name}"

        print(f"データを取得中: {target_range}")
        try:
            result = self.sheet_api.values().get(
                spreadsheetId=self.spreadsheet_id,
                range=target_range
            ).execute()
            values = result.get('values', [])

            if not values:
                print(f"範囲 '{target_range}' にデータがありません。")
                # ヘッダー行のみが存在する場合も考慮
                if return_dataframe:
                     # ヘッダー情報を使って空のDataFrameを返す
                     if headers_if_create and len(values) == 0: # 新規作成直後
                          return pd.DataFrame(columns=headers_if_create)
                     elif len(values) == 1: # ヘッダー行だけある場合
                           return pd.DataFrame(columns=values[0])
                     else: # ヘッダー情報も取得できなかった場合
                           return pd.DataFrame()
                else:
                     return [] # ヘッダーのみでもリストで返すか、空を返すか（ここでは空）

            # --- DataFrame または List への変換処理 (前回と同様) ---
            if return_dataframe:
                header = values[0]
                data = values[1:]
                num_columns = len(header)
                data_fixed = [row[:num_columns] + [None] * (num_columns - len(row)) for row in data if len(row) <= num_columns]
                data_fixed += [row[:num_columns] for row in data if len(row) > num_columns]
                return pd.DataFrame(data_fixed, columns=header)
            else:
                return values # ヘッダー行も含んだリストを返す

        except HttpError as error:
            print(f"データの取得中にAPIエラーが発生しました ({target_range}): {error}")
            return None
        except Exception as e:
            print(f"データの取得中に予期せぬエラーが発生しました ({target_range}): {e}")
            return None

    def append_rows(self, sheet_name, values, headers_if_create=None):
        """
        指定されたシートの末尾に複数の行を追加します。
        シートが存在しない場合は作成します。
        """
        try:
            # ヘッダー情報は、もしシート作成時に必要なら指定
            self.ensure_sheet_exists(sheet_name, headers=headers_if_create)
        except RuntimeError as e:
             print(f"エラー: {e}")
             return None # エラー時は None を返す

        # --- 以降は元の append_rows の処理 ---
        if not isinstance(values, list) or not all(isinstance(row, list) for row in values):
             print("エラー: valuesはリストのリストである必要があります。")
             return None
        if not values:
            print("追加するデータがありません。")
            return None

        print(f"シート '{sheet_name}' に {len(values)} 行追加中...")
        try:
            body = {'values': values}
            target_range = f"'{sheet_name}'!A1" # 範囲はA1で良い (appendは末尾に追加)
            result = self.sheet_api.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=target_range,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            updated_range = result.get('updates', {}).get('updatedRange', 'N/A')
            print(f"{result.get('updates', {}).get('updatedRows', 0)}行が追加されました。範囲: {updated_range}")
            return result
        except HttpError as error:
            print(f"データの追加中にAPIエラーが発生しました ({sheet_name}): {error}")
            return None
        except Exception as e:
            print(f"データの追加中に予期せぬエラーが発生しました ({sheet_name}): {e}")
            return None


    def update_range(self, sheet_name, range_name, values, headers_if_create=None):
        """
        指定された範囲のセルを更新します。
        シートが存在しない場合は作成します。
        """
        try:
            self.ensure_sheet_exists(sheet_name, headers=headers_if_create)
        except RuntimeError as e:
             print(f"エラー: {e}")
             return None

        # --- 以降は元の update_range の処理 ---
        if not isinstance(values, list) or not all(isinstance(row, list) for row in values):
             print("エラー: valuesはリストのリストである必要があります。")
             return None
        if not values:
            print("更新するデータがありません。")
            return None

        target_range = f"'{sheet_name}'!{range_name}"
        print(f"範囲 {target_range} を更新中...")
        try:
            body = {'values': values}
            result = self.sheet_api.values().update(
                spreadsheetId=self.spreadsheet_id,
                range=target_range,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"{result.get('updatedCells', 0)}セルが範囲'{target_range}'で更新されました。")
            return result
        except HttpError as error:
            print(f"データの更新中にAPIエラーが発生しました ({target_range}): {error}")
            return None
        except Exception as e:
            print(f"データの更新中に予期せぬエラーが発生しました ({target_range}): {e}")
            return None


    def find_rows(self, sheet_name, search_column_header, search_value, return_dataframe=True, headers_if_create=None):
        """
        指定された列ヘッダーの値に基づいて行を検索します（完全一致）。
        シートが存在しない場合は作成します。
        """
        try:
            # シート作成時に検索対象のヘッダーが含まれるように指定
            self.ensure_sheet_exists(sheet_name, headers=headers_if_create)
        except RuntimeError as e:
             print(f"エラー: {e}")
             return pd.DataFrame() if return_dataframe else [] # エラー時は空を返す

        # --- 以降は元の find_rows の処理をベースにする ---
        print(f"シート '{sheet_name}' で '{search_column_header}' が '{search_value}' の行を検索中...")
        # headers_if_create を get_data にも渡す
        all_data_df = self.get_data(sheet_name, return_dataframe=True, headers_if_create=headers_if_create)

        if all_data_df is None: # get_data でエラー
             return None
        if all_data_df.empty:
            print("検索対象のデータがありません。")
            return pd.DataFrame() if return_dataframe else []

        if search_column_header not in all_data_df.columns:
            print(f"エラー: 列ヘッダー '{search_column_header}' がシート '{sheet_name}' に見つかりません。利用可能な列: {all_data_df.columns.tolist()}")
            return pd.DataFrame() if return_dataframe else []

        try:
            search_value_str = str(search_value)
            found_df = all_data_df[all_data_df[search_column_header].astype(str) == search_value_str]

            if found_df.empty:
                print(f"条件に一致する行は見つかりませんでした。")

            if return_dataframe:
                return found_df
            else:
                return found_df.values.tolist()
        except Exception as e:
             print(f"検索処理中にエラーが発生しました: {e}")
             return pd.DataFrame() if return_dataframe else []


    def clear_range(self, sheet_name, range_name, headers_if_create=None):
        """
        指定された範囲のセルの内容をクリアします。
        シートが存在しない場合は作成します (クリア対象のデータはない)。
        """
        try:
            self.ensure_sheet_exists(sheet_name, headers=headers_if_create)
        except RuntimeError as e:
             print(f"エラー: {e}")
             return None # エラー時は None を返す

        # --- 以降は元の clear_range の処理 ---
        target_range = f"'{sheet_name}'!{range_name}"
        print(f"範囲 {target_range} の内容をクリア中...")
        try:
            # クリアAPIを呼び出す前に、範囲が存在するか確認した方が親切かもしれないが、
            # APIがエラーを返してくれるので、ここではそのまま呼び出す。
            result = self.sheet_api.values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=target_range,
                body={}
            ).execute()
            cleared_range = result.get('clearedRange', 'N/A')
            # clearedRange が返らない場合もある (対象範囲にデータがないなど)
            if cleared_range != 'N/A':
                print(f"範囲'{cleared_range}'の内容がクリアされました。")
            else:
                 print(f"範囲'{target_range}'のクリアが要求されました (応答にclearedRangeなし)。")
            return result
        except HttpError as error:
            # クリア対象範囲が存在しない場合などもエラーになる可能性がある
            print(f"範囲のクリア中にAPIエラーが発生しました ({target_range}): {error}")
            # 存在しない範囲のクリアはエラーではなく警告として扱うこともできる
            # if error.resp.status == 400 and 'Unable to parse range' in str(error):
            #      print(f"警告: クリア対象の範囲 {target_range} が無効か存在しません。")
            #      return None # または空の成功応答を模倣
            return None
        except Exception as e:
            print(f"範囲のクリア中に予期せぬエラーが発生しました ({target_range}): {e}")
            return None


# --- メインの実行部分 (使い方サンプル) ---
if __name__ == '__main__':
    # --- 設定 (★要変更★) ---
    SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID_HERE' # ★★★★★★★★★★★
    SHEET_NAME = '商品リスト' # ★★★★★★★★★★★
    # ★ 新規シート作成時に使用されるヘッダー (必要に応じて変更) ★
    DEFAULT_HEADERS = ['商品ID', '商品名', '価格', 'カテゴリ', '在庫数']

    if not SPREADSHEET_ID or SPREADSHEET_ID == 'YOUR_SPREADSHEET_ID_HERE':
         print("エラー: スクリプトを実行する前に SPREADSHEET_ID を設定してください。")
    else:
        try:
            db = SpreadsheetDB(SPREADSHEET_ID)

            # --- 操作例 ---
            # 各メソッド呼び出し時に headers_if_create を指定

            # 1. データ追加 (シートがなければ DEFAULT_HEADERS で作成される)
            print("\n--- 1. データ追加 ---")
            new_products = [
                ['P004', 'ぶどう', 350, '果物', 40],
                ['V001', 'キャベツ', 180, '野菜', 70],
            ]
            db.append_rows(SHEET_NAME, new_products, headers_if_create=DEFAULT_HEADERS)

            # 2. 全データ読み取り (シートがなければ DEFAULT_HEADERS で作成される)
            print("\n--- 2. 全データ読み取り (DataFrame) ---")
            all_data_df = db.get_data(SHEET_NAME, return_dataframe=True, headers_if_create=DEFAULT_HEADERS)
            if all_data_df is not None:
                print(all_data_df)

            # 3. データ更新 (シートがなければ DEFAULT_HEADERS で作成される)
            print("\n--- 3. データ更新 ---")
            # 例: 商品ID 'P001' の価格を更新 (行・列は要特定)
            # 更新前にシートが存在するか確認され、なければ作成される
            db.update_range(SHEET_NAME, 'C2', [[165]], headers_if_create=DEFAULT_HEADERS) # 価格を165に更新

            # 4. データ検索 (シートがなければ DEFAULT_HEADERS で作成される)
            print("\n--- 4. データ検索 ---")
            fruit_items_df = db.find_rows(SHEET_NAME, 'カテゴリ', '果物', return_dataframe=True, headers_if_create=DEFAULT_HEADERS)
            if fruit_items_df is not None:
                print("検索結果 (カテゴリ='果物'):")
                print(fruit_items_df)

            # 5. データ削除 (クリア) (シートがなければ DEFAULT_HEADERS で作成される)
            print("\n--- 5. データ削除 (クリア) ---")
            # 例: 4行目から5行目をクリア
            db.clear_range(SHEET_NAME, 'A4:E5', headers_if_create=DEFAULT_HEADERS)

            # 6. 存在しないシート名を指定してデータを読み取る (自動作成されるはず)
            print("\n--- 6. 存在しないシートの読み取りテスト ---")
            NEW_SHEET_NAME = '新しいシート'
            NEW_HEADERS = ['列A', '列B', '列C']
            new_sheet_data = db.get_data(NEW_SHEET_NAME, return_dataframe=True, headers_if_create=NEW_HEADERS)
            if new_sheet_data is not None:
                 print(f"'{NEW_SHEET_NAME}' のデータ:")
                 print(new_sheet_data) # 最初は空のDataFrame (ヘッダーのみ) が返るはず

            # 7. 作成された新しいシートにデータを追加
            print("\n--- 7. 新しいシートにデータを追加 ---")
            new_sheet_rows = [
                 ['データ1', 'Data A', 100],
                 ['データ2', 'Data B', 200],
            ]
            db.append_rows(NEW_SHEET_NAME, new_sheet_rows) # headers_if_create は不要 (既に作成済みのため)

            print("\n--- 8. 新しいシートのデータを再度読み取り ---")
            new_sheet_data_after = db.get_data(NEW_SHEET_NAME, return_dataframe=True)
            if new_sheet_data_after is not None:
                 print(f"'{NEW_SHEET_NAME}' のデータ (追加後):")
                 print(new_sheet_data_after)

        except ConnectionError as ce:
            print(f"接続エラー: {ce}")
        except Exception as e:
            print(f"メイン処理中に予期せぬエラーが発生しました: {e}")
            import traceback
            traceback.print_exc()

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