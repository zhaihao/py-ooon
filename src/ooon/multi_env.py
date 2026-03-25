import os

from dotenv import load_dotenv

def init_env():
    env = os.getenv("env", "dev")
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        print(f"loading {env} config")
    load_dotenv(env_file)
    load_dotenv()
