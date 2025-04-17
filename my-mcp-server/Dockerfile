# Python 3.11をベースにする
FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlitアプリケーションを実行
CMD ["python", "-m", "app.sse"]