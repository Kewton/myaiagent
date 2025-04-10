import html2text
from aiagent.googleapis.drive import get_or_create_folder, upload_file
from bs4 import BeautifulSoup, NavigableString
from aiagent.utils.file_operation import delete_file
import re
import requests
import uuid
from pathlib import Path


def getMarkdown(url, isUpload=True):
    try:
        result = {
            "state": "failed",
            "result": ""
        }
        response = requests.get(url)

        if response.status_code == 200:
            html_content = response.text
            # 関数を使ってHTMLをMarkdownに変換
            markdown_content = html_to_markdown(html_content)
            result["state"] = "success"
            result["result"] = markdown_content
            
            if isUpload:
                # マークダウンファイル生成
                temp_dir = Path("./temp")
                try:
                    temp_dir.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    return f"エラー: 一時ディレクトリ '{temp_dir}' の作成に失敗しました: {e}"
                unique_filename = f"{uuid.uuid4()}.md"
                md_file_path = temp_dir / unique_filename

                try:
                    with open(md_file_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                except IOError as e:
                    print(f"ファイルの書き込みエラー: {e}")

                # googl drive にアップロード
                folder_id = get_or_create_folder("./MyAiAgent/knowledge")
                upload_file(f"{url}.md", md_file_path, 'text/plain', folder_id)
                delete_file(str(md_file_path))
            return result
        else:
            return str(response.status_code) + "エラー"
    except Exception as e:
        print(e)
        result["result"] = e
        return result


def convert_html_to_markdown(html_content):
    print("convert start")
    # html2textのインスタンスを作成
    converter = html2text.HTML2Text()

    # リンクを無視する
    converter.ignore_links = True
    # 画像を無視する
    converter.ignore_images = True
    # 幅制限を無効にする
    converter.body_width = 0

    # HTMLをMarkdownに変換
    markdown_content = converter.handle(html_content)
    return markdown_content


def html_to_markdown(html_content):
    # BeautifulSoupでHTMLをパース
    soup = BeautifulSoup(html_content, 'html.parser')

    # 不要な要素を削除（例: スクリプト、スタイル、ナビゲーションなど）
    for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
        element.decompose()

    # html2textを設定してコードブロックに対応
    converter = html2text.HTML2Text()
    converter.body_width = 0
    converter.ignore_links = False
    converter.ignore_images = True
    converter.bypass_tables = False
    converter.single_line_break = True
    converter.code_style = True  # コードブロックを適切に処理

    # HTMLをMarkdownに変換
    markdown = converter.handle(str(soup))

    return markdown
