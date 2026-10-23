# Provider API, calibration and billing audit

The [capture manifest](index.json) binds read-only observations from 22 October 2026. The IQM reads
began at 20:53:53.983284 UTC and ended at 20:54:08.939870 UTC; the manifest records the later
Open Quantum and Quandela reads' overall completion. The reads form a sequence, not an atomic snapshot.
The capture created neither a circuit upload, preparation, provider job nor booking.

## Authority and replay

| Artifact | Establishes | Boundary |
|---|---|---|
| [iqm.json](iqm.json) | General REST schema, GraphQL schema, per-QPU REST schemas, limits/prices, calibration-pinned architectures and metrics, account credit | Job execution and billing settlement remain unexercised |
| [Open Quantum catalogue](open-quantum/catalogue.json) | Six complete constraint documents, configuration schemas, token-reachable account balances and job count, vendor tool schemas | Catalogue status differs from admission and a guaranteed reservation |
| [39 pricing estimates](open-quantum/estimates.json) | Circuit-free sampled quotes under both offered plans and priorities | A concrete uploaded program still requires its own quote and approval |
| [Live tariff](open-quantum/pricing.json), [page/chunk identities](open-quantum/pricing-sources.json) | Live pricing-page rows and calculator/source statements; sampled estimates match the ceiling rule | Neither a universal credit/dollar exchange rate nor a multi-circuit billing contract |
| [quandela.json](quandela.json) | Explorer and detailed processor status, token concurrency and consumed credit totals | Token usage is not account-wide remaining credit; hidden offer fees remain unknown |
| [packing.json](packing.json) | Connected disjoint four-qubit template witnesses attaining width bounds | No quality, physical concurrency, independence, native compilation or throughput guarantee |

Capture into a new directory using the documented credential environment variables and the Open Quantum interpreter:

```sh
export PYTHON="$OQ_PYTHON"
"$PYTHON" scripts/provider_api_audit.py --capture NEW_AUDIT_DIRECTORY
```

Replay the retained bytes and graph witnesses with the repository's pinned runtime:

```sh
"$PYTHON" scripts/provider_api_audit.py --check docs/evidence/provider-api-audit
"$PYTHON" scripts/oq_platform.py check docs/evidence/provider-api-audit/open-quantum
"$PYTHON" scripts/provider_patch_packing.py docs/evidence/provider-api-audit --check docs/evidence/provider-api-audit/packing.json
```

The manifest binds API artifacts. The independently generated packing record binds its two source files and
records NetworkX/SciPy versions. Its integer-program solver supplies a feasible witness; attaining the independent
floor(width/4) bound proves maximal count for the connected four-qubit template without relying on solver optimality.
The checker validates retained membership, source hashes, disjointness, connectivity, role edges and width bounds.
It does not require a new solver run to select the same member of a tied solution set.
The first two-matching construction misses valid three-leaf stars; the connected-set search includes those stars.

## Findings and repair boundary

1. IQM's general REST schema matches the earlier retained schema. All six catalogue entries report station
   control 50.0.0. The old hardware table remains a dated snapshot, rather than the live status authority.
2. IQM PAYG rounds compilation plus execution upward per job. Request rate-limit units are unrelated to compute credits.
3. IQM architecture and metrics use a resolved immutable calibration identity. The MCP accepts an explicit identity
   and rejects a returned mismatch; `_observation` separates retrieval time from calibration creation time.
4. The repository Open Quantum adapter preserves physical width and maximum job width separately, follows filtered
   pagination, and raises MCP errors for vendor JSON error payloads. The installed vendor package remains unchanged.
   The adapter delegates preparation and submission to the same vendor tools and retains their spending checks.
5. The source graph witnesses fit 13 four-qubit cells on Emerald, five on Garnet, nine on Forte-1, 26 on Rigetti,
   and three on IBEX. IBEX's catalogue refuses jobs. Sirius needs MOVE/resonator routing and is outside this direct-CZ template.
6. The Quandela token report records 56 jobs: five Ascella jobs consume zero free credits, 17 Belenos simulator jobs
   consume 16, and 34 Belenos QPU jobs consume 32.46742. Purchased-credit consumption is zero in those rows.
   A zero shot tariff or zero purchased-credit field therefore does not establish zero total cost.
7. Quandela's detailed Belenos record reports calibration while its public list reports available. Preserve the
   disagreement. Its transport/MCP/acquisition repairs remain under the separate `quandela-mcp-contract-repairs` owner.

Fresh SDK stdio observations at 21:03 UTC discovered 13 Open Quantum tools and preserved Rigetti's 108 physical /
107 maximum job qubits. The IQM session discovered 12 tools and used one Garnet calibration identity for both
architecture and metrics. A credential-free synthetic vendor error produced `isError=true` through stdio.
The IQM settings forward reference is rebuilt after SDK import; its strict warning-as-error import regression passes.

## Open evidence obligations

- IQM native compiler availability, execution ordering, reset/repetition time and a defensible total billed-time
  bound must close before the proposed acquisition can use credits. The documented `iqm-python` environment was
  absent from the inspected local executable paths; installation metadata is not executable validation.
- The Open Quantum constraint advertises 1024 circuits, but the inspected preparation interface accepts one input
  upload. The audit establishes neither a multi-circuit upload representation nor how its circuit multiplicity
  is charged. Every proposed broker job therefore contains one packed reference program.
- IQM failed/interrupted-job charges and slot charging interactions require explicit provider evidence; the
  current token lacks slot-management scope and the current balance cannot afford the listed slots.
- Historical Open Quantum refunds lack an account measurement: the account lists zero jobs. Documentation states
  the refund rule; a circuit-free quote cannot validate settlement.
- Quandela job-token access does not expose every offer fee or the remaining account balance. The report leaves
  those fields unknown and requests a read-only portal/support record rather than treating them as zero.
- Ordinary hardware and its conventional complex encodings cannot decide a fundamental hypercomplex scalar field.
  The [run case](../../design/packed-pauli-response-current-balance.md) targets an operational response question.
