import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from main import app, get_db
from src.database import Base
from src.models import Location
from src.schemas import LocationCreate


# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    """Clear database before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_create_location():
    """Test creating a location."""
    payload = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "time": "2026-04-29T12:00:00",
        "source": "gps",
        "trip": "trip-001"
    }
    response = client.post("/locations", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["latitude"] == 40.7128
    assert data["longitude"] == -74.0060
    assert data["source"] == "gps"
    assert data["trip"] == "trip-001"
    assert "id" in data


def test_create_location_invalid_latitude():
    """Test creating location with invalid latitude."""
    payload = {
        "latitude": 100,  # Invalid: > 90
        "longitude": -74.0060,
        "time": "2026-04-29T12:00:00",
        "source": "gps",
        "trip": "trip-001"
    }
    response = client.post("/locations", json=payload)
    assert response.status_code == 422


def test_create_location_invalid_longitude():
    """Test creating location with invalid longitude."""
    payload = {
        "latitude": 40.7128,
        "longitude": 200,  # Invalid: > 180
        "time": "2026-04-29T12:00:00",
        "source": "gps",
        "trip": "trip-001"
    }
    response = client.post("/locations", json=payload)
    assert response.status_code == 422


def test_list_locations_empty():
    """Test listing locations when none exist."""
    response = client.get("/locations")
    assert response.status_code == 200
    assert response.json() == []


def test_list_locations():
    """Test listing locations after creating some."""
    # Create two locations
    payload1 = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "time": "2026-04-29T12:00:00",
        "source": "gps",
        "trip": "trip-001"
    }
    payload2 = {
        "latitude": 34.0522,
        "longitude": -118.2437,
        "time": "2026-04-29T13:00:00",
        "source": "mobile",
        "trip": "trip-002"
    }
    
    client.post("/locations", json=payload1)
    client.post("/locations", json=payload2)
    
    response = client.get("/locations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["source"] == "gps"
    assert data[1]["source"] == "mobile"


def test_get_location():
    """Test getting a location by ID."""
    # Create a location
    payload = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "time": "2026-04-29T12:00:00",
        "source": "gps",
        "trip": "trip-001"
    }
    create_response = client.post("/locations", json=payload)
    location_id = create_response.json()["id"]
    
    # Get the location
    response = client.get(f"/locations/{location_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == location_id
    assert data["latitude"] == 40.7128


def test_get_location_not_found():
    """Test getting a location that doesn't exist."""
    response = client.get("/locations/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_location():
    """Test updating a location."""
    # Create a location
    payload = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "time": "2026-04-29T12:00:00",
        "source": "gps",
        "trip": "trip-001"
    }
    create_response = client.post("/locations", json=payload)
    location_id = create_response.json()["id"]
    
    # Update the location
    update_payload = {
        "latitude": 35.0,
        "source": "updated-gps"
    }
    response = client.put(f"/locations/{location_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == location_id
    assert data["latitude"] == 35.0
    assert data["source"] == "updated-gps"
    # Original longitude should remain unchanged
    assert data["longitude"] == -74.0060


def test_update_location_invalid_latitude():
    """Test updating location with invalid latitude."""
    # Create a location
    payload = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "time": "2026-04-29T12:00:00",
        "source": "gps",
        "trip": "trip-001"
    }
    create_response = client.post("/locations", json=payload)
    location_id = create_response.json()["id"]
    
    # Try to update with invalid latitude
    update_payload = {"latitude": 100}
    response = client.put(f"/locations/{location_id}", json=update_payload)
    assert response.status_code == 422


def test_update_location_not_found():
    """Test updating a location that doesn't exist."""
    update_payload = {"latitude": 35.0}
    response = client.put("/locations/999", json=update_payload)
    assert response.status_code == 404


def test_delete_location():
    """Test deleting a location."""
    # Create a location
    payload = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "time": "2026-04-29T12:00:00",
        "source": "gps",
        "trip": "trip-001"
    }
    create_response = client.post("/locations", json=payload)
    location_id = create_response.json()["id"]
    
    # Delete the location
    response = client.delete(f"/locations/{location_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/locations/{location_id}")
    assert response.status_code == 404


def test_delete_location_not_found():
    """Test deleting a location that doesn't exist."""
    response = client.delete("/locations/999")
    assert response.status_code == 404


def test_full_crud_workflow():
    """Test a complete CRUD workflow."""
    # CREATE
    payload = {
        "latitude": 51.5074,
        "longitude": -0.1278,
        "time": "2026-04-29T15:30:00",
        "source": "api",
        "trip": "london-trip"
    }
    create_response = client.post("/locations", json=payload)
    assert create_response.status_code == 201
    location_id = create_response.json()["id"]
    
    # READ
    read_response = client.get(f"/locations/{location_id}")
    assert read_response.status_code == 200
    assert read_response.json()["trip"] == "london-trip"
    
    # UPDATE
    update_payload = {
        "latitude": 51.5100,
        "trip": "london-trip-updated"
    }
    update_response = client.put(f"/locations/{location_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json()["latitude"] == 51.5100
    assert update_response.json()["trip"] == "london-trip-updated"
    
    # DELETE
    delete_response = client.delete(f"/locations/{location_id}")
    assert delete_response.status_code == 204
    
    # VERIFY DELETED
    verify_response = client.get(f"/locations/{location_id}")
    assert verify_response.status_code == 404
