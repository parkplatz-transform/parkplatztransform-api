import uuid

from app.models.subsegment import SubsegmentNonParking, SubsegmentParking
from sqlalchemy import (
    Column,
    ForeignKey,
    Text,
)
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship, column_property
from geoalchemy2 import Geometry
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping

from .base_mixin import BaseMixin, Base


class Segment(BaseMixin, Base):
    __tablename__ = "segments"

    id = Column(UUID, default=lambda: uuid.uuid4().hex, primary_key=True, index=True)

    owner_id = Column("owner_id", UUID, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="segments")

    further_comments = Column(Text)
    data_source = Column(Text)

    subsegments_non_parking = relationship(
        "SubsegmentNonParking",
        back_populates="segment",
        cascade="all, delete",
        lazy="joined",
    )
    subsegments_parking = relationship(
        "SubsegmentParking",
        back_populates="segment",
        cascade="all, delete",
        lazy="joined",
    )

    _geometry = Column(
        "geometry", Geometry(geometry_type="GEOMETRY", srid=4326), nullable=False
    )

    # GeoJSON Specific properties

    @hybrid_property
    def geom(self):
        return to_shape(self._geometry)

    @hybrid_property
    def geometry(self):
        return mapping(self.geom)

    @hybrid_property
    def bbox(self):
        return self.geom.bounds

    total_non_parking = column_property(
        select(func.count(SubsegmentNonParking.id))
        .where(SubsegmentNonParking.segment_id == id)
        .correlate_except(SubsegmentNonParking)
        .scalar_subquery()
    )

    total_parking = column_property(
        select(func.count(SubsegmentParking.id))
        .where(SubsegmentParking.segment_id == id)
        .correlate_except(SubsegmentParking)
        .scalar_subquery()
    )

    @hybrid_property
    def properties(self):
        subsegments = self.subsegments_parking + self.subsegments_non_parking
        total = self.total_non_parking + self.total_parking
        return {
            "subsegments": subsegments,
            "has_subsegments": True if total else False,
            "further_comments": self.further_comments,
            "data_source": self.data_source,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
        }

    @hybrid_property
    def as_geojson_feature(self):
        return {
            "properties": self.properties,
            "bbox": self.bbox,
            "id": self.id,
            "geometry": self.geometry,
        }
