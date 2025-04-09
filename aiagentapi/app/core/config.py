from pydantic_settings import BaseSettings  # pydantic_settingsからインポート
from pydantic import Field


class Settings(BaseSettings):
    OPENAI_API_KEY: str = Field(default="INFO", env="OPENAI_API_KEY")
    GEMINI_API_KEY: str = Field(default="INFO", env="GEMINI_API_KEY")
    GOOGLE_APIS_TOKEN_PATH: str = Field(default="INFO", env="GOOGLE_APIS_TOKEN_PATH")
    GOOGLE_APIS_CREDENTIALS_PATH: str = Field(default="INFO", env="GOOGLE_APIS_CREDENTIALS_PATH")
    MAIL_TO: str = Field(default="INFO", env="MAIL_TO")
    CONFIG_TEST: str = Field(default="sss", env="CONFIG_TEST")
    LOG_DIR: str = Field(default="./", env="LOG_DIR")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    PODCAST_SCRIPT_DEFAULT_MODEL: str = Field(default="gpt-4o-mini", env="PODCAST_SCRIPT_DEFAULT_MODEL")

    class Config:
        env_file = ".env"  # .envファイルを使用して環境変数を読み込む設定


# インスタンス生成
settings = Settings()
