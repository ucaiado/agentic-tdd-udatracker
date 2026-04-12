AI-Assisted TDD: Flask Order Tracker
==============================

This project is part of the [AI-Powered Software Engineer](https://www.udacity.com/course/ai-powered-software-engineer--nd770)
 program from Udacity. I implement a Flask-based order-tracking API following a
 strict **Test-Driven Development (TDD)** workflow, using Claude Code as an AI
 pair programmer throughout the red-green-refactor cycle.

The project covers two layers of implementation driven entirely by a pre-existing
 test suite. No code is written without a failing test first:
- **OrderTracker**: core business logic for adding, retrieving, and updating orders
- **REST API**: Flask endpoints that expose the OrderTracker to the frontend

The `.ai/` directory documents the AI collaboration workflow, including the TDD
 skill used to guide each red-green-refactor cycle.


### Install

Install Docker and Make in your machine, then build the Docker image:

```shell
$ make docker-build
```


### Run

In a terminal or command window, navigate to the top-level project directory
 `agentic-tdd-udatracker/` (that contains this README) and run the following
 commands.

**Run the Flask application:**
```shell
$ make run-app      # Access at http://localhost:5000
```

**Run tests:**
```shell
$ make test-unit    # Run OrderTracker unit tests
$ make test-api     # Run API integration tests
$ make test-all     # Run the full test suite
```


### Project Structure
```
agentic-tdd-udatracker/
├── src/
│   ├── backend/
│   │   ├── app.py                  # Flask application and API routes
│   │   ├── order_tracker.py        # Core business logic
│   │   ├── in_memory_storage.py    # In-memory storage backend
│   │   ├── requirements.txt
│   │   └── tests/
│   │       ├── test_order_tracker.py   # Unit tests for OrderTracker
│   │       └── test_api.py             # Integration tests for API endpoints
│   ├── frontend/
│   │   ├── index.html
│   │   ├── css/style.css
│   │   └── js/script.js
│   └── pytest.ini
├── .ai/
│   ├── CLAUDE.md                   # Project context and AI workflow instructions
│   └── skills/
│       └── tdd.md                  # TDD skill used with Claude Code
├── docs/
├── Dockerfile & docker-compose.yml
└── Makefile                        # Automation commands
```


### License
The contents of this repository are covered under the [MIT License](LICENSE).
