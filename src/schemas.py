from enum import Enum
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional


class Trip(str, Enum):
    south_america = "South America"
    middle_east = "Middle East"
    other = "Other"

class LocationCreate(BaseModel):
    latitude: float
    longitude: float
    time: datetime
    source: str
    trip: Trip

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v


class LocationUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    time: Optional[datetime] = None
    source: Optional[str] = None
    trip: Optional[str] = None

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    latitude: float
    longitude: float
    time: datetime
    source: str
    trip: str
