import motor.motor_asyncio

from app.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.mongo_url,
    uuidRepresentation='standard'
    )
db = client['xtransform']
