# Fresh Rocq kernel replay on a Kaggle kernel

Hosted CI carries no Rocq, so its gates verify the bytes of the retained
proof receipts rather than re-deriving them. `result.json` records a fresh
re-derivation away from the build host: `scripts/rocq_kaggle_replay.py`, run
as the Kaggle CPU kernel `gororoba-rocq-replay` (version 2, run directory
results/kaggle/2026-10-16T054628Z-gororoba-rocq-replay), built OCaml 5.5.0
and Rocq 9.2.0 with opam from source, required `rocq --version` to equal
`docs/evidence/c881_exhaustive/toolchain.txt`, cloned open_gororoba at
7d95d228, and ran each replay script unchanged with `--folding`.

| Replay | Seconds | Result |
| --- | ---: | --- |
| `docs/evidence/formal_certificates/replay_rocq.sh` | 123 | compile, kernel and assumption receipts byte-identical for all three proofs |
| `docs/evidence/c881_exhaustive/replay_rocq.sh` | 36 | compile, kernel, assumptions and source identities pass |
| `docs/evidence/stiefel_witness/replay_rocq.sh` | 563 | compile, kernel, assumptions and source identities pass |
| `docs/evidence/folding_proofs/replay_rocq.sh` | 55 | six sources compile without warning, seven closed assumption queries, no axioms, log byte-identical |
| TargetFlipN21 (AGENTS.md procedure) | 34 | no warning under `-w +all`; no axioms, no assumed positivity |

The toolchain build took 346 s for OCaml and 522 s for Rocq. Each replay
script compares its fresh output with the retained receipt byte for byte, so
a pass means the receipts the CI gates check are what Rocq 9.2 produces from
the retained sources today. The c881 and Stiefel source identities hold at
both 7d95d228 and the earlier b977e43f. [result-b977e43f.json](result-b977e43f.json)
is version 1 of the kernel at b977e43f, which passed the other four replays
before the folding bundle was re-pinned.
