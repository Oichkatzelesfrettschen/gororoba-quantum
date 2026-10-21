# Principal skew atlas evidence

The [proof note](../../notes/principal_skew_atlas.md) gives an all-real
cover by fifteen four-coordinate principal pivots in dimension 32 and a
uniform version at every stage. The [replay](replay.py) checks the expanded
implementation, exact rank refinements, rectangular residual-coordinate
maps, and pointwise kernel isomorphisms. The retained result identifies a
global incidence presentation; smooth subdivisions and computed global
topology remain separate obligations.

Run from the repository root with its pinned dependencies:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -W error docs/evidence/principal_skew_atlas/replay.py --check
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -O -W error docs/evidence/principal_skew_atlas/replay.py --check
(cd docs/evidence/principal_skew_atlas && sha256sum -c SHA256SUMS)
```

`GOROROBA_WORKERS=1` exercises the serial path. The replay verifies import
locations and compares source and proof-note hashes before and after each
calculation. `result.json` records the Python and SymPy versions (`--check`
carries the retained Python patch release when major.minor agree, gate
core-609), exact
input coordinates, selected pivots, elimination steps, pivot determinants,
output hashes, and mutation controls. Each output hash binds the exact
Schur matrix, elimination lift, Gram metric, and full kernel; the replay
reconstructs those matrices before comparing the retained bytes.
`SHA256SUMS` binds the README, replay, and result. A source or dependency
change requires reviewed regeneration.

The finite symbolic denominator contains all 247 coordinate-quaternion
pivots through dimension 256. Each check keeps every allowed coefficient
symbol, proves the exact four-by-four block and determinant, and checks
that the coefficient-pair norms sum to the full norm. The written doubling
argument carries the unbounded stage statement.

Independent rational fixtures cover nullities 0, 4, 8, 12, and 16. The
invertible fixture has nonzero values in all 30 doubly-pure coordinates.
Every fixture compares the reduced result with an independent full-matrix
rank certificate. Each fixture uses admitted four-coordinate charts, a
greedy maximal principal refinement, and an independently selected
rank-sized principal block. The dense fixture uses the first, middle, and
last admitted cover charts; symbolic checks cover the entire family.

The replay checks the full ambient residual-factor identities, then
checks reconstruction, inverse, metric, and cocycle identities on the
complete pointwise kernels. Different pivot sizes exercise rectangular
coordinate maps. The invertible endpoint exercises zero-column full
kernels and zero-row overlap maps with their dimensions retained. The
production audit supplies changed-certificate and invalid-input controls.
All checks execute under normal and optimized Python with explicit
exceptions.

The calculations use exact CPU arithmetic and submit zero QPU jobs.
The cover and overlap theorem is a global semialgebraic presentation,
not a computed CW complex, a smooth-stratum classification, or a Rocq
kernel proof. The proof note gives literature attribution and the
remaining geometric obligations.
