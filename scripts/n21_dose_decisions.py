"""Preregistered decisions D1-D3 of an N=21 orbit window-dose sweep against its idle-padded exact model.

The run directory holds the submitted record (record.json: observable contracts, shots), the collected result
(collect.json: each member's measured law per replica) and the scheduled-idle replay (idle-replay.json from
scripts/scheduled_idle_replay.py: exact_laws.idle_padded, each replica's exact branch-resolved law with the explicit
doses and the service-scheduled idle charged under the execution Target). A contract's measured value is the signed
sum of its members' scores; its shot variance is the sum over members of (E[w^2] - E[w]^2) / shots for score vector
w. A pooled value is the replica mean, with sigma sqrt(sum s^2) / n over independent replicas.

A collection whose group carries comparisons_withheld (its PUBs did not all run under one calibration) is refused.

Decisions (docs/design/n21-orbit-window-dose-envelope.md):
- D1: the pooled plain contrast at the largest dose lies below the dose-0 contrast at one-sided 95 percent.
- D2: at every nonzero dose d, the pooled plain dose response, measured(d) - measured(0) against model(d) - model(0),
  lies within the Bonferroni two-sided 95 percent bound over the nonzero doses (z = 2.638 at six). A
  dose-independent level offset (readout, initialization, the model residual) cancels in the response.
- D3: at the largest dose, each replica's excess echo gain, (echo - plain) measured minus the same in the model, is
  tested across replicas by a chi-square of its z with one degree of freedom per replica at 5 percent, because a
  static detuning moves each replica's plain arm with the sign of that replica's detuning and a replica mean
  cancels it. A rejection reads as coherent detuning refocused by the echo only when the echo arm's own dose
  response agrees with the model across replicas (chi-square at 5 percent) and D2 holds at that dose; an effective
  T1 off the Target's moves the echo arm as well.

Preflight. --preflight RECORD_DIR checks a fresh dry-run record against the approved envelope before it is
submitted: a planned n21-orbit-rca window-dose record on an approved backend with the envelope's doses, shots,
repetition delay (DESIGN_REP_DELAYS), ceiling, replica floor and count, twirling and dynamical decoupling off, the
cross-group buffer, the QRNG seed references and a clean source tree at the checked-out commit. The calibration,
layout and model values are the record's own; they are what the fresh plan adapts.

Usage: "$PYTHON" scripts/n21_dose_decisions.py RUN_DIR [--out FILE]
       "$PYTHON" scripts/n21_dose_decisions.py --preflight RECORD_DIR [--head COMMIT]
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
# The approved envelope a fresh dry-run record must carry (docs/design/n21-orbit-window-dose-envelope.md).
DESIGN_DOSES = [0, 1752, 3500, 5252, 7000, 10500, 14000]
DESIGN_SHOTS = 8192
DESIGN_REP_DELAYS = (2e-05, 5e-05)
DESIGN_CEILING_SECONDS = 30.0
DESIGN_MIN_REPLICAS = 4
DESIGN_REPLICA_FLOOR = 0.45
DESIGN_BACKENDS = {"ibm_fez", "ibm_kingston", "ibm_marrakesh"}
DESIGN_SEED_SOURCES = {
    "--seed-transpiler": ["qrng:docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json#0"],
    "--seed-simulator": ["qrng:docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json#1"],
}
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


Row = tuple[float, float, float]


def pool(rows: Sequence[Row]) -> Row:
    """(replica-mean measured value, its shot-noise sigma, replica-mean model value)."""
    value, sigma = pooled([(v, s) for v, s, _ in rows])
    return value, sigma, sum(m for _, _, m in rows) / len(rows)


def chi_square(z: Sequence[float]) -> dict[str, float]:
    statistic = sum(x * x for x in z)
    return {"statistic": statistic, "df": float(len(z)), "p": float(stats.chi2.sf(statistic, len(z)))}


def decide(replicas: Mapping[str, Sequence[Row]]) -> dict[str, Any]:
    """D1-D3 from each contract's per-replica (measured, sigma, model) rows."""
    doses, plain, echo = arms(list(replicas))
    count = {len(rows) for rows in replicas.values()}
    require(len(count) == 1, f"contracts hold different replica counts {sorted(count)}")
    pooled_rows = {name: pool(rows) for name, rows in replicas.items()}
    nonzero = doses[1:]
    bound = float(stats.norm.ppf(1 - 0.025 / len(nonzero)))
    top = doses[-1]
    out: dict[str, Any] = {"doses_dt": doses, "replicas": count.pop(), "bonferroni_z": bound, "arms": {}}
    for dose in doses:
        for kind, name in (("plain", plain[dose]), ("echo", echo.get(dose))):
            if name is None:
                continue
            value, sigma, model = pooled_rows[name]
            # The level offset is descriptive: a dose-independent offset (readout, initialization, the residual of
            # the earlier orbit run) leaves every dose response unchanged.
            out["arms"][name] = {
                "dose_dt": dose,
                "kind": kind,
                "measured": value,
                "sigma": sigma,
                "model": model,
                "level_z": (value - model) / sigma,
            }
    zero = pooled_rows[plain[0]]
    top_plain = pooled_rows[plain[top]]
    drop = top_plain[0] - zero[0]
    drop_sigma = math.hypot(top_plain[1], zero[1])
    out["d1_idle_response"] = {
        "difference": drop,
        "upper": drop + ONE_SIDED * drop_sigma,
        "holds": drop + ONE_SIDED * drop_sigma < 0,
    }
    responses = {}
    for dose in nonzero:
        v, s, m = pooled_rows[plain[dose]]
        sigma = math.hypot(s, zero[1])
        responses[str(dose)] = {
            "measured": v - zero[0],
            "model": m - zero[2],
            "sigma": sigma,
            "z": ((v - zero[0]) - (m - zero[2])) / sigma,
        }
    out["d2_dose_response"] = {
        "responses": responses,
        "holds": all(abs(r["z"]) <= bound for r in responses.values()),
        "holds_at_largest_dose": abs(responses[str(top)]["z"]) <= bound,
    }
    # D3 per replica: a static detuning shifts each replica's plain arm by a first-order term whose sign follows
    # that replica's detuning, so a replica mean cancels it; the echo refocuses it. The excess echo gain is tested
    # across replicas by a chi-square of its per-replica z, and the echo arm's own dose response separates a
    # refocused detuning (echo agrees with the model) from an effective T1 that departs (echo departs as well).
    excess_z, echo_z, rows_out = [], [], []
    for (ep, es, em), (pp, ps, pm), (zp, zs, zm) in zip(
        replicas[echo[top]], replicas[plain[top]], replicas[plain[0]], strict=True
    ):
        excess = (ep - pp) - (em - pm)
        excess_sigma = math.hypot(es, ps)
        echo_sigma = math.hypot(es, zs)
        excess_z.append(excess / excess_sigma)
        echo_z.append(((ep - zp) - (em - zm)) / echo_sigma)
        rows_out.append({"excess": excess, "sigma": excess_sigma, "z": excess_z[-1], "echo_response_z": echo_z[-1]})
    e_value, e_sigma, e_model = pooled_rows[echo[top]]
    excess_pooled = (e_value - top_plain[0]) - (e_model - top_plain[2])
    excess_test = chi_square(excess_z)
    echo_test = chi_square(echo_z)
    if excess_test["p"] >= 0.05:
        verdict = "consistent with the model's echo gain"
    elif echo_test["p"] < 0.05:
        verdict = "inconclusive: the echo arm departs from the model, as an effective T1 off the Target's would"
    elif not out["d2_dose_response"]["holds_at_largest_dose"]:
        verdict = "inconclusive: the pooled plain dose response departs from the model at the largest dose"
    else:
        verdict = "coherent detuning refocused by the echo beyond the model"
    out["d3_coherent_detuning"] = {
        "dose_dt": top,
        "per_replica": rows_out,
        "excess_chi_square": excess_test,
        "echo_response_chi_square": echo_test,
        "pooled_excess": excess_pooled,
        "pooled_excess_sigma": math.hypot(e_sigma, top_plain[1]),
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
    contracts = [c for c in record["observable_contracts"] if NAME.fullmatch(c["name"])]
    shots = int(record["shots"])
    per_replica = replica_values(contracts, laws, shots)
    exact = exact_replica_values(contracts, replay["exact_laws"]["idle_padded"])
    model = replay["contracts"]["idle_padded_exact"]
    rows: dict[str, list[Row]] = {}
    for name, measured_rows in per_replica.items():
        require(len(exact[name]) == len(measured_rows), f"{name}: the replay holds a different replica count")
        require(
            abs(sum(exact[name]) / len(exact[name]) - model[name]) < 1e-9,
            f"{name}: the replay's replica laws do not average to its idle-padded exact contract",
        )
        rows[name] = [(v, s, m) for (v, s), m in zip(measured_rows, exact[name], strict=True)]
    out = decide(rows)
    out["run"] = run_dir.name
    out["model_source"] = "idle-replay.json exact_laws.idle_padded, per replica"
    return out


def preflight(record_dir: Path, head: str | None = None) -> dict[str, Any]:
    """The fresh record's binding facts, after requiring every invariant of the approved envelope."""
    record = json.loads((record_dir / "record.json").read_text(encoding="utf-8"))
    policy = record["policy"]
    design = policy["design"]
    require(record["state"] == "planned", f"{record_dir}: state {record['state']}, not planned")
    require(design.get("family") == "n21-orbit-rca", f"family {design.get('family')}")
    require(design.get("window_doses") == DESIGN_DOSES, f"doses {design.get('window_doses')}, not {DESIGN_DOSES}")
    require(design.get("init_herald") is True, "the design runs without the initialization herald")
    require(int(record["shots"]) == DESIGN_SHOTS, f"shots {record['shots']}, not {DESIGN_SHOTS}")
    require(policy.get("rep_delay_seconds") in DESIGN_REP_DELAYS, f"repetition delay {policy.get('rep_delay_seconds')}")
    require(
        float(design.get("max_total_execution_seconds", math.inf)) <= DESIGN_CEILING_SECONDS
        and float(policy.get("max_execution_seconds", math.inf)) <= DESIGN_CEILING_SECONDS,
        "a ceiling exceeds the design's 30 s",
    )
    optimization = record["optimization"]
    chosen = [c for c in optimization["candidates"] if c["name"] == optimization["selected"]]
    require(len(chosen) == 1 and chosen[0]["feasible"], "the record selects no feasible candidate")
    charge = float(chosen[0]["estimated_charge_seconds"])
    require(charge <= DESIGN_CEILING_SECONDS, f"estimated charge {charge} s exceeds the ceiling")
    groups = record["groups"]
    require(len(groups) == 1, f"{len(groups)} groups")
    replicas = len(groups[0]["replicas"])
    require(replicas >= DESIGN_MIN_REPLICAS, f"{replicas} replicas, below the design's {DESIGN_MIN_REPLICAS}")
    sources = {row["flag"]: row["sources"] for row in record.get("seed_source") or []}
    require(sources == DESIGN_SEED_SOURCES, f"seed sources {sources}")
    require(groups[0]["backend"] in DESIGN_BACKENDS, f"backend {groups[0]['backend']} lies outside the envelope")
    require(policy.get("replica_floor") == DESIGN_REPLICA_FLOOR, f"replica floor {policy.get('replica_floor')}")
    require(policy.get("twirl") is False and not policy.get("dd"), "twirling or dynamical decoupling is on")
    require(policy.get("cross_group_buffer") is True, "the plan runs without the cross-group buffer")
    commit = record.get("code_commit") or {}
    require(commit.get("sources_modified") is False, "the plan was made from a modified source tree")
    if head is not None:
        require(commit.get("head") == head, f"the plan was made at {commit.get('head')}, not the checked-out {head}")
    return {
        "record": record_dir.name,
        "backend": groups[0]["backend"],
        "calibration": groups[0]["calibration"],
        "replicas": replicas,
        "rep_delay_seconds": policy["rep_delay_seconds"],
        "estimated_charge_seconds": charge,
    }


def self_test() -> str:
    doses = (0, 3500, 7000, 14000)
    model: dict[str, float] = {}
    for d in doses:
        model[f"n21_orbit_window_dose_d{d}_feedback_contrast"] = 0.22 - 0.0000168 * d
        if d:
            model[f"n21_orbit_window_dose_echo_d{d}_feedback_contrast"] = 0.22 - 0.0000112 * d
    plain_top = "n21_orbit_window_dose_d14000_feedback_contrast"
    echo_top = "n21_orbit_window_dose_echo_d14000_feedback_contrast"

    def sweep(shift: Any) -> dict[str, list[Row]]:
        return {name: [(m + shift(name, r), 0.008, m) for r in range(4)] for name, m in model.items()}

    agree = decide(sweep(lambda name, r: 0.0))
    require(agree["d1_idle_response"]["holds"] and agree["d2_dose_response"]["holds"], f"agreement: {agree}")
    require(agree["d3_coherent_detuning"]["verdict"].startswith("consistent"), "an exact sweep reads as an excess")
    offset = decide(sweep(lambda name, r: 0.03))
    require(offset["d2_dose_response"]["holds"], "a dose-independent level offset fails the dose-response test")
    # Detuning of alternating sign: each replica's plain arm moves, the replica mean does not, the echo agrees.
    detuned = decide(sweep(lambda name, r: (0.06 if r % 2 else -0.06) if name == plain_top else 0.0))
    coherent = detuned["d3_coherent_detuning"]["verdict"]
    require(coherent.startswith("coherent"), f"replica-alternating detuning reads {coherent}")
    # An effective T1 off the Target's lowers the plain and the echo arm at the top dose in every replica.
    relaxed = decide(sweep(lambda name, r: -0.05 if name in (plain_top, echo_top) else 0.0))
    require(not relaxed["d2_dose_response"]["holds"], "a plain dose response 4 sigma off the model passes D2")
    require(not relaxed["d3_coherent_detuning"]["verdict"].startswith("coherent"), "a T1 departure reads coherent")
    flat = {name: [(0.2, 0.008, m)] * 4 for name, m in model.items()}
    require(not decide(flat)["d1_idle_response"]["holds"], "a flat sweep shows an idle response")
    return (
        "n21 dose decisions: agreement, level offset, replica-alternating detuning, T1 departure and flat-sweep "
        "cases decide as stated"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path, nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--preflight", type=Path, metavar="RECORD_DIR")
    parser.add_argument("--head", help="with --preflight: the commit the plan must have been made at")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    if args.preflight is not None:
        print(json.dumps(preflight(args.preflight, args.head), sort_keys=True))
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
