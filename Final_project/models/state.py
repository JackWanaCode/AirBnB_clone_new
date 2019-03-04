#!/usr/bin/python3
"""
State Class from Models Module
"""
import models
from models.base_model import BaseModel, Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float

class State(BaseModel, Base):
    """State class handles all application states"""
    __tablename__ = 'states'
    name = Column(String(128), nullable=False)
    cities = relationship('City', backref='state', cascade='delete')
