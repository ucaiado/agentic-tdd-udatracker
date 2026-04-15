---
name: tdd
description: Test-driven development with a strict red-green-refactor loop using pytest. Invoke this skill whenever adding or changing behavior in OrderTracker (`src/backend/order_tracker.py`) or the Flask API (`src/backend/app.py`) — including new methods, new endpoints, bug fixes, or edge-case handling. Consult it before writing any test or production code in this repo, even for small changes, since the whole project is graded on TDD discipline.
---

# Test-Driven Development (pytest)

## Why this skill exists

This repo is a capstone for demonstrating TDD discipline. The `git log` itself
is evidence — a reviewer should see a rhythm of RED → GREEN → (REFACTOR)
commits. Writing production code before a failing test, or writing many tests
in a batch, breaks that story even when the final code works.

## Philosophy

**Core principle**: tests verify behavior through public interfaces, not
implementation details. Code can change entirely; tests shouldn't.

**Good tests** exercise real code paths through public APIs. They describe
*what* the system does, not *how*. `test_add_order_rejects_duplicate_id` tells
you exactly what capability exists, and it survives refactors because it
doesn't care about internal structure.

**Bad tests** couple to implementation — mocking internal collaborators,
asserting on private attributes, checking `call_args` positionally when the
real contract is the stored order shape. Warning sign: the test breaks when
you refactor even though behavior is unchanged.

## Anti-pattern: horizontal slices

Do not write all the tests first, then fill in all the code. That treatment
produces tests for *imagined* behavior — they lock in shape before you
understand the design, and they often pass when behavior is actually broken
because you never saw them go red against real code.

The correct approach is vertical slices (tracer bullets): one test → one
implementation → repeat.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1 → impl1
  RED→GREEN: test2 → impl2
  RED→GREEN: test3 → impl3
```

The rationale: each small red gives you feedback about whether the behavior
you imagined is the one that actually matters. You learn the design by
writing it, one decision at a time.

## Workflow

### 1. Plan the method or endpoint

Before any code:

- Confirm the public interface: method signature, or endpoint URL + method +
  request/response shape.
- List the behaviors to cover, ordered happy path → edge cases. Use the
  project rubric as the source of truth (see `docs/README.md` for context).
  A good heuristic: one rubric bullet ≈ one test.
- Share the plan and wait for user approval before starting cycles.

You cannot test everything; pick the behaviors that matter most. Ask the user
to prioritize if the list is long.

### 2. Tracer bullet

Write ONE test that confirms ONE behavior end-to-end:

```
RED:   write the test → run it → see it fail for the right reason
GREEN: write the minimum code → run it → see the test pass
```

"For the right reason" is the hinge. After running RED, read the failure
message and confirm it matches what the test claims to check. A test that
fails because of an import error, typo, or fixture mistake is not a real
red — fix the mistake and re-run until the failure reflects the behavior you
intended to assert.

### 3. Incremental loop

For each remaining behavior:

```
RED:   next test → fails for the right reason
GREEN: minimum code to pass → passes
```

Rules, and why they matter:

- **One test at a time** — multiple tests in one RED step means you lose the
  one-to-one mapping between behavior and implementation, and you're back to
  horizontal slicing.
- **One behavior per test** — if a test name needs "and" to describe it, it
  is probably two tests. Splitting them makes failure messages tell you
  exactly what broke.
- **Only enough code to pass the current test** — don't add fields,
  validations, or branches that no test requires yet; the next test will
  motivate them.
- **Test observable behavior, not call shapes** — prefer asserting on the
  order returned or stored over asserting exact positional args on a mock.

### 4. Refactor

Only once every test is green, look for concrete improvements. For this
project, likely candidates:

- Extract a helper for building the order dict if `add_order` grows.
- Centralize status validation if multiple methods need it.
- Pull error-response JSON shaping into a Flask error handler instead of
  repeating it in each route.

Run the full test suite after each refactor step. If a test goes red,
revert — refactor means changing structure without changing behavior, so a
red test means the change was not really a refactor.

**Never refactor while any test is red.** Get back to green first. Stop
refactoring when no duplication is obvious and every module reads clearly;
do not invent abstractions to prepare for features the rubric does not ask
for.

## Per-cycle checklist

Run through this every cycle before committing:

```
[ ] Test describes behavior, not implementation
[ ] Test uses the public interface only
[ ] Test name describes a single behavior (no "and")
[ ] RED was seen and the failure message matched the intent
[ ] GREEN code is the minimum to satisfy this test
[ ] No speculative features introduced
```

## Commit discipline

One commit per state transition so the history reads as a TDD log:

- `test: add failing test for <behavior>` — the RED commit
- `feat: implement <behavior>` — the GREEN commit
- `refactor: <what and why>` — optional, only when all tests pass

If test and implementation land together in one commit, the RED state is
lost from history and the TDD evidence weakens. Keep them separate.

For a bug fix, the same shape applies: first a `test:` commit with a failing
test that reproduces the bug, then a `fix:` commit making it pass.

## AAA pattern

Each test has three clear sections:

```python
def test_add_order_defaults_status_to_pending(order_tracker, mock_storage):
    # Arrange
    mock_storage.get_order.return_value = None

    # Act
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # Assert — check the saved order, not the exact call shape
    saved_call = mock_storage.save_order.call_args
    saved_order = saved_call.kwargs.get("order_data") or saved_call.args[1]
    assert saved_order["status"] == "pending"
    assert saved_order["order_id"] == "ORD001"
```

The assertion checks what matters (the order saved has the right fields)
rather than the exact positional shape of the call, so the test survives
small signature refactors in the storage interface.

## Guardrails specific to this repo

- **Do not modify `src/backend/tests/test_api.py`.** It is the graded
  specification for the API layer. Your job is to make it pass by
  implementing `app.py`.
- **Do not modify `src/backend/in_memory_storage.py`.** It is provided.
- **Fixtures already exist** in `test_order_tracker.py`: `mock_storage` and
  `order_tracker`. Use them; do not reinvent.
- **Business logic lives in `OrderTracker`, not in `app.py`.** Flask routes
  should be thin delegators.

## Project structure

```
src/backend/
├── order_tracker.py            # business logic (TDD target)
├── app.py                      # Flask API (TDD target)
├── in_memory_storage.py        # provided — do not modify
└── tests/
    ├── test_order_tracker.py   # learner-authored unit tests
    └── test_api.py             # pre-written integration tests — do not modify
```

- Test files: `test_` prefix.
- Test functions: `test_` prefix, named after the behavior being checked.
- Shared fixtures live at the top of `test_order_tracker.py`; introduce a
  `conftest.py` only if fixtures need to be shared across test files.

## Test markers: `official` vs `learner`

Two test categories coexist in this project:

- `@pytest.mark.official` — integration tests provided by Udacity in
  `test_api.py`. Their assertions and logic are the graded specification;
  marking is categorization metadata only and does not count as modification.
- `@pytest.mark.learner` — tests authored during this project: all unit tests
  in `test_order_tracker.py` and any additional integration tests (e.g.
  covering 400/409 error paths not in the provided suite).

Markers are registered in `src/pytest.ini` and applied per function with
a decorator above each test (not at module level), so learner-authored tests
can live alongside the official ones in the same file without a global tag
misclassifying them.

Typical usage:

```bash
pytest -m learner        # only our tests — fast feedback during TDD cycles
pytest -m official       # only the provided suite — sanity check
pytest                   # everything
```

Any new test function you write must carry `@pytest.mark.learner`. Do not
add or remove marks on existing `official` tests.

## Running tests

```bash
make test-unit    # OrderTracker unit tests
make test-api     # API integration tests
make test-all     # full suite
```

All commands run inside the project's Docker image; do not run `pytest`
directly on the host since the environment is pinned in the container.

## When you feel stuck

A few diagnostic questions if a cycle is not moving:

- Is the current test checking one behavior, or several smuggled together?
  Split it.
- Is the failure message telling you what you expected? If not, the test
  is wrong before the code is wrong — fix the test.
- Did you jump ahead and write more code than the test required? Delete the
  extra code; the next RED will ask for it legitimately.
- Are you mocking something you control directly? Prefer real objects in
  unit tests when the dependency is trivial; reserve mocks for boundaries
  (storage, external services).
