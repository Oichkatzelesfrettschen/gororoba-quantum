# Fresh Rocq kernel replay on a Kaggle kernel

Hosted CI carries no Rocq, so its gates verify the bytes of the retained
proof receipts rather than re-deriving them. `result.json` records a fresh
re-derivation away from the build host: `scripts/rocq_kaggle_replay.py`, run
as the Kaggle CPU kernel `gororoba-rocq-replay` (run directory under
results/kaggle/), built OCaml 5.5.0 and Rocq 9.2.0 with opam from source,
required `rocq --version` to equal `docs/evidence/c881_exhaustive/toolchain.txt`,
cloned open_gororoba at b977e43f, and ran each replay script unchanged.

| Replay | Seconds | Result |
| --- | ---: | --- |
| `docs/evidence/formal_certificates/replay_rocq.sh` | 113 | compile, kernel and assumption receipts byte-identical for all three proofs |
| `docs/evidence/c881_exhaustive/replay_rocq.sh` | 32 | compile, kernel, assumptions and source identities pass |
| `docs/evidence/stiefel_witness/replay_rocq.sh` | 512 | compile, kernel, assumptions and source identities pass |
| TargetFlipN21 (AGENTS.md procedure) | 32 | no warning under `-w +all`; no axioms, no assumed positivity |

The toolchain build took 306 s for OCaml and 516 s for Rocq. Each replay
script compares its fresh output with the retained receipt byte for byte, so
a pass means the receipts the CI gates check are what Rocq 9.2 produces from
the retained sources today. The folding-proof replay is not included: its
source identities pin open_gororoba files that have since changed, and its
SchreierSignCode needs the Rocq 9.2 fix in open_gororoba pull request 215.
