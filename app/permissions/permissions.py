from fastapi import HTTPException

from app.strings import validation


access_levels = {
    "guest": 0,
    "contributor": 1,
}

def user_can_operate(user: dict, resource_owner_id: str):
    if (
        user['id'] != resource_owner_id
        and user['permission_level'] < access_levels["contributor"]
    ):
        raise HTTPException(403, validation["permission"])
