from pydantic import BaseModel, EmailStr
from app.models.user import access


class UserBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class User(UserBase):
    id: str
    permission_level: int = access.get("guest")

    class Config:
        orm_mode = True


class UserVerified(BaseModel):
    access_token: str
    token_type: str = "Bearer"
