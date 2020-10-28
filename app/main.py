from fastapi import Depends, FastAPI, HTTPException, Header

from .pypale import Pypale
from . import models, strings
from .database import SessionLocal
from .config import get_settings


app = FastAPI()

settings = get_settings()

pypale = Pypale(
    base_url=settings.base_url,
    secret_key=settings.secret_key,
    token_ttl_minutes=int(settings.token_ttl_minutes),
    token_issue_ttl_seconds=int(settings.token_issue_ttl_seconds),
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def authenticate(token: str):
    valid = pypale.valid_token(token)
    if not valid:
        raise HTTPException(401, strings.validation["forbidden"])

