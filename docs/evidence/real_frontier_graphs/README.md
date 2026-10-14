# Real circle-frontier graph certificates

The [proof note](../../notes/real_circle_frontier_graphs.md) computes the
complete real kernel-graph closure on the named dimension-32 affine cone
slice. Its global rational frame covers arbitrary real amplitudes and
circle directions. The exact point API accepts real algebraic numbers.
The trace inverse rejects endpoint subplanes that satisfy kernel and rank
conditions but fail actual closure membership.

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/real_frontier_graphs/replay.py --check
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/real_frontier_graphs/replay.py --check
(cd docs/evidence/real_frontier_graphs && sha256sum -c SHA256SUMS)
```

The replay verifies global kernel/projector and trace-inverse identities
modulo the real circle relation, strictly positive denominator factors,
independent rational projector and projective-path controls, algebraic
points, damaged pencils, unreachable endpoint planes, and ordinary embedding
through dimension 256. Labelled integer chains retain boundary, projection,
inclusion, homotopy and evaluation matrices. Their contraction and Smith
checks preserve degree coincidences and verify torsion and induced maps.
The geometric proof establishes why those chains describe the actual
restricted evaluation map. The source and target cohomology statements
retain their sphere-product and suspension proofs in the note.

`SHA256SUMS` binds every loaded repository module, proof inputs, replay and
result. Python 3.14.7 and SymPy 1.14.0 supply the retained runtime.
Ambient coverage, unrestricted global invariants and Rocq formalization
remain obligations in `proof_obligations.json`. QPU jobs contribute zero
measurements to these deterministic mathematical certificates.
