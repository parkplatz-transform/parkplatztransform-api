from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    postgres_password: str
    secret_key: str
    database_url: str
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()

