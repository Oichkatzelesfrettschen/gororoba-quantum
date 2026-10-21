# Four-support cellular homology replay

The [geometric proof](../../notes/four_support_cellular_homology.md) identifies
a 1,200-cell CW complex with the unit zero-product incidence whose first
operand has support `{1,10,18,25}` and whose partner retains every ambient
coordinate. The replay derives every cellular generator and boundary,
checks the characteristic-map identities and orientation conventions,
and independently replays all 552 integral unit cancellations.

The zero residual certifies torsion-free integral homology in degrees
`0,2,h+1,2h,3h,4h-1` with ranks `1,23,40,8,16,8`, where
`h=4*2^(n-5)` for every ordinary zero-padding stage `n>=5`. The complete
top-factor grading preserves the matrices under this degree change.
Symbolic degree exclusion establishes zero products among positive-degree
integral cohomology classes. The evidence makes no wedge decomposition or
unrestricted pair-space classification claim.

Run from the repository root with the pinned Python dependencies:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -W error docs/evidence/four_support_homology/replay.py --check
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -O -W error docs/evidence/four_support_homology/replay.py --check
(cd docs/evidence/four_support_homology && sha256sum -c SHA256SUMS)
```

`GOROROBA_WORKERS=1` reproduces identical certificate bytes. Independent
fiber fixtures use the repository's spawn-based ordered process pool;
integer basis transformations remain sequential.

`result.json` retains all base labels, degree-indexed cell lists and sparse
matrices, the complete unit-pivot sequence with row and column vectors,
surviving generators and their top-factor summands, degree-exclusion
certificates, and meaningful mutation controls. Matrix entries use
`[row,column,value]`; generator indices are zero-based within each degree.
The absent/point/top labels `0,1,4` denote shifted states at the base stage.
The replay transports the top state to `h` through the separately bound
doubling theorem. Concrete integer-degree expansion checks a stage-4096
resource bound before any shift; exponent/multiplier/offset descriptors retain
the unrestricted stage formulas without power-of-two allocation.

The replay hashes source and proof-note bytes before and after execution,
checks the loaded paths, and rejects digest and path mutations. Changed
sources, proof notes, SymPy versions or Python major.minor require reviewed
evidence regeneration; `--check` carries the retained Python patch release
when major.minor agree (gate core-609). The checksum manifest binds this README, the replay, the
result, and the new module and proof note. Execution uses exact local CPU
arithmetic and makes zero QPU submissions.
