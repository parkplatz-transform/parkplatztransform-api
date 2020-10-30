from typing import List

from pydantic import BaseModel

from . import Segment, Shape


class RecordingBase(BaseModel):
    quality: int

    segments: List[Segment]
    shapes: List[Shape]


class Recording(RecordingBase):
    id: int
