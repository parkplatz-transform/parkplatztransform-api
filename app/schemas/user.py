from pydantic import BaseModel, EmailStr, StrictBool, validator

from app.strings import validation


class UserBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    accepted_terms_and_conditions: StrictBool

    @validator("accepted_terms_and_conditions", pre=True, always=True)
    def must_accept_terms(cls, v):
        if v is True:
            return v
        raise ValueError(validation["must_accept_terms"])


class User(UserBase):
    id: str
    permission_level: int

    class Config:
        orm_mode = True


class UserVerified(BaseModel):
    access_token: str
    token_type: str = "Bearer"
