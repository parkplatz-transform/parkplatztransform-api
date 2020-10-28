from fastapi import Depends, FastAPI, HTTPException, Header
from sqlalchemy.orm import Session

from .pypale import Pypale
from . import strings, schemas, crud
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


async def verify_token(token: str):
    valid = pypale.valid_token(token)
    if not valid:
        raise HTTPException(401, strings.validation["forbidden"])


@app.post("/users/", response_model=schemas.UserCreate)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    token = pypale.generate_token(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db=db, user=user)
    user.token = token
    return user


@app.get("/users/{user_id}", response_model=schemas.User, dependencies=[Depends(verify_token)])
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user