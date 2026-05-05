
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
import logging

from app.database import init_db, get_db
from app.models import Location
from app.locations_controller import SetupLocationsController


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on app startup."""
    init_db()
    yield
    
    
app = FastAPI(lifespan=lifespan)

origins = [
    'http://localhost:5173', 
    'https://localhost:5173', 
    'http://127.0.0.1:5173',
    'https://127.0.0.1:5173',
    'http://michael-hello.github.io/react-app/*',
    'https://michael-hello.github.io/react-app/*',
    'http://michael-hello.github.io/react-app',
    'https://michael-hello.github.io/react-app',
    'https://michael-hello.github.io/*'  ] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://michael-hello\.github\.io/.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event(db: Session = Depends(get_db)):
    # Code here runs once when the app starts
    print("FastAPI app is starting up...")

    #delete any test locations from development to prevent cluttering the database
    test_locations = db.query(Location).filter(Location.source == "test").all()
    [db.delete(loc) for loc in test_locations]
    db.commit()



logger = logging.getLogger('myapp')
logging.basicConfig(filename='myapp.log', level=logging.WARNING, format='%(asctime)s %(levelname)s:%(message)s')


@app.get("/")
async def root():
    return {"message": "Hello World"}


#endpoint to stop web app hosted in renderer from sleeping
@app.head("/health")
async def health():
    return {"message": "alive"}


SetupLocationsController(app)
