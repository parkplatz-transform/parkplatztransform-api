from typing import Optional, List

from pydantic import BaseModel
from geojson_pydantic.features import Feature
from geojson_pydantic.features import FeatureCollection
from geojson_pydantic.geometries import Geometry

class Properties(BaseModel):
    name: str
    count: int = 0

class Cluster(Feature):
    id: str
    properties: Properties
    geometry: Optional[Geometry]

    class Config:
        orm_mode = True


class ClusterCollection(FeatureCollection):
    features: List[Cluster]

    class Config:
        orm_mode = True