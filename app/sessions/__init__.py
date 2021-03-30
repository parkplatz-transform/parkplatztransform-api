import json
from uuid import uuid4
from typing import Optional

from fastapi import Depends, HTTPException, Cookie

from app.strings import validation
from app.services.redis_cache import redis_cache
from app.schemas import User
from app.config import settings


class SessionStorage:
    async def create_session(self, user: User):
        session_id = uuid4().hex
        session_dict = {
            "id": user.id,
            "email": user.email,
            "permission_level": user.permission_level,
        }
        await redis_cache.set(
            session_id, json.dumps(session_dict), expires=settings.session_expiry
        )
        return session_id

    async def get_session(self, id: str):
        return await redis_cache.get(id)

    async def delete_session(self, id: str):
        await redis_cache.delete(id)


async def get_session(
    sessionid: Optional[str] = Cookie(None),
    session_storage: SessionStorage = Depends(SessionStorage),
) -> Optional[User]:
    if sessionid:
        session = await session_storage.get_session(sessionid)
        if session:
            data = json.loads(session)
            return User(id=data["id"], email=data["email"], permission_level=data["permission_level"])
        else:
            raise HTTPException(401, validation["unauthorized"])
    else:
        raise HTTPException(401, validation["unauthorized"])
