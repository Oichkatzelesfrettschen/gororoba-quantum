"""Contract for ci/gate_timings.json: it parses and names only gates the manifest lists after case
expansion, so a removed or renamed gate fails until its timing goes with it.
"""

from __future__ import annotations

from pathlib import Path

import merge_gate_timings
import pytest

pytestmark = pytest.mark.audit

ROOT = Path(__file__).resolve().parents[2]


def test_timings_name_manifest_gates() -> None:
    merge_gate_timings.check(ROOT / "ci/gate_timings.json", ROOT)
