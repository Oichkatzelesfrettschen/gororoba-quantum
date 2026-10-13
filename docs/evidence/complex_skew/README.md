# Complex skew certificate replay

The replay verifies the exact coordinate reduction and complete point kernels
against the original real multiplication matrices. The written all-stage proof
lives in [the note](../../notes/complex_skew_rank_geometry.md).

From the repository root:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/complex_skew/replay.py --check
GOROROBA_WORKERS=1 PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/complex_skew/replay.py --check
(cd docs/evidence/complex_skew && sha256sum -c SHA256SUMS)
```

`result.json` records computed certificates. Replay checks loaded-module paths
and source stability during execution; Git binds the source revision, and
SHA256SUMS binds the retained artifacts. Result comparison follows the existing
result-only evidence policy. Python and SymPy versions print separately in
check mode. The pinned runtime uses SymPy 1.14.0.

The controls cover 114 coefficient operators, six dimension-32 coefficient
points, all 1365 quadratic cover identities, generic order-six Pfaffians,
chart corruptions and invalid inputs. Finite checks test implementation;
the proof note supplies universal statements. New Rocq formalization retains
the raw-collection/adjudication prerequisite. The replay submits zero QPU jobs.
