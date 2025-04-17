from pydantic_settings import BaseSettings  # pydantic_settingsからインポート
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    LOG_DIR: str = Field(default="./", env="LOG_DIR")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")


# インスタンス生成
settings = Settings()