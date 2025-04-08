```
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

```
uvicorn app.main:app --reload
```

```
docker-compose up --build
```


scp ./aiagentapi/token/token.json newton@192.168.11.8:/mnt/my_ssd/k3s_storage/secret/token

# token格納フォルダ
/mnt/my_ssd/k3s_storage/secret/token


server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}



location / {
    proxy_pass http://127.0.0.1:7860/;
    proxy_read_timeout 180s;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
