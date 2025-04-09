# マルチプラットフォーム対応のPythonイメージをベースにする
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel

# 依存関係をインストール (ターゲットアーキテクチャに合わせて実行される)
# RUN ビルドキャッシュを無効化したい場合などは --no-cache を使う
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Flaskアプリケーションを実行
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
