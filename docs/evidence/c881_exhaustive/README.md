# Exhaustive finite separating-degree proof

The [source audit](../../notes/c881_exhaustive_proof.md) binds the complete
C881 lower bound to `open_gororoba` HEAD
`b977e43f71e8ec22a2eabc83197b649056e63a67`. The replay checks the two-file
source closure, fresh compilation, six closed assumption queries, and the
independent kernel checker under Rocq 9.3.0, OCaml 5.5.1 and Stdlib 9.2.0.
Fresh compilation and kernel checking retain the exact six assumption reports
and the complete Rocq 9.3 kernel diagnostic.

```sh
export GOROROBA_ROOT
ROCQ="${ROCQ:-rocq}" sh docs/evidence/c881_exhaustive/replay_rocq.sh
```

`GOROROBA_ROOT` names the latest audited source checkout. The script checks
the source identities before copying, verifies the copied bytes, and checks
the source identities again after replay. It compares each compiler and
kernel output with the retained receipt and removes its own temporary proof
objects. `SHA256SUMS` binds local evidence; `source_hashes.sha256` binds the
external inputs. Earlier folding receipts retain their historical compiler
and source identities. The finite theorem supplies no continuous topology
classification and invokes zero QPU jobs.
