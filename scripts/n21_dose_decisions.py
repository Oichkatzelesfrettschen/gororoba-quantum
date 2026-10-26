"""Preregistered decisions D1-D3 of an N=21 orbit window-dose sweep against its idle-padded exact model.

The run directory holds the dry-run record (record.json: observable contracts, shots), the collected result
(collect.json: each member's measured law, one replica) and the scheduled-idle replay (idle-replay.json from
scripts/scheduled_idle_replay.py: contracts.idle_padded_exact, the exact branch-resolved law with the explicit doses
and the service-scheduled idle charged under the execution Target). A contract's measured value is the signed sum of
its members' scores; its shot variance is the sum over members of (E[w^2] - E[w]^2) / shots for score vector w.

A collection whose group carries comparisons_withheld (its PUBs did not all run under one calibration) is refused.

Decisions (the run's DOSE_CASE.md):
- D1: the plain contrast at the largest dose lies below the dose-0 contrast at one-sided 95 percent.
- D2: every plain arm's z = (measured - model) / sigma lies within the Bonferroni two-sided 95 percent bound over
  the plain doses (z = 2.498 at four doses).
- D3: the excess echo gain at the largest dose, (echo - plain) measured minus the same in the model, is tested
  one-sided at 95 percent; a positive lower bound reads as coherent detuning only when D2 holds at that dose, since
  an echo gain beyond the model can also come from an effective T1 that departs from the Target's.

Usage: "$PYTHON" scripts/n21_dose_decisions.py RUN_DIR [--out FILE]
       "$PYTHON" scripts/n21_dose_decisions.py --self-test
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ONE_SIDED = float(stats.norm.ppf(0.95))
NAME = re.compile(r"n21_orbit_window_dose(?P<echo>_echo)?_d(?P<dose>\d+)_feedback_contrast")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def replica_values(
    contracts: Sequence[Mapping[str, Any]], laws: Mapping[str, Sequence[Sequence[float]]], shots: int
) -> dict[str, list[tuple[float, float]]]:
    """{contract name: [(value, sigma) per replica]} from each member's measured law per replica at shots."""
    out: dict[str, list[tuple[float, float]]] = {}
    for contract in contracts:
        count = {len(laws[term["member"]]) for term in contract["terms"]}
        require(len(count) == 1, f"{contract['name']}: its members hold different replica counts {sorted(count)}")
        rows = []
        for r in range(count.pop()):
            value = 0.0
            variance = 0.0
            for term in contract["terms"]:
                law = np.asarray(laws[term["member"]][r], dtype=float)
                law = law / law.sum()
                w = np.asarray(term["values"], dtype=float)
                mean = float(w @ law)
                value += term["sign"] * mean
                variance += (float((w * w) @ law) - mean * mean) / shots
            rows.append((value, math.sqrt(variance)))
        out[contract["name"]] = rows
    return out


def pooled(rows: Sequence[tuple[float, float]]) -> tuple[float, float]:
    """The replica mean, as the collector's contract value is, and its shot-noise sigma."""
    n = len(rows)
    return sum(v for v, _ in rows) / n, math.sqrt(sum(s * s for _, s in rows)) / n


def measured(
    contracts: Sequence[Mapping[str, Any]], laws: Mapping[str, Sequence[Sequence[float]]], shots: int
) -> dict[str, tuple[float, float]]:
    """{contract name: (replica-mean value, sigma)} from each member's measured laws at shots."""
    return {name: pooled(rows) for name, rows in replica_values(contracts, laws, shots).items()}


def exact_replica_values(
    contracts: Sequence[Mapping[str, Any]], laws: Mapping[str, Sequence[Sequence[float]]]
) -> dict[str, list[float]]:
    """{contract name: [model value per replica]} from the idle-padded exact laws of each replica."""
    return {name: [v for v, _ in rows] for name, rows in replica_values(contracts, laws, 1).items()}


def arms(names: Sequence[str]) -> tuple[list[int], dict[int, str], dict[int, str]]:
    """Sorted doses with each dose's plain and echo contract names."""
    plain: dict[int, str] = {}
    echo: dict[int, str] = {}
    for name in names:
        match = NAME.fullmatch(name)
        if match is None:
            continue
        (echo if match["echo"] else plain)[int(match["dose"])] = name
    doses = sorted(plain)
    require(len(doses) >= 3 and doses[0] == 0, f"a dose sweep needs dose 0 and two more plain arms, not {doses}")
    require(set(echo) == set(doses[1:]), f"echo arms {sorted(echo)} do not match the nonzero doses {doses[1:]}")
    return doses, plain, echo


def decide(values: Mapping[str, tuple[float, float]], model: Mapping[str, float]) -> dict[str, Any]:
    doses, plain, echo = arms(list(values))
    bound = float(stats.norm.ppf(1 - 0.025 / len(doses)))
    top = doses[-1]
    out: dict[str, Any] = {"doses_dt": doses, "bonferroni_z": bound, "arms": {}}
    for dose in doses:
        for kind, name in (("plain", plain[dose]), ("echo", echo.get(dose))):
            if name is None:
                continue
            value, sigma = values[name]
            out["arms"][name] = {
                "dose_dt": dose,
                "kind": kind,
                "measured": value,
                "sigma": sigma,
                "model": model[name],
                "z": (value - model[name]) / sigma,
            }
    (top_value, top_sigma), (zero_value, zero_sigma) = values[plain[top]], values[plain[0]]
    drop = top_value - zero_value
    drop_sigma = math.hypot(top_sigma, zero_sigma)
    out["d1_idle_response"] = {
        "difference": drop,
        "upper": drop + ONE_SIDED * drop_sigma,
        "holds": drop + ONE_SIDED * drop_sigma < 0,
    }
    z_plain = {dose: out["arms"][plain[dose]]["z"] for dose in doses}
    out["d2_incoherent_model"] = {
        "z": {str(d): z for d, z in z_plain.items()},
        "holds": all(abs(z) <= bound for z in z_plain.values()),
        "holds_at_largest_dose": abs(z_plain[top]) <= bound,
    }
    (echo_value, echo_sigma) = values[echo[top]]
    gain = echo_value - top_value
    model_gain = model[echo[top]] - model[plain[top]]
    excess = gain - model_gain
    sigma = math.hypot(echo_sigma, top_sigma)
    low, high = excess - ONE_SIDED * sigma, excess + ONE_SIDED * sigma
    if low > 0:
        verdict = (
            "coherent detuning refocused beyond the model"
            if out["d2_incoherent_model"]["holds_at_largest_dose"]
            else "inconclusive: the plain arm departs from the model at the largest dose"
        )
    elif high < 0:
        verdict = "the echo costs more than it refocuses"
    else:
        verdict = "unresolved"
    out["d3_coherent_detuning"] = {
        "measured_gain": gain,
        "model_gain": model_gain,
        "excess": excess,
        "lower": low,
        "upper": high,
        "verdict": verdict,
    }
    return out


def analyze(run_dir: Path) -> dict[str, Any]:
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    collected = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    replay = json.loads((run_dir / "idle-replay.json").read_text(encoding="utf-8"))
    groups = [g for g in collected if isinstance(g, dict) and "measured" in g]
    require(len(groups) == 1, f"{run_dir}: collect.json holds {len(groups)} measured groups, not one")
    # The collector withholds comparisons across PUBs whose calibration differed or changed during their shots
    # (live_run._comparisons_withheld); a dose response read across such PUBs would include the calibration change.
    withheld = groups[0].get("comparisons_withheld")
    require(withheld is None, f"{run_dir}: the collector withheld the sweep's comparisons: {withheld}")
    laws = groups[0]["measured"]
    contracts = record["observable_contracts"]
    shots = int(record["shots"])
    values = measured(contracts, laws, shots)
    model = replay["contracts"]["idle_padded_exact"]
    require(set(values) <= set(model), "idle-replay.json lacks an idle-padded exact value for a contract")
    out = decide(values, model)
    # Each replica against its own exact model, for the spread across qubit sets the pooled test averages over.
    per_replica = replica_values(contracts, laws, shots)
    exact = exact_replica_values(contracts, replay["exact_laws"]["idle_padded"])
    out["replicas"] = {
        name: [
            {"measured": v, "sigma": s, "model": m, "z": (v - m) / s}
            for (v, s), m in zip(per_replica[name], exact[name], strict=True)
        ]
        for name in per_replica
    }
    out["run"] = run_dir.name
    out["model_source"] = "idle-replay.json contracts.idle_padded_exact"
    return out


def self_test() -> str:
    doses = (0, 3500, 7000, 14000)
    model = {}
    for d in doses:
        model[f"n21_orbit_window_dose_d{d}_feedback_contrast"] = 0.22 - 0.0000168 * d
        if d:
            model[f"n21_orbit_window_dose_echo_d{d}_feedback_contrast"] = 0.22 - 0.0000112 * d
    exact = {name: (value, 0.008) for name, value in model.items()}
    agree = decide(exact, model)
    require(agree["d1_idle_response"]["holds"] and agree["d2_incoherent_model"]["holds"], f"agreement: {agree}")
    require(agree["d3_coherent_detuning"]["verdict"] == "unresolved", "an echo gain equal to the model's resolves")
    lifted = dict(exact)
    echo_top = "n21_orbit_window_dose_echo_d14000_feedback_contrast"
    lifted[echo_top] = (model[echo_top] + 0.06, 0.008)
    coherent = decide(lifted, model)["d3_coherent_detuning"]["verdict"]
    require(coherent.startswith("coherent"), f"an echo gain 0.06 above the model reads {coherent}")
    strayed = dict(lifted)
    plain_top = "n21_orbit_window_dose_d14000_feedback_contrast"
    strayed[plain_top] = (model[plain_top] + 0.05, 0.008)
    confounded = decide(strayed, model)
    require(not confounded["d2_incoherent_model"]["holds"], "a plain arm 6 sigma off the model passes D2")
    flat = {name: (0.2, 0.008) for name in model}
    require(not decide(flat, model)["d1_idle_response"]["holds"], "a flat sweep shows an idle response")
    return "n21 dose decisions: agreement, coherent excess, plain-arm departure and flat-sweep cases decide as stated"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path, nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    if args.run_dir is None:
        parser.error("a run directory or --self-test is required")
    text = json.dumps(analyze(args.run_dir), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
