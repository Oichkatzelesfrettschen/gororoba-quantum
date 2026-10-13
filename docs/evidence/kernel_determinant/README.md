# Kernel determinant-line certificate

The [written proof](../../notes/annihilator_determinant_line.md) trivializes
the determinant line of every constant-rank complex skew kernel family.
The Cayley-Dickson application covers arbitrary real coefficients on each
rank locus at every stage. The proof establishes an oriented real
annihilator bundle and zero first integral Chern class; full bundle
classification and frontier attachments remain open.

The exact replay checks eight rational points, 72 chart overlaps, complete
complementary coordinates on the indicated fixtures, and six symbolic
complementary identities on an arbitrary-complex rank-two chart. The controls
include imaginary transition determinants, origin and full-rank conventions,
rejected certificate mutations, and the zero limit of a polynomial volume.
Finite controls validate implementation conventions; the written exterior
algebra argument supplies the all-dimensional statement.

Run from the repository root:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/kernel_determinant/replay.py --check
GOROROBA_WORKERS=1 PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -O -W error docs/evidence/kernel_determinant/replay.py --check
(cd docs/evidence/kernel_determinant && sha256sum -c SHA256SUMS)
```

`result.json` holds deterministic exact outputs. `SHA256SUMS` binds the
local evidence files, all loaded repository modules, and the proof note.
The replay also checks module paths and input hashes during execution.
The retained environment uses Python 3.14.7 and SymPy 1.14.0.
`proof_obligations.json` separates written results from the open Rocq port
and unrestricted topology. The controls submit zero QPU jobs.
