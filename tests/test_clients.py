import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import SessionLocal
from main import app
from models.clients import Client
from routers.clients import get_db_session
from schemas.clients import ClientCreate, ClientUpdate

# Create a test database engine
test_engine = create_engine("sqlite:///test.db")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Override the get_db_session function to use the test database
def override_get_db_session():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db_session] = override_get_db_session

# Create a test client
client = TestClient(app)

# Test data
test_client_1 = ClientCreate(name="John Doe", email="john.doe@example.com")
test_client_2 = ClientCreate(name="Jane Smith", email="jane.smith@example.com")
test_client_update = ClientUpdate(name="John Doe Updated", email="john.doe.updated@example.com")

@pytest.fixture(autouse=True)
def setup_database():
    # Create the test database
    Client.__table__.create(test_engine)
    yield
    # Clean up the test database
    Client.__table__.drop(test_engine)

def test_create_client():
    response = client.post("/clients/", json=test_client_1.dict())
    assert response.status_code == 201
    assert response.json()["data"]["name"] == test_client_1.name
    assert response.json()["data"]["email"] == test_client_1.email

def test_get_clients():
    # Create some test clients
    client.post("/clients/", json=test_client_1.dict())
    client.post("/clients/", json=test_client_2.dict())

    response = client.get("/clients/")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2

def test_get_client():
    # Create a test client
    response = client.post("/clients/", json=test_client_1.dict())
    client_id = response.json()["data"]["id"]

    response = client.get(f"/clients/{client_id}")
    assert response.status_code == 200
    assert response.json()["data"]["name"] == test_client_1.name
    assert response.json()["data"]["email"] == test_client_1.email

def test_update_client():
    # Create a test client
    response = client.post("/clients/", json=test_client_1.dict())
    client_id = response.json()["data"]["id"]

    response = client.put(f"/clients/{client_id}", json=test_client_update.dict())
    assert response.status_code == 200
    assert response.json()["data"]["name"] == test_client_update.name
    assert response.json()["data"]["email"] == test_client_update.email

def test_delete_client():
    # Create a test client
    response = client.post("/clients/", json=test_client_1.dict())
    client_id = response.json()["data"]["id"]

    response = client.delete(f"/clients/{client_id}")
    assert response.status_code == 200
    assert response.json()["data"] == {"message": "Client deleted successfully."}