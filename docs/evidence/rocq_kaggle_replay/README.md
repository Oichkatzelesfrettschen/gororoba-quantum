# Fresh Rocq kernel replay on a Kaggle kernel

`result.json` preserves a historical Rocq 9.2 re-derivation away from the
build host: `scripts/rocq_kaggle_replay.py`, run
as the Kaggle CPU kernel `gororoba-rocq-replay` (version 3, run directory
results/kaggle/2026-10-16T085651Z-gororoba-rocq-replay), built OCaml 5.5.0
and Rocq 9.2.0 with opam from source, required `rocq --version` to equal
`docs/evidence/c881_exhaustive/toolchain.txt`, cloned open_gororoba at
7d95d228, and ran each replay script unchanged with `--folding`.

| Replay | Seconds | Result |
| --- | ---: | --- |
| `docs/evidence/formal_certificates/replay_rocq.sh` | 121 | compile, kernel and assumption receipts byte-identical for all three proofs |
| `docs/evidence/c881_exhaustive/replay_rocq.sh` | 33 | compile, kernel, assumptions and source identities pass |
| `docs/evidence/stiefel_witness/replay_rocq.sh` | 541 | compile, kernel, assumptions and source identities pass |
| `docs/evidence/folding_proofs/replay_rocq.sh` | 57 | six sources compile without warning, seven closed assumption queries, no axioms; complete stdout equaled the folding log retained with that run |
| TargetFlipN21 (AGENTS.md procedure) | 43 | no `Warning:` line in the complete compile output under `-w +all`; no axioms, no assumed positivity |

The toolchain build took 324 s for OCaml and 543 s for Rocq. The first three
replay scripts compare their fresh output with the retained
receipts byte for byte with `cmp`; for the folding bundle, which prints its
receipt, `rocq_kaggle_replay.py` compares the complete stdout with the
retained log, and every replay records each `Warning:` line of its complete
output (none here). The historical pass establishes that the receipts retained with that
execution matched its Rocq 9.2 output. Current CI checks the renewed Rocq 9.3
receipts described below. The c881 and
Stiefel source identities hold at both 7d95d228 and the earlier b977e43f.
[result-b977e43f.json](result-b977e43f.json)
is version 1 of the kernel at b977e43f, which passed the other four replays
before the folding bundle was re-pinned.

The ci.yml job `rocq-replay` runs the same driver on a GitHub runner with
`--rocq`, `--gororoba-root` and `--only`: the opam switch of
`ci/rocq_toolchain.pin` comes from a cache keyed on that file, open_gororoba
comes from `ci/fetch_open_gororoba.sh` at `ci/open_gororoba.pin`, and
`rocq --version` must still equal `toolchain.txt`. Its record is the
`rocq-replay` artifact of the run; these retained results stay the Kaggle
runs.

The current toolchain pins Rocq 9.3.0, OCaml 5.5.1 and independently
released Stdlib 9.2.0. Fresh local compilation and independent kernel
checking renew the bundle receipts; the historical Kaggle records retain
their original compiler identity. Independent bundles run concurrently
through `parallel.ordered_map`, capped by the detected CPU allowance and
`GOROROBA_WORKERS`, and records retain the selected bundle order.
Each replay creates separate temporary proof storage.
