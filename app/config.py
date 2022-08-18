from pydantic import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    session_identifier: str = "sessionid"
    database_url: str = "postgresql://postgres:postgres@postgres/postgres"
    mongo_url: str = "mongodb://root:example@localhost:27017/?authMechanism=DEFAULT"
    token_ttl_minutes: str = 14 * 24 * 60  # 2 weeks
    token_issue_ttl_seconds: str = 2 * 60 * 60  # 2 hours
    base_url: str = "http://localhost:8023"
    mailgun_api_key: str = ""
    mailgun_domain: str = ""
    jwt_algorithm: str = "HS256"
    frontend_url: str = "https://app.xtransform.org"
    sentry_url: str = ""
    session_expiry: int = 7 * 24 * 60 * 60  # 1 Week
    redis_url: str = "redis://redis:6379"

    class Config:
        env_file = ".env"


settings = Settings()
