from pydantic import BaseModel


class Segment(BaseModel):
    id: int

    created_at: str
    modified_at: str

    user_id: int
    line: str

    class Config:
        orm_mode = True
