"""Preregistered decisions of the N=21 orbit detuning-sign test: the orbit's phase rate against two Ramsey offsets.

Data. The run directory holds the submitted record (record.json), the collected result (collect.json) and the
lossless shot-ordered registers --collect writes under raw/<job_id>/. The group is n21-orbit-rca with window_doses
and detuning_sign (diagnostic_experiments.n21_detuning_sign_group): at every dose d the free-idle window-dose member
without feed-forward in two quadratures (window_dose reads the cosine, window_dose_y the sine of the work
superposition's relative phase), the echo member in both quadratures at the largest dose, and Ramsey arms of the
work bits for 1 and for 16 in X and Y over the same idles. Each PUB packs every replica, and a shot enters a
replica's estimate when that replica's initialization herald reads all zeros.

Estimates. From an orbit member's herald-kept counts n_k over the phase outcome k = b0 + 2 b1, the control's
second-round contrast given b0 is x0 = (n0 - n2) / (n0 + n2) and x1 = (n1 - n3) / (n1 + n3), and the coherence
c = x0 - x1 cancels the relaxation offset both branches share (the relaxation of the work excitation sends the
control to 0 in either branch). The cosine member gives c, the sine member s; a Ramsey member gives
(n0 - n2) / (n0 + n2), so X and Y. A phase is atan2(s, c) with the delta-method variance
(s^2 var c + c^2 var s) / (c^2 + s^2)^2 under binomial counts. Phases are unwrapped along the dose order over the
leading run of doses whose amplitude exceeds RESOLVED times its standard error, and a weighted line through them
gives the rate f in kHz, its standard error scaled by sqrt(max(1, chi2/df)). A rate needs MIN_DOSES such doses.

Prediction. A frame offset turns each work bit's Ramsey phase by 2 pi f t, and the orbit's relative phase by the
offset of the bit for 16 minus that of the bit for 1, in the same sense (tests/gororoba_quantum/test_detuning_sign.py),
so f_orbit = f_sixteen - f_one replica by replica.

Decisions (docs/design/n21-orbit-detuning-sign-envelope.md):
- D1, slope: the weighted line through the origin of f_orbit on f_sixteen - f_one over the replicas with three
  rates, weights 1 / (var f_orbit + var f_one + var f_sixteen), its standard error scaled by sqrt(max(1, chi2/df)).
  The account holds when the 95 percent interval lies inside [1 - SLOPE_BAND, 1 + SLOPE_BAND] and is refuted when
  it misses that band; it needs MIN_REPLICAS replicas.
- D2, sign: among replicas whose prediction and orbit rate both exceed three standard errors, the fraction whose
  signs agree. At least SIGN_HOLDS holds, below SIGN_REFUTES refutes (random signs give one half); it needs
  MIN_REPLICAS resolved replicas.
- D3, echo: the echo's phase at the largest dose minus the free-idle phase at dose 0, per replica, against three
  standard errors. At least ECHO_HOLDS of the replicas whose free-idle phase moved by more than three standard
  errors over the sweep (the fitted rate times the largest dose) returning within three standard errors reads as
  precession during the dose.
- D1 also reports the weighted line with a free intercept, and every rate its largest phase step between doses.
- Every replica's rates, the per-qubit offsets and their standard errors are reported, not decided.

Preflight. --preflight RECORD_DIR checks a fresh dry-run record against the approved envelope before it is
submitted: the full design projection (EXPECTED_DESIGN), the planning policy (EXPECTED_POLICY), one dynamic job of
one PUB per member, one routed candidate, an envelope backend, the replica count, the shots, the repetition delay,
the ceilings, the seed draw and the commit. The calibration, layout and model values are the record's own; they are
what the fresh plan adapts.

Usage: "$PYTHON" scripts/n21_detuning_sign.py RUN_DIR [--out FILE]
       "$PYTHON" scripts/n21_detuning_sign.py --preflight RECORD_DIR [--head COMMIT]
       "$PYTHON" scripts/n21_detuning_sign.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

Z95 = 1.959963984540054
RESOLVED = 3.0
MIN_DOSES = 4
MIN_REPLICAS = 6
SLOPE_BAND = 0.2
SIGN_HOLDS = 0.9
SIGN_REFUTES = 0.75
ECHO_HOLDS = 0.8
DT_SECONDS = 4e-9
# docs/evidence/outshift_qrng/draw-2026-10-27T154654Z.json index 2.
SELF_TEST_SEED = 39927
ROLES = ("one", "sixteen")

# The approved envelope a fresh dry-run record must carry (docs/design/n21-orbit-detuning-sign-envelope.md).
DESIGN_DOSES = [0, 1752, 3504, 5256, 7008, 8760, 10512, 12264, 14016]
DESIGN_SHOTS = 4096
DESIGN_REP_DELAYS = (2e-05, 5e-05)
DESIGN_CEILING_SECONDS = 40.0
DESIGN_MIN_REPLICAS = 8
DESIGN_BACKENDS = {"ibm_fez", "ibm_kingston", "ibm_marrakesh"}
DESIGN_DRAW = "docs/evidence/outshift_qrng/draw-2026-10-27T154654Z.json"
DESIGN_DRAW_SHA256 = "d1acdc9c63881c068cde2d2ea1dcc28fbf3e60b31e7a3ceaa639609baf86aef5"
DESIGN_SEED_SOURCES = {
    "--seed-transpiler": [f"qrng:{DESIGN_DRAW}#0"],
    "--seed-simulator": [f"qrng:{DESIGN_DRAW}#1"],
}
EXPECTED_DESIGN: dict[str, Any] = {
    "alpha": 0.05,
    "classical_latency_us": 20.0,
    "cost_scenarios": [],
    "detuning_sign": True,
    "family": "n21-orbit-rca",
    "init_herald": True,
    "job_overhead_seconds": 2.3,
    "max_total_execution_seconds": DESIGN_CEILING_SECONDS,
    "model_method": "sampled",
    "model_shots": 32768,
    "objective": "minimum_charge",
    "optimize": True,
    "optimizer_candidates": 1,
    "patch_qubits": None,
    "power": 0.8,
    "precision": 0.09,
    "replica_tiers": [24],
    "replica_variance_bound": None,
    "reserve_seconds": 0.0,
    "shot_allocation": "uniform",
    "shot_tiers": [DESIGN_SHOTS],
    "simulation_alpha": 0.01,
    "window_doses": DESIGN_DOSES,
}
EXPECTED_POLICY: dict[str, Any] = {
    "max_readout_error": 0.08,
    "max_cz_error": 0.03,
    "max_sx_error": 0.01,
    "min_t1_us": 20.0,
    "min_t2_us": 20.0,
    "max_pending": 200,
    "seeds": 8,
    "joint_candidates": 3,
    "replica_floor": 0.45,
    "max_replicas": None,
    "isolated_reference": False,
    "cross_group_buffer": True,
    "twirl": False,
    "dd": None,
    "min_remaining_seconds": 60.0,
    "max_execution_seconds": int(DESIGN_CEILING_SECONDS),
    "seed_transpiler": DESIGN_SEED_SOURCES["--seed-transpiler"][0],
    "seed_simulator": DESIGN_SEED_SOURCES["--seed-simulator"][0],
    "operator_excluded_qubits": {},
}
# Nine doses in two orbit quadratures, the echo pair, and four Ramsey arms at every dose.
DESIGN_MEMBERS = 2 * len(DESIGN_DOSES) + 2 + 4 * len(DESIGN_DOSES)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def orbit_quadrature(counts: Sequence[float] | np.ndarray) -> tuple[float, float]:
    """(c, var c) of an orbit member's herald-kept phase counts: x0 - x1 and its binomial variance."""
    n = np.asarray(counts, dtype=float)
    require(n.size == 4 and n[0] + n[2] > 0 and n[1] + n[3] > 0, f"an orbit branch holds no shot: {n.tolist()}")
    x0 = (n[0] - n[2]) / (n[0] + n[2])
    x1 = (n[1] - n[3]) / (n[1] + n[3])
    return float(x0 - x1), float((1 - x0 * x0) / (n[0] + n[2]) + (1 - x1 * x1) / (n[1] + n[3]))


def ramsey_quadrature(counts: Sequence[float] | np.ndarray) -> tuple[float, float]:
    """(X or Y, variance) of a work Ramsey member's herald-kept phase counts, read on clbit 1."""
    n = np.asarray(counts, dtype=float)
    total = n[0] + n[2]
    require(n.size == 4 and total > 0, f"a Ramsey member holds no shot: {n.tolist()}")
    value = (n[0] - n[2]) / total
    return float(value), float((1 - value * value) / total)


def phase(c: tuple[float, float], s: tuple[float, float]) -> tuple[float, float, float, float]:
    """(phase, its standard error, amplitude, amplitude standard error) of a cosine and sine estimate."""
    (cv, cvar), (sv, svar) = c, s
    r2 = cv * cv + sv * sv
    amplitude = math.sqrt(r2)
    if r2 == 0.0:
        return 0.0, math.inf, 0.0, math.sqrt(cvar + svar)
    return (
        math.atan2(sv, cv),
        math.sqrt((sv * sv * cvar + cv * cv * svar) / (r2 * r2)),
        amplitude,
        math.sqrt((cv * cv * cvar + sv * sv * svar) / r2),
    )


def rate(times_us: Sequence[float], phases: Sequence[tuple[float, float, float, float]]) -> dict[str, Any]:
    """Weighted line through the unwrapped phases of the leading resolved doses: f in kHz with its scaled error."""
    kept = 0
    for _, se, amplitude, amplitude_se in phases:
        if not (math.isfinite(se) and amplitude > RESOLVED * amplitude_se):
            break
        kept += 1
    if kept < MIN_DOSES:
        return {"doses": kept, "khz": None, "se_khz": None}
    t = np.asarray(times_us[:kept], dtype=float)
    theta = np.unwrap(np.asarray([p[0] for p in phases[:kept]], dtype=float))
    w = 1.0 / np.asarray([p[1] for p in phases[:kept]], dtype=float) ** 2
    design = np.stack([np.ones_like(t), 2 * math.pi * t * 1e-3], axis=1)
    normal = design.T @ (design * w[:, None])
    coefficients = np.linalg.solve(normal, design.T @ (w * theta))
    residual = theta - design @ coefficients
    chi2 = float(np.sum(w * residual * residual))
    df = kept - 2
    scale = math.sqrt(max(1.0, chi2 / df)) if df > 0 else 1.0
    return {
        "doses": kept,
        "khz": float(coefficients[1]),
        "se_khz": float(math.sqrt(np.linalg.inv(normal)[1, 1]) * scale),
        "offset_rad": float(coefficients[0]),
        "chi2": chi2,
        "df": df,
        # A step near pi between doses is where a rate above the 1 / (2 step) limit would alias.
        "max_step_rad": float(np.max(np.abs(np.diff(theta)))),
    }


def wrapped(angle: float) -> float:
    return float((angle + math.pi) % (2 * math.pi) - math.pi)


def replica_fit(item: tuple[Sequence[float], Mapping[str, Any]]) -> dict[str, Any]:
    """Every rate and the echo comparison of one replica from its quadrature estimates."""
    times_us, quad = item
    orbit = [phase(c, s) for c, s in zip(quad["orbit_c"], quad["orbit_s"], strict=True)]
    out: dict[str, Any] = {"orbit": rate(times_us, orbit)}
    for role in ROLES:
        out[role] = rate(times_us, [phase(x, y) for x, y in zip(quad[f"{role}_x"], quad[f"{role}_y"], strict=True)])
    echo = phase(*quad["echo"])
    returned = wrapped(echo[0] - orbit[0][0])
    # The precession over the sweep is the fitted rate times the largest dose, which a whole number of turns
    # cannot hide; without a rate it is the wrapped phase change.
    fitted = out["orbit"]
    span = 2 * math.pi * times_us[-1] * 1e-3
    out["echo"] = {
        "moved_rad": fitted["khz"] * span if fitted["khz"] is not None else wrapped(orbit[-1][0] - orbit[0][0]),
        "moved_se": fitted["se_khz"] * span if fitted["khz"] is not None else math.hypot(orbit[-1][1], orbit[0][1]),
        "returned_rad": returned,
        "returned_se": math.hypot(echo[1], orbit[0][1]),
    }
    return out


def decide(fits: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [
        (fit["orbit"]["khz"], fit["orbit"]["se_khz"], fit["sixteen"]["khz"] - fit["one"]["khz"],
         math.hypot(fit["one"]["se_khz"], fit["sixteen"]["se_khz"]))
        for fit in fits
        if all(fit[key]["khz"] is not None for key in ("orbit", *ROLES))
    ]  # fmt: skip
    out: dict[str, Any] = {"replicas_with_rates": len(rows)}
    if len(rows) < MIN_REPLICAS:
        out["d1_slope"] = {"verdict": f"withheld: {len(rows)} replicas with three rates, below {MIN_REPLICAS}"}
    else:
        f_o, se_o, pred, se_p = (np.asarray(column, dtype=float) for column in zip(*rows, strict=True))
        w = 1.0 / (se_o**2 + se_p**2)
        slope = float(np.sum(w * f_o * pred) / np.sum(w * pred * pred))
        chi2 = float(np.sum(w * (f_o - slope * pred) ** 2))
        df = len(rows) - 1
        se = math.sqrt(1.0 / float(np.sum(w * pred * pred))) * math.sqrt(max(1.0, chi2 / df))
        low, high = slope - Z95 * se, slope + Z95 * se
        if 1 - SLOPE_BAND <= low and high <= 1 + SLOPE_BAND:
            verdict = "holds: the orbit precesses at the Ramsey offset of the bit for 16 minus that of the bit for 1"
        elif high < 1 - SLOPE_BAND or low > 1 + SLOPE_BAND:
            verdict = "refuted: the orbit's phase rate is not the Ramsey offset difference"
        else:
            verdict = "inconclusive: the interval overlaps the band without lying inside it"
        # Reported beside the decision: a free intercept shows a rate common to every replica that the line
        # through the origin would fold into its slope.
        design = np.stack([np.ones_like(pred), pred], axis=1)
        intercept, free_slope = np.linalg.solve(design.T @ (design * w[:, None]), design.T @ (w * f_o))
        out["d1_slope"] = {
            "slope": slope,
            "lower": low,
            "upper": high,
            "chi2": chi2,
            "df": df,
            "with_intercept": {"intercept_khz": float(intercept), "slope": float(free_slope)},
            "verdict": verdict,
        }
    resolved = [(o, p) for o, so, p, sp in rows if abs(o) > RESOLVED * so and abs(p) > RESOLVED * sp]
    if len(resolved) < MIN_REPLICAS:
        out["d2_sign"] = {"verdict": f"withheld: {len(resolved)} resolved replicas, below {MIN_REPLICAS}"}
    else:
        agree = sum(1 for o, p in resolved if o * p > 0) / len(resolved)
        verdict = (
            "holds: the orbit turns with the sign of the offset difference"
            if agree >= SIGN_HOLDS
            else "refuted: the signs disagree"
            if agree < SIGN_REFUTES
            else "inconclusive"
        )
        out["d2_sign"] = {"resolved": len(resolved), "agreement": agree, "verdict": verdict}
    moved = [fit["echo"] for fit in fits if abs(fit["echo"]["moved_rad"]) > RESOLVED * fit["echo"]["moved_se"]]
    if not moved:
        out["d3_echo"] = {"verdict": "withheld: no replica's free-idle phase moved over the sweep"}
    else:
        back = sum(1 for e in moved if abs(e["returned_rad"]) <= RESOLVED * e["returned_se"]) / len(moved)
        out["d3_echo"] = {
            "moved": len(moved),
            "returned_fraction": back,
            "verdict": "holds: the echo returns the undosed phase" if back >= ECHO_HOLDS else "fails",
        }
    return out


def quadratures(
    run_dir: Path, record: Mapping[str, Any]
) -> tuple[list[float], list[dict[str, Any]], list[dict[str, int]]]:
    """Dose times in us, each replica's quadrature estimates, and each replica's dose-time work qubits.

    The family configuration's dose_roles names the logical index whose initial qubit holds each work role at
    the dose (qpu_planning.dose_roles).
    """
    import n21_exact_planning
    import qpe_diagnostics

    configuration = record["family_configuration"]
    doses = sorted(int(d) for d in configuration["window_doses"])
    components = {}
    for pub in record["execution_pubs"]:
        require(len(pub["components"]) == 1, f"{pub['name']}: a PUB holds one member")
        components[pub["components"][0]["member"]] = (pub["name"], pub["components"][0]["registers_by_replica"])
    registers = n21_exact_planning.retained_registers(run_dir, {name for name, _ in components.values()})
    replicas = len(next(iter(components.values()))[1])

    def counts(member: str) -> list[np.ndarray]:
        name, by_replica = components[member]
        out = []
        for names in by_replica:
            outcomes = n21_exact_planning.replica_outcomes(registers[name], names)
            bits = len(registers[name][names[0]][0])
            kept = outcomes[outcomes >> bits == 0]
            out.append(np.bincount(kept, minlength=1 << bits).astype(float))
        return out

    def orbit(variant: str, dose: int) -> list[np.ndarray]:
        return counts(qpe_diagnostics.n21_dose_name(variant, dose, False))

    def ramsey(role: str, quadrature: str, dose: int) -> list[np.ndarray]:
        return counts(qpe_diagnostics.n21_work_ramsey_name(role, quadrature, dose))

    table: dict[str, list[list[tuple[float, float]]]] = {}
    for key, read in (
        ("orbit_c", lambda d: [orbit_quadrature(n) for n in orbit("window_dose", d)]),
        ("orbit_s", lambda d: [orbit_quadrature(n) for n in orbit("window_dose_y", d)]),
        *(
            (f"{role}_{q}", lambda d, role=role, q=q: [ramsey_quadrature(n) for n in ramsey(role, q, d)])
            for role in ROLES
            for q in ("x", "y")
        ),
    ):
        table[key] = [read(d) for d in doses]
    echo_c = [orbit_quadrature(n) for n in orbit("window_dose_echo", doses[-1])]
    echo_s = [orbit_quadrature(n) for n in orbit("window_dose_echo_y", doses[-1])]
    per_replica = [
        {
            **{key: [table[key][k][r] for k in range(len(doses))] for key in table},
            "echo": (echo_c[r], echo_s[r]),
        }
        for r in range(replicas)
    ]
    roles = configuration.get("dose_roles") or {"one": 1, "sixteen": 3}
    layouts = [
        {role: replica["initial_layout"][index] for role, index in roles.items()}
        for replica in record["groups"][0]["replicas"]
    ]
    return [d * DT_SECONDS * 1e6 for d in doses], per_replica, layouts


def analyze(run_dir: Path) -> dict[str, Any]:
    import parallel

    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    collected = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    groups = [g for g in collected if isinstance(g, dict) and "measured" in g]
    require(len(groups) == 1, f"{run_dir}: collect.json holds {len(groups)} measured groups, not one")
    withheld = groups[0].get("comparisons_withheld")
    require(withheld is None, f"{run_dir}: the collector withheld the comparisons: {withheld}")
    times, per_replica, layouts = quadratures(run_dir, record)
    fits = parallel.ordered_map(replica_fit, [(times, quad) for quad in per_replica], min_items=2)
    out = decide(fits)
    out["replicas"] = [
        {"replica": r, "qubit_one": layout["one"], "qubit_sixteen": layout["sixteen"], **fit}
        for r, (layout, fit) in enumerate(zip(layouts, fits, strict=True))
    ]
    out["run"] = run_dir.name
    out["dose_us"] = times
    return out


def preflight(record_dir: Path, head: str | None = None) -> dict[str, Any]:
    """The fresh record's binding facts, after requiring every invariant of the approved envelope."""
    record = json.loads((record_dir / "record.json").read_text(encoding="utf-8"))
    policy = record["policy"]
    design = policy["design"]
    require(record["state"] == "planned", f"{record_dir}: state {record['state']}, not planned")
    require(design == EXPECTED_DESIGN, f"design {design} differs from the envelope's {EXPECTED_DESIGN}")
    planning = {key: policy.get(key) for key in EXPECTED_POLICY}
    require(planning == EXPECTED_POLICY, f"planning policy {planning} differs from the envelope's {EXPECTED_POLICY}")
    require(int(record["shots"]) == DESIGN_SHOTS, f"shots {record['shots']}, not {DESIGN_SHOTS}")
    require(policy.get("rep_delay_seconds") in DESIGN_REP_DELAYS, f"repetition delay {policy.get('rep_delay_seconds')}")
    optimization = record["optimization"]
    require(optimization.get("searched_routed_sets") == 1, "the plan searched more than one routed candidate set")
    chosen = [c for c in optimization["candidates"] if c["name"] == optimization["selected"]]
    require(len(chosen) == 1 and chosen[0]["feasible"], "the record selects no feasible candidate")
    charge = float(chosen[0]["estimated_charge_seconds"])
    require(charge <= DESIGN_CEILING_SECONDS, f"estimated charge {charge} s exceeds the ceiling")
    groups = record["groups"]
    require(len(groups) == 1, f"{len(groups)} groups")
    replicas = len(groups[0]["replicas"])
    require(replicas >= DESIGN_MIN_REPLICAS, f"{replicas} replicas, below the design's {DESIGN_MIN_REPLICAS}")
    require(groups[0]["backend"] in DESIGN_BACKENDS, f"backend {groups[0]['backend']} lies outside the envelope")
    pubs = record.get("execution_pubs") or []
    require(
        len(pubs) == DESIGN_MEMBERS and all(len(pub["components"]) == 1 for pub in pubs),
        f"{len(pubs)} PUBs, not one per each of the {DESIGN_MEMBERS} members",
    )
    jobs = [(job.get("kind"), job.get("pubs")) for job in record.get("budget_plan", {}).get("jobs", [])]
    require(jobs == [("dynamic", DESIGN_MEMBERS)], f"jobs {jobs}, not one dynamic job of {DESIGN_MEMBERS} PUBs")
    sources = {row["flag"]: row["sources"] for row in record.get("seed_source") or []}
    require(sources == DESIGN_SEED_SOURCES, f"seed sources {sources}")
    draw_bytes = (ROOT / DESIGN_DRAW).read_bytes()
    require(hashlib.sha256(draw_bytes).hexdigest() == DESIGN_DRAW_SHA256, f"{DESIGN_DRAW} differs from its bound bytes")
    values = json.loads(draw_bytes)["values"]
    require(record.get("seed_simulator") == values[1], "the simulator seed is not the draw's index 1")
    offset = int(groups[0]["seed_transpiler"]) - int(values[0])
    require(0 <= offset < int(EXPECTED_POLICY["seeds"]), "the layout seed is not among the draw's index-0 seeds")
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


def synthetic(
    rng: np.random.Generator, replicas: int, shots: int, orbit_of: Any, echo_refocuses: bool = True
) -> tuple[list[float], list[dict[str, Any]]]:
    """Sampled quadrature estimates of replicas with random work-bit offsets and orbit_of(f_one, f_sixteen)."""
    times = [0.0, 7.0, 14.0, 21.0, 28.0, 35.0, 42.0, 49.0, 56.0]
    out = []
    for _ in range(replicas):
        f_one, f_six = rng.uniform(-25.0, 25.0, size=2)
        offset = rng.uniform(-math.pi, math.pi)
        f_orbit = orbit_of(f_one, f_six)

        def orbit_counts(theta: float, amplitude: float) -> list[tuple[float, float]]:
            reads = []
            for value in (amplitude * math.cos(theta), amplitude * math.sin(theta)):
                # Branch b0 = 0 reads +value / 2 above the relaxation offset, branch b0 = 1 reads -value / 2.
                p = 0.1
                x0, x1 = p + (1 - p) * value / 2, p - (1 - p) * value / 2
                n0 = rng.binomial(shots // 2, (1 + x0) / 2)
                n1 = rng.binomial(shots // 2, (1 + x1) / 2)
                reads.append(orbit_quadrature([n0, n1, shots // 2 - n0, shots // 2 - n1]))
            return reads

        def ramsey_counts(f: float, t: float) -> list[tuple[float, float]]:
            amplitude = 0.9 * math.exp(-t / 120.0)
            theta = 2 * math.pi * f * t * 1e-3
            reads = []
            for value in (amplitude * math.cos(theta), amplitude * math.sin(theta)):
                n0 = rng.binomial(shots, (1 + value) / 2)
                reads.append(ramsey_quadrature([n0, 0, shots - n0, 0]))
            return reads

        quad: dict[str, Any] = {
            "orbit_c": [],
            "orbit_s": [],
            "one_x": [],
            "one_y": [],
            "sixteen_x": [],
            "sixteen_y": [],
        }
        for t in times:
            c, s = orbit_counts(offset + 2 * math.pi * f_orbit * t * 1e-3, 0.6 * math.exp(-t / 100.0))
            quad["orbit_c"].append(c)
            quad["orbit_s"].append(s)
            for role, f in (("one", f_one), ("sixteen", f_six)):
                x, y = ramsey_counts(f, t)
                quad[f"{role}_x"].append(x)
                quad[f"{role}_y"].append(y)
        echo_theta = offset if echo_refocuses else offset + 2 * math.pi * f_orbit * times[-1] * 1e-3
        quad["echo"] = tuple(orbit_counts(echo_theta, 0.6 * math.exp(-times[-1] / 200.0)))
        out.append(quad)
    return times, out


def self_test() -> str:
    import parallel

    rng = np.random.default_rng(SELF_TEST_SEED)

    def run(orbit_of: Any, echo_refocuses: bool = True) -> dict[str, Any]:
        times, quads = synthetic(rng, 19, 4096, orbit_of, echo_refocuses)
        return decide(parallel.ordered_map(replica_fit, [(times, q) for q in quads], min_items=2))

    true = run(lambda one, six: six - one)
    require(true["d1_slope"]["verdict"].startswith("holds"), f"the frame-offset account reads {true['d1_slope']}")
    require(true["d2_sign"]["verdict"].startswith("holds"), f"the frame-offset account reads {true['d2_sign']}")
    require(true["d3_echo"]["verdict"].startswith("holds"), f"the refocusing echo reads {true['d3_echo']}")
    flipped = run(lambda one, six: one - six)
    require(flipped["d1_slope"]["verdict"].startswith("refuted"), f"a reversed orbit reads {flipped['d1_slope']}")
    require(flipped["d2_sign"]["verdict"].startswith("refuted"), f"a reversed orbit reads {flipped['d2_sign']}")
    summed = run(lambda one, six: six + one)
    require(not summed["d1_slope"]["verdict"].startswith("holds"), f"the offset sum reads {summed['d1_slope']}")
    unrelated = run(lambda one, six: float(rng.uniform(-25.0, 25.0)))
    require(not unrelated["d1_slope"]["verdict"].startswith("holds"), f"unrelated rates read {unrelated['d1_slope']}")
    stuck = run(lambda one, six: six - one, echo_refocuses=False)
    require(stuck["d3_echo"]["verdict"] == "fails", f"an echo that keeps the precession reads {stuck['d3_echo']}")
    return (
        "n21 detuning sign: the frame-offset account holds; reversed, summed and unrelated orbit rates and an echo "
        "that keeps the precession decide against it"
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
