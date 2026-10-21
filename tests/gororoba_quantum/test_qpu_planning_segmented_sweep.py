"""A pinned segmented ground sweep plans an xy and a z arm per delay and its backaction arms on FakeFez, plays
each segment on the spectator alone with no control flow, and binds its configuration and analyzer closure.
"""

from __future__ import annotations

import qpu_planning_contracts


def test_segmented_sweep_plan() -> None:
    qpu_planning_contracts._verify_segmented_sweep_only()
