"""OrderTracker class encapsulating the core business logic for managing orders."""


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """

    VALID_STATUSES = {"pending", "processing", "shipped", "delivered", "cancelled"}

    def __init__(self, storage):
        required_methods = ["save_order", "get_order", "get_all_orders"]
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(
                    f"Storage object must implement a callable '{method}' method."
                )
        self.storage = storage

    def _validate_status(self, status: str):
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}': must be one of {sorted(self.VALID_STATUSES)}."
            )

    def _require_order_id(self, order_id: str):
        if not order_id:
            raise ValueError("Field 'order_id' must be a non-empty string.")

    def add_order(
        self,
        order_id: str,
        item_name: str,
        quantity: int,
        customer_id: str,
        status: str = "pending",
    ):
        """Add a new order, validating required fields and persisting it to storage."""
        for name, value in (
            ("order_id", order_id),
            ("item_name", item_name),
            ("customer_id", customer_id),
        ):
            if not value:
                raise ValueError(f"Field '{name}' must be a non-empty string.")
        if quantity <= 0:
            raise ValueError(
                f"Invalid quantity '{quantity}': must be a positive integer."
            )
        self._validate_status(status)
        if self.storage.get_order(order_id) is not None:
            raise ValueError(f"Order with ID '{order_id}' already exists.")
        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order)

    def get_order_by_id(self, order_id: str):
        """Return the order dict for the given id, or None if it does not exist."""
        self._require_order_id(order_id)
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        """Change the status of an existing order and persist the updated record."""
        self._require_order_id(order_id)
        self._validate_status(new_status)
        order = self.storage.get_order(order_id)
        if order is None:
            raise ValueError(f"Order with ID '{order_id}' not found.")
        updated = {**order, "status": new_status}
        self.storage.save_order(order_id, updated)
        return updated

    def list_all_orders(self):
        """Return a list with all stored orders."""
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        """Return only the orders whose status matches the given value."""
        self._validate_status(status)
        return [
            o for o in self.storage.get_all_orders().values() if o["status"] == status
        ]
