import enum
from typing import Optional, List
from datetime import date, datetime
from uuid import uuid4

from pydantic import BaseModel
from geojson_pydantic.features import Feature
from geojson_pydantic.features import FeatureCollection
from geojson_pydantic.geometries import Geometry


class Alignment(str, enum.Enum):
    parallel = "parallel"
    perpendicular = "perpendicular"
    diagonal = "diagonal"


class StreetLocation(str, enum.Enum):
    street = "street"
    curb = "curb"
    sidewalk = "sidewalk"
    parking_bay = "parking_bay"
    middle = "middle"
    car_park = "car_park"


class UserRestriction(str, enum.Enum):
    all_users = "all_users"
    handicap = "handicap"
    residents = "residents"
    car_sharing = "car_sharing"
    gender = "gender"
    electric_cars = "electric_cars"
    other = "other"


class NoParkingReason(str, enum.Enum):
    private_parking = "private_parking"
    bus_stop = "bus_stop"
    bus_lane = "bus_lane"
    taxi = "taxi"
    tree = "tree"
    bike_racks = "bike_racks"
    pedestrian_crossing = "pedestrian_crossing"
    pedestrian_zone = "pedestrian_zone"
    driveway = "driveway"
    loading_zone = "loading_zone"
    standing_zone = "standing_zone"
    emergency_exit = "emergency_exit"
    lowered_curb_side = "lowered_curb_side"
    no_stopping = "no_stopping"
    lane = "lane"


class AlternativeUsageReason(str, enum.Enum):
    bus_stop = "bus_stop"
    bus_lane = "bus_lane"
    market = "market"
    lane = "lane"
    taxi = "taxi"
    loading = "loading"
    other = "other"


class SubsegmentBase(BaseModel):
    parking_allowed: bool
    order_number: int = 0
    length_in_meters: Optional[float]
    car_count: Optional[int]
    quality: int = 1

    # Public parking allowed
    fee: Optional[bool]
    street_location: Optional[StreetLocation]
    marked: Optional[bool]
    alignment: Optional[Alignment]
    duration_constraint: Optional[bool]
    user_restriction: Optional[bool]
    user_restriction_reason: Optional[UserRestriction]
    alternative_usage_reason: Optional[AlternativeUsageReason]
    time_constraint: Optional[bool]
    time_constraint_reason: Optional[str]
    duration_constraint_reason: Optional[str]

    # Public parking not allowed
    no_parking_reasons: List[NoParkingReason] = []


class Subsegment(SubsegmentBase):
    class Config:
        orm_mode = True


class SubsegmentsBase(BaseModel):
    subsegments: List[SubsegmentBase]


class Properties(BaseModel):
    subsegments: List[Subsegment]
    has_subsegments: Optional[bool]
    owner_id: Optional[str]
    data_source: Optional[str]
    further_comments: Optional[str]
    modified_at: Optional[datetime]
    created_at: Optional[datetime]


class Segment(Feature):
    id: str
    properties: Properties
    geometry: Geometry

    class Config:
        orm_mode = True


class SegmentCollection(FeatureCollection):
    features: List[Segment]

    class Config:
        orm_mode = True


class SegmentBase(BaseModel):
    feature: Segment

    class Config:
        orm_mode = True


class SegmentCreate(BaseModel):
    _id: uuid4 = uuid4()
    type: str = "Feature"
    properties: Properties
    geometry: Geometry


class SegmentUpdate(SegmentCreate):
    properties: Properties


class SegmentQuery(BaseModel):
    bbox: List[List[float]]
    details: bool
    exclude_ids: List[str]
    include_if_modified_after: Optional[datetime]
