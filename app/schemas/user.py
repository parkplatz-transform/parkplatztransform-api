from pydantic import BaseModel, EmailStr, StrictBool, validator

from ..strings import validation


class UserBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    accepted_terms_and_conditions: StrictBool

    @validator("accepted_terms_and_conditions")
    def must_accept_terms(cls, v):
        if not v:
            raise ValueError(validation["must_accept_terms"])
        return v


class User(UserBase):
    id: str
    permission_level: int

    class Config:
        orm_mode = True


class UserVerified(BaseModel):
    access_token: str
    token_type: str = "Bearer"
