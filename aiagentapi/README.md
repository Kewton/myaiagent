# コンテナ化
```bash
cd aiagentapi
docker build --platform linux/arm64 -t mynoo/aiagentapi:v0.1.1 . --no-cache
docker push mynoo/aiagentapi:v0.1.1

cd aiagentui
docker build --platform linux/arm64 -t mynoo/aiagentui:v0.1.1 . --no-cache
docker push mynoo/aiagentui:v0.1.1

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