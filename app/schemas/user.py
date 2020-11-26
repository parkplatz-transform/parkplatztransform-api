from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserVerified(BaseModel):
    access_token: str
    token_type: str = "Bearer"
