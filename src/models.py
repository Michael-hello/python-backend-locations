from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
from src.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    time = Column(Integer, nullable=False)
    source = Column(String, nullable=False)
    trip = Column(String, nullable=False)
