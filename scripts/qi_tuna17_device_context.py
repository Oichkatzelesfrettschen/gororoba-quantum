"""Per-qubit device context for the Tuna-17 readout ring-down pilot, from the retained Tuna-17 measurements it names.

The pilot (qi_readout_ringdown_cases) reads delta(tau), the rate offset of a
mid-circuit-read target against an unread reference on the same circuit. This
record gathers what the repository measured on each Tuna-17 qubit and prints
it beside that verdict; it feeds no estimator and leaves the preregistered
decision rule untouched. Four blocks per qubit:

- Coupler map (coupler_zz_tuna_17_analysis.json and the four retained map
  batches): the idle detuning omega from the qubit's frame, known modulo the
  map's alias period 1 / (75 x 20 ns) = 666.7 kHz; Ramsey visibility at the
  map's delays (25 and 100 cycles) in the sector where every neighbor is in
  |0>, which is the pilot's configuration, and its minimum over sectors; and
  every incident coupler's J with its standard error. delta wraps
  dphi(tau) - dphi(reference) on the circle, and the arm rates are
  reference + wrap(difference) / SPAN, so a detuning at the pilot's alias edge
  |nu| = 1 / (2 SPAN x 20 ns) moves only the absolute rate of the reference
  (a sign flip of the common offset c) and leaves every delta, chi-square and
  fit parameter A and T unchanged. The edge flag marks omega within 30 kHz of
  the edge.
- Spectator-drive crosstalk (the retained crosstalk run's analysis.json): P1
  after 40 X gates when the qubit is driven alone and with its star partner,
  and the per-X over-rotation lower bound where a driver exceeds P1 = 0.5.
  Over-rotation eps turns the Ramsey's X90 into a rotation of angle
  pi/2 + eps/2 about X, and the final X90 or Y90 into the same angle about X
  or Y; the estimator phi_hat = atan2(2 P1(Y) - 1, 2 P1(X) - 1) minus its
  eps = 0 value is evaluated on a grid of 2001 phases phi, and the rate error
  is the phase-error spread (max - min) over the pilot's SPAN. The two delays
  see the same phase error, so the spread bounds the difference at that eps.
  The crosstalk run gives eps only a lower bound, so the block is the
  scenario at the measured lower bound; a larger eps gives a larger spread.
- Readout (the readout-0 and readout-1 circuits of the Tuna-17 runs that
  READOUT_RUNS names, oldest first): P(1|0) and P(1|1) per run, and the wait before readout parsed from the
  circuit text. Where a run waits before the readout of a prepared |1>
  (the pilot's SETTLE_CYCLES), the implied T1 is wait / ln(P1_nowait / P1_wait)
  with P1_nowait from the earliest no-wait run within 24 h before it. The
  formula assumes the whole P(1|1) drop is T1 decay during the wait and that
  the assignment fidelity is unchanged between the two runs.
- Visibility prediction at d2 plus the wait: the in-batch calibration's
  e10 includes the relaxation during the wait, so the corrected quadratures
  of a pure T1 channel equal 2 p - 1 exactly and the wait costs shot noise,
  not visibility. The conservative prediction multiplies the map's 2 us
  visibility (2 us exceeds the pilot's d2 of 1.54 us) by exp(-wait / T1); the
  absorbed prediction keeps the map value. Both are predicted values and are
  compared with MIN_VISIBILITY.

The common-mode text lists which effects cancel in delta(tau) and which stay.
Floats are written at SIGNIFICANT digits. --check recomputes the record and
compares bytes. READOUT_RUNS fixes the record's inputs, so retaining a new
Tuna-17 run leaves the record and its research-state sha256 unchanged until a
change adds the run to the list; --check names every retained Tuna-17 run
with a readout pair that the list omits.

Usage: "$PYTHON" scripts/qi_tuna17_device_context.py [--check] [--out PATH]
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
from qi_coupler_zz_map import (
    CYCLE_SECONDS,
    MIN_VISIBILITY,
    QUADRATURES,
    ROLES,
    bit,
    members,
    neighbors,
    retained_path,
    tabulate,
)
from qi_coupler_zz_map import DELAYS as MAP_DELAYS
from qi_readout_ringdown_cases import DELAYS as PILOT_DELAYS
from qi_readout_ringdown_cases import SETTLE_CYCLES, SPAN, TO_HZ

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "results/quantum_inspire/runs"
MAP_ANALYSIS = ROOT / "results/quantum_inspire/coupler_zz_tuna_17_analysis.json"
CROSSTALK_RUN = RUNS / "2026-10-16T211635Z-tuna_17"
OUT = ROOT / "results/quantum_inspire/readout_ringdown_tuna_17_device_context.json"
SCHEMA = "qi-readout-ringdown-device-context-v1"
SIGNIFICANT = 6
NQUBITS = 17
PILOT_SERIES = ("P", "Q")
EDGE_WINDOW_HZ = 30e3
PHASE_GRID = 2001
NOWAIT_WINDOW = timedelta(hours=24)
RUN_STAMP = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{6}Z)-")
READOUT_RUNS = (
    "2026-10-16T221133Z-zero_divisor_tuna_17",
    "2026-10-16T224924Z-coupler_zz_tuna_17-batch-00",
    "2026-10-17T032034Z-readout_ringdown_tuna_17_P-batch-00",
    "2026-10-17T032034Z-readout_ringdown_tuna_17_P-recal-041520",
    "2026-10-17T032034Z-readout_ringdown_tuna_17_P-recal-042425",
    "2026-10-17T032034Z-readout_ringdown_tuna_17_Q-batch-00",
    "2026-10-17T032034Z-readout_ringdown_tuna_17_Q-recal-053951",
    "2026-10-17T052547Z-zero_divisor_tuna_17-batch-00",
    "2026-10-17T052915Z-zero_divisor_tuna_17-batch-01",
    "2026-10-17T053226Z-zero_divisor_tuna_17-batch-02",
)
WAIT_LINE = re.compile(r"^wait\((\d+)\) q\[(\d+)\]$")
FLIP_LINE = re.compile(r"^X q\[(\d+)\]$")

COMMON_MODE = (
    "Cancels in delta(tau), because the reference arm and every readout arm of a target share it: "
    "the static ZZ shift from neighbors that stay in |0> (every neighbor of a target is a spectator "
    "in |0>); the simultaneous-drive crosstalk of the shared X90 schedule, since every arm plays the "
    "same gates on the same targets at the same cycles; the coherent over-rotation, whose phase-estimate "
    "bias depends on the gate angle alone (over_rotation block: the scenario at the measured lower bound of the "
    "over-rotation, which bounds nothing above it); and "
    "the readout assignment, which the in-batch calibration inverts per target and which scales "
    "visibility without moving a phase. Does not cancel: the readout-induced effects of the other "
    "targets' simultaneous mid-circuit readouts, which the readout arms carry and the reference's "
    "wait does not, so they are part of what delta(tau) measures; and drift between batches, which "
    "the reference sharing a batch with tau 0 and tau 5 handles for those two arms and which moves "
    "delta(15), delta(40) and delta(100) together otherwise."
)
TEMPORAL_ASSUMPTION = (
    "The implied T1 assumes the P(1|1) drop between the no-wait and the wait run comes only from T1 "
    "decay during the wait and that readout fidelity stayed constant between the runs; a readout-fidelity "
    "drift between the runs enters T1 directly."
)


def quantized(value: Any) -> Any:
    """value with every float rounded to SIGNIFICANT significant digits."""
    if isinstance(value, float):
        return float(f"{value:.{SIGNIFICANT}g}")
    if isinstance(value, dict):
        return {key: quantized(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [quantized(item) for item in value]
    return value


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fold(rate_hz: float, period_hz: float) -> float:
    """rate_hz folded into (-period / 2, period / 2]."""
    folded = (rate_hz + period_hz / 2) % period_hz - period_hz / 2
    return period_hz / 2 if folded == -period_hz / 2 else folded


def rotation(axis: str, angle: float) -> np.ndarray:
    pauli = {"x": np.array([[0, 1], [1, 0]]), "y": np.array([[0, -1j], [1j, 0]])}[axis]
    return np.cos(angle / 2) * np.eye(2) - 1j * np.sin(angle / 2) * pauli


def ramsey_p1(phi: float, eps: float, last: str) -> float:
    """P1 after X90, a Z phase phi and X90 (last = x) or Y90 (last = y) with each pulse over-rotated."""
    angle = math.pi / 2 + eps / 2
    unitary = rotation(last, angle) @ np.diag([1, np.exp(1j * phi)]) @ rotation("x", angle)
    return float(abs(unitary[1, 0]) ** 2)


def estimate(phi: float, eps: float) -> float:
    return math.atan2(2 * ramsey_p1(phi, eps, "y") - 1, 2 * ramsey_p1(phi, eps, "x") - 1)


def over_rotation_bias(eps: float) -> dict[str, float]:
    """Phase-estimate error range over phi and the rate-error spread across the pilot's SPAN at eps."""
    phis = np.linspace(0, 2 * np.pi, PHASE_GRID)
    reference = [estimate(float(p), 0.0) for p in phis]
    errors = [wrap(estimate(float(p), eps) - r) for p, r in zip(phis, reference, strict=True)]
    low, high = min(errors), max(errors)
    seconds = SPAN * CYCLE_SECONDS
    return {
        "phase_error_min_rad": low,
        "phase_error_max_rad": high,
        "rate_error_spread_at_eps_khz": (high - low) / (2 * math.pi * seconds) / 1e3,
    }


def circuit_waits(text: str) -> tuple[dict[int, int], set[int]]:
    """Cycles waited per qubit and the qubits flipped by a bare X in a readout circuit."""
    waits: dict[int, int] = {}
    flips: set[int] = set()
    for line in text.splitlines():
        if wait := WAIT_LINE.match(line.strip()):
            waits[int(wait.group(2))] = waits.get(int(wait.group(2)), 0) + int(wait.group(1))
        elif flip := FLIP_LINE.match(line.strip()):
            flips.add(int(flip.group(1)))
    return waits, flips


def run_time(run: Path) -> datetime:
    stamp = RUN_STAMP.match(run.name)
    if stamp is None:
        raise SystemExit(f"{run.name} carries no UTC timestamp prefix")
    return datetime.strptime(stamp.group(1), "%Y-%m-%dT%H%M%SZ")


def has_readout_pair(run: Path) -> bool:
    """run is a collected Tuna-17 run holding readout-0 and readout-1 circuits and their raw shots."""
    files = [run / "cases.json", run / "readout-0.cq", run / "readout-1.cq", run / "results.json"]
    raw = [run / "raw" / "readout-0.cq.json", run / "raw" / "readout-1.cq.json"]
    return all(p.is_file() for p in [*files, *raw]) and read_json(run / "cases.json").get("backend") == "tuna_17"


def unlisted_runs() -> list[str]:
    """Retained Tuna-17 runs with a readout pair that READOUT_RUNS omits."""
    return [run.name for run in sorted(RUNS.iterdir()) if run.name not in READOUT_RUNS and has_readout_pair(run)]


def readout_runs() -> list[dict[str, Any]]:
    """The READOUT_RUNS runs, oldest first; the earliest no-wait run is the implied-T1 reference."""
    if list(READOUT_RUNS) != sorted(set(READOUT_RUNS)):
        raise SystemExit("READOUT_RUNS must list distinct runs in timestamp order")
    found = []
    for name in READOUT_RUNS:
        run = RUNS / name
        if not has_readout_pair(run):
            raise SystemExit(f"{retained_path(run)} holds no collected Tuna-17 readout-0 and readout-1 pair")
        files = [run / "readout-0.cq", run / "readout-1.cq"]
        zero, one = (read_json(run / "raw" / f"{f.name}.json") for f in files)
        waits, flips = circuit_waits(files[1].read_text(encoding="utf-8"))
        prepared = flips or set(range(NQUBITS))
        found.append(
            {
                "run": retained_path(run),
                "time": run_time(run),
                "shots": [len(zero), len(one)],
                "waits": waits,
                "prepared": prepared,
                "p1_given_0": {q: sum(bit(s, q) for s in zero) / len(zero) for q in range(NQUBITS)},
                "p1_given_1": {q: sum(bit(s, q) for s in one) / len(one) for q in sorted(prepared)},
            }
        )
    return found


def implied_t1(
    wait_us: float, no_wait: float, waited: float, floor_no_wait: float, floor_waited: float
) -> float | None:
    """wait / ln((P1_nowait - floor) / (P1_wait - floor)), each run's P(1|0) as its floor.

    Under one assignment channel the observed P(1|1) is P(1|0) + scale * P(excited), so the
    additive floor comes off before the survival ratio; None when the wait run reads no lower.
    """
    high, low = no_wait - floor_no_wait, waited - floor_waited
    if not (0 < low < high):
        return None
    return wait_us / math.log(high / low)


def readout_block(qubit: int, runs: list[dict[str, Any]], series: str) -> dict[str, Any]:
    rows = []
    for r in runs:
        wait_us = r["waits"].get(qubit, 0) * CYCLE_SECONDS * 1e6
        p11 = r["p1_given_1"].get(qubit)
        rows.append(
            {
                "run": r["run"],
                "shots": r["shots"][0],
                "wait_before_readout_us": wait_us,
                "p1_given_0": r["p1_given_0"][qubit],
                "p1_given_1": p11,
            }
        )
    waited = [r for r in runs if r["waits"].get(qubit, 0) > 0 and qubit in r["p1_given_1"]]
    t1: dict[str, Any] | None = None
    if waited:
        # The series' batch-00 calibration is the one its verdict inverts, so the T1 beside the verdict
        # comes from that device state; a series without one falls back to its earliest waited run.
        own = [r for r in waited if r["run"].endswith(f"_{series}-batch-00")]
        wait_run = (own or waited)[0]
        wait_us = wait_run["waits"][qubit] * CYCLE_SECONDS * 1e6
        candidates = [
            r
            for r in runs
            if r["waits"].get(qubit, 0) == 0
            and qubit in r["p1_given_1"]
            and timedelta(0) < wait_run["time"] - r["time"] <= NOWAIT_WINDOW
        ]
        by_run = {
            r["run"]: implied_t1(
                wait_us,
                r["p1_given_1"][qubit],
                wait_run["p1_given_1"][qubit],
                r["p1_given_0"][qubit],
                wait_run["p1_given_0"][qubit],
            )
            for r in candidates
        }
        if candidates:
            reference = candidates[0]
            t1 = {
                "us": by_run[reference["run"]],
                "wait_us": wait_us,
                "wait_run": wait_run["run"],
                "no_wait_run": reference["run"],
                "us_by_no_wait_run": by_run,
                "assumption": TEMPORAL_ASSUMPTION,
            }
    return {"runs": rows, "implied_t1": t1}


def map_visibility(analysis: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Sector-resolved visibility of every target at the map's delays, recomputed from the retained batches."""
    meta, _ = members("tuna_17")
    adjacent = neighbors(meta["pairs"])
    shots: dict[str, list[str]] = {}
    for run in analysis["runs"]:
        directory = ROOT / run
        for row in read_json(directory / "cases.json")["circuits"]:
            if row["file"].startswith("targets-"):
                shots[row["file"]] = read_json(directory / "raw" / f"{row['file']}.json")
    table = tabulate(meta, shots)
    out: dict[int, dict[str, Any]] = {}
    for role in ROLES:
        for target in meta["parts"][role]:
            e01, e10 = analysis["readout_assignment"][str(target)]
            per_delay: dict[int, dict[tuple[int, ...], float]] = {d: {} for d in MAP_DELAYS}
            for z, delay in itertools.product(itertools.product((0, 1), repeat=len(adjacent[target])), MAP_DELAYS):
                expect = {}
                for quadrature in QUADRATURES:
                    ones, total = table.get((role, quadrature, delay, target, z), (0.0, 0.0))
                    if total <= 0:
                        break
                    expect[quadrature] = 2 * (ones / total - e01) / (1 - e01 - e10) - 1
                if len(expect) == 2:
                    per_delay[delay][z] = math.hypot(expect["x"], expect["y"])
            zero = tuple(0 for _ in adjacent[target])
            out[target] = {
                "role": role,
                "zero_sector": [per_delay[d][zero] for d in MAP_DELAYS],
                "min_sector": [min(per_delay[d].values()) for d in MAP_DELAYS],
            }
    return out


def crosstalk() -> dict[int, dict[str, Any]]:
    """Driver rows of the crosstalk run keyed by driven qubit, with the over-rotation bound where one exists."""
    out: dict[int, dict[str, Any]] = {}
    for star in read_json(CROSSTALK_RUN / "analysis.json")["additivity"]:
        for key in ("A", "B"):
            driver = star["drivers"][key]
            row = {
                "partner": star["B" if key == "A" else "A"],
                "p1_driven_alone": driver["p1_driven_alone"],
                "p1_driven_with_partner": driver["p1_driven_with_other"],
                "simultaneous_change_z": driver["simultaneous_change_z"],
                "over_rotation": None,
            }
            bound = driver.get("overrotation_lower_bound_rad_per_x")
            if bound is not None:
                row["over_rotation"] = {"lower_bound_rad_per_x": bound, **over_rotation_bias(bound)}
            out[driver["qubit"]] = row
    return out


def build() -> dict[str, Any]:
    analysis = read_json(MAP_ANALYSIS)
    meta, _ = members("tuna_17")
    series_of = {q: s for s in PILOT_SERIES for q in meta["parts"][s]}
    map_period_hz = TO_HZ * 2 * math.pi / (MAP_DELAYS[1] - MAP_DELAYS[0])
    edge_hz = TO_HZ * math.pi / SPAN
    visibility = map_visibility(analysis)
    drivers = crosstalk()
    runs = readout_runs()
    wait_us = SETTLE_CYCLES * CYCLE_SECONDS * 1e6
    targets = {row["target"]: row for row in analysis["targets"]}
    incident: dict[int, list[dict[str, Any]]] = {q: [] for q in range(NQUBITS)}
    for edge in analysis["edges"]:
        a, b = edge["edge"]
        for q, other in ((a, b), (b, a)):
            incident[q].append(
                {
                    "neighbor": other,
                    "j_hz": edge["j_hz"],
                    "j_se_hz": edge["j_se_hz"],
                    "usable_ends": edge["usable_ends"],
                    "own_end_j_hz": targets[q]["j_hz"][str(other)],
                    "own_end_j_se_hz": targets[q]["j_se_hz"][str(other)],
                }
            )
    qubits: dict[str, Any] = {}
    for q in range(NQUBITS):
        omega = targets[q]["omega_hz"]
        nu = fold(omega, map_period_hz)
        vis = visibility[q]
        check = min(vis["min_sector"])
        if abs(check - targets[q]["min_visibility"]) > 1e-9 * max(1.0, check):
            raise SystemExit(f"qubit {q}: recomputed map visibility {check} differs from the analysis")
        readout = readout_block(q, runs, series_of[q])
        t1 = readout["implied_t1"]
        prediction: dict[str, Any] | None = None
        if t1 is not None and t1["us"] is not None:
            base = vis["zero_sector"][1]
            conservative = base * math.exp(-t1["wait_us"] / t1["us"])
            prediction = {
                "label": "predicted",
                "basis": "map zero-sector visibility at 2 us (conservative for the pilot's d2 of 1.54 us)",
                "visibility_conservative": conservative,
                "visibility_calibration_absorbed": base,
                "min_visibility": MIN_VISIBILITY,
                "clears_conservative": conservative >= MIN_VISIBILITY,
                "clears_calibration_absorbed": base >= MIN_VISIBILITY,
            }
        driver = drivers.get(q)
        qubits[str(q)] = {
            "series": series_of[q],
            "coupler_map": {
                "role": vis["role"],
                "usable_target": targets[q]["usable"],
                "omega_hz": omega,
                "omega_se_hz": targets[q]["omega_se_hz"],
                "folded_detuning_hz": nu,
                "edge_distance_hz": edge_hz - abs(nu),
                "pilot_alias_edge_flag": abs(edge_hz - abs(nu)) <= EDGE_WINDOW_HZ,
                "visibility_delays_us": [d * CYCLE_SECONDS * 1e6 for d in MAP_DELAYS],
                "visibility_zero_sector": vis["zero_sector"],
                "visibility_min_over_sectors": vis["min_sector"],
                "max_abs_j_hz": max(abs(c["j_hz"]) for c in incident[q]),
                "couplers": incident[q],
            },
            "spectator_drive": driver,
            "readout": readout,
            "visibility_at_d2_plus_wait": prediction,
        }
    return {
        "schema": SCHEMA,
        "profile": "tuna_17",
        "role": "context printed beside each ring-down verdict; the preregistered decision rule is untouched",
        "pilot": {
            "series_targets": {s: meta["parts"][s] for s in PILOT_SERIES},
            "delays_cycles": list(PILOT_DELAYS),
            "span_cycles": SPAN,
            "cycle_seconds": CYCLE_SECONDS,
            "alias_edge_hz": edge_hz,
            "alias_edge_flag_window_hz": EDGE_WINDOW_HZ,
            "edge_scope": "absolute reference rate only; delta, its chi-square fits, A and T are unchanged",
            "settle_wait_us": wait_us,
            "min_visibility": MIN_VISIBILITY,
        },
        "coupler_map": {
            "analysis": retained_path(MAP_ANALYSIS),
            "runs": analysis["runs"],
            "delays_cycles": list(MAP_DELAYS),
            "alias_period_hz": map_period_hz,
        },
        "spectator_drive_run": retained_path(CROSSTALK_RUN),
        "over_rotation_model": (
            "X90 and the final X90 or Y90 turn through pi/2 + eps/2; the rate error is the phase-error "
            f"spread over {PHASE_GRID} phases divided by 2 pi SPAN x {CYCLE_SECONDS * 1e9:g} ns"
        ),
        "common_mode": COMMON_MODE,
        "qubits": qubits,
    }


def render() -> str:
    return json.dumps(quantized(build()), indent=1) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="recompute the record and compare bytes")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    text = render()
    if args.check:
        if not args.out.is_file() or args.out.read_text(encoding="utf-8") != text:
            print(f"{args.out} differs from its recomputation", file=sys.stderr)
            return 1
        print(f"{args.out}: device context reproduces")
        for name in unlisted_runs():
            print(f"{name}: retained Tuna-17 readout pair outside READOUT_RUNS")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(f"{NQUBITS} qubits -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
