# Python 3.11をベースにする
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlitアプリケーションを実行
CMD ["streamlit", "run", "app.py", "--server.port", "8502"]