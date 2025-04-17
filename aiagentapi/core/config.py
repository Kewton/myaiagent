from pydantic_settings import BaseSettings  # pydantic_settingsからインポート
from pydantic import Field


class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(default="INFO", env="OPENAI_API_KEY")
    GEMINI_API_KEY: str = Field(default="INFO", env="GEMINI_API_KEY")
    MAIL_TO: str = Field(default="INFO", env="MAIL_TO")
    CONFIG_TEST: str = Field(default="sss", env="CONFIG_TEST")
    LOG_DIR: str = Field(default="./", env="LOG_DIR")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")


# インスタンス生成
settings = Settings()
