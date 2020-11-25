from typing import Optional, List
import datetime

from pydantic import BaseModel
from geojson_pydantic.features import Feature
from geojson_pydantic.features import FeatureCollection
from geojson_pydantic.geometries import LineString as PydanticLineString

from ..models import Alignment, StreetLocation


class LineString(PydanticLineString):
    type: str = "LineString"


class SubsegmentBase(BaseModel):
    order_number: int = 0
    parking_allowed: bool = True
    count: int = 0
    marked: bool = True
    alignment: Alignment = Alignment.parallel
    street_location: StreetLocation = StreetLocation.street
    length_in_meters: int = 0
    car_count: int = 0
    quality: int = 1


class Subsegment(SubsegmentBase):
    id: Optional[int]
    created_at: Optional[datetime.datetime]
    modified_at: Optional[datetime.datetime]


class SubsegmentsBase(BaseModel):
    subsegments: List[SubsegmentBase]


class Subsegments(BaseModel):
    subsegments: List[Subsegment]


class Segment(Feature):
    properties: Subsegments
    geometry: LineString

    class Config:
        orm_mode = True


class SegmentCollection(FeatureCollection):
    features: List[Segment]


class SegmentBase(BaseModel):
    feature: Segment

    class Config:
        orm_mode = True


class SegmentCreate(BaseModel):
    type: str = "Feature"
    properties: SubsegmentsBase
    geometry: LineString
