import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


def init_env():
    env = os.getenv("APP_ENV", "dev")
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        print(f"loading {env} config")
        load_dotenv(env_file)
    load_dotenv()

class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{os.getenv('APP_ENV', 'dev')}"),
        extra='ignore' # 忽略多余的环境变量
    )