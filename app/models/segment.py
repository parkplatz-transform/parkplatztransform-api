import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship

from .base_mixin import BaseMixin, Base


class Alignment(enum.Enum):
    along_street = 0
    diagonal = 1
    orthogonal = 2


class Allowed(enum.Enum):
    never = 0
    temporarily = 1
    always = 2


class Segment(BaseMixin, Base):
    __tablename__ = "segments"

    order_number = Column(Integer)
    allowed = Column(Enum(Allowed))
    marked = Column(Boolean)
    alignment = Column(Enum(Alignment))
    length_in_meters = Column(Integer)
    count = Column(Integer)
    quality = Column(Integer)

    reason_for_refusal = relationship("Reason", back_populates="segment")

    recording_id = Column(Integer, ForeignKey("recordings.id"))
    recordings = relationship("Recording", back_populates="segments")
