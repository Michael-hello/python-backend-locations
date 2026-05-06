import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app, get_db
from app.database import Base
from app.models import Location
from app.schemas import LocationCreate
from app.locations_controller import SetupLocationsController, api_key_get, api_key_all


# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./tests/test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def create_test_location(**kwargs):
    lat = kwargs.get("latitude", 40.7128)
    lon = kwargs.get("longitude", -74.0060)
    trip = kwargs.get("trip", "South America")

    location = {
        "latitude": lat,
        "longitude": lon,
        "time": int(datetime.now().timestamp()),
        "source": "test",
        "trip": trip,
    }
    return location



def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
SetupLocationsController(app)

client = TestClient(app, headers={"api-key-secret": api_key_all})


@pytest.fixture(autouse=True)
def clear_db():
    """Clear database before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_create_location():
    """Test creating a location."""
    payload = [ create_test_location(), create_test_location() ]
    response = client.post("/locations", json= {"locations": payload})
    assert response.status_code == 201
    data = response.json()[0]
    assert data["latitude"] == 40.7128
    assert data["longitude"] == -74.0060
    assert data["source"] == "test"
    assert data["trip"] == "South America"
    assert data["time"] > 10000
    assert "id" in data


def test_create_location_invalid_latitude():
    """Test creating location with invalid latitude."""
    payload = [ create_test_location() ]
    payload[0]["latitude"] = 100  # Invalid: > 90
    response = client.post("/locations", json= {"locations": payload})
    assert response.status_code == 422


def test_create_location_invalid_longitude():
    """Test creating location with invalid longitude."""
    payload = [ create_test_location() ]
    payload[0]["longitude"] = 200  # Invalid: > 180
    response = client.post("/locations", json= {"locations": payload})
    assert response.status_code == 422



def test_list_locations_empty():
    """Test listing locations when none exist."""
    response = client.get("/locations")
    assert response.status_code == 200
    assert response.json() == []


def test_list_locations():
    """Test listing locations after creating some."""
    # Create two locations
    payload1 = [ create_test_location() ]
    payload2 = [ create_test_location(latitude=34.0522, longitude=-118.2437) ]

    client.post("/locations", json={"locations": payload1})
    client.post("/locations", json={"locations": payload2})
    
    response = client.get("/locations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["source"] == "test"
    assert data[1]["latitude"] == 34.0522


def test_get_location():
    """Test getting a location by ID."""
    payload = [ create_test_location() ]
    create_response = client.post("/locations", json={"locations": payload})
    location_id = create_response.json()[0]["id"]
    
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
    payload = [create_test_location()]
    create_response = client.post("/locations", json={"locations": payload})
    location_id = create_response.json()[0]["id"]
    
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
    payload = [create_test_location()]
    create_response = client.post("/locations", json={"locations": payload})
    location_id = create_response.json()[0]["id"]
    
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
    payload = [create_test_location()]
    create_response = client.post("/locations", json={"locations": payload})
    location_id = create_response.json()[0]["id"]
    
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
    payload = [create_test_location(
        latitude=51.5074,
        longitude=-0.1278,
        trip="london-trip"
    )]
    create_response = client.post("/locations", json={"locations": payload})
    assert create_response.status_code == 201
    location_id = create_response.json()[0]["id"]
    
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
