from fastapi import HTTPException

from app.models import access_levels
from app.schemas import User
from app.strings import validation


def user_can_operate(user: User, resource_owner_id: str):
  print(user, resource_owner_id)
  if user.id != resource_owner_id and user.permission_level < access_levels['contributor']:
    raise HTTPException(403, validation["permission"])
