"""A window-dose sweep plans its pairs on FakeFez, keeps each dose as a top-level delay and binds the doses."""

from __future__ import annotations

import qpu_planning_contracts


def test_window_dose_sweep_plan() -> None:
    qpu_planning_contracts._verify_window_dose_sweep_only()
