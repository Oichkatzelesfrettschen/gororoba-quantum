# Projective kernel-limit certificates

The [proof note](../../notes/projective_kernel_frontiers.md) gives a finite
polynomial saturation algorithm, a leading-Pfaffian formula, and an
all-dimensional quotient construction from real frontier graphs. The exact
API computes polynomial-path certificates; the graph closures remain to be
classified before the construction yields global topological invariants.

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/projective_kernel_limits/replay.py --check
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/projective_kernel_limits/replay.py --check
(cd docs/evidence/projective_kernel_limits && sha256sum -c SHA256SUMS)
```

The replay checks Gaussian coefficients, rational endpoints, three exact
factor removals at constant operator rank, scaling and reparametrization,
complex congruence, zero and full rank, and odd ambient dimension. Leading
coordinates are checked against independently enumerated complementary
Pfaffians on the small fixtures. Seven dimension-32 paths and one
dimension-64 embedding agree with the full real-matrix projector algorithm.
Damaged certificates and invalid polynomial inputs fail admission.

`result.json` retains deterministic results. `SHA256SUMS` binds every loaded
repository module, the note, replay and proof obligations. The retained
runtime uses Python 3.14.7 and SymPy 1.14.0. QPU outcomes and finite examples
do not establish unrestricted frontier coverage. The written quotient
argument and its open computational and Rocq obligations remain separate
from the exact rational controls.
