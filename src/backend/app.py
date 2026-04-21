"""Flask application exposing the OrderTracker REST API and static frontend."""

from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder="../frontend")
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


@app.route("/")
def serve_index():
    """Serve the frontend entry point."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static assets from the frontend directory."""
    return send_from_directory(app.static_folder, filename)


@app.route("/api/orders", methods=["POST"])
def add_order_api():
    """Create a new order from JSON payload."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400
    try:
        order_tracker.add_order(
            order_id=data.get("order_id", ""),
            item_name=data.get("item_name", ""),
            quantity=data.get("quantity", 0),
            customer_id=data.get("customer_id", ""),
            status=data.get("status", "pending"),
        )
    except ValueError as e:
        msg = str(e)
        if "already exists" in msg:
            return jsonify({"error": msg}), 409
        return jsonify({"error": msg}), 400
    order = order_tracker.get_order_by_id(data["order_id"])
    return jsonify(order), 201


@app.route("/api/orders/<string:order_id>", methods=["GET"])
def get_order_api(order_id):
    """Return the order with the given id or 404 if not found."""
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        return jsonify({"error": f"Order with ID '{order_id}' not found."}), 404
    return jsonify(order), 200


@app.route("/api/orders/<string:order_id>/status", methods=["PUT"])
def update_order_status_api(order_id):
    """Update the status of an existing order."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400
    try:
        updated = order_tracker.update_order_status(order_id, data.get("new_status", ""))
    except ValueError as e:
        msg = str(e)
        if "not found" in msg:
            return jsonify({"error": msg}), 404
        return jsonify({"error": msg}), 400
    return jsonify(updated), 200


@app.route("/api/orders", methods=["GET"])
def list_orders_api():
    """List all orders, optionally filtered by status query param."""
    status = request.args.get("status")
    if status:
        try:
            orders = order_tracker.list_orders_by_status(status)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    else:
        orders = order_tracker.list_all_orders()
    return jsonify(orders), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
