"""Read collected runs of a six-seed-slot Belenos diagnostic built by scripts/bdsc_diagnostic_v2_case.py.

scripts/bdsc_diagnostic_acquisition_analysis.py keeps its bytes (six retained manifests bind its sha256), so this
reader runs a fork of it (scripts/bdsc_diagnostic_v2.py `fork`) whose `diag` is the six-slot fork of
scripts/bdsc_diagnostic.py and whose `acquisition` is the six-slot builder. A run is admitted under the same checks
as the original reader: the record equals a fresh build, the manifest equals the frozen rebuild of its job for the
record's draw, the submission and the service report qpu:belenos, and the bound sources equal the tree's. The
integrity checks, the nine components of the analysis and the branch rule are the functions of
scripts/bdsc_diagnostic.py at SLOTS 6.

Usage:
  "$PYTHON" scripts/bdsc_diagnostic_v2_analysis.py --case DIR/case.json RUN...
  "$PYTHON" scripts/bdsc_diagnostic_v2_analysis.py --case DIR/case.json --matched-check B1J2_RUN B2J1_RUN
  "$PYTHON" scripts/bdsc_diagnostic_v2_analysis.py --case DIR/case.json --admit-only RUN...
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_diagnostic_acquisition_analysis as original  # noqa: E402
import bdsc_diagnostic_v2 as layout  # noqa: E402
import bdsc_diagnostic_v2_case as builder  # noqa: E402

SCOPE: dict[str, Any] = layout.fork(original, diag=layout.diag, acquisition=builder.case, __doc__=__doc__)
analysis = types.SimpleNamespace(**SCOPE)

if __name__ == "__main__":
    raise SystemExit(SCOPE["main"]())
