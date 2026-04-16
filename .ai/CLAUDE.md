# CLAUDE.md — AI Collaboration Guide

This file tells Claude Code how to work on this repo. It is the single source of
truth for project context, workflow conventions, and guardrails. Read it before
making changes.

## Project Context

This is the capstone exercise for Udacity's **AI-Powered Software Engineer**
program — a Flask-based Order Tracker built under a strict TDD discipline with
Claude Code acting as an AI pair programmer.

- The assignment text lives in [`docs/README.md`](../docs/README.md) — read it
  for the full scenario, cycle examples (`add_order`, duplicate-ID check) and
  the operations CRUD table. Treat it as canonical context for what the app
  must do.
- The learner-facing reflection is written to `src/backend/README.md`.

### Application Layers

- `src/backend/order_tracker.py` — **business logic** (to implement via TDD)
- `src/backend/app.py` — **Flask API** (endpoints delegate to `OrderTracker`)
- `src/backend/in_memory_storage.py` — already implemented; injected into
  `OrderTracker`
- `src/backend/tests/test_order_tracker.py` — **unit tests** (written by the
  learner during TDD cycles; fixtures already provided)
- `src/backend/tests/test_api.py` — **integration tests** (pre-written; do
  not modify)
- `scripts/smoke_api.sh` — curl-based API smoke test for end-to-end verification

### Public Interface of `OrderTracker`

- `add_order(order_id, item_name, quantity, customer_id, status="pending")`
- `get_order_by_id(order_id)`
- `update_order_status(order_id, new_status)`
- `list_all_orders()`
- `list_orders_by_status(status)`

### API Endpoints

- `POST /api/orders` — create
- `GET /api/orders/<order_id>` — read one
- `PUT /api/orders/<order_id>/status` — update status
- `GET /api/orders` (with optional `?status=` filter) — list

## Workflow

### TDD Discipline

Use the [`skills/tdd.md`](skills/tdd.md) skill for every change to business
logic or API behavior. **Vertical slices only** — one test → minimum code to
pass → next test. Never write all tests upfront and then fill in code.

The loop is:

1. **RED** — write one failing test that describes one behavior
2. **GREEN** — write the minimum code needed to make it pass
3. **REFACTOR** — only after green, look for duplication or design improvements
   without changing behavior; run tests after each refactor step

### Order of Work

1. Implement and unit-test `OrderTracker` (one cycle per behavior)
2. Only after all unit tests pass, implement Flask endpoints guided by
   `test_api.py`
3. Run the full suite (`make test-all`) and verify the frontend manually

### Commit Conventions

- `test: <message>` — adds a failing test (RED)
- `feat: <message>` — implements code to make the test pass (GREEN)
- `refact: <message>` — restructures without behavior change (only when all
  tests pass)
- `chore: <message>` — tooling, docs, CI
- One commit per TDD cycle is preferred so the history reads as a sequence of
  red → green → (refactor) steps.

### Test Commands

Run from repo root:

```bash
make test-unit     # OrderTracker unit tests
make test-api      # API integration tests
make test-all      # Full suite
make smoke-api     # Curl smoke script against a running app
```

All commands use Docker (`docker-compose run --rm udatracker ...`). Do not
bypass the container for test runs — the environment is pinned there.

### Linting

```bash
make lint-files LINT_FILE=src/backend/order_tracker.py
```

Runs `ruff format`, `ruff check --fix`, then `pylint`.

## Test Markers

All test functions carry a pytest marker:

- `@pytest.mark.official` — provided by Udacity in `test_api.py`. Assertions
  and logic are frozen; only the decorator above each function is added for
  categorization.
- `@pytest.mark.learner` — anything authored in this project.

Run subsets with `pytest -m learner` or `pytest -m official`. Markers are
registered in `src/pytest.ini`.

## Guardrails

- Do not modify **assertions or logic** in `src/backend/tests/test_api.py` —
  it is the graded specification for the API layer. Adding
  `@pytest.mark.official` above each existing function is allowed (metadata
  only). New learner-authored tests may live in the same file, marked
  `@pytest.mark.learner`.
- Do not modify `src/backend/in_memory_storage.py` — it is provided.
- Keep business logic out of `app.py`; endpoints should be thin delegators to
  `OrderTracker`.
- Do not introduce persistence, auth, or other features outside the rubric
  unless explicitly requested.
- Match existing code style; prefer clarity over cleverness. PEP 8, type hints
  where they aid readability.

## What NOT to Do

- No horizontal slicing (all tests first, then all code).
- No over-engineering (frameworks, ORMs, dependency-injection containers).
- No speculative endpoints or methods not in the rubric.
- No logging/print debugging left in committed code.
