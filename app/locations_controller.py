

from fastapi import Depends, HTTPException, status, Request

from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Location
from app.schemas import LocationUpdate, LocationResponse, LocationCreateBatch


api_key_all = "0w6ph89tvHVkcyKzClMwRFtIczJFPHZb"
api_key_get = "e9c53798cd2f424f81dcd248f9c77f5a"


def check_header_api_key(request: Request) -> bool:
    key = request.headers.get('api-key-secret')
    method = request.method

    if key == api_key_all:
        return True
    elif method == "GET" and key == api_key_get:  
        return True
    else:
        return False
    

def SetupLocationsController(app):


    @app.get("/locations", response_model=List[LocationResponse])
    async def list_locations(request: Request, db: Session = Depends(get_db)):
        """Get all locations."""

        if not check_header_api_key(request):
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED )
        
        locations = db.query(Location).all()
        return locations
    



    @app.post("/locations", response_model=List[LocationResponse], status_code=status.HTTP_201_CREATED)
    async def create_location(batch: LocationCreateBatch, request: Request, db: Session = Depends(get_db)):
        """Create one or more new locations."""

        if not check_header_api_key(request):
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED )

        created_locations = []
        for location in batch.locations:
            db_location = Location(**location.model_dump())
            db.add(db_location)
            db.commit()
            db.refresh(db_location)
            created_locations.append(db_location)
        
        return created_locations
    

    @app.get("/locations_latest", response_model=List[LocationResponse], status_code=status.HTTP_201_CREATED)
    async def get_latest_location(request: Request, db: Session = Depends(get_db)):
        """Get most recent location."""

        if not check_header_api_key(request):
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED )

        location = db.query(Location).order_by(Location.id.desc()).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No locations found"
            )
        return [ location ]



    @app.get("/locations/{location_id}", response_model=LocationResponse)
    async def get_location(location_id: int, request: Request, db: Session = Depends(get_db)):
        """Get a location by ID."""

        if not check_header_api_key(request):
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED )

        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with id {location_id} not found"
            )
        return location




    @app.put("/locations/{location_id}", response_model=LocationResponse)
    async def update_location(
        location_id: int,
        location_update: LocationUpdate,
        request: Request,
        db: Session = Depends(get_db)
    ):
        """Update a location by ID."""
        if not check_header_api_key(request):
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED )

        db_location = db.query(Location).filter(Location.id == location_id).first()
        if not db_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with id {location_id} not found"
            )

        update_data = location_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_location, key, value)

        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        return db_location



    @app.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_location(location_id: int, request: Request, db: Session = Depends(get_db)):
        """Delete a location by ID."""

        if not check_header_api_key(request):
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED )

        db_location = db.query(Location).filter(Location.id == location_id).first()
        if not db_location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with id {location_id} not found"
            )

        db.delete(db_location)
        db.commit()
        return None

