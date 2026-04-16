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
