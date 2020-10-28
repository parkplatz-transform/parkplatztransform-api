from typing import List

from pydantic import BaseModel, EmailStr


class Segment(BaseModel):
    id: int

    created_at: str
    modified_at: str

    user_id: int
    line: str

    class Config:
        orm_mode = True


class Shape(BaseModel):
    id: int

    created_at: str
    modified_at: str

    user_id: int
    area: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    email: EmailStr
    token: str

    class Config:
        orm_mode = True


class User(UserBase):
    id: int

    segments: List[Segment] = []
    shapes: List[Shape] = []

    class Config:
        orm_mode = True

