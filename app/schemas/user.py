from pydantic import BaseModel, EmailStr, StrictBool, validator
from app.models.user import access_levels


class UserBase(BaseModel):
    email: EmailStr
    accepted_terms_and_conditions: StrictBool

    @validator("accepted_terms_and_conditions")
    def must_accept_terms(cls, v):
        if not v:
            raise ValueError("User must accept terms and conditions")
        return v

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
