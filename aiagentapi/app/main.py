from fastapi import FastAPI
from app.api.v1 import common_endpoints
from app.core.logger import setup_logging

setup_logging()

app = FastAPI(
    title="My API",
    description="APIドキュメント",
    version="1.0.0",
    root_path="/my_root",
    swagger_ui_parameters={
        "docExpansion": "list",  # サイドバーにAPIリンクを表示
        "defaultModelsExpandDepth": -1  # モデルはサイドバーに表示しない
    }
)

app.include_router(common_endpoints.router, prefix="/v1")