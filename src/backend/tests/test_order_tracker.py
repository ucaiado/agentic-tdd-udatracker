import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- Learner-authored tests ---
#

@pytest.mark.learner
def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()


@pytest.mark.learner
def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")


@pytest.mark.learner
@pytest.mark.parametrize("quantity", [0, -1])
def test_add_order_rejects_non_positive_quantity(order_tracker, mock_storage, quantity):
    """Tests that adding an order with quantity <= 0 raises a ValueError."""
    with pytest.raises(ValueError, match="quantity"):
        order_tracker.add_order("ORD002", "Laptop", quantity, "CUST001")

    mock_storage.save_order.assert_not_called()


@pytest.mark.learner
@pytest.mark.parametrize("bad_status", ["unknown", "ready", ""])
def test_add_order_rejects_invalid_initial_status(order_tracker, mock_storage, bad_status):
    """Tests that an invalid initial status raises ValueError."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.add_order("ORD004", "Laptop", 1, "CUST001", status=bad_status)

    mock_storage.save_order.assert_not_called()


# --- get_order_by_id ---

@pytest.mark.learner
def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    """Tests that get_order_by_id returns the order dict when it exists."""
    stored_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = stored_order

    result = order_tracker.get_order_by_id("ORD001")

    mock_storage.get_order.assert_called_once_with("ORD001")
    assert result == stored_order


@pytest.mark.learner
def test_get_order_by_id_returns_none_when_not_found(order_tracker, mock_storage):
    """Tests that get_order_by_id returns None for a non-existent order."""
    result = order_tracker.get_order_by_id("NONEXISTENT")

    mock_storage.get_order.assert_called_once_with("NONEXISTENT")
    assert result is None


@pytest.mark.learner
def test_get_order_by_id_rejects_empty_id(order_tracker, mock_storage):
    """Tests that get_order_by_id raises ValueError for empty order_id."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.get_order_by_id("")

    mock_storage.get_order.assert_not_called()


# --- list_all_orders ---

@pytest.mark.learner
def test_list_all_orders_returns_all(order_tracker, mock_storage):
    """Tests that list_all_orders returns a list of all stored orders."""
    orders = {
        "ORD001": {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"},
        "ORD002": {"order_id": "ORD002", "item_name": "Mouse", "quantity": 2, "customer_id": "CUST002", "status": "shipped"},
    }
    mock_storage.get_all_orders.return_value = orders

    result = order_tracker.list_all_orders()

    assert isinstance(result, list)
    assert len(result) == 2
    assert orders["ORD001"] in result
    assert orders["ORD002"] in result


@pytest.mark.learner
def test_list_all_orders_returns_empty_list_when_no_orders(order_tracker, mock_storage):
    """Tests that list_all_orders returns an empty list when storage is empty."""
    result = order_tracker.list_all_orders()

    assert result == []


# --- list_orders_by_status ---

@pytest.mark.learner
def test_list_orders_by_status_filters_correctly(order_tracker, mock_storage):
    """Tests that list_orders_by_status returns only orders matching the status."""
    orders = {
        "ORD001": {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"},
        "ORD002": {"order_id": "ORD002", "item_name": "Mouse", "quantity": 2, "customer_id": "CUST002", "status": "shipped"},
        "ORD003": {"order_id": "ORD003", "item_name": "Keyboard", "quantity": 1, "customer_id": "CUST003", "status": "pending"},
    }
    mock_storage.get_all_orders.return_value = orders

    result = order_tracker.list_orders_by_status("pending")

    assert len(result) == 2
    assert all(o["status"] == "pending" for o in result)


@pytest.mark.learner
def test_list_orders_by_status_returns_empty_when_no_match(order_tracker, mock_storage):
    """Tests that list_orders_by_status returns empty list when no orders match."""
    orders = {
        "ORD001": {"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001", "status": "pending"},
    }
    mock_storage.get_all_orders.return_value = orders

    result = order_tracker.list_orders_by_status("shipped")

    assert result == []


@pytest.mark.learner
@pytest.mark.parametrize("bad_status", ["unknown", "ready", ""])
def test_list_orders_by_status_rejects_invalid_status(order_tracker, mock_storage, bad_status):
    """Tests that list_orders_by_status raises ValueError for invalid status."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.list_orders_by_status(bad_status)

    mock_storage.get_all_orders.assert_not_called()


@pytest.mark.learner
@pytest.mark.parametrize("order_id,item_name,customer_id", [
    ("", "Laptop", "CUST001"),
    ("ORD003", "", "CUST001"),
    ("ORD003", "Laptop", ""),
])
def test_add_order_rejects_empty_required_field(
    order_tracker, mock_storage, order_id, item_name, customer_id
):
    """Tests that empty required string fields raise ValueError."""
    with pytest.raises(ValueError):
        order_tracker.add_order(order_id, item_name, 1, customer_id)

    mock_storage.save_order.assert_not_called()


# --- update_order_status ---

@pytest.mark.learner
def test_update_order_status_happy_path(order_tracker, mock_storage):
    """Tests that update_order_status changes and persists the new status."""
    existing_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing_order

    result = order_tracker.update_order_status("ORD001", "shipped")

    assert result["status"] == "shipped"
    assert result["order_id"] == "ORD001"
    mock_storage.save_order.assert_called_once()
    saved_order = mock_storage.save_order.call_args[0][1]
    assert saved_order["status"] == "shipped"


@pytest.mark.learner
@pytest.mark.parametrize("bad_status", ["unknown", "ready", ""])
def test_update_order_status_rejects_invalid_status(order_tracker, mock_storage, bad_status):
    """Tests that an invalid new_status raises ValueError before reading storage."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("ORD001", bad_status)

    mock_storage.get_order.assert_not_called()


@pytest.mark.learner
def test_update_order_status_raises_for_nonexistent_order(order_tracker, mock_storage):
    """Tests that updating a non-existent order raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        order_tracker.update_order_status("NONEXISTENT", "shipped")


@pytest.mark.learner
def test_update_order_status_rejects_empty_order_id(order_tracker, mock_storage):
    """Tests that update_order_status raises ValueError for empty order_id."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.update_order_status("", "shipped")

    mock_storage.get_order.assert_not_called()
