from sqlalchemy import Column, Integer, Float, String, DateTime
import datetime
from src.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.timezone.utc)
    source = Column(String, nullable=False)
    trip = Column(String, nullable=False)
