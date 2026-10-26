"""Contracts of the N=21 window-dose decisions."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import n21_dose_decisions as dose
import numpy as np
import pytest


def test_self_test_cases_decide_as_stated() -> None:
    message = dose.self_test()
    if "decide as stated" not in message:
        raise AssertionError(message)


def test_member_moments_match_the_sample_covariance_and_drop_heralded_shots() -> None:
    scores = np.asarray([[1.0, 1.0], [-1.0, 1.0], [1.0, -1.0], [-1.0, -1.0]] * 8)
    keep = np.ones_like(scores)
    moments = dose.member_moments(keep, scores, batches=4)
    expected = np.cov(scores, rowvar=False, bias=True) / scores.shape[0]
    if not np.allclose(moments["covariance"], expected, atol=1e-15) or np.abs(moments["means"]).max() > 1e-15:
        raise AssertionError(f"{moments}")
    heralded = keep.copy()
    heralded[::4, 0] = 0.0
    shifted = scores.copy()
    shifted[::4, 0] = 100.0
    # Replica 0 keeps -1, +1, -1 of every four shots.
    dropped = dose.member_moments(heralded, shifted, batches=4)
    if abs(dropped["means"][0] + 1 / 3) > 1e-12 or dropped["kept"].tolist() != [24, 32]:
        raise AssertionError(f"a heralded shot entered the mean: {dropped['means']}, kept {dropped['kept']}")


def test_block_dispersion_exceeds_one_under_drift() -> None:
    drift = np.repeat(np.linspace(-0.5, 0.5, 8), 16)[:, None] * np.ones((1, 3))
    scores = drift + np.tile([0.5, -0.5], 64)[:, None]
    moments = dose.member_moments(np.ones_like(scores), scores, batches=8)
    if moments["dispersion"] < 2.0:
        raise AssertionError(f"block-constant drift gives dispersion {moments['dispersion']}")


def test_conditioned_value_keeps_only_the_all_zero_herald() -> None:
    values = [0.0, 1.0, 0.0, -1.0] * 4
    law = [0.1, 0.2, 0.0, 0.1] + [0.0, 0.6, 0.0, 0.0] + [0.0] * 8
    if abs(dose.conditioned_value(law, values, 2) - (0.2 - 0.1) / 0.4) > 1e-12:
        raise AssertionError("the herald-conditioned value reads the wrong outcomes")


def _raw_run(tmp_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """A one-contract record with two replicas per PUB and its shot-ordered registers under raw/job/."""
    contract = {
        "name": "n21_orbit_window_dose_d0_feedback_contrast",
        "terms": [
            {"member": "fb", "sign": 1, "values": [0.0, 1.0, 0.0, -1.0] * 2},
            {"member": "nf", "sign": -1, "values": [0.0, 1.0, 0.0, -1.0] * 2},
        ],
    }
    registers = [["g0_r0_phase", "g0_r0_herald"], ["g0_r1_phase", "g0_r1_herald"]]
    record = {
        "observable_contracts": [contract],
        "execution_pubs": [
            {"name": f"pub_{m}", "components": [{"member": m, "registers_by_replica": registers}]} for m in ("fb", "nf")
        ],
    }
    phase = {"fb": ["01", "01", "11", "01"], "nf": ["00", "11", "01", "11"]}
    herald = {"fb": ["0", "1", "0", "0"], "nf": ["0", "0", "0", "0"]}
    raw = tmp_path / "raw" / "job"
    raw.mkdir(parents=True)
    index: dict[str, str] = {}
    laws: dict[str, list[list[float]]] = {}
    for k, member in enumerate(("fb", "nf")):
        regs = {
            name: {"bitstrings": phase[member] if name.endswith("phase") else herald[member]}
            for pair in registers
            for name in pair
        }
        payload = json.dumps({"pub_name": f"pub_{member}", "registers": regs}).encode()
        (raw / f"pub_{k:02d}.json").write_bytes(payload)
        index[f"pub_{k:02d}.json"] = hashlib.sha256(payload).hexdigest()
        counts = [0.0] * 8
        for p, h in zip(phase[member], herald[member], strict=True):
            counts[int(h + p, 2)] += 1
        laws[member] = [counts, list(counts)]
    (raw / "index.json").write_text(json.dumps({"files": index}))
    return record, laws


def test_measured_from_raw_binds_the_marginals_and_conditions_on_the_herald(tmp_path: Path) -> None:
    record, laws = _raw_run(tmp_path)
    moments = dose.measured_from_raw(tmp_path, record, laws)
    # fb keeps shots 0, 2 and 3 (outcomes 1, 3, 1), scoring +1, -1, +1.
    if not np.allclose(moments["fb"]["means"], [1 / 3, 1 / 3]) or moments["fb"]["kept"].tolist() != [3, 3]:
        raise AssertionError(f"{moments['fb']}")
    tampered = copy.deepcopy(laws)
    tampered["nf"][1] = [1.0] + [0.0] * 7
    with pytest.raises(ValueError, match="collected marginal"):
        dose.measured_from_raw(tmp_path, record, tampered)


def test_withheld_comparisons_are_refused(tmp_path: Path) -> None:
    (tmp_path / "record.json").write_text(json.dumps({"observable_contracts": [], "shots": 10}))
    (tmp_path / "collect.json").write_text(
        json.dumps([{"measured": {}, "comparisons_withheld": "the group's PUBs did not all run under one calibration"}])
    )
    (tmp_path / "idle-replay.json").write_text(json.dumps({"exact_laws": {"idle_padded": {}}}))
    with pytest.raises(ValueError, match="withheld"):
        dose.analyze(tmp_path)


def _draw_values() -> list[int]:
    values: list[int] = json.loads((dose.ROOT / dose.DESIGN_DRAW).read_text())["values"]
    return values


def _design_record() -> dict[str, Any]:
    members = 2 * (2 * len(dose.DESIGN_DOSES) - 1)
    values = _draw_values()
    return {
        "seed_simulator": values[1],
        "state": "planned",
        "shots": dose.DESIGN_SHOTS,
        "policy": dict(dose.EXPECTED_POLICY)
        | {"rep_delay_seconds": 2e-05, "design": copy.deepcopy(dose.EXPECTED_DESIGN)},
        "optimization": {
            "selected": "c",
            "searched_routed_sets": 1,
            "candidates": [{"name": "c", "feasible": True, "estimated_charge_seconds": 12.0}],
        },
        "groups": [{"backend": "ibm_fez", "calibration": "t", "replicas": [{}] * 8, "seed_transpiler": values[0] + 1}],
        "execution_pubs": [{"name": f"p{k}", "components": [{}]} for k in range(members)],
        "budget_plan": {"jobs": [{"kind": "dynamic", "pubs": members}]},
        "code_commit": {"head": "abc", "sources_modified": False},
        "seed_source": [{"flag": flag, "sources": sources} for flag, sources in dose.DESIGN_SEED_SOURCES.items()],
    }


def test_preflight_admits_the_design_and_refuses_each_departure(tmp_path: Path) -> None:
    def check(record: dict[str, Any]) -> dict[str, Any]:
        (tmp_path / "record.json").write_text(json.dumps(record))
        return dose.preflight(tmp_path, "abc")

    if check(_design_record())["replicas"] != 8:
        raise AssertionError("the design record does not pass")
    departures = [
        lambda r: r.update(shots=16384),
        lambda r: r["policy"].update(rep_delay_seconds=1e-04),
        lambda r: r["groups"][0].update(replicas=[{}]),
        lambda r: r["policy"]["design"].update(window_doses=[0, 3500]),
        lambda r: r["policy"]["design"].update(replica_tiers=[4]),
        lambda r: r["policy"]["design"].update(model_shots=131072),
        lambda r: r["policy"]["design"].update(objective="precision_at_budget"),
        lambda r: r["policy"]["design"].update(shot_allocation="neyman"),
        lambda r: r["policy"].update(max_pending=25),
        lambda r: r.update(seed_source=[]),
        lambda r: r["optimization"]["candidates"][0].update(estimated_charge_seconds=31.0),
        lambda r: r["optimization"].update(searched_routed_sets=2),
        lambda r: r["groups"][0].update(backend="ibm_torino"),
        lambda r: r["policy"].update(replica_floor=None),
        lambda r: r["policy"].update(twirl=True),
        lambda r: r["execution_pubs"].pop(),
        lambda r: r["budget_plan"]["jobs"].append({"kind": "static", "pubs": 1}),
        lambda r: r["code_commit"].update(sources_modified=True),
        lambda r: r["code_commit"].update(head="def"),
        lambda r: r.update(seed_simulator=r["seed_simulator"] + 1),
        lambda r: r["groups"][0].update(seed_transpiler=r["groups"][0]["seed_transpiler"] + 8),
    ]
    for k, mutate in enumerate(departures):
        record = _design_record()
        mutate(record)
        with pytest.raises(ValueError):
            check(record)
            raise AssertionError(f"departure {k} passed the preflight")


def test_retry_check_admits_one_retry_after_an_unexecuted_1305(tmp_path: Path) -> None:
    record = {
        "state": "submitted",
        "policy": dict(dose.EXPECTED_POLICY)
        | {"rep_delay_seconds": 2e-05, "design": copy.deepcopy(dose.EXPECTED_DESIGN)},
        "submission": {"jobs": [{"job_id": "j"}]},
    }
    job = {
        "usage": {"job_status": "ERROR", "qpu_charge_time_seconds": "2"},
        "pub_timing": {},
        "result_unavailable": "RuntimeJobMaxTimeoutError: 'Error code 1305; Job ran longer than allowed.'",
    }
    (tmp_path / "record.json").write_text(json.dumps(record))
    (tmp_path / "collect.json").write_text(json.dumps([{"jobs": {"j": job}}]))
    if dose.retry_check(tmp_path)["job_id"] != "j":
        raise AssertionError("an unexecuted 1305 at 20 us does not admit the retry")
    (tmp_path / "retry-consumed.json").write_text("{}")
    with pytest.raises(ValueError, match="spent"):
        dose.retry_check(tmp_path)
    (tmp_path / "retry-consumed.json").unlink()
    changes: list[dict[str, Any]] = [{"pub_timing": {"p": {}}}, {"result_unavailable": "Error code 1517"}]
    for change in changes:
        (tmp_path / "collect.json").write_text(json.dumps([{"jobs": {"j": job | change}}]))
        with pytest.raises(ValueError):
            dose.retry_check(tmp_path)
    (tmp_path / "collect.json").write_text(json.dumps([{"jobs": {"other": job}}]))
    with pytest.raises(ValueError, match="not the submitted"):
        dose.retry_check(tmp_path)
    for mutate in (lambda r: r.update(state="planned"), lambda r: r["policy"]["design"].update(family="x")):
        changed = copy.deepcopy(record)
        mutate(changed)
        (tmp_path / "record.json").write_text(json.dumps(changed))
        (tmp_path / "collect.json").write_text(json.dumps([{"jobs": {"j": job}}]))
        with pytest.raises(ValueError):
            dose.retry_check(tmp_path)
