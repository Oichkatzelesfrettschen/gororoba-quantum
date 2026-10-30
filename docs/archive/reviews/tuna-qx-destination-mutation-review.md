Bounded PASS. The earlier type and per-gate regression gaps are closed. I found zero FATAL, SERIOUS, or SLOPPY findings within this scope.

The regression at [test_qi_tuna_qx_destination.py](../../../tests/scripts/test_qi_tuna_qx_destination.py) now independently mutates:

- Boolean backend ID.
- Floating-point qubit, shot, execution-time, and batch-job capacities.
- Boolean queue capacity.
- Non-list gate-set shape.
- Each required gate separately: `X`, `init`, `measure`, and `barrier`.

Each loop iteration changes one field, and the default arguments at [line 168](../../../tests/scripts/test_qi_tuna_qx_destination.py) bind that iteration’s filename and mutation, preventing late-binding cross-contamination.

The corresponding predicates at [qi_tuna_qx_destination.py](../../../scripts/qi_tuna_qx_destination.py) use exact integer checks, exact booleans, a list requirement, and a four-gate subset check. Read-only probes confirmed that every malformed type and every independently missing gate raises:

```text
backend snapshot differs from the historical case limits
```

Checks completed:

- All three `local hash binding list` hashes match staged and working bytes.
- The bound paths have zero unstaged differences and pass targeted `diff --check`.
- Exact manifest replay passed.
- Ruff check and formatting passed.
- Mypy passed.
- Direct execution of the checked-in mutation regression passed.
- Eleven independent read-only predicate probes passed.

The checks cover only local historical-snapshot validation and its regression strength. They do not authenticate the snapshot, inspect current provider capacity, establish fresh admission, or exercise credentials, provider APIs, submissions, uploads, simulator jobs, or filesystem writes.
