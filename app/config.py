from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    database_url: str = "postgresql://postgres:postgres@postgres/postgres"
    token_ttl_minutes: str = 14 * 24 * 60  # 2 weeks
    token_issue_ttl_seconds: str = 2 * 60 * 60  # 2 hours
    base_url: str = "localhost:8023"
    mailgun_api_key: str = ""
    mailgun_domain: str = ""
    jwt_algorithm: str = "HS256"
    frontend_url: str = "https://app.xtransform.org"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
