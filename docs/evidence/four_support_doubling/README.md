# Four-support ordinary-doubling replay

The [written structural induction](../../notes/four_support_doubling.md)
extends the fixed four-coordinate family to every integer stage at least
five. The exact regression verifies the implementation through dimension
256. The retained result separates the unbounded theorem and descriptor
from the resource-bound expanded artifacts.

Run from the repository root with its pinned Python dependencies:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -W error docs/evidence/four_support_doubling/replay.py --check
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -O -W error docs/evidence/four_support_doubling/replay.py --check
(cd docs/evidence/four_support_doubling && sha256sum -c SHA256SUMS)
```

`GOROROBA_WORKERS=1` produces identical output through the serial path.
The replay writes stdout and verifies source/proof-note hashes before
and after calculation. A changed dependency, proof note, or Python
major.minor requires explicit reviewed regeneration; `--check` carries the
retained Python patch release when major.minor agree (gate core-609).

The result retains independent basis-action checks at three doubling
transitions, complete frame identities, 24 exact rational API cases,
closure inclusions, and negative controls. The stage `10^9` descriptor
retains exponent metadata without expansion. Expanded calls reject an
oversized stage before constructing any exponentially sized artifact.

The replay checks exact CPU arithmetic and makes zero QPU submissions.
The uniform claim rests on the written conjugation and doubling induction.
A Rocq kernel proof, other coefficient supports, and computed topological
invariants remain separate work.
