from typing import Optional

from fastapi import HTTPException, BackgroundTasks, Depends, APIRouter, Cookie
from fastapi.responses import RedirectResponse, ORJSONResponse

from app import controllers
from app.services import OneTimeAuth, EmailService
from app.strings import validation
from app.config import settings


router = APIRouter()
email_service = EmailService()
one_time_auth = OneTimeAuth()


async def get_session(
    sessionid: Optional[str] = Cookie(None),
) -> Optional[dict]:
    if sessionid:
        user = await controllers.get_logged_in_user(
            session_id=sessionid
        )
        if user:
            return user
        else:
            raise HTTPException(401, validation["unauthorized"])
    else:
        raise HTTPException(401, validation["unauthorized"])


@router.post("/users/", response_class=ORJSONResponse)
def send_magic_link(
    user: dict,
    background_tasks: BackgroundTasks
):
    token = one_time_auth.generate_token(user['email'])
    background_tasks.add_task(
        email_service.send_email_verification_link, user['email'], token
    )
    return user


@router.get("/users/verify/")
async def verify_magic_link(
    code: str,
    email: str,
    dev: bool = False
):
    if not one_time_auth.valid_token(code, email):
        raise HTTPException(401, validation["unauthorized"])
    decoded = one_time_auth.get_decoded_token(code)

    user = await controllers.get_user_by_email(email)
    if not user:
        user = await controllers.create_user(
            decoded["sub"]
        )

    session_id = await controllers.create_session(user_id=user['id'])

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


@router.get("/users/me/", response_class=ORJSONResponse)
def get_logged_in_user(
    session: Optional[dict] = Depends(get_session),
):
    session['id'] = session['_id']
    return session


@router.post("/users/logout/")
async def logout_user(
    sessionid: Optional[str] = Cookie(None),
):
    id = await controllers.clear_session(session_id=sessionid)
    return {"deleted": id}
