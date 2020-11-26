import base64

from fastapi import HTTPException, BackgroundTasks

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app import schemas, controllers
from app.database import get_db
from app.services import OneTimeAuth, EmailService
from app.config import get_settings
from app.strings import validation

router = APIRouter()
email_service = EmailService()

settings = get_settings()

one_time_auth = OneTimeAuth(
    base_url=settings.base_url,
    secret_key=settings.secret_key,
    token_ttl_minutes=int(settings.token_ttl_minutes),
    token_issue_ttl_seconds=int(settings.token_issue_ttl_seconds),
)


@router.post("/users/", response_model=schemas.UserBase)
def send_magic_link(
        user: schemas.UserBase,
        background_tasks: BackgroundTasks
):
    token = one_time_auth.generate_token(user.email)
    background_tasks.add_task(
        email_service.send_email_verification_link, user.email, token
    )
    return user


@router.get("/users/verify/", response_model=schemas.UserVerified)
def verify_magic_link(code: str, email: str, db: Session = Depends(get_db)):
    if not one_time_auth.valid_token(code, email):
        raise HTTPException(401, validation["unauthorized"])
    decoded = one_time_auth.get_decoded_token(code)
    if not controllers.get_user_by_email(db, email):
        controllers.create_user(db, schemas.UserBase(email=decoded["email"]))
    access_token = base64.b64decode(code).decode("utf8")
    return schemas.UserVerified(access_token=access_token)
