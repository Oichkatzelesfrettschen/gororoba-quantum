"""A window-dose sweep plans its pairs on FakeFez, keeps each dose as a top-level delay and binds the doses."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import qpu_planning
import qpu_planning_contracts


def test_window_dose_sweep_plan() -> None:
    qpu_planning_contracts._verify_window_dose_sweep_only()


@pytest.mark.audit
def test_window_dose_sweep_packs_replicas() -> None:
    qpu_planning_contracts._verify_window_dose_packing_only()


def test_only_a_dose_sweep_lifts_the_orbit_rca_replica_cap() -> None:
    def args(doses: list[int] | None) -> SimpleNamespace:
        return SimpleNamespace(
            family="n21-orbit-rca", optimize=True, replica_tiers=[1, 4, 16], max_replicas=None, window_doses_dt=doses
        )

    if qpu_planning.n21_replica_tiers(args(None)) != [1]:
        raise AssertionError("the orbit-rca window variants plan more than one replica")
    if qpu_planning.n21_replica_tiers(args([0, 3500, 7000])) != [1, 4, 16]:
        raise AssertionError("a dose sweep keeps the one-replica cap")
