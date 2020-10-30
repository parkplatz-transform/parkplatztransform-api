from pydantic import BaseModel


class Shape(BaseModel):
    id: int

    created_at: str
    modified_at: str

    user_id: int
    area: str

    class Config:
        orm_mode = True

