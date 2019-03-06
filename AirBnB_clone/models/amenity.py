#!/usr/bin/python3
"""
Amenity Class from Models Module
"""
from models.base_model import BaseModel, Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import backref


class Amenity(BaseModel, Base):
    """Amenity class handles all application amenities"""
    __tablename__ = 'amenities'
    name = Column(String(128), nullable=False)
    place_amenities = relationship('PlaceAmenity',
                                   backref='amenities',
                                   cascade='delete')
