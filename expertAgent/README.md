# expertAgent プロジェクト概要

本ディレクトリは、LangGraphで開発したユーティリティAIエージェント群、MCPサーバー、及びそれらをAPIとして公開するFastAPIサーバーで構成されています。

## ディレクトリ構成

- `aiagent/`
  - LangGraphベースのAIエージェント本体
  - `langgraph/`
    - `common.py`：LangGraphエージェント共通処理
    - `util.py`：モデル判定等のユーティリティ
    - `sampleagent/`：サンプルエージェント
    - `utilityaiagents/`：ユーティリティ系エージェント（例: explorer, jsonOutput）
- `app/`
  - FastAPIアプリケーション
  - `main.py`：FastAPIエントリポイント
  - `api/v1/agent_endpoints.py`：エージェントAPIエンドポイント
  - `schemas/`：リクエスト・レスポンス用Pydanticモデル
  - `core/`：設定・ロガー
- `mymcp/`
  - MCPサーバー・ツール群
  - `stdioall.py`/`stdio_explorer.py`：MCPサーバー実装
  - `tool/`/`specializedtool/`/`googleapis/`：各種ツール
- `requirements.txt`：必要パッケージ
- `Dockerfile`：コンテナ化用

---

# コンテナ化
```bash
cd aiagentapi
docker build --platform linux/arm64 -t mynoo/aiagentapi:v0.1.2 . --no-cache
docker push mynoo/aiagentapi:v0.1.2

cd aiagentui
docker build --platform linux/arm64 -t mynoo/aiagentui:v0.1.2 . --no-cache
docker push mynoo/aiagentui:v0.1.2

cd gradioui
docker build --platform linux/arm64 -t mynoo/gradioui:v0.1.2 . --no-cache
docker push mynoo/gradioui:v0.1.2

docker run -it　-p 8000:8000 --rm mynoo/aiagentapi:latest
docker run -d -p 8000:8000 mynoo/aiagentapi:v0.1.1
```

```
curl -X POST "http://127.0.0.1:8000/my_root/v1/aiagent" \
    -H "Content-Type: application/json" \
    -d '{
      "user_input": "葛飾区の人口を教えて"
    }'
```

```
cd aiagentapi
docker build --platform linux/arm64 -t mynoo/aiagentapi:v0.1.1 . --no-cache
docker push mynoo/aiagentapi:v0.1.1

cd gradioui
docker build --platform linux/arm64 -t mynoo/gradioui:v0.1.1 . --no-cache
docker push mynoo/gradioui:v0.1.1

docker run -it　-p 8000:8000 --rm mynoo/aiagentapi:latest
docker run -d -p 8001:7860 mynoo/gradioui:v0.1.1
```