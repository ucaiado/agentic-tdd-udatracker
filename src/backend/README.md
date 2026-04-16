# Backend Reflection

- **Status validation centralized after real duplication appeared.** Three methods
  ended up inlining the same set of allowed statuses. A post-Part 1 refactor
  extracted `VALID_STATUSES` and a `_validate_status` helper, keeping the rule
  in one place without anticipating it before the duplication was real.
- **`update_order_status` is fail-fast and non-mutating.** The new status is
  validated before touching storage, and the updated record is built with a
  dict spread (`{**order, "status": new_status}`) so the object returned by
  `get_order` is never mutated in place.
- **Several RED cycles passed immediately.** Earlier green steps had already
  satisfied later contracts — `get_order_by_id` returning `None` by
  delegation, or `list_all_orders` returning `[]` for an empty storage. Those
  tests were kept as executable documentation of the contract.
- **Next step.** Add `DELETE /api/orders/<id>` and swap the in-memory storage
  for SQLite so restarts do not lose state.
