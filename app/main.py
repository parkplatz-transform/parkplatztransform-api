from fastapi import Depends, FastAPI, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .pypale import Pypale
from . import strings, schemas, crud, email_service
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


bearer_scheme = HTTPBearer()


async def verify_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    valid = pypale.valid_token(token.credentials)
    if not valid:
        raise HTTPException(401, strings.validation["unauthorized"])


@app.post("/users/", response_model=schemas.UserCreate)
def create_user(user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    token = pypale.generate_token(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail=strings.validation["email_in_use"])
    user = crud.create_user(db=db, user=user)
    background_tasks.add_task(email_service.send_email_verification_link, user.email, token)
    return user


@app.get("/users/me", response_model=schemas.UserCreate, dependencies=[Depends(verify_token)])
async def read_user(db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    decoded = pypale.get_decoded_token(return_token=token.credentials)
    db_user = crud.get_user_by_email(db, email=decoded["email"])
    if db_user is None:
        raise HTTPException(status_code=404, detail=strings.validation["user_not_found"])
    return db_user
