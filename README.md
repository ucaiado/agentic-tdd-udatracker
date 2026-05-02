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

Three files document how the project was built. `.ai/CLAUDE.md` holds the
 workflow contract for the repo and the guardrails (what Claude can and cannot
 touch). `.ai/skills/tdd.md` is a self-contained skill that guides the
 red-green-refactor loop without depending on any personal setup. The commit
 log is organized to mirror the TDD cycle, with `test` commits introducing a
 failing test, `feat` commits adding the minimal code to make it pass, and
 `refact` commits extracting shared structure when real duplication appeared.
 Running `git log --reverse --oneline` replays the full trajectory one cycle
 at a time.


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
$ make smoke-api    # Run curl smoke script against a running app
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
│   │   ├── README.md               # Design reflection and next steps
│   │   └── tests/
│   │       ├── test_order_tracker.py   # Unit tests for OrderTracker
│   │       └── test_api.py             # Integration tests for API endpoints
│   ├── frontend/
│   │   ├── index.html
│   │   ├── css/style.css
│   │   └── js/script.js
│   └── pytest.ini
├── scripts/
│   └── smoke_api.sh                # Curl-based API smoke test
├── .ai/
│   ├── CLAUDE.md                   # Project context and AI workflow instructions
│   └── skills/
│       └── tdd.md                  # TDD skill used with Claude Code
├── docs/
├── Dockerfile & docker-compose.yml
└── Makefile                        # Automation commands
```


### Reflection

A short write-up of design decisions, testing insights, and next steps lives
in [`src/backend/README.md`](src/backend/README.md).


### License
The contents of this repository are covered under the [MIT License](LICENSE).
