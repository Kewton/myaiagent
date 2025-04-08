# setup
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
```
streamlit run app.py
```


```
docker build --platform linux/arm64 -t mynoo/myragui_arm64:v0.0.1 . --no-cache
docker push mynoo/myragui_arm64:v0.0.1

docker build -t mynoo/myragui:v0.0.1 . --no-cache

docker run -d -p 8502:8502 mynoo/myragui:v0.0.1
```