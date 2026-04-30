from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from typing import List
import logging

from src.database import init_db, get_db
from src.models import Location
from src.schemas import LocationCreate, LocationUpdate, LocationResponse

def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on app startup."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


logger = logging.getLogger('myapp')
logging.basicConfig(filename='myapp.log', level=logging.error, format='%(asctime)s %(levelname)s:%(message)s')


@app.get("/")
async def root(background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, 'Hello World endpoint was called\n')
    return {"message": "Hello World"}


@app.get("/locations", response_model=List[LocationResponse])
async def list_locations(db: Session = Depends(get_db)):
    print(db, 'DB SESSION')
    """Get all locations."""
    logger.info('Started')
    locations = db.query(Location).all()
    return locations


@app.post("/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    """Create a new location."""
    db_location = Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


@app.get("/locations/{location_id}", response_model=LocationResponse)
async def get_location(location_id: int, db: Session = Depends(get_db)):
    """Get a location by ID."""
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
    db: Session = Depends(get_db)
):
    """Update a location by ID."""
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
async def delete_location(location_id: int, db: Session = Depends(get_db)):
    """Delete a location by ID."""
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if not db_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {location_id} not found"
        )

    db.delete(db_location)
    db.commit()
    return None

