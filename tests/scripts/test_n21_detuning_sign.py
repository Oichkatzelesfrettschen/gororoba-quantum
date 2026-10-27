"""Contracts of the N=21 detuning-sign decisions."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import n21_detuning_sign as sign
import pytest


def _require(condition: bool, message: object = "") -> None:
    if not condition:
        raise AssertionError(message)


def test_self_test_cases_decide_as_stated() -> None:
    message = sign.self_test()
    _require("decide against it" in message, message)


def test_orbit_quadrature_cancels_the_relaxation_offset() -> None:
    # Both branches lean +0.2 toward 0 from relaxation; the coherence +-0.3 survives only in x0 - x1.
    c, var = sign.orbit_quadrature([750, 250, 250, 750])
    _require(c == pytest.approx(1.0) and var == pytest.approx(2 * 0.75 / 1000), (c, var))
    offset, _ = sign.orbit_quadrature([750, 750, 250, 250])
    _require(offset == pytest.approx(0.0), offset)


def test_rate_recovers_a_known_slope_and_stops_at_an_unresolved_dose() -> None:
    times = [0.0, 7.0, 14.0, 21.0, 28.0]
    phases = [(math.remainder(2 * math.pi * 12e-3 * t, 2 * math.pi), 0.02, 0.5, 0.02) for t in times]
    fit = sign.rate(times, phases)
    _require(fit["khz"] == pytest.approx(12.0, abs=1e-9) and fit["doses"] == 5, fit)
    # An unresolved third dose cuts the run to two doses, below MIN_DOSES.
    phases[2] = (phases[2][0], 0.02, 0.01, 0.02)
    _require(sign.rate(times, phases)["khz"] is None)


def test_decisions_withhold_below_the_replica_floor() -> None:
    times = [0.0, 7.0, 14.0, 21.0, 28.0]
    still = [(0.0, 0.02, 0.5, 0.02)] * len(times)
    fit = sign.rate(times, still)
    rows = [
        {
            "orbit": fit,
            "one": fit,
            "sixteen": fit,
            "echo": dict.fromkeys(("moved_rad", "returned_rad"), 0.0) | {"moved_se": 0.1, "returned_se": 0.1},
        }
    ] * (sign.MIN_REPLICAS - 1)
    out = sign.decide(rows)
    _require(out["d1_slope"]["verdict"].startswith("withheld"), out)
    _require(out["d2_sign"]["verdict"].startswith("withheld"), out)
    _require(out["d3_echo"]["verdict"].startswith("withheld"), out)


def _design_record() -> dict[str, Any]:
    values = json.loads((sign.ROOT / sign.DESIGN_DRAW).read_text(encoding="utf-8"))["values"]
    members = sign.DESIGN_MEMBERS
    return {
        "seed_simulator": values[1],
        "state": "planned",
        "shots": sign.DESIGN_SHOTS,
        "policy": dict(sign.EXPECTED_POLICY)
        | {"rep_delay_seconds": 2e-05, "design": copy.deepcopy(sign.EXPECTED_DESIGN)},
        "optimization": {
            "selected": "c",
            "searched_routed_sets": 1,
            "candidates": [{"name": "c", "feasible": True, "estimated_charge_seconds": 15.4}],
        },
        "groups": [
            {"backend": "ibm_kingston", "calibration": "t", "replicas": [{}] * 19, "seed_transpiler": values[0]}
        ],
        "execution_pubs": [{"name": f"p{k}", "components": [{}]} for k in range(members)],
        "budget_plan": {"jobs": [{"kind": "dynamic", "pubs": members}]},
        "code_commit": {"head": "abc", "sources_modified": False},
        "seed_source": [{"flag": flag, "sources": sources} for flag, sources in sign.DESIGN_SEED_SOURCES.items()],
    }


def test_preflight_admits_the_design_and_refuses_each_departure(tmp_path: Path) -> None:
    def check(record: dict[str, Any]) -> dict[str, Any]:
        (tmp_path / "record.json").write_text(json.dumps(record))
        return sign.preflight(tmp_path, "abc")

    _require(check(_design_record())["replicas"] == 19)
    fallback = _design_record()
    fallback["policy"]["rep_delay_seconds"] = 5e-05
    _require(check(fallback)["rep_delay_seconds"] == 5e-05)
    departures = [
        lambda r: r.update(shots=8192),
        lambda r: r["policy"].update(rep_delay_seconds=1e-04),
        lambda r: r["groups"][0].update(replicas=[{}] * 7),
        lambda r: r["policy"]["design"].update(window_doses=[0, 3504, 7008]),
        lambda r: r["policy"]["design"].pop("detuning_sign"),
        lambda r: r["policy"]["design"].update(init_herald=False),
        lambda r: r["policy"]["design"].update(model_shots=131072),
        lambda r: r["policy"].update(max_execution_seconds=60),
        lambda r: r["policy"].update(twirl=True),
        lambda r: r.update(seed_source=[]),
        lambda r: r["optimization"]["candidates"][0].update(estimated_charge_seconds=41.0),
        lambda r: r["optimization"].update(searched_routed_sets=2),
        lambda r: r["groups"][0].update(backend="ibm_torino"),
        lambda r: r["execution_pubs"].pop(),
        lambda r: r["budget_plan"]["jobs"].append({"kind": "static", "pubs": 1}),
        lambda r: r["code_commit"].update(sources_modified=True),
        lambda r: r["code_commit"].update(head="def"),
        lambda r: r.update(seed_simulator=r["seed_simulator"] + 1),
        lambda r: r["groups"][0].update(seed_transpiler=r["groups"][0]["seed_transpiler"] + 8),
        lambda r: r.update(state="approval_required"),
    ]
    for k, mutate in enumerate(departures):
        record = _design_record()
        mutate(record)
        with pytest.raises(ValueError):
            check(record)
            raise AssertionError(f"departure {k} passed the preflight")


def _bits(probabilities: list[float], shots: int) -> list[int]:
    """Outcomes spread evenly through the shots with counts rounded from probabilities, so blocks carry no drift."""
    counts = [round(p * shots) for p in probabilities]
    counts[0] += shots - sum(counts)
    out: list[int] = []
    for outcome, count in enumerate(counts):
        out.extend([outcome] * count)
    return [out[(k * 7919) % shots] for k in range(shots)]


def _signed_run(tmp_path: Path) -> list[float]:
    """A run directory of six replicas whose orbit turns at f_sixteen - f_one; returns the replicas' orbit rates."""
    import qpe_diagnostics

    doses = sign.DESIGN_DOSES
    replicas = 6
    shots = 4096
    f_one = [3.0 * r - 7.0 for r in range(replicas)]
    f_six = [5.0 - 2.0 * r for r in range(replicas)]
    names = [[f"g0_r{r}_phase", f"g0_r{r}_herald"] for r in range(replicas)]
    pubs: list[dict[str, Any]] = []
    raw = tmp_path / "raw" / "job"
    raw.mkdir(parents=True)
    index: dict[str, str] = {}

    def orbit_law(theta: float) -> list[float]:
        c = 0.5 * math.cos(theta)
        x0, x1 = 0.1 + c / 2, 0.1 - c / 2
        return [(1 + x0) / 4, (1 + x1) / 4, (1 - x0) / 4, (1 - x1) / 4]

    def ramsey_law(value: float) -> list[float]:
        return [(1 + value) / 2, 0.0, (1 - value) / 2, 0.0]

    def emit(member: str, laws: list[list[float]]) -> None:
        pub = f"pub_{len(pubs):02d}"
        pubs.append({"name": pub, "components": [{"member": member, "registers_by_replica": names}]})
        regs: dict[str, Any] = {}
        for r, law in enumerate(laws):
            outcomes = _bits(law, shots)
            regs[names[r][0]] = {"bitstrings": [format(o, "02b") for o in outcomes]}
            regs[names[r][1]] = {"bitstrings": ["0001" if k % 97 == 0 else "0000" for k in range(shots)]}
        payload = json.dumps({"pub_name": pub, "registers": regs}).encode()
        (raw / f"{pub}.json").write_bytes(payload)
        index[f"{pub}.json"] = hashlib.sha256(payload).hexdigest()

    def theta(r: int, d: int) -> float:
        return 0.3 + 2 * math.pi * (f_six[r] - f_one[r]) * d * sign.DT_SECONDS * 1e3

    for variant, shift in (("window_dose", 0.0), ("window_dose_y", -math.pi / 2)):
        for d in doses:
            emit(
                qpe_diagnostics.n21_dose_name(variant, d, False),
                [orbit_law(theta(r, d) + shift) for r in range(replicas)],
            )
    for variant, shift in (("window_dose_echo", 0.0), ("window_dose_echo_y", -math.pi / 2)):
        emit(
            qpe_diagnostics.n21_dose_name(variant, doses[-1], False), [orbit_law(0.3 + shift) for _ in range(replicas)]
        )
    for role, rates in (("one", f_one), ("sixteen", f_six)):
        for quadrature, part in (("x", math.cos), ("y", math.sin)):
            for d in doses:
                laws = [ramsey_law(0.8 * part(2 * math.pi * f * d * sign.DT_SECONDS * 1e3)) for f in rates]
                emit(qpe_diagnostics.n21_work_ramsey_name(role, quadrature, d), laws)
    (raw / "index.json").write_text(json.dumps({"files": index}))
    record = {
        "execution_pubs": pubs,
        "shots": shots,
        "family_configuration": {"window_doses": doses, "detuning_sign": True},
        "groups": [
            {"replicas": [{"initial_layout": [4 * r, 4 * r + 1, 4 * r + 2, 4 * r + 3]} for r in range(replicas)]}
        ],
    }
    (tmp_path / "record.json").write_text(json.dumps(record))
    (tmp_path / "collect.json").write_text(json.dumps([{"jobs": {"job": {}}}, {"measured": {}}]))
    return [b - a for a, b in zip(f_one, f_six, strict=True)]


def test_analyze_reads_the_signed_rates_from_shot_registers(tmp_path: Path) -> None:
    expected = _signed_run(tmp_path)
    out = json.loads(json.dumps(sign.analyze(tmp_path)))
    rates = [row["orbit"]["khz"] for row in out["replicas"]]
    _require(all(abs(a - b) < 0.2 for a, b in zip(rates, expected, strict=True)), (rates, expected))
    _require(out["d1_slope"]["verdict"].startswith("holds"), out["d1_slope"])
    _require(out["d2_sign"]["verdict"].startswith("holds"), out["d2_sign"])
    _require(out["d3_echo"]["verdict"].startswith("holds"), out["d3_echo"])
    _require(out["replicas"][1]["qubit_one"] == 5 and out["replicas"][1]["qubit_sixteen"] == 7, out["replicas"][1])
