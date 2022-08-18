from uuid import uuid4
from datetime import datetime

from ..services import db

user_collection = db['users']
session_collection = db['sessions']


async def get_user(user_id: str) -> dict:
    user = await db.user_collection.find_one({'_id': user_id})
    user['id'] = user['_id']
    return user


async def get_user_by_email(email: str) -> dict:
    print(email)
    user = await user_collection.find_one({'email': email})
    if user is not None:
        user['id'] = user['_id']
    return user


async def create_user(email: str) -> dict:
    user = {}
    user['_id'] = str(uuid4())
    user['permission_level'] = 0
    user['created_at'] = datetime.now()
    user['modified_at'] = datetime.now()
    user['email'] = email
    result = await user_collection.insert_one(user)
    if result.acknowledged is True:
        user['id'] = user['_id']
        return user


async def create_session(user_id: str) -> str:
    session = {}
    session['_id'] = str(uuid4())
    session['owner_id'] = user_id
    result = await session_collection.insert_one(session)
    if result.acknowledged is True:
        return session['_id']


async def get_logged_in_user(session_id: str) -> dict:
    session = await session_collection.find_one({'_id': session_id})
    if session is None:
        return None
    user = await user_collection.find_one({'_id': session['owner_id']})
    print(user)
    return user


async def clear_session(session_id: str):
    await session_collection.delete_one({'_id': session_id})
    return session_id
