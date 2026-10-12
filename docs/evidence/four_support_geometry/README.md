# Four-support incidence geometry replay

The [written proof](../../notes/four_support_incidence_geometry.md) derives
96 connected smooth strata, 704 closure incidences including 96 reflexive
ones, and the global five-block incidence homeomorphism on the fixed
support `{1,10,18,25}`. The exact replay retains the finite relation,
constructive approach identities, kernel-frame identities, and falsifiers.

Run from the repository root with its pinned Python dependencies:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -W error docs/evidence/four_support_geometry/replay.py --check
GOROROBA_WORKERS=4 PYTHONDONTWRITEBYTECODE=1 \
  "$PYTHON" -O -W error docs/evidence/four_support_geometry/replay.py --check
(cd docs/evidence/four_support_geometry && sha256sum -c SHA256SUMS)
```

`GOROROBA_WORKERS=1` produces identical output through the serial path.
The replay writes stdout and records source and proof-note hashes before
and after execution. A changed source, proof note, or recorded runtime
requires explicit reviewed regeneration. `result.json` uses zero-based
positions in its `strata` list for closure target identifiers.

Finite enumeration checks coverage labels and incidence combinatorics.
The log-coordinate and constructive-density arguments in the proof note
establish their real geometric interpretation. Polynomial identities and
the prior all-real rank theorem establish the frame homeomorphism.
The evidence claims neither Whitney conditions, computed homology, nor
classification of other coefficient supports. The replay invokes exact
CPU arithmetic and makes zero QPU submissions.
