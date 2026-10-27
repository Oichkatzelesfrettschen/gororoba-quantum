"""Contracts of the N=21 window-dose decisions."""

from __future__ import annotations

import copy
import hashlib
import json
import math
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
        | {"rep_delay_seconds": 5e-05, "design": copy.deepcopy(dose.EXPECTED_DESIGN)},
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
        lambda r: r["optimization"]["candidates"][0].update(estimated_charge_seconds=91.0),
        lambda r: r["policy"].update(rep_delay_seconds=2e-05),
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


def _sweep_run(tmp_path: Path) -> None:
    """A three-dose run directory: record, collect.json, shot-ordered raw registers and idle-replay.json."""
    doses = [0, 3500, 7000]
    registers = [["g0_r0_phase", "g0_r0_herald"], ["g0_r1_phase", "g0_r1_herald"]]
    score = [0.0, 1.0, 0.0, -1.0] * 2
    contracts: list[dict[str, Any]] = []
    pubs: list[dict[str, Any]] = []
    laws: dict[str, list[list[float]]] = {}
    model_base: dict[str, list[list[float]]] = {}
    scaled: dict[str, dict[str, list[list[float]]]] = {repr(s): {} for s in dose.DOSE_SCALES}
    raw = tmp_path / "raw" / "job"
    raw.mkdir(parents=True)
    index: dict[str, str] = {}

    def law(p1: float) -> list[float]:
        # Phase outcome 1 with probability p1, 3 otherwise, herald 0 with probability 0.98.
        head = [0.0, p1, 0.0, 1.0 - p1]
        return [0.98 * x for x in head] + [0.02 * x for x in head]

    for d in doses:
        for echo in (False, True):
            if echo and not d:
                continue
            name = f"n21_orbit_window_dose{'_echo' if echo else ''}_d{d}"
            members = [f"{name}_feedback", f"{name}_no_feedback"]
            contracts.append(
                {
                    "name": f"{name}_feedback_contrast",
                    "terms": [
                        {"member": members[0], "sign": 1, "values": score},
                        {"member": members[1], "sign": -1, "values": score},
                    ],
                }
            )
            tau = 14000.0 if echo else 9000.0
            for k, member in enumerate(members):
                p1 = 0.5 + (0.1 if k == 0 else 0.0) * math.exp(-d / tau)
                model_base[member] = [law(p1), law(p1)]
                for s in dose.DOSE_SCALES:
                    scaled[repr(s)][member] = [law(0.5 + (0.1 if k == 0 else 0.0) * math.exp(-s * d / tau))] * 2
                shots = 2048
                # Outcome 1 spread evenly through the shots, so the blocks carry no drift.
                phase = ["01" if math.floor((s + 1) * p1) > math.floor(s * p1) else "11" for s in range(shots)]
                herald = ["1" if s % 50 == 0 else "0" for s in range(shots)]
                pub = f"pub_{len(pubs):02d}"
                pubs.append({"name": pub, "components": [{"member": member, "registers_by_replica": registers}]})
                regs = {n: {"bitstrings": phase if n.endswith("phase") else herald} for pair in registers for n in pair}
                payload = json.dumps({"pub_name": pub, "registers": regs}).encode()
                (raw / f"{pub}.json").write_bytes(payload)
                index[f"{pub}.json"] = hashlib.sha256(payload).hexdigest()
                counts = [0.0] * 8
                for ph, he in zip(phase, herald, strict=True):
                    counts[int(he + ph, 2)] += 1
                laws[member] = [counts, list(counts)]
    (raw / "index.json").write_text(json.dumps({"files": index}))
    (tmp_path / "record.json").write_text(
        json.dumps({"observable_contracts": contracts, "execution_pubs": pubs, "shots": 2048})
    )
    (tmp_path / "collect.json").write_text(json.dumps([{"jobs": {"job": {}}}, {"measured": laws}]))
    replay = {"exact_laws": {"idle_padded": model_base}, "dose_scaled_exact_laws": scaled}
    (tmp_path / "idle-replay.json").write_text(json.dumps(replay))


def test_analyze_runs_end_to_end_and_serializes(tmp_path: Path) -> None:
    _sweep_run(tmp_path)
    out = json.loads(json.dumps(dose.analyze(tmp_path)))
    for key in ("d1_idle_response", "d2_plain_rate", "d3_echo_refocusing", "kappa_p_per_replica", "drift"):
        if key not in out:
            raise AssertionError(f"analyze omits {key}")
    if out["replicas"] != 2 or not out["d1_idle_response"]["holds"]:
        raise AssertionError(f"the decaying fixture reads {out['d1_idle_response']}")
