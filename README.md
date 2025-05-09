# setup
```
cd expertAgent
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```
# exec
```
uvicorn app.main:app --reload
```

```
curl http://127.0.0.1:8000/aiagent-api/v1


curl -X POST "http://127.0.0.1:8000/aiagent-api/v1/aiagent/sample" \
    -H "Content-Type: application/json" \
    -d '{
      "user_input": "ドラゴンボールの作者をメールで送信して"
    }'
```

# graphAI
## 1. インストール
```
npm i -g  @receptron/graphai_cli
```

## .env
```
OPENAI_API_KEY=<OPENAI_API_KEY>
GEMINI_API_KEY=<GEMINI_API_KEY>
CLAUDE_API_KEY=<CLAUDE_API_KEY>
```