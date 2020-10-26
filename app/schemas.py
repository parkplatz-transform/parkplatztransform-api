from typing import List, Optional

from pydantic import BaseModel

class Line(BaseModel):
    id: int

    created_at: str
    modified_at: str
    
    user_id: int
    line: str

    class Config:
        orm_mode = True


class Area(BaseModel):
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
    email: str
    token: str

    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    
    lines: List[Line] = []
    areas: List[Area] = []

    class Config:
        orm_mode = True



