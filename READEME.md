```
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

```
uvicorn app.main:app --reload
```