from pydantic import BaseModel, EmailStr
from app.models.user import access_levels


class UserBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class User(UserBase):
    id: str
    permission_level: int

    class Config:
        orm_mode = True


class UserVerified(BaseModel):
    access_token: str
    token_type: str = "Bearer"
