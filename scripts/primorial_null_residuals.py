"""Static ZZ and axis tilt against the null-subtracted phase-gradient estimator of the primorial cover defects.

scripts/primorial_cover_noise.py predicts the gap88 phase-gradient tomography
under the incoherent model of the ibm_kingston snapshot and under three
coherent families (CZ conditional phase, sx amplitude, static detuning), and
leaves static ZZ and drive-axis tilt unsimulated. This script closes that gap
on the same compiled arms (optimization level 0, ALAP against the snapshot
Target, the best and median three-qubit paths of
docs/evidence/primorial_cover/noise.json):

1. **Physical identity of signal and null.** For every edge setting (j, x,
   basis) the compiled gap88 arm and the zero-angle null arm must carry the
   same sequence of sx, x, cz and delay instructions on the same qubits with
   the same durations, differing only in rz. RZ is a zero-duration frame
   change in the snapshot Target, so the two arms drive identical pulses and
   any error that is a property of the pulses enters both.
2. **Static ZZ.** Each path coupler carries a ZZ rate zeta (kHz), entering
   before each pulse on either of its qubits over the interval since the
   previous pulse start on either, in the two frames of
   scripts/atlas_coherent_families.py: ``zz`` is CPhase(-2 pi zeta t), the
   frame calibrated with the partner in |0>, and ``zz_symmetric`` is
   RZZ(pi zeta t).
3. **Axis tilt.** Every sx and x pulse R on the tilted qubit becomes
   RY(-beta) R RY(beta), a drive axis cos(beta) X + sin(beta) Z, on one path
   qubit at a time and on all three at once, and at each path qubit's
   gate-error bound: the largest coherent tilt its snapshot sx error r allows,
   acos(2 sqrt(1 - 1.5 r) - 1) (``atlas_coherent_families.gate_bounds``), on
   all three qubits at once in each of the eight sign patterns.

Pulse starts come from the compiled ALAP schedule: each path qubit's timeline
is padded with delays, so a per-qubit cursor over instruction durations gives
every start. Laws are noise-free statevector laws of the three path qubits.
Each scenario reports the raw and the null-subtracted largest coefficient bias
of the phase fit of primorial_cover_noise. Falsifier: a scenario leaves a
device question when its null-subtracted bias reaches one standard deviation
of the noisy null-subtracted estimate at the shot budget noise.json retains
for that path (``shots_identify_all``). An exploratory build-host run of the
fixed-value scenarios preceded this criterion; the gate-bound scenarios and
the retained Kaggle run followed it. The record also
gives the shots per setting at which a hardware run would resolve the residual
at three standard deviations.

``--out FILE`` writes the record; ``--check FILE --run DIR`` requires FILE to
be byte-identical to the collected output of Kaggle run DIR, recomputes the
record and requires layouts, pulse identity and verdicts to match exactly and
each bias to 1e-8.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import primorial_cover_noise as noise  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402

NOISE_RECORD = ROOT / "docs/evidence/primorial_cover/noise.json"
OUTPUT = "results/kaggle_out/primorial_null_residuals.json"
KHZ = 1e3
# ZZ rates span the 1 to 2.5 kHz values the atlas self-test recovers and a tenfold margin; fixed tilts span
# the 0.002 to 0.005 rad atlas self-test range and four times its top, and each path adds its gate-error bound.
Scenario = tuple[str, tuple[int, ...], float | tuple[float, ...]]
SCENARIOS: tuple[Scenario, ...] = (
    *(("zz", (0, 1, 2), zeta) for zeta in (2.0, 5.0, 20.0)),
    *(("zz_symmetric", (0, 1, 2), zeta) for zeta in (2.0, 5.0, 20.0)),
    *(("axis_tilt", (q,), beta) for q in range(3) for beta in (0.005, 0.02)),
    *(("axis_tilt", (0, 1, 2), beta) for beta in (0.005, 0.02)),
)
COUPLERS = ((0, 1), (1, 2))
DRIVEN = ("sx", "x")
PATCHES = ("best", "median")

Timed = list[tuple[Any, list[int], float]]


def timed(
    compiled: QuantumCircuit, layout: list[int], durations: dict[tuple[str, tuple[int, ...]], float], dt: float
) -> Timed:
    """(operation, path wires, start in s) for every instruction of the compiled arm before its measurements.

    Circuit order need not be chronological across wires, so the events are sorted by (start, circuit
    position). Starts never decrease along one wire, so the sort keeps every wire's own order, zero-duration
    rz included, and the ZZ intervals between pulses on a coupler are never negative.
    """
    wire = {q: k for k, q in enumerate(layout)}
    cursor = [0.0, 0.0, 0.0]
    out: Timed = []
    for instruction in compiled.data:
        operation = instruction.operation
        if operation.name in ("barrier", "measure"):
            continue
        physical = [compiled.find_bit(q).index for q in instruction.qubits]
        local = [wire[q] for q in physical]
        start = max(cursor[k] for k in local)
        if operation.name == "delay":
            seconds = float(operation.duration) * (dt if operation.unit == "dt" else 1.0)
        else:
            seconds = durations.get((operation.name, tuple(physical)), 0.0)
        for k in local:
            cursor[k] = start + seconds
        out.append((operation, local, start))
    order = sorted(range(len(out)), key=lambda k: (out[k][2], k))
    return [out[k] for k in order]


def pulses(arm: Timed) -> list[tuple[str, tuple[int, ...], float]]:
    """The arm's physical instruction stream: every non-rz instruction with its wires and start."""
    return [(op.name, tuple(local), round(start, 15)) for op, local, start in arm if op.name != "rz"]


class ScenarioLaw:
    """Picklable worker: one (scenario, timed arm) -> the arm's noise-free law on the path."""

    def __call__(self, item: tuple[Scenario, dict[str, Any], Timed]) -> dict[str, Any]:
        (family, qubits, value), meta, arm = item
        # A per-wire tuple gives each wire its own tilt; a float is one rate or tilt for every wire in ``qubits``.
        tilt = dict(enumerate(value)) if isinstance(value, tuple) else dict.fromkeys(qubits, value)
        rate = 0.0 if isinstance(value, tuple) else value
        out = QuantumCircuit(3)
        last: dict[tuple[int, int], float] = {}
        for operation, local, start in arm:
            if operation.name == "delay":
                continue
            if family.startswith("zz") and operation.name != "rz":
                for pair in COUPLERS:
                    if pair[0] in local or pair[1] in local:
                        if pair in last:
                            interval = start - last[pair]
                            if family == "zz":
                                out.cp(-2.0 * math.pi * rate * KHZ * interval, *pair)
                            else:
                                out.rzz(math.pi * rate * KHZ * interval, *pair)
                        last[pair] = start
            beta = tilt.get(local[0], 0.0) if family.startswith("axis_tilt") and operation.name in DRIVEN else 0.0
            if beta:
                out.ry(beta, local[0])
            out.append(operation, local)
            if beta:
                out.ry(-beta, local[0])
        law = Statevector(out).probabilities()
        return {**meta, "law": [float(v) for v in law]}


class ScenarioFit:
    """Picklable worker: one scenario's arm laws -> its raw and null-subtracted phase fits against the budget."""

    def __init__(self, table: list[int], sigma: float, variance: float) -> None:
        self.table = table
        self.sigma = sigma
        self.variance = variance

    def __call__(self, item: tuple[Scenario, list[dict[str, Any]]]) -> dict[str, Any]:
        scenario, chunk = item
        readings = noise.gradient_readings(chunk, "gap88")
        null = noise.gradient_readings(chunk, "null")
        raw = noise.phase_fit(self.table, *readings, noise.raw_phase_variance(*readings))
        subtracted = noise.null_subtracted(
            self.table, *readings, null, noise.raw_phase_variance(*readings), noise.raw_phase_variance(*null)
        )
        residual = subtracted["max_coefficient_bias"]
        return {
            "family": scenario[0],
            "qubits": list(scenario[1]),
            "value": list(scenario[2]) if isinstance(scenario[2], tuple) else scenario[2],
            "max_coefficient_bias": raw["max_coefficient_bias"],
            "cycle_residual_rms": raw["cycle_residual_rms"],
            "min_visibility": min(raw["visibility"]),
            "null_subtracted_max_bias": residual,
            "detectable_at_budget": residual >= self.sigma,
            "shots_to_resolve_at_3sd": math.ceil(9.0 * self.variance / residual**2) if residual > 1e-12 else None,
        }


def tilt_bounds(snapshot: dict[str, Any], layout: list[int]) -> list[float]:
    """Largest coherent axis tilt each path qubit's snapshot sx error allows (atlas_coherent_families.gate_bounds)."""
    error = {tuple(row["qargs"]): row["error"] for row in snapshot["instructions"]["sx"]}
    return [math.acos(2.0 * math.sqrt(1.0 - 1.5 * error[(q,)]) - 1.0) for q in layout]


def budget(record: dict[str, Any], patch: str) -> tuple[int, float]:
    """noise.json's null-subtracted gap88 shot budget and the per-shot variance of its worst coefficient."""
    fit = record["patches"][patch]["summary"]["gradient"]["gap88"]["null_subtracted"]
    return int(fit["shots_identify_all"]), float(max(fit["per_shot_coefficient_variance"].values()))


def evaluate(snapshot: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    view = calibration_snapshot.snapshot_backend(snapshot)
    dt = float(view.target.dt)
    table = noise.cost_table("gap88")
    logical = [(m, c) for m, c in noise.arms() if m["family"] == "gradient" and m["cost"] in ("gap88", "null")]
    out: dict[str, Any] = {"layouts": {}, "patches": {}}
    for patch in PATCHES:
        layout = record["layouts"]["3"][patch]
        if noise.layouts(snapshot, 3)[patch] != layout:
            raise SystemExit(f"{patch} path {noise.layouts(snapshot, 3)[patch]} differs from noise.json {layout}")
        out["layouts"][patch] = layout
        durations = {
            (name, tuple(qargs)): float(props.duration)
            for name in view.target.operation_names
            for qargs, props in view.target[name].items()
            if qargs is not None and props is not None and props.duration and set(qargs) <= set(layout)
        }
        compiled = parallel.ordered_map(noise.ArmCompile(snapshot), [(c, layout) for _, c in logical], min_items=1)
        arms: list[tuple[dict[str, Any], Timed]] = []
        for (meta, _), circuit in zip(logical, compiled, strict=True):
            arms.append((meta, timed(circuit, layout, durations, dt)))
        streams = {(m["cost"], m["j"], m["x"], m["basis"]): pulses(a) for m, a in arms}
        identical = all(streams["gap88", j, x, b] == streams["null", j, x, b] for _, j, x, b in streams)
        shots, variance = budget(record, patch)
        sigma = math.sqrt(variance / shots)
        bound = tilt_bounds(snapshot, layout)
        signs = list(itertools.product((1.0, -1.0), repeat=3))
        scenarios: list[Scenario] = [
            ("none", (), 0.0),
            *SCENARIOS,
            *(
                ("axis_tilt_gate_bound", (0, 1, 2), tuple(s * b for s, b in zip(sign, bound, strict=True)))
                for sign in signs
            ),
        ]
        items = [(scenario, meta, arm) for scenario in scenarios for meta, arm in arms]
        laws = parallel.ordered_map(ScenarioLaw(), items, min_items=1)
        fits = [(scenario, laws[k * len(arms) : (k + 1) * len(arms)]) for k, scenario in enumerate(scenarios)]
        rows = parallel.ordered_map(ScenarioFit(table, sigma, variance), fits, min_items=1)
        if rows[0]["max_coefficient_bias"] > 1e-9:
            raise SystemExit(
                f"{patch}: noise-free arms miss the exact coefficients by {rows[0]['max_coefficient_bias']}"
            )
        out["patches"][patch] = {
            "signal_and_null_pulses_identical": identical,
            "tilt_gate_bounds": bound,
            "budget_shots_per_setting": shots,
            "budget_coefficient_sd": sigma,
            "scenarios": rows[1:],
            "device_question": (not identical) or any(r["detectable_at_budget"] for r in rows[1:]),
        }
    return out


def run() -> dict[str, Any]:
    snapshot = json.loads(noise.SNAPSHOT.read_text(encoding="utf-8"))
    record = json.loads(NOISE_RECORD.read_text(encoding="utf-8"))
    started = time.time()
    result = evaluate(snapshot, record)
    return {
        "schema": "gororoba-primorial-null-residuals-v1",
        "snapshot": str(noise.SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": hashlib.sha256(noise.SNAPSHOT.read_bytes()).hexdigest(),
        "noise_record": str(NOISE_RECORD.relative_to(ROOT)),
        "noise_record_sha256": hashlib.sha256(NOISE_RECORD.read_bytes()).hexdigest(),
        "calibration": snapshot["calibration"],
        **calibration_snapshot.backend_identity(snapshot),
        "gradient_gamma_over_pi": "1/9",
        "environment": {k: v for k, v in noise.environment("CPU").items() if k != "device"},
        "seconds": round(time.time() - started, 1),
        **result,
    }


def bound_to_run(path: Path, run_dir: Path) -> list[str]:
    """FILE must be the byte-identical output that run_dir's collect.json ledger records."""
    ledger = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    recorded = ledger["files"].get(f"output/repo/{OUTPUT}")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if recorded is None:
        return [f"{run_dir}/collect.json records no {OUTPUT}"]
    return [] if digest == recorded else [f"{path} sha256 {digest} differs from the collected {recorded}"]


def check(path: Path, run_dir: Path) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    failures = bound_to_run(path, run_dir)
    replay = run()
    for key in ("snapshot_sha256", "noise_record_sha256", "layouts"):
        if replay[key] != retained[key]:
            failures.append(f"{key} {replay[key]} against {retained[key]}")
    for patch, fresh in replay["patches"].items():
        kept = retained["patches"][patch]
        for key in ("signal_and_null_pulses_identical", "budget_shots_per_setting", "device_question"):
            if fresh[key] != kept[key]:
                failures.append(f"{patch} {key} {fresh[key]} against {kept[key]}")
        for new, old in zip(fresh["scenarios"], kept["scenarios"], strict=True):
            label = f"{patch} {new['family']} {new['qubits']} {new['value']}"
            if new["detectable_at_budget"] != old["detectable_at_budget"]:
                failures.append(
                    f"{label}: detectable {new['detectable_at_budget']} against {old['detectable_at_budget']}"
                )
            for key in ("max_coefficient_bias", "null_subtracted_max_bias"):
                if not math.isclose(new[key], old[key], rel_tol=1e-8, abs_tol=1e-10):
                    failures.append(f"{label}: {key} {new[key]} against {old[key]}")
    for failure in failures:
        print(failure)
    print(f"primorial null residual replay: {len(failures)} departures")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--run", type=Path, help="Kaggle run directory whose collected output --check binds")
    args = parser.parse_args()
    if args.check:
        if args.run is None:
            parser.error("--check needs --run")
        return check(args.check, args.run)
    if args.out is None:
        parser.error("--out is required without --check")
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out} in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
