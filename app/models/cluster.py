import uuid
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

from sqlalchemy import (
    Column,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID

from geoalchemy2 import Geometry

from .base_mixin import Base


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(UUID, default=lambda: uuid.uuid4().hex, primary_key=True)
    count = Column(Integer, default=0, nullable=False)
    name = Column(Text)

    _geometry = Column(
        "geometry",
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
        nullable=False,
    )

    @hybrid_property
    def geometry(self):
        geom = to_shape(self._geometry)
        return mapping(geom)

    @hybrid_property
    def bbox(self):
        geom = to_shape(self._geometry)
        return geom.bounds

    @hybrid_property
    def properties(self):
        return {
            "name": self.name,
            "count": self.count,
        }
