# 全体概要
# 初期セットアップ
## expertAgent
### setup
```bash
cd expertAgent
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### .env
```
OPENAI_API_KEY=<OPENAI_API_KEY>
GOOGLE_API_KEY=<GOOGLE_API_KEY>
ANTHROPIC_API_KEY=<ANTHROPIC_API_KEY>
LOG_DIR=./log
LOG_LEVEL=INFO
GRAPH_AGENT_MODEL=gpt-4o-mini
GOOGLE_APIS_TOKEN_PATH=./token/token.json
GOOGLE_APIS_CREDENTIALS_PATH=./token/credentials.json
PODCAST_SCRIPT_DEFAULT_MODEL=gpt-4o-mini
MAIL_TO=<MAIL_TO>
SPREADSHEET_ID=<SPREADSHEET_ID>
```

### exec
```bash
uvicorn app.main:app --reload
```

```
curl http://127.0.0.1:8000/aiagent-api/v1/


curl -X POST "http://127.0.0.1:8000/aiagent-api/v1/aiagent/sample" \
    -H "Content-Type: application/json" \
    -d '{
      "user_input": "ドラゴンボールの作者をメールで送信して"
    }'
```

## graphAiServer
- yarnのインストール
  ```bash
  brew install yarn
  ```
### setup
```bash
cd graphAiServer
yarn install
```

### exec
```bash
NODE_OPTIONS="--loader ts-node/esm" npx ts-node src/app.js
```

```bash
curl http://localhost:3000/
```

# graphAI
## 1. インストール
```
sudo npm i -g  @receptron/graphai_cli
```

## .env
```
OPENAI_API_KEY=<OPENAI_API_KEY>
GEMINI_API_KEY=<GEMINI_API_KEY>
CLAUDE_API_KEY=<CLAUDE_API_KEY>
```