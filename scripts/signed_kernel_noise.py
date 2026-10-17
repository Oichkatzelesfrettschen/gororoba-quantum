"""The signed kernel probe and its dark count under a retained calibration's noise.

gororoba_quantum/signed_kernel_probe.py prices two readouts of the
perturbed sedenion kernel B(t) u = t v / (2 + |t|):

- the dark count, p(t) = t^2 / (2 + |t|)^2 on the selector;
- the signed Hadamard test, <Z_c> = s(t) = t / (2 + |t|) on the control.

It scales the signed visibility by (1 - e)^CZ at a median CZ error. This
script replaces that factor with the noise model itself:

1. It compiles every probe to the snapshot Target at optimization level 3,
   with the layout pinned by the LAYOUT_T compile: the retained dark and
   signed probes, their structure-matched forms (one parametrized compile,
   bound per t), and the bright control u' = (e4 + e15)/sqrt2 of both dark
   forms, whose ideal success is (4 + t^2)/(2 + |t|)^2.
2. Each arm's exact noisy law comes from snapshot_laws.outcome_law (gate,
   idle and assignment noise of live_run's model), arm by arm through
   parallel.ordered_map. The matched signed probe also runs a null arm at
   t = 0 with each sign phase, and six term arms: the selector loaded with
   one LCU term (e2, e1 or e10) at each phase, which separate the terms'
   contributions to the readout.
3. It fits each probe's readout against its ideal law by least squares and
   compares the signed visibility with the median-error factor and with the
   product of (1 - e) over the CZ edges the compile uses.
4. It prices a z = 3 resolution of each contrast at t = 1/20, 1/10 and 1/5,
   with the direction of every dark contrast against its t = 0 arm.

Noiseless laws of the same compiled circuits must equal their ideal laws to
1e-9, which checks the compile and the register move. The entry reads
GOROROBA_AER_DEVICE (CPU by default). ``--check FILE --run DIR`` requires
FILE to be byte-identical to the result collected in the Kaggle run DIR (its
collect.json ledger), then recompiles and recomputes the laws at the ``--t``
values (LAYOUT_T is always included) on GOROROBA_AER_DEVICE, and requires the layouts
and CZ counts to match FILE exactly and each law to match it to 1e-8.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit, transpile  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402
import signed_kernel_probe as probe  # noqa: E402
import snapshot_laws  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/calibration/ibm_kingston.json"
OUTPUT = "results/kaggle_out/signed_kernel_noise.json"
T_GRID = (-0.2, -0.1, -0.05, 0.0, 0.05, 0.1, 0.2)
PRICE_T = (0.05, 0.1, 0.2)
LAYOUT_T = -0.05
Z_SCORE = probe.Z_SCORE
# Selector RY angles (prep_high, prep_low) that load one LCU term: s = 00 is
# e2, s = 01 is e1 and s = 10 is e10 (signed_kernel_probe.SELECTOR_UNITS).
TERM_ANGLES = {"e2": (0.0, 0.0), "e1": (0.0, math.pi), "e10": (math.pi, 0.0)}


def signal(t: float) -> float:
    return t / (2.0 + abs(t))


def dark_success(t: float) -> float:
    return signal(t) ** 2


# Retained probes synthesize sign(t) inside a diagonal, so each t compiles to
# its own circuit; matched probes compile once with parameters and bind t.
PER_T: dict[str, Callable[[float], QuantumCircuit]] = {
    "dark": probe.dark_probe,
    "dark_bright": lambda t: probe.dark_probe(t, bright=True),
    "signed": probe.signed_probe,
}
MATCHED: dict[str, Callable[[], QuantumCircuit]] = {
    "dark_matched": probe.matched_dark_probe,
    "dark_matched_bright": lambda: probe.matched_dark_probe(bright=True),
    "signed_matched": probe.matched_signed_probe,
}


def kind(name: str) -> str:
    return name.split("_")[0]


def ideal(name: str, t: float) -> float:
    if kind(name) == "signed":
        return signal(t)
    return probe.bright_success(t) if name.endswith("bright") else dark_success(t)


def readout(name: str, law: np.ndarray) -> float:
    """P(selector = 00) for a dark or bright probe, <Z_c> for a signed probe."""
    return float(law[0]) if kind(name) == "dark" else float(law[0] - law[1])


def compile_circuit(view: Any, circuit: QuantumCircuit, layout: list[int] | None) -> QuantumCircuit:
    return transpile(circuit, view, initial_layout=layout, optimization_level=3, seed_transpiler=probe.SEED)


def natural_phase(t: float) -> float:
    return float(probe.matched_values(t)[probe.SIGN_PHASE])


def arm_phase(name: str, t: float) -> float | None:
    """The sign phase a probe's arm at t runs with; None for a per-t probe."""
    return natural_phase(t) if name in MATCHED else None


def bind(compiled: QuantumCircuit, values: dict[str, float]) -> QuantumCircuit:
    return compiled.assign_parameters({parameter: values[parameter.name] for parameter in compiled.parameters})


def t_values(t: float, phase: float) -> dict[str, float]:
    values = {parameter.name: value for parameter, value in probe.matched_values(t).items()}
    values[probe.SIGN_PHASE.name] = phase
    return values


def compile_all(snapshot: dict[str, Any], ts: tuple[float, ...]) -> tuple[dict[str, list[int]], list[Any]]:
    """Layouts per probe and every arm as (metadata, circuit).

    A matched signed probe adds the null arm (0, pi): at t = 0 the phase
    multiplies a zero amplitude, so both null arms ideally read 0. Its term
    arms load one LCU term at phase 0 or pi; the e2 term ideally reads
    +1 or -1 and the e1 and e10 terms 0.
    """
    view, _ = calibration_snapshot.noise_model(snapshot)
    layouts: dict[str, list[int]] = {}
    arms: list[Any] = []
    for name, builder in PER_T.items():
        width = builder(LAYOUT_T).num_qubits
        reference = compile_circuit(view, builder(LAYOUT_T), None)
        layouts[name] = list(reference.layout.initial_index_layout(filter_ancillas=True)[:width])
        for t in ts:
            meta = {"probe": name, "t": t, "sign_phase": None, "ideal": ideal(name, t)}
            arms.append((meta, compile_circuit(view, builder(t), layouts[name])))
    for name, matched in MATCHED.items():
        layout = layouts[name.replace("_matched", "")]
        layouts[name] = layout
        compiled = compile_circuit(view, matched(), layout)
        keys = [(t, natural_phase(t)) for t in ts]
        if name == "signed_matched":
            keys.append((0.0, math.pi))
        for t, phase in keys:
            meta = {"probe": name, "t": t, "sign_phase": phase, "ideal": ideal(name, t)}
            arms.append((meta, bind(compiled, t_values(t, phase))))
        if name == "signed_matched":
            for term, (high, low) in TERM_ANGLES.items():
                for phase in (0.0, math.pi):
                    expected = (1.0 if phase == 0.0 else -1.0) if term == "e2" else 0.0
                    values = {"prep_high": high, "prep_low": low, "sign_phase": phase}
                    meta = {"probe": "signed_matched_terms", "term": term, "sign_phase": phase, "ideal": expected}
                    arms.append((meta, bind(compiled, values)))
    return layouts, arms


def cz_edges(snapshot: dict[str, Any], compiled: QuantumCircuit) -> list[float]:
    errors = {tuple(sorted(row["qargs"])): row["error"] for row in snapshot["instructions"]["cz"]}
    return [
        errors[tuple(sorted(compiled.find_bit(q).index for q in instruction.qubits))]
        for instruction in compiled.data
        if instruction.operation.name == "cz"
    ]


class ArmLaw:
    """Picklable worker: one compiled arm -> its noiseless check and exact noisy law."""

    def __init__(self, snapshot: dict[str, Any], device: str) -> None:
        self.snapshot = snapshot
        self.device = device

    def __call__(self, item: tuple[dict[str, Any], QuantumCircuit]) -> dict[str, Any]:
        meta, circuit = item
        name = meta["probe"]
        noiseless = readout(name, snapshot_laws.outcome_law(self.snapshot, circuit, self.device, noisy=False))
        if abs(noiseless - meta["ideal"]) > 1e-9:
            raise SystemExit(f"{meta}: compiled noiseless readout {noiseless} against {meta['ideal']}")
        law = snapshot_laws.outcome_law(self.snapshot, circuit, self.device)
        edges = cz_edges(self.snapshot, circuit)
        return {
            **meta,
            "law": [float(x) for x in law],
            "readout": readout(name, law),
            "cz": len(edges),
            "depth": circuit.depth(),
            "active_qubits": snapshot_laws.active_qubits(circuit),
            "cz_product": float(np.prod([1.0 - e for e in edges])),
        }


def fit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Least-squares intercept and slope of ys on xs, and the largest residual."""
    slope, intercept = np.polyfit(np.asarray(xs), np.asarray(ys), 1)
    residual = max(abs(y - (intercept + slope * x)) for x, y in zip(xs, ys, strict=True))
    return float(intercept), float(slope), float(residual)


def evaluate(snapshot: dict[str, Any], ts: tuple[float, ...], device: str) -> dict[str, Any]:
    layouts, arms = compile_all(snapshot, ts)
    median_cz = float(np.median([row["error"] for row in snapshot["instructions"]["cz"] if row["error"] < 1.0]))
    rows = parallel.ordered_map(ArmLaw(snapshot, device), arms, min_items=1)
    probes: dict[str, Any] = {}
    for name in (*PER_T, *MATCHED):
        own = [row for row in rows if row["probe"] == name]
        natural = [r for r in own if r["sign_phase"] == arm_phase(name, r["t"])]
        intercept, slope, residual = fit([r["ideal"] for r in natural], [r["readout"] for r in natural])
        reference = next(r for r in natural if r["t"] == LAYOUT_T)
        probes[name] = {
            "layout": layouts[name],
            "rows": own,
            "intercept": intercept,
            "slope": slope,
            "max_fit_residual": residual,
            "median_cz_factor": (1.0 - median_cz) ** reference["cz"],
            "edge_cz_factor": reference["cz_product"],
        }
    terms = [row for row in rows if row["probe"] == "signed_matched_terms"]
    return {"median_cz_error": median_cz, "probes": probes, "signed_matched_terms": terms}


def _shots(variances: list[float], difference: float) -> int:
    """Total shots over equal arms for |difference| = Z_SCORE standard errors."""
    return math.ceil(len(variances) * Z_SCORE**2 * sum(variances) / difference**2)


def price(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Readout contrasts and the shots that resolve them at z = Z_SCORE, from the model's laws.

    - minus_zero (dark and bright probes): the selector-00 rate at t minus
      the t = 0 arm, its ideal value, whether its sign is inverted against
      the ideal, and the shots that resolve it. A resolved inverted contrast
      detects a t-dependent background, not p(t).
    - raw_differential: <Z_c>(t) - <Z_c>(-t), two arms.
    - null_subtracted (matched probe): (<Z_c>(t) - N_0) - (<Z_c>(-t) - N_pi),
      four arms, with N_phi the t = 0 arm at sign phase phi; ideally 2 s(t).
    - visibility: each signed contrast divided by its ideal 2 s(t).
    """
    rows = []
    for t in PRICE_T:
        row: dict[str, Any] = {"t": t, "ideal_differential": 2.0 * signal(t)}
        for name, entry in result["probes"].items():
            got = {(r["t"], r["sign_phase"]): r["readout"] for r in entry["rows"]}
            plus, minus, zero = (got[(x, arm_phase(name, x))] for x in (t, -t, 0.0))
            if kind(name) == "dark":
                d = plus - zero
                expected = ideal(name, t) - ideal(name, 0.0)
                row[f"{name}_minus_zero"] = d
                row[f"{name}_ideal_minus_zero"] = expected
                row[f"{name}_inverted"] = bool(d * expected < 0)
                row[f"{name}_shots"] = _shots([plus * (1.0 - plus), zero * (1.0 - zero)], d) if d else None
                continue
            raw = plus - minus
            row[f"{name}_raw_differential"] = raw
            row[f"{name}_raw_visibility"] = raw / (2.0 * signal(t))
            row[f"{name}_raw_shots"] = _shots([1.0 - plus * plus, 1.0 - minus * minus], raw)
            if name in MATCHED:
                null_pi = got[(0.0, math.pi)]
                corrected = (plus - zero) - (minus - null_pi)
                row["null_offset_difference"] = zero - null_pi
                row[f"{name}_null_subtracted"] = corrected
                row[f"{name}_null_subtracted_visibility"] = corrected / (2.0 * signal(t))
                row[f"{name}_null_subtracted_shots"] = _shots(
                    [1.0 - x * x for x in (plus, minus, zero, null_pi)], corrected
                )
        rows.append(row)
    return rows


def environment(device: str) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "qiskit": qiskit.__version__,
        "qiskit_aer": qiskit_aer.__version__,
        "device": device,
        "workers": parallel.workers(),
    }


def run(ts: tuple[float, ...], device: str) -> dict[str, Any]:
    ts = tuple(sorted(set(ts) | {LAYOUT_T, 0.0}))
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    started = time.time()
    result = evaluate(snapshot, ts, device)
    if all(t in ts and -t in ts for t in PRICE_T):
        result["shots"] = price(result)
    return {
        "schema": "gororoba-signed-kernel-noise-v2",
        "snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
        "calibration": snapshot["calibration"],
        **calibration_snapshot.backend_identity(snapshot),
        "seed_transpiler": probe.SEED,
        "layout_t": LAYOUT_T,
        "environment": environment(device),
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


def _row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (row["probe"], row.get("t"), row.get("term"), row["sign_phase"])


def check(path: Path, run_dir: Path, ts: tuple[float, ...]) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    failures = bound_to_run(path, run_dir)
    replay = run(ts, calibration_snapshot.aer_device())
    kept_rows = {
        _row_key(row): row
        for row in [r for entry in retained["probes"].values() for r in entry["rows"]]
        + retained["signed_matched_terms"]
    }
    for name, fresh in replay["probes"].items():
        if fresh["layout"] != retained["probes"][name]["layout"]:
            failures.append(f"{name} layout {fresh['layout']} against {retained['probes'][name]['layout']}")
    fresh_rows = [r for entry in replay["probes"].values() for r in entry["rows"]] + replay["signed_matched_terms"]
    for row in fresh_rows:
        old = kept_rows.get(_row_key(row))
        if old is None:
            failures.append(f"{_row_key(row)} is absent from {path}")
            continue
        if row["cz"] != old["cz"]:
            failures.append(f"{_row_key(row)}: {row['cz']} CZ against {old['cz']}")
        if not np.allclose(row["law"], old["law"], rtol=1e-8, atol=1e-10):
            failures.append(f"{_row_key(row)}: law {row['law']} against {old['law']}")
    for failure in failures:
        print(failure)
    print(f"signed kernel noise replay: t = {sorted(set(ts) | {LAYOUT_T, 0.0})}, {len(failures)} departures")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--t", default="-0.05,0,0.05", help="comma-separated t values for --check")
    parser.add_argument("--run", type=Path, help="Kaggle run directory whose collected output --check binds")
    args = parser.parse_args()
    if args.check:
        if args.run is None:
            parser.error("--check needs --run")
        return check(args.check, args.run, tuple(float(t) for t in args.t.split(",")))
    if args.out is None:
        parser.error("--out is required without --check")
    result = run(T_GRID, calibration_snapshot.aer_device())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(T_GRID)} t values per probe in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
