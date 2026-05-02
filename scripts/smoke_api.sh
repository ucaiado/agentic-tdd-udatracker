#!/usr/bin/env bash
# Smoke test for the OrderTracker API. Assumes the app is running at $BASE_URL.
#
# Usage:
#   make run-app          # in another terminal
#   ./scripts/smoke_api.sh
#
# Each case prints the HTTP status and a PASS/FAIL line. Exits 1 if any case fails.
# Uses a unique id prefix per run so the script does not collide with existing data
# in the in-memory storage.

set -u

BASE_URL="${BASE_URL:-http://localhost:5000}"
PREFIX="SMOKE_$(date +%s)"
FAILED=0

# --- helpers ---

assert_status() {
    local name="$1" expected="$2" actual="$3"
    if [[ "$actual" == "$expected" ]]; then
        echo "  PASS  $name (status $actual)"
    else
        echo "  FAIL  $name (expected $expected, got $actual)"
        FAILED=1
    fi
}

# Run a curl request and capture body + status into two temp files.
# Echoes the status to stdout so callers can consume it with $(...).
curl_capture() {
    local method="$1" url="$2" data="${3:-}"
    local body_file="$4"
    local args=(-s -o "$body_file" -w "%{http_code}" -X "$method" "$url")
    if [[ -n "$data" ]]; then
        args+=(-H "Content-Type: application/json" -d "$data")
    fi
    curl "${args[@]}"
}

# --- cases ---

echo
echo "== OrderTracker API smoke @ $BASE_URL =="
echo "   id prefix: $PREFIX"
echo

BODY=$(mktemp)
trap 'rm -f "$BODY"' EXIT

ORDER_ID="${PREFIX}_A"

# 1. POST /api/orders — happy path → 201
STATUS=$(curl_capture POST "$BASE_URL/api/orders" \
    "{\"order_id\":\"$ORDER_ID\",\"item_name\":\"Laptop\",\"quantity\":1,\"customer_id\":\"C1\"}" \
    "$BODY")
assert_status "POST new order" 201 "$STATUS"

# 2. GET /api/orders/<id> — happy path → 200
STATUS=$(curl_capture GET "$BASE_URL/api/orders/$ORDER_ID" "" "$BODY")
assert_status "GET order by id" 200 "$STATUS"

# 3. GET /api/orders/<id> — not found → 404
STATUS=$(curl_capture GET "$BASE_URL/api/orders/${PREFIX}_NONE" "" "$BODY")
assert_status "GET unknown order returns 404" 404 "$STATUS"

# 4. PUT /api/orders/<id>/status — happy path → 200
STATUS=$(curl_capture PUT "$BASE_URL/api/orders/$ORDER_ID/status" \
    '{"new_status":"shipped"}' "$BODY")
assert_status "PUT update status" 200 "$STATUS"

# 5. GET /api/orders — list all → 200
STATUS=$(curl_capture GET "$BASE_URL/api/orders" "" "$BODY")
assert_status "GET list all" 200 "$STATUS"

# 6. GET /api/orders?status=shipped — filtered → 200
STATUS=$(curl_capture GET "$BASE_URL/api/orders?status=shipped" "" "$BODY")
assert_status "GET list filtered" 200 "$STATUS"

# 7. POST /api/orders — duplicate id → 409
STATUS=$(curl_capture POST "$BASE_URL/api/orders" \
    "{\"order_id\":\"$ORDER_ID\",\"item_name\":\"Laptop\",\"quantity\":1,\"customer_id\":\"C1\"}" \
    "$BODY")
assert_status "POST duplicate id returns 409" 409 "$STATUS"

# 8. POST /api/orders — invalid quantity → 400
STATUS=$(curl_capture POST "$BASE_URL/api/orders" \
    "{\"order_id\":\"${PREFIX}_BAD\",\"item_name\":\"Laptop\",\"quantity\":0,\"customer_id\":\"C1\"}" \
    "$BODY")
assert_status "POST invalid quantity returns 400" 400 "$STATUS"

# 9. PUT /api/orders/<id>/status — invalid new_status → 400
STATUS=$(curl_capture PUT "$BASE_URL/api/orders/$ORDER_ID/status" \
    '{"new_status":"nope"}' "$BODY")
assert_status "PUT invalid status returns 400" 400 "$STATUS"

# 10. PUT /api/orders/<id>/status — unknown order → 404
STATUS=$(curl_capture PUT "$BASE_URL/api/orders/${PREFIX}_NONE/status" \
    '{"new_status":"shipped"}' "$BODY")
assert_status "PUT unknown order returns 404" 404 "$STATUS"

# 11. GET /api/orders?status=<invalid> — invalid filter → 400
STATUS=$(curl_capture GET "$BASE_URL/api/orders?status=nope" "" "$BODY")
assert_status "GET invalid status filter returns 400" 400 "$STATUS"

echo
if [[ "$FAILED" -eq 0 ]]; then
    echo "All smoke cases passed."
    exit 0
else
    echo "Smoke test failed."
    exit 1
fi
