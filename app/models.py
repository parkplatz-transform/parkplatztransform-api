from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from geoalchemy2.types import Geometry
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)

    lines = relationship("Line", back_populates="user")
    areas = relationship("Area", back_populates="user")


class Line(Base):
    __tablename__ = "line"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)

    line = Column(Geometry('LINESTRING', 4326))
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="lines")


class Area(Base):
    __tablename__ = "area"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    
    area = Column(Geometry('POLYGON', 4326))
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="areas")
