import pytest
from backend.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

@pytest.mark.official
def test_add_order_api_success(client):
    order_data = {
        "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 201
    assert response.json['order_id'] == "API001"

@pytest.mark.official
def test_get_order_api_success(client):
    client.post('/api/orders', json={
        "order_id": "GET001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.get('/api/orders/GET001')
    assert response.status_code == 200
    assert response.json['order_id'] == "GET001"

@pytest.mark.official
def test_get_order_api_not_found(client):
    response = client.get('/api/orders/NONEXISTENT')
    assert response.status_code == 404

@pytest.mark.official
def test_update_order_status_api_success(client):
    client.post('/api/orders', json={
        "order_id": "UPDATE001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.put('/api/orders/UPDATE001/status', json={"new_status": "shipped"})
    assert response.status_code == 200
    assert response.json['status'] == "shipped"

@pytest.mark.official
def test_list_all_orders_api_with_data(client):
    client.post('/api/orders', json={"order_id": "LST001", "item_name": "Item A", "quantity": 1, "customer_id": "C1"})
    client.post('/api/orders', json={"order_id": "LST002", "item_name": "Item B", "quantity": 2, "customer_id": "C2"})
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert len(response.json) == 2

@pytest.mark.official
def test_list_orders_by_status_api_matching(client):
    client.post('/api/orders', json={"order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"})
    client.post('/api/orders', json={"order_id": "S002", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"})
    response = client.get('/api/orders?status=pending')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['order_id'] == "S001"


# --- Learner-authored error tests ---

@pytest.mark.learner
def test_add_order_api_duplicate_returns_409(client):
    """Tests that posting a duplicate order_id returns 409."""
    order_data = {"order_id": "DUP001", "item_name": "Laptop", "quantity": 1, "customer_id": "C1"}
    client.post('/api/orders', json=order_data)
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 409
    assert "error" in response.json


@pytest.mark.learner
@pytest.mark.parametrize("payload", [
    {"order_id": "V001", "item_name": "Laptop", "quantity": 0, "customer_id": "C1"},
    {"order_id": "V001", "item_name": "Laptop", "quantity": 1, "customer_id": "C1", "status": "invalid"},
    {"order_id": "", "item_name": "Laptop", "quantity": 1, "customer_id": "C1"},
])
def test_add_order_api_invalid_payload_returns_400(client, payload):
    """Tests that invalid payloads return 400."""
    response = client.post('/api/orders', json=payload)
    assert response.status_code == 400
    assert "error" in response.json


@pytest.mark.learner
def test_update_order_status_api_invalid_status_returns_400(client):
    """Tests that PUT with invalid new_status returns 400."""
    client.post('/api/orders', json={"order_id": "UPD001", "item_name": "Laptop", "quantity": 1, "customer_id": "C1"})
    response = client.put('/api/orders/UPD001/status', json={"new_status": "invalid"})
    assert response.status_code == 400
    assert "error" in response.json


@pytest.mark.learner
def test_update_order_status_api_not_found_returns_404(client):
    """Tests that PUT on nonexistent order returns 404."""
    response = client.put('/api/orders/NONEXISTENT/status', json={"new_status": "shipped"})
    assert response.status_code == 404
    assert "error" in response.json


@pytest.mark.learner
def test_list_orders_api_invalid_status_returns_400(client):
    """Tests that GET /api/orders?status=invalid returns 400."""
    response = client.get('/api/orders?status=invalid')
    assert response.status_code == 400
    assert "error" in response.json


@pytest.mark.learner
def test_add_order_api_missing_keys_returns_400(client):
    """Tests that POST with missing required fields returns 400 with JSON error."""
    response = client.post('/api/orders', json={"order_id": "X"})
    assert response.status_code == 400
    assert "error" in response.json


@pytest.mark.learner
def test_update_order_status_api_missing_new_status_returns_400(client):
    """Tests that PUT without new_status key returns 400 with JSON error."""
    client.post('/api/orders', json={"order_id": "UPD002", "item_name": "Laptop", "quantity": 1, "customer_id": "C1"})
    response = client.put('/api/orders/UPD002/status', json={})
    assert response.status_code == 400
    assert "error" in response.json
