"""Build the six-seed-slot Belenos diagnostic request for qpu:belenos under the qd_platform.job_billing rule.

scripts/bdsc_diagnostic_acquisition_case.py keeps its bytes (six retained manifests bind its sha256), so this builder
runs a fork of it (scripts/bdsc_diagnostic_v2.py `fork`) whose `diag` is the six-slot fork of
scripts/bdsc_diagnostic.py. The fork shares the draw claim, the QRNG binding, the billing-rule supersession and the
manifest binding of the original builder, and changes four things:

- the layout is 6 seed slots: 4 jobs of 36 iterations (6 groups of 6 states, 40000 samples, an 80000-shot cap), 144
  instances, from a draw of at least 150 uint16 values (scripts/bdsc_diagnostic_v2.py);
- the case record carries the authorization wording of issue 930, so approval covers the provider jobs and not the
  free ANU draw, and the power statement of the six-slot design;
- the only admitted platform is qpu:belenos: a 36-iteration job needs about 480 s on sim:belenos against its 300 s
  limit (results/quandela/cases/bdsc_diagnostic_packed_qpu_belenos/CASE.md, "Rehearsal");
- every manifest binds SOURCES, which adds this module, its analyzer and scripts/bdsc_diagnostic_v2.py.

Usage:
  "$PYTHON" scripts/bdsc_diagnostic_v2_case.py --build --platform qpu:belenos --out DIR --draw FILE
  "$PYTHON" scripts/bdsc_diagnostic_v2_case.py --check DIR [--draw FILE]
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_diagnostic_acquisition_case as original  # noqa: E402
import bdsc_diagnostic_v2 as layout  # noqa: E402

PLATFORMS = ("qpu:belenos",)
BUILDER = "scripts/bdsc_diagnostic_v2_case.py"
ANALYZER = "scripts/bdsc_diagnostic_v2_analysis.py"
# The original builder's bound modules, with the two files that this builder and the layout fork add.
SOURCES = tuple(
    sorted(
        {
            *original.SOURCES,
            "scripts/bdsc_diagnostic_v2.py",
            "scripts/bdsc_diagnostic_v2_analysis.py",
            "scripts/bdsc_diagnostic_v2_case.py",
        }
    )
)

SCOPE: dict[str, Any] = layout.fork(
    original,
    diag=layout.diag,
    PLATFORMS=PLATFORMS,
    BUILDER=BUILDER,
    ANALYZER=ANALYZER,
    SOURCES=SOURCES,
    __doc__=__doc__,
)
case = types.SimpleNamespace(**SCOPE)

if __name__ == "__main__":
    raise SystemExit(SCOPE["main"]())
