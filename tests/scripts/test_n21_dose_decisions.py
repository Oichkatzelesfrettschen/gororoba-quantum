"""Contracts of the N=21 window-dose decisions."""

from __future__ import annotations

from pathlib import Path

import n21_dose_decisions as dose


def test_self_test_cases_decide_as_stated() -> None:
    message = dose.self_test()
    if "decide as stated" not in message:
        raise AssertionError(message)


def test_measured_contrast_and_sigma_follow_the_score_vector() -> None:
    contracts = [
        {
            "name": "c",
            "terms": [
                {"member": "fb", "sign": 1, "values": [0.0, 1.0, 0.0, -1.0]},
                {"member": "nf", "sign": -1, "values": [0.0, 1.0, 0.0, -1.0]},
            ],
        }
    ]
    laws = {"fb": [[0.25, 0.5, 0.0, 0.25]], "nf": [[0.25, 0.25, 0.25, 0.25]]}
    value, sigma = dose.measured(contracts, laws, 100)["c"]
    if abs(value - 0.25) > 1e-12:
        raise AssertionError(f"contrast {value}")
    expected = ((0.75 - 0.25**2) + (0.5 - 0.0)) / 100
    if abs(sigma**2 - expected) > 1e-12:
        raise AssertionError(f"variance {sigma**2} against {expected}")


def test_withheld_comparisons_are_refused(tmp_path: Path) -> None:
    import json

    import pytest

    (tmp_path / "record.json").write_text(json.dumps({"observable_contracts": [], "shots": 10}))
    (tmp_path / "collect.json").write_text(
        json.dumps([{"measured": {}, "comparisons_withheld": "the group's PUBs did not all run under one calibration"}])
    )
    (tmp_path / "idle-replay.json").write_text(json.dumps({"contracts": {"idle_padded_exact": {}}}))
    with pytest.raises(ValueError, match="withheld"):
        dose.analyze(tmp_path)


def test_replicas_pool_as_the_collector_averages_them() -> None:
    contracts = [{"name": "c", "terms": [{"member": "fb", "sign": 1, "values": [0.0, 1.0, 0.0, -1.0]}]}]
    laws = {"fb": [[0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]]}
    value, sigma = dose.measured(contracts, laws, 100)["c"]
    if abs(value) > 1e-12 or abs(sigma) > 1e-12:
        raise AssertionError(f"two deterministic replicas pool to {value} +- {sigma}")


def _design_record() -> dict:
    return {
        "state": "planned",
        "shots": dose.DESIGN_SHOTS,
        "policy": {
            "rep_delay_seconds": 2e-05,
            "max_execution_seconds": 30,
            "design": {
                "family": "n21-orbit-rca",
                "window_doses": list(dose.DESIGN_DOSES),
                "init_herald": True,
                "max_total_execution_seconds": 30.0,
            },
        },
        "optimization": {
            "selected": "c",
            "candidates": [{"name": "c", "feasible": True, "estimated_charge_seconds": 12.0}],
        },
        "groups": [{"backend": "ibm_fez", "calibration": "t", "replicas": [{}] * 8}],
        "seed_source": [{"flag": flag, "sources": sources} for flag, sources in dose.DESIGN_SEED_SOURCES.items()],
    }


def test_preflight_admits_the_design_and_refuses_each_departure(tmp_path: Path) -> None:
    import copy
    import json

    import pytest

    def check(record: dict) -> dict:
        (tmp_path / "record.json").write_text(json.dumps(record))
        return dose.preflight(tmp_path)

    if check(_design_record())["replicas"] != 8:
        raise AssertionError("the design record does not pass")
    departures = [
        ("shots", lambda r: r.update(shots=16384)),
        ("repetition delay", lambda r: r["policy"].update(rep_delay_seconds=1e-04)),
        ("replicas", lambda r: r["groups"][0].update(replicas=[{}])),
        ("doses", lambda r: r["policy"]["design"].update(window_doses=[0, 3500])),
        ("seed sources", lambda r: r.update(seed_source=[])),
        ("estimated charge", lambda r: r["optimization"]["candidates"][0].update(estimated_charge_seconds=31.0)),
    ]
    for label, mutate in departures:
        record = copy.deepcopy(_design_record())
        mutate(record)
        with pytest.raises(ValueError):
            check(record)
        del label
