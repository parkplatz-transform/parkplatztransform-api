from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base_mixin import BaseMixin, Base


class Reason(BaseMixin, Base):
    __tablename__ = "reasons"

    segment_id = Column(Integer, ForeignKey("segments.id"))
    segment = relationship("Segment", back_populates="reason_for_refusal")

    description = Column(String)

