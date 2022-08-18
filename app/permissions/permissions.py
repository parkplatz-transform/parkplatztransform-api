from fastapi import HTTPException

from app.models import access_levels
from app.strings import validation


def user_can_operate(user: dict, resource_owner_id: str):
    if (
        user['id'] != resource_owner_id
        and user.permission_level < access_levels["contributor"]
    ):
        raise HTTPException(403, validation["permission"])
