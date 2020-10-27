import enum

from geoalchemy2.types import Geometry
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship

from .database import Base


class Alignment(enum.Enum):
    along_street = 0
    diagonal = 1
    orthogonal = 2


class Allowed(enum.Enum):
    never = 0
    temporarily = 1
    always = 2


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)

    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    segments = relationship("Segment", back_populates="user")
    shapes = relationship("Shape", back_populates="user")
    recordings = relationship("Recording", back_populates="user")


class Recording(Base):
    __tablename__ = "recordings"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    quality = Column(Integer)

    user_id = relationship("User", back_populates="recordings")
    user = relationship("User", back_populates="recordings")


class Shape(Base):
    __tablename__ = "shapes"

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    area = Column(Geometry("POLYGON", 4326))

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="shapes")


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    allowed = Column(Enum(Allowed))
    marked = Column(Boolean)
    alignment = Column(Enum(Alignment))
    length = Column(Integer)
    count = Column(Integer)
    quality = Column(Integer)

    reason_id = Column(Integer, ForeignKey("reasons.id"))
    reason = relationship("Reason", back_populates="reasons")

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="segments")


class Reason(Base):
    __tablename__ = "reasons"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)

    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    segments = relationship("Segments", back_populates="reason")
