from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test case for successful client creation
def test_create_client_success():
    response = client.post("/clients/", json={"name": "John Doe", "email": "john.doe@example.com"})
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data["data"]
    assert data["data"]["name"] == "John Doe"
    assert data["data"]["email"] == "john.doe@example.com"


# Test case for retrieving all clients
def test_get_clients_success():
    # Create some clients
    client.post("/clients/", json={"name": "Client A", "email": "client.a@example.com"})
    client.post("/clients/", json={"name": "Client B", "email": "client.b@example.com"})
    
    response = client.get("/clients/", params={"limit": 10, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) > 0  # Should return at least one client
    assert "total_count" in data["metadata"]["pagination"]


# Test case for retrieving a single client by ID
def test_get_client_success():
    # Create a client first
    response = client.post("/clients/", json={"name": "Jane Doe", "email": "jane.doe@example.com"})
    client_id = response.json()["data"]["id"]
    
    response = client.get(f"/clients/{client_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["id"] == client_id
    assert data["data"]["name"] == "Jane Doe"
    assert data["data"]["email"] == "jane.doe@example.com"

# Test case for retrieving a client that doesn't exist
def test_get_client_not_found():
    response = client.get("/clients/999999")  # Assuming ID 999999 doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Client not found"

# Test case for updating a client successfully
def test_update_client_success():
    # Create a client first
    response = client.post("/clients/", json={"name": "John Doe", "email": "john.doe@example.com"})
    client_id = response.json()["data"]["id"]
    
    # Update client
    response = client.put(f"/clients/{client_id}", json={"name": "John Updated", "email": "john.updated@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["name"] == "John Updated"
    assert data["data"]["email"] == "john.updated@example.com"

# Test case for updating a non-existent client
def test_update_client_not_found():
    response = client.put("/clients/999999", json={"name": "Non Existent", "email": "non.existent@example.com"})
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Client not found"

# Test case for successful client deletion
def test_delete_client_success():
    # Create a client first
    response = client.post("/clients/", json={"name": "Client To Delete", "email": "delete.me@example.com"})
    client_id = response.json()["data"]["id"]
    
    response = client.delete(f"/clients/{client_id}")
    assert response.status_code == 204  # No content, just success

# Test case for deleting a non-existent client
def test_delete_client_not_found():
    response = client.delete("/clients/999999")  # Assuming ID 999999 doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["message"] == "Client not found"
