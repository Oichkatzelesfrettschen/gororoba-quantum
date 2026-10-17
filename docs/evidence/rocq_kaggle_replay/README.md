# Fresh Rocq kernel replay on a Kaggle kernel

Hosted CI carries no Rocq, so its gates verify the bytes of the retained
proof receipts rather than re-deriving them. `result.json` records a fresh
re-derivation away from the build host: `scripts/rocq_kaggle_replay.py`, run
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
| `docs/evidence/folding_proofs/replay_rocq.sh` | 57 | six sources compile without warning, seven closed assumption queries, no axioms; complete stdout equals `folding_proofs/rocq_replay.log` |
| TargetFlipN21 (AGENTS.md procedure) | 43 | no `Warning:` line in the complete compile output under `-w +all`; no axioms, no assumed positivity |

The toolchain build took 324 s for OCaml and 543 s for Rocq. The first three
replay scripts compare their fresh output with the retained
receipts byte for byte with `cmp`; for the folding bundle, which prints its
receipt, `rocq_kaggle_replay.py` compares the complete stdout with the
retained log, and every replay records each `Warning:` line of its complete
output (none here). A pass therefore means the receipts the CI gates check
are what Rocq 9.2 produces from the retained sources today. The c881 and
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
