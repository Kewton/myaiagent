# マルチプラットフォーム対応のPythonイメージをベースにする
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt requirements.txt

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# Gradioがデフォルトで使用するポートを公開
EXPOSE 7860

# アプリケーションを実行するコマンド
CMD ["python", "app.py"]