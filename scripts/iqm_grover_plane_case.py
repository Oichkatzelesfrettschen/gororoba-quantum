"""IQM Garnet depth dependence of the line-native Grover retention, read as a mechanism-free departure from geometric.

The retained run grover-depth-sedenion-walsh measured the marked probability of mark 101 at depths 1, 2 and 3 and read a
bend against the geometric law of the calibrated model (docs/design/iqm-garnet-grover-depth-sedenion-walsh.md). The
case grover-fourth-depth-mirrored (scripts/iqm_grover_fourth_depth.py) asks which of three gate-error families explains
it. This case asks the question that every such family shares and answers it without naming a gate: does the marked
probability at depths 1 to 4 depart from the geometric law, P_k = 1/8 + a (Q_k(s, 0) - 1/8), toward the same law with a
rotation eps of the Grover plane per iteration (docs/design/iqm-garnet-grover-plane-model.md)? A coherent gate error
(a CZ phase, a PRX amplitude, a ZZ coupling) acts on the plane to first order as a rotation, so eps measures the
departure whatever its source; a depth-independent offset a is not a per-iteration loss, and a coherent term that is
merely unresolved is not read as geometric.

Job "grover" (path QB20-QB16-QB17, as scripts/iqm_garnet_followup.py): COPIES[k] copies of m101-k{k} at depths 1 to 4
and the eight readout preparations in two copies each, in a palindromic order that puts every kind at mirrored
positions. The depths of two mirror pairs stay at least 11 positions apart (first-half positions up to MAX_EDGE), so
no pair sits back to back at the center and a transient there reaches at most one copy of each. Every response is the
calibrated noisy density-matrix path of the committed circuits (gororoba_quantum/grover_plane_sim.py); the analysis
rebuilds it from the circuit files the run carries and compares its digest with prediction.json. The case draws no
random number.

Usage: "$PYTHON" scripts/iqm_grover_plane_case.py (build DIR (--calibration SRC | --live) | check DIR |
       analyze RUN_DIR --out OUT.json | search)
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_garnet_followup as followup  # noqa: E402
import iqm_grover_line as grover  # noqa: E402
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import CALIBRATION_FILES, OPTIONS  # noqa: E402

import grover_plane_analysis as run_analysis  # noqa: E402
import grover_plane_calibration as calibration  # noqa: E402
import grover_plane_decision as decision  # noqa: E402
import grover_plane_sim as sim  # noqa: E402

CASE = "grover-plane-mirrored"
QCS = ["garnet:mock", "garnet"]
PRICE = grover.PRICE
PATH = followup.FORWARD_PATH
MARKED = "101"
SHOTS = 16000
COPIES = {1: 4, 2: 4, 3: 10, 4: 4}
COPIES_011 = {1: 4, 2: 4, 3: 6}
MARKS = ("101", "011")
# Kinds of the job's circuits: 0 a readout preparation, 1 to 4 depths 1 to 4 of mark 101,
# 5 to 7 depths 1 to 3 of mark 011.
KIND = {**{k: ("101", k) for k in COPIES}, **{4 + k: ("011", k) for k in COPIES_011}}
KIND_COPIES = {**COPIES, **{4 + k: n for k, n in COPIES_011.items()}}
SEPARATION = 11
READOUTS = 8
READOUT_COPIES = 2
KEPT_PLAN = 0.84
PLANNED_KEPT_PER_COPY = SHOTS * KEPT_PLAN
READOUT_TOLERANCE = 0.05
CANCEL_MARGIN = 1.0
HEADROOM = 1.5
RETAINED_JOB = ROOT / "results" / "iqm" / "runs" / "2026-11-21T220358Z-garnet-grover-depth-sedenion-walsh-grover"
RETAINED_EXECUTION_SECONDS = 1.998523
RETAINED_COMPILATION_SECONDS = 0.436857
RETAINED_FIXED_SECONDS = 0.13
GATE_DURATIONS = {"prx": 16, "cz": 40, "measure": 480}
# Kinds of the first half (0 a readout preparation, k a copy of depth k), the local optimum of single exchanges of
# best_first_half(); a test reruns the search.
FIRST_HALF: tuple[int, ...] = (3, 7, 0, 0, 0, 0, 1, 5, 2, 6, 4, 0, 3, 4, 6, 3, 2, 0, 5, 3, 1, 7, 3, 7, 0, 0)
ARRIVAL_LOG2N = 10
CELL_LOG2N = 5
POWER_LOG2N = 9
INFLUENCE_LOG2N = 8


def kinds_multiset() -> list[int]:
    return [0] * READOUTS + [k for k, n in KIND_COPIES.items() for _ in range(n // 2)]


def feasible(order: Sequence[int]) -> bool:
    """Kinds of two pairs sit at least SEPARATION positions from their mirror images, the position next to the center
    holds a readout, kinds of more pairs stay off the last two positions, and no depth appears at adjacent positions."""
    half = len(order)
    for p, k in enumerate(order):
        if k and KIND_COPIES[k] == 4 and 2 * half - 1 - 2 * p < SEPARATION:
            return False
        if k and p > half - 3:
            return False
        if p == half - 1 and k != 0:
            return False
        if p and k and order[p - 1] == k:
            return False
    return True


def depth_spread(order: Sequence[int]) -> float:
    """Largest minus smallest over the depth kinds of the mean squared offset of their positions from the center."""
    center = len(order) - 0.5
    means = []
    for k in KIND_COPIES:
        offsets = [(p - center) ** 2 for p, kind in enumerate(order) if kind == k]
        means.append(sum(offsets) / len(offsets))
    return max(means) - min(means)


def start_orders() -> list[tuple[int, ...]]:
    """Feasible starting orders: the depth copies in the order of a greedy rearrangement (most copies left first, never
    the previous kind), readouts at every fourth position and at the last two, then single exchanges of kinds that
    break the separation rule with kinds of more pairs until the order is feasible."""
    half = sum(kinds_count().values())
    out: list[tuple[int, ...]] = []
    for shift in range(len(KIND_COPIES)):
        left = {k: n // 2 for k, n in KIND_COPIES.items()}
        depth: list[int] = []
        while any(left.values()):
            kinds = sorted(
                (k for k in left if left[k] and (not depth or depth[-1] != k)),
                key=lambda k: (-left[k], (k + shift) % 8),
            )
            if not kinds:
                break
            depth.append(kinds[0])
            left[kinds[0]] -= 1
        if any(left.values()):
            continue
        order: list[int] = []
        slots = iter(depth)
        for p in range(half):
            order.append(0 if (p % 4 == 3 and p < half - 2) or p >= half - 2 else next(slots, 0))
        if sorted(order) != sorted(kinds_multiset()):
            continue
        for _ in range(200):
            bad = [p for p, k in enumerate(order) if k and KIND_COPIES[k] == 4 and 2 * half - 1 - 2 * p < SEPARATION]
            if not bad:
                break
            donors = [p for p, k in enumerate(order) if k and KIND_COPIES[k] > 4 and p < bad[0]]
            if not donors:
                break
            q = donors[-1]
            order[bad[0]], order[q] = order[q], order[bad[0]]
        if feasible(order) and tuple(order) not in out:
            out.append(tuple(order))
    return out


def kinds_count() -> dict[int, int]:
    return {0: READOUTS, **{k: n // 2 for k, n in KIND_COPIES.items()}}


def descend(order: tuple[int, ...]) -> tuple[int, ...]:
    best = order
    improved = True
    while improved:
        improved = False
        for i, j in itertools.combinations(range(len(best)), 2):
            if best[i] == best[j]:
                continue
            trial = list(best)
            trial[i], trial[j] = trial[j], trial[i]
            if feasible(trial) and (depth_spread(trial), tuple(trial)) < (depth_spread(best), tuple(best)):
                best, improved = tuple(trial), True
    return best


def best_first_half() -> tuple[int, ...]:
    from parallel import ordered_map

    found = ordered_map(descend, start_orders(), min_items=1)
    return min(found, key=lambda o: (depth_spread(o), o))


def arrangement() -> list[int]:
    if sorted(FIRST_HALF) != sorted(kinds_multiset()):
        raise AssertionError("FIRST_HALF does not hold the planned copies")
    if not feasible(FIRST_HALF):
        raise AssertionError("FIRST_HALF breaks the placement constraints")
    return [*FIRST_HALF, *FIRST_HALF[::-1]]


def depth_arms() -> list[dict[str, Any]]:
    order = arrangement()
    total = len(order)
    seen = {k: 0 for k in KIND_COPIES}
    out: list[dict[str, Any]] = []
    bits = ["".join(b) for b in itertools.product("01", repeat=3)]
    readout = 0
    for position, kind in enumerate(order):
        if kind == 0:
            if position < total // 2:
                name_bits = bits[readout]
                readout += 1
                circuit = followup.readout_circuit(name_bits, PATH, "ro")
            else:
                name_bits = out[total - 1 - position]["name"].removeprefix("ro-")
                circuit = followup.readout_circuit(name_bits, PATH, "ro")
                circuit = {**circuit, "name": f"{circuit['name']}-m"}
            out.append({"name": circuit["name"], "circuit": circuit, "marked": None, "k": None, "kind": 0})
            continue
        mark, depth = KIND[kind]
        name = f"m{mark}-k{depth}-c{seen[kind]}"
        seen[kind] += 1
        out.append(
            {
                "name": name,
                "circuit": grover.line_arm(mark, depth, PATH, name)[1],
                "marked": mark,
                "k": depth,
                "kind": kind,
            }
        )
    if seen != KIND_COPIES or readout != READOUTS:
        raise AssertionError(f"arrangement holds {seen} and {readout} readouts")
    for kind in [*KIND_COPIES, 0]:
        at = [n for n, a in enumerate(out) if a["kind"] == kind]
        if sum(at) != len(at) * (total - 1) / 2 or any(out[total - 1 - n]["kind"] != kind for n in at):
            raise AssertionError(f"kind {kind} circuits are not mirrored: positions {at}")
    return out


def rounded(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    if isinstance(x, np.ndarray):
        return rounded(x.tolist())
    if isinstance(x, (list, tuple)):
        return [rounded(v) for v in x]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return None if math.isnan(float(x)) else round(float(x), 9)
    return x


def final_distribution(circuit: dict[str, Any], cal: Any) -> np.ndarray:
    steps, measured = sim.build_steps(circuit, cal, PATH, True)
    rho = np.zeros((1, 8, 8), dtype=complex)
    rho[0, 0, 0] = 1
    return sim.outcome_distribution(sim.apply_steps(steps, rho)[0], measured, PATH, cal)


def key_of(index: int) -> str:
    return "".join(str((index >> q) & 1) for q in range(3))


def schedule_nanoseconds(circuit: dict[str, Any]) -> int:
    """ASAP duration of a circuit on its qubits plus the joint measurement."""
    clock: dict[str, int] = {}
    for op in circuit["instructions"]:
        if op["name"] == "measure":
            continue
        start = max(clock.get(q, 0) for q in op["locus"])
        for q in op["locus"]:
            clock[q] = start + GATE_DURATIONS[op["name"]]
    return max(clock.values(), default=0) + GATE_DURATIONS["measure"]


def retained_schedule_total() -> int:
    case = json.loads((RETAINED_JOB / "cases.json").read_text(encoding="utf-8"))
    job = next(j for j in case["jobs"] if j["job"] == "grover")
    total = 0
    for entry in job["circuits"]:
        circuit = json.loads((RETAINED_JOB / entry["file"]).read_text(encoding="utf-8"))
        total += schedule_nanoseconds(circuit) * job["shots"]
    return total


def cost_estimates(arms: list[dict[str, Any]]) -> dict[str, Any]:
    """Execution seconds of the job from the retained job's execution time scaled by the ratio of ASAP schedule
    totals (gate durations of the retained schedule model): with and without the retained job's fixed part; the
    sibling Emerald run that took 2.2 times its estimate is the stress the credit ceiling carries."""
    new_total = sum(schedule_nanoseconds(a["circuit"]) * SHOTS for a in arms)
    ratio = new_total / retained_schedule_total()
    scaled = RETAINED_EXECUTION_SECONDS * ratio
    fixed_removed = RETAINED_FIXED_SECONDS + (RETAINED_EXECUTION_SECONDS - RETAINED_FIXED_SECONDS) * ratio
    best = max(scaled, fixed_removed)
    run = best + RETAINED_COMPILATION_SECONDS
    billed = math.ceil(HEADROOM * run + CANCEL_MARGIN)
    return {
        "schedule_ratio": ratio,
        "scaled_execution_seconds": scaled,
        "fixed_part_removed_execution_seconds": fixed_removed,
        "best_execution_seconds": best,
        "compilation_seconds": RETAINED_COMPILATION_SECONDS,
        "headroom": HEADROOM,
        "billed_seconds_of_ceiling": billed,
        "max_credits_garnet": billed * PRICE["garnet"],
        "emerald_stress_execution_seconds": 2.2 * best,
        "mock_compile_estimate": "required before approval; not read",
    }


def readout_plan(
    arm_distributions: dict[str, np.ndarray], first: dict[int, str], mark: str, copies: dict[int, int]
) -> dict[str, Any]:
    """The marked row of the model's assignment matrix and the model's depth distributions over the prepared states
    of one mark, with the planned common-mode covariance of the corrected depth frequencies."""
    index = grover_index(mark)
    a = np.column_stack([arm_distributions[f"ro-{key_of(j)}"] for j in range(8)])
    q = np.array([np.linalg.solve(a, arm_distributions[first[k]]) for k in copies])
    r_model = a[index]
    shots = 2 * PLANNED_KEPT_PER_COPY
    variance = decision.PHI * r_model * (1 - r_model) / (2 * shots) * 2
    cov = (q * variance) @ q.T
    return {
        "marked_index": index,
        "r_model": r_model,
        "q": q,
        "planned_covariance": cov,
        "tolerance": READOUT_TOLERANCE,
        "sides_dof": 56,
        "sides_threshold": float(decision.stats.chi2.isf(decision.ALPHA, 56)),
    }


def grover_index(marked: str) -> int:
    return sum(int(c) << q for q, c in enumerate(marked))


def mechanism_slopes(
    fitter: decision.Fitter, circuits: dict[int, dict[str, Any]], cal: Any, mark: str
) -> dict[str, Any]:
    out = {}
    for name, key, x in (
        ("cz_phase_rad", "cz_phase", 0.004),
        ("prx_amplitude_fraction", "prx_scale", 0.002),
        ("zz_hz", "zz_hz", 5e3),
    ):
        eps = []
        for sign in (-1, 1):
            kwargs: dict[str, Any] = {key: sign * x}
            response = sim.Response(circuits, cal, PATH, mark, **kwargs)
            fit = fitter.fit(response.probabilities(1, 1, 0.0), np.diag(np.full(len(circuits), 1e-8)), True)
            eps.append(fit["eps"])
        out[name] = {"eps_per_unit": (eps[1] - eps[0]) / (2 * x)}
    return out


def mark_block(
    mark: str, arms: list[dict[str, Any]], cal: Any, distributions: dict[str, np.ndarray]
) -> tuple[dict[int, dict[str, Any]], sim.Response, decision.Fitter, dict[str, Any], dict[int, int]]:
    copies = COPIES if mark == "101" else COPIES_011
    first = {k: next(a["name"] for a in arms if a["marked"] == mark and a["k"] == k) for k in copies}
    circuits = {k: next(a["circuit"] for a in arms if a["marked"] == mark and a["k"] == k) for k in copies}
    response = sim.Response(circuits, cal, PATH, mark)
    return circuits, response, decision.Fitter(response), readout_plan(distributions, first, mark, copies), copies


def decisions(arms: list[dict[str, Any]], cal: Any, distributions: dict[str, np.ndarray]) -> dict[str, Any]:
    circuits, response, fitter, plan, copies = mark_block("101", arms, cal, distributions)
    circuits_b, response_b, fitter_b, plan_b, copies_b = mark_block("011", arms, cal, distributions)
    kept = [copies[k] * PLANNED_KEPT_PER_COPY for k in copies]
    kept_b = [copies_b[k] * PLANNED_KEPT_PER_COPY for k in copies_b]
    readout_cov = plan["planned_covariance"]
    cal_block = calibration.calibrate(fitter, kept, readout_cov, ARRIVAL_LOG2N, CELL_LOG2N)
    delta = cal_block["delta_resolve"]
    corners = [(0.92, 0.92), (0.92, 1.04), (1.06, 0.92), (1.06, 1.04)]
    mechs: list[tuple[str, dict[str, Any]]] = [
        ("cz -0.015 rad", {"cz_phase": -0.015}),
        ("cz +0.015 rad", {"cz_phase": 0.015}),
        ("prx -0.8 %", {"prx_scale": -0.008}),
        ("prx +0.8 %", {"prx_scale": 0.008}),
        ("zz -10 kHz", {"zz_hz": -1e4}),
        ("zz +10 kHz", {"zz_hz": 1e4}),
    ]
    truths = []
    for label, kw in mechs:
        r = sim.Response(circuits, cal, PATH, "101", **kw)
        truths += [(f"{label} a={a} s={s}", r.probabilities(a, s, 0.0)) for a, s in corners]
    for e in (-0.03, -0.02, -0.015, -0.01, 0.01, 0.015, 0.02, 0.03):
        truths += [(f"plane eps={e} a={a} s={s}", response.probabilities(a, s, e)) for a, s in corners]
    box = calibration.sobol_box(
        (calibration.POWER_A[0], calibration.POWER_S[0]), (calibration.POWER_A[1], calibration.POWER_S[1]), 4
    )
    for e in (-0.02, 0.02):
        truths += [
            (f"plane eps={e} a={a:.4f} s={s:.4f}", response.probabilities(float(a), float(s), e)) for a, s in box
        ]
    power = calibration.power(fitter, truths, kept, readout_cov, delta, POWER_LOG2N)
    resolved = [
        p for p in power if "eps=" not in p["truth"] or abs(float(p["truth"].split("eps=")[1].split()[0])) >= 0.02
    ]
    worst = min(resolved, key=lambda p: p["coherent"])
    gated_truths = [
        t
        for t in truths
        if t[0].startswith(
            ("cz -0.015", "prx +0.8", "zz -10", "plane eps=0.02 a=0.92 s=0.92", "plane eps=-0.02 a=0.92 s=0.92")
        )
    ]
    pairs = [n // 2 for n in copies.values()]
    gated = {
        label: calibration.influence_power(
            fitter, gated_truths, pairs, PLANNED_KEPT_PER_COPY, readout_cov, delta, INFLUENCE_LOG2N, noise_phi
        )
        for label, noise_phi in (("binomial_phi_1", 1.0), ("overdispersed_phi_bound", decision.PHI))
    }
    slopes = {
        "101": mechanism_slopes(fitter, circuits, cal, "101"),
        "011": mechanism_slopes(fitter_b, circuits_b, cal, "011"),
    }
    ratio = (
        slopes["011"]["prx_amplitude_fraction"]["eps_per_unit"]
        / slopes["101"]["prx_amplitude_fraction"]["eps_per_unit"]
    )
    contrast_truths = []
    for label, key, x in (
        ("cz -0.03 rad", "cz_phase", -0.03),
        ("prx -1.6 %", "prx_scale", -0.016),
        ("zz +20 kHz", "zz_hz", 2e4),
    ):
        contrast_kw: dict[str, Any] = {key: x}
        ra = sim.Response(circuits, cal, PATH, "101", **contrast_kw)
        rb = sim.Response(circuits_b, cal, PATH, "011", **contrast_kw)
        contrast_truths += [
            (f"{label} a={a} s={s}", ra.probabilities(a, s, 0.0), rb.probabilities(a, s, 0.0)) for a, s in corners
        ]
    contrast_block = calibration.contrast_power(
        fitter,
        fitter_b,
        contrast_truths,
        kept,
        kept_b,
        readout_cov,
        plan_b["planned_covariance"],
        ratio,
        POWER_LOG2N - 1,
    )
    grid_s, grid_e = [0.9, 1.0], [-0.04, 0.0, 0.04]

    def digest(resp: sim.Response) -> dict[str, Any]:
        table = [[list(resp.centered(s, e)) for e in grid_e] for s in grid_s]
        return {
            "s": grid_s,
            "eps": grid_e,
            "centered": table,
            "sha256": hashlib.sha256(json.dumps(rounded(table)).encode()).hexdigest(),
        }

    return {
        "model_probabilities": response.probabilities(1.0, 1.0, 0.0),
        "response": digest(response),
        "readout": plan,
        "mark_011": {
            "model_probabilities": response_b.probabilities(1.0, 1.0, 0.0),
            "response": digest(response_b),
            "readout": plan_b,
            "copies": {str(k): n for k, n in copies_b.items()},
        },
        "gate": {
            "copy_floor": decision.COPY_FLOOR,
            "planned_kept_per_copy": PLANNED_KEPT_PER_COPY,
            "heterogeneity_threshold_by_dof": decision.heterogeneity_thresholds(12),
        },
        "rule": {
            "primary": (
                "departure of the marked probabilities of mark 101 from the geometric law toward a plane rotation eps"
            ),
            "delta_resolve": delta,
            "eps_equivalence": decision.EPS_EQUIV,
            "z_equivalence": decision.Z_EQUIV,
            "z_loss": decision.Z_LOSS,
            "phi": decision.PHI,
            "boxes": {"a": decision.A_BOX, "s": decision.S_BOX, "eps": decision.E_BOX},
            "boxes_note": (
                "the fitting box of a and s equals the calibrated null box; a fit on a bound reads out of domain"
            ),
        },
        "calibration": cal_block,
        "power": {"design_effect_eps": 0.02, "worst_resolved_truth": worst, "truths": power},
        "gated_power": gated,
        "mechanism_slopes": slopes["101"],
        "contrast": {
            "rule": "eps_011 against 0 (CZ phase) and against ratio times eps_101 (PRX amplitude); decides nothing",
            "ratio_prx": ratio,
            "slopes": slopes,
            "power": contrast_block,
        },
        "cost": None,
    }


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    cal = iqm_sim.Calibration.from_directory(calibration_dir)
    arms = depth_arms()
    files = {f"circuits/{a['name']}.json": dump(a["circuit"]) for a in arms}
    distributions = {a["name"]: final_distribution(a["circuit"], cal) for a in arms}
    arm_records: dict[str, Any] = {}
    for position, arm in enumerate(arms):
        c = arm["circuit"]
        record: dict[str, Any] = {
            "job": "grover",
            "position": position,
            "locus": c["instructions"][-1]["locus"],
            "cz": followup.count(c, "cz"),
            "prx": followup.count(c, "prx"),
            "predicted": {key_of(i): round(float(x), 9) for i, x in enumerate(distributions[arm["name"]])},
        }
        if arm["marked"] is not None:
            p = float(distributions[arm["name"]][grover_index(arm["marked"])])
            record |= {
                "marked": arm["marked"],
                "iterations": arm["k"],
                "ideal_marked": math.sin((2 * arm["k"] + 1) * sim.THETA) ** 2,
                "predicted_marked": round(p, 9),
            }
        arm_records[arm["name"]] = record
    cost = cost_estimates(arms)
    block = decisions(arms, cal, distributions)
    block["cost"] = cost
    job = {
        "job": "grover",
        "circuits": [
            {"file": f"circuits/{a['name']}.json", "sha256": sha256(files[f"circuits/{a['name']}.json"].encode())}
            for a in arms
        ],
        "shots": SHOTS,
        "options": {**OPTIONS, "calibration_set_id": {"garnet": cal.set_id}},
        "expected_seconds": round(cost["best_execution_seconds"], 3),
        "max_credits": {qc: (cost["max_credits_garnet"] if PRICE[qc] else 0.0) for qc in QCS},
    }
    prediction = {
        "calibration_set": cal.set_id,
        "forward_path": PATH,
        "copies": {str(k): n for k, n in COPIES.items()},
        "copies_011": {str(k): n for k, n in COPIES_011.items()},
        "arms": arm_records,
        "decisions": rounded(block),
        "model": (
            "exact noisy density matrix of the committed circuits: depolarizing PRX and CZ, ASAP idle T1/T2, "
            "herald-conditioned readout; no coherent error, leakage or crosstalk"
        ),
    }
    files["prediction.json"] = dump(prediction)
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "prediction_sha256": sha256(files["prediction.json"].encode()),
            "question": (
                "With the line-native Grover of mark 101 at depths 1 to 4 and of mark 011 at depths 1 to 3 placed at "
                "positions mirrored about the job's center on one Garnet calibration, does the marked probability of "
                "mark 101 depart from the geometric law of the calibrated model toward a rotation of the Grover plane "
                "per iteration, whatever gate error causes it, and does mark 011 rotate as a CZ phase (not at all) or "
                "as a PRX amplitude (1.4 times mark 101) predicts?"
            ),
            "qcs": QCS,
            "jobs": [job],
        }
    )
    return files, prediction


def fetch_live(calibration_dir: Path) -> None:
    from iqm_cancellation_probe import fetch_calibration

    fetch_calibration(calibration_dir)


def write(directory: Path, source: Path | None, live: bool = False) -> None:
    if live == (source is not None):
        raise ValueError("build takes exactly one of --calibration and --live")
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    if live:
        fetch_live(calibration_dir)
    elif source is not None:
        for name in CALIBRATION_FILES:
            shutil.copyfile(source / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir)
    for stale in (directory / "circuits").glob("*.json"):
        if stale.relative_to(directory).as_posix() not in files:
            stale.unlink()
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(json.dumps({k: prediction["decisions"][k] for k in ("rule", "calibration", "cost")}, indent=1))


def check(directory: Path) -> None:
    files, _ = build_from(directory / "calibration")
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(files) | {f"calibration/{name}" for name in CALIBRATION_FILES}
    if present != expected:
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ expected)}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")
    b = sub.add_parser("build")
    b.add_argument("directory", type=Path)
    group = b.add_mutually_exclusive_group(required=True)
    group.add_argument("--calibration", type=Path)
    group.add_argument("--live", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("directory", type=Path)
    a = sub.add_parser("analyze")
    a.add_argument("run_dir", type=Path)
    a.add_argument("--out", type=Path, required=True)
    sub.add_parser("search")
    args = parser.parse_args()
    if args.command == "build":
        write(args.directory, args.calibration, args.live)
    elif args.command == "check":
        check(args.directory)
        print(f"{args.directory}: matches the build")
    elif args.command == "analyze":
        run_analysis.write_record(run_analysis.analyze(args.run_dir), args.out)
    elif args.command == "search":
        print(best_first_half())
    else:
        parser.print_help()
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
