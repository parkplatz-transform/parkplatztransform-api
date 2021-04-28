from typing import Optional

from fastapi import HTTPException, BackgroundTasks, Response, Depends, APIRouter, Cookie
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from app import schemas, controllers
from app.services import OneTimeAuth, EmailService, get_db
from app.strings import validation
from app.sessions import SessionStorage, get_session
from app.config import settings


router = APIRouter()
email_service = EmailService()
one_time_auth = OneTimeAuth()


@router.post("/users/", response_model=schemas.UserBase)
def send_magic_link(user: schemas.UserCreate, background_tasks: BackgroundTasks):
    token = one_time_auth.generate_token(user.email)
    background_tasks.add_task(
        email_service.send_email_verification_link, user.email, token
    )
    return user


@router.get("/users/verify/")
async def verify_magic_link(
    code: str,
    email: str,
    dev: bool = False,
    db: Session = Depends(get_db),
    session_storage: SessionStorage = Depends(SessionStorage),
):
    if not one_time_auth.valid_token(code, email):
        raise HTTPException(401, validation["unauthorized"])
    decoded = one_time_auth.get_decoded_token(code)

    user = controllers.get_user_by_email(db, email)
    if not user:
        user = controllers.create_user(db, schemas.UserBase(email=decoded["sub"]))

    session_id = await session_storage.create_session(user)

    response = RedirectResponse(
        "http://localhost:3000" if dev else settings.frontend_url
    )
    response.set_cookie(
        key=settings.session_identifier,
        value=session_id,
        domain="localhost" if dev else "api.xtransform.org",
        path="/",
        httponly=True,
        max_age=settings.session_expiry,
        samesite="strict",
        secure=False if dev else True,
    )
    return response


@router.get("/users/me/", response_model=schemas.User)
async def get_logged_in_user(
    session: Optional[schemas.UserBase] = Depends(get_session),
):
    return session


@router.post("/users/logout/")
async def logout_user(
    response: Response,
    sessionid: Optional[str] = Cookie(None),
    session_storage: SessionStorage = Depends(SessionStorage),
):
    await session_storage.delete_session(sessionid)
    return response
