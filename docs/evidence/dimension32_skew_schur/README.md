# Dimension-32 skew-Schur evidence

The [proof note](../../notes/dimension32_skew_schur_charts.md) proves the
all-real local congruence, rank identity, kernel transport, and metric
incidence homeomorphism on each invertible pivot domain. The
[replay](replay.py) retains exact rational production certificates and an
independent symbolic same-tangent fixture. The certificate leaves global
coverage, smooth stratification, and attachments as separate obligations.

Run from the repository root with its pinned dependencies:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -W error docs/evidence/dimension32_skew_schur/replay.py --check
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -O -W error docs/evidence/dimension32_skew_schur/replay.py --check
(cd docs/evidence/dimension32_skew_schur && sha256sum -c SHA256SUMS)
```

`GOROROBA_WORKERS=1` exercises the serial implementation. The replay
verifies imported module locations and compares source and proof-note
hashes before and after evaluation. `result.json` binds those hashes,
Python and SymPy versions, input coordinates, exact output matrices, and
negative controls. `SHA256SUMS` binds the retained replay and result bytes.
Regeneration requires an explicit reviewed source or dependency change.

The finite denominator includes all 30 coordinate perturbations
`e_1+e_10+e_i/7`, with `i` different from 0 and 16, and derivative maps on
all 30 directions at four centers of nullity 4, 8, 12, and 16. The replay
checks every perturbation against an independent full-rank certificate and
checks kernel residuals, metric transport, and inverse coordinates. Input
and output hashes bind each case. The derivative records retain the full
coefficient matrices and the fixed-norm tangent-kernel bases.

The nonlinear fixture uses center `e_1+e_10` and tangent `e_3`. The straight
path `e_1+t e_3+e_10` becomes invertible for every nonzero real parameter.
The rational curved path in the proof note has the same center and tangent
and retains nullity eight. Exact determinants establish the complete real
parameter domain for both paths. Independent full-matrix certificates
check the rational points `e_1+e_3+e_10`, `3e_1+4e_3+5e_10`, and `e_3+e_10`.
The recorded matrices expose the quadratic term that linearization omits.
Both paths share the exact elimination lift and metric; their distinct
residuals retain the kernel membership information that those two artifacts
alone omit.

The replay computes exact CPU arithmetic and submits zero QPU jobs. Its
finite test denominator establishes regression coverage, while the written
block identities establish the all-real local result. Publication priority,
unrestricted pair-space topology, and Rocq formalization remain open.
