"""The signed kernel probe and its dark count under a retained calibration's noise.

gororoba_quantum/signed_kernel_probe.py prices two readouts of the
perturbed sedenion kernel B(t) u = t v / (2 + |t|):

- the dark count, p(t) = t^2 / (2 + |t|)^2 on the selector;
- the signed Hadamard test, <Z_c> = s(t) = t / (2 + |t|) on the control.

It scales the signed visibility by (1 - e)^CZ at a median CZ error. This
script replaces that factor with the noise model itself:

1. It compiles both probes to the snapshot Target at optimization level 3,
   with the layout pinned by the t = -1/20 compile.
2. For each t of T_GRID it computes the exact noisy outcome law
   (snapshot_laws.outcome_law: gate, idle and assignment noise of
   live_run's model).
3. It fits <Z_c> = c0 + V s(t) and P(selector = 00) = b + g p(t) by least
   squares, and compares V with the median-error factor and with the product
   of (1 - e) over the CZ edges the compile actually uses.
4. It prices shots for a z = 3 resolution at t = 1/20, 1/10 and 1/5,
   reporting the offset c0 against the signal V s.

Noiseless laws of the same compiled circuits must equal the statevector
laws s(t) and p(t) to 1e-9, which checks the compile and the register move.
The entry reads GOROROBA_AER_DEVICE (CPU by default). ``--check FILE``
recompiles and recomputes the laws at the ``--t`` values on the CPU, and
requires the CZ counts and layouts to match FILE exactly and each law to
match it to 1e-8.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
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
import signed_kernel_probe as probe  # noqa: E402
import snapshot_laws  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/calibration/ibm_kingston.json"
T_GRID = (-0.2, -0.1, -0.05, 0.0, 0.05, 0.1, 0.2)
PRICE_T = (0.05, 0.1, 0.2)
LAYOUT_T = -0.05
Z_SCORE = probe.Z_SCORE


def signal(t: float) -> float:
    return t / (2.0 + abs(t))


def dark_success(t: float) -> float:
    return signal(t) ** 2


# Retained probes synthesize sign(t) inside a diagonal, so each t compiles to
# its own circuit; matched probes compile once with parameters and bind t.
PER_T: dict[str, Callable[[float], QuantumCircuit]] = {"dark": probe.dark_probe, "signed": probe.signed_probe}
MATCHED: dict[str, Callable[[], QuantumCircuit]] = {
    "dark_matched": probe.matched_dark_probe,
    "signed_matched": probe.matched_signed_probe,
}


def kind(name: str) -> str:
    return name.split("_")[0]


def compile_circuit(view: Any, circuit: QuantumCircuit, layout: list[int] | None) -> QuantumCircuit:
    return transpile(circuit, view, initial_layout=layout, optimization_level=3, seed_transpiler=probe.SEED)


def natural_phase(t: float) -> float:
    return float(probe.matched_values(t)[probe.SIGN_PHASE])


def arm_phase(name: str, t: float) -> float | None:
    """The sign phase a probe's arm at t runs with; None for a per-t probe."""
    return natural_phase(t) if name in MATCHED else None


def bind(compiled: QuantumCircuit, t: float, phase: float) -> QuantumCircuit:
    values = {parameter.name: value for parameter, value in probe.matched_values(t).items()}
    values[probe.SIGN_PHASE.name] = phase
    return compiled.assign_parameters({parameter: values[parameter.name] for parameter in compiled.parameters})


def compile_all(snapshot: dict[str, Any], ts: tuple[float, ...]) -> dict[str, Any]:
    """Circuits keyed by (t, sign phase); the phase is None for the per-t probes.

    A matched probe also runs the null arm (0, pi): at t = 0 the phase acts
    on a zero amplitude, so both null arms ideally read 0, and their
    difference is the offset the sign phase alone induces under noise.
    """
    view, _ = calibration_snapshot.noise_model(snapshot)
    out: dict[str, Any] = {}
    for name, builder in PER_T.items():
        width = builder(LAYOUT_T).num_qubits
        reference = compile_circuit(view, builder(LAYOUT_T), None)
        layout = list(reference.layout.initial_index_layout(filter_ancillas=True)[:width])
        circuits = {(t, None): compile_circuit(view, builder(t), layout) for t in ts}
        out[name] = {"layout": layout, "circuits": circuits}
    for name, matched in MATCHED.items():
        layout = out[kind(name)]["layout"]
        compiled = compile_circuit(view, matched(), layout)
        keys = [(t, natural_phase(t)) for t in ts]
        if 0.0 in ts:
            keys.append((0.0, math.pi))
        out[name] = {"layout": layout, "circuits": {(t, phase): bind(compiled, t, phase) for t, phase in keys}}
    return out


def cz_edges(snapshot: dict[str, Any], compiled: QuantumCircuit) -> list[float]:
    errors = {tuple(sorted(row["qargs"])): row["error"] for row in snapshot["instructions"]["cz"]}
    return [
        errors[tuple(sorted(compiled.find_bit(q).index for q in instruction.qubits))]
        for instruction in compiled.data
        if instruction.operation.name == "cz"
    ]


def readout(name: str, law: np.ndarray) -> float:
    """P(selector = 00) for the dark probe, <Z_c> for the signed probe."""
    return float(law[0]) if kind(name) == "dark" else float(law[0] - law[1])


def ideal(name: str, t: float) -> float:
    return dark_success(t) if kind(name) == "dark" else signal(t)


def fit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Least-squares intercept and slope of ys on xs, and the largest residual."""
    slope, intercept = np.polyfit(np.asarray(xs), np.asarray(ys), 1)
    residual = max(abs(y - (intercept + slope * x)) for x, y in zip(xs, ys, strict=True))
    return float(intercept), float(slope), float(residual)


def evaluate(snapshot: dict[str, Any], ts: tuple[float, ...], device: str) -> dict[str, Any]:
    compiled = compile_all(snapshot, ts)
    median_cz = float(np.median([row["error"] for row in snapshot["instructions"]["cz"] if row["error"] < 1.0]))
    probes: dict[str, Any] = {}
    for name, entry in compiled.items():
        rows = []
        for (t, phase), circuit in entry["circuits"].items():
            noiseless = readout(name, snapshot_laws.outcome_law(snapshot, circuit, device, noisy=False))
            if abs(noiseless - ideal(name, t)) > 1e-9:
                raise SystemExit(f"{name} at t = {t}: compiled noiseless law {noiseless} against {ideal(name, t)}")
            law = snapshot_laws.outcome_law(snapshot, circuit, device)
            edges = cz_edges(snapshot, circuit)
            rows.append(
                {
                    "t": t,
                    "sign_phase": phase,
                    "law": [float(x) for x in law],
                    "readout": readout(name, law),
                    "ideal": ideal(name, t),
                    "cz": len(edges),
                    "depth": circuit.depth(),
                    "active_qubits": snapshot_laws.active_qubits(circuit),
                    "cz_product": float(np.prod([1.0 - e for e in edges])),
                }
            )
        natural = [r for r in rows if r["sign_phase"] in (None, natural_phase(r["t"]))]
        xs = [signal(r["t"]) if kind(name) == "signed" else dark_success(r["t"]) for r in natural]
        intercept, slope, residual = fit(xs, [r["readout"] for r in natural])
        reference = next(r for r in natural if r["t"] == LAYOUT_T)
        probes[name] = {
            "layout": entry["layout"],
            "rows": rows,
            "intercept": intercept,
            "slope": slope,
            "max_fit_residual": residual,
            "median_cz_factor": (1.0 - median_cz) ** reference["cz"],
            "edge_cz_factor": reference["cz_product"],
        }
    return {"median_cz_error": median_cz, "probes": probes}


def _shots(variances: list[float], difference: float) -> int:
    """Total shots over equal arms for |difference| = Z_SCORE standard errors."""
    return math.ceil(len(variances) * Z_SCORE**2 * sum(variances) / difference**2)


def price(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Readout contrasts and the shots that resolve them at z = Z_SCORE, from the model's laws.

    - dark_minus_zero: P(00) at t minus the t = 0 arm; dark_shots is None
      when it is not positive, since no shot count then resolves p(t).
    - raw_differential: <Z_c>(t) - <Z_c>(-t), two arms.
    - null_subtracted (matched probe): (<Z_c>(t) - N_0) - (<Z_c>(-t) - N_pi),
      four arms, with N_phi the t = 0 arm at sign phase phi; ideally 2 s(t).
    - visibility: each contrast divided by its ideal 2 s(t).
    """
    rows = []
    for t in PRICE_T:
        row: dict[str, Any] = {"t": t, "ideal_differential": 2.0 * signal(t)}
        for name, entry in result["probes"].items():
            got = {(r["t"], r["sign_phase"]): r["readout"] for r in entry["rows"]}
            plus, minus, zero = (got[(x, arm_phase(name, x))] for x in (t, -t, 0.0))
            if kind(name) == "dark":
                d = plus - zero
                row[f"{name}_minus_zero"] = d
                row[f"{name}_shots"] = _shots([plus * (1.0 - plus), zero * (1.0 - zero)], d) if d > 0 else None
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
    }


def run(ts: tuple[float, ...], device: str) -> dict[str, Any]:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    started = time.time()
    result = evaluate(snapshot, ts, device)
    if set(PRICE_T) <= set(ts):
        result["shots"] = price(result)
    return {
        "schema": "gororoba-signed-kernel-noise-v1",
        "snapshot": str(SNAPSHOT.relative_to(ROOT)),
        "snapshot_sha256": hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
        "calibration": snapshot["calibration"],
        "seed_transpiler": probe.SEED,
        "layout_t": LAYOUT_T,
        "environment": environment(device),
        "seconds": round(time.time() - started, 1),
        **result,
    }


def check(path: Path, ts: tuple[float, ...]) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    replay = run(ts, "CPU")
    failures = []
    for name, fresh in replay["probes"].items():
        kept = retained["probes"][name]
        if fresh["layout"] != kept["layout"]:
            failures.append(f"{name} layout {fresh['layout']} against {kept['layout']}")
        by_key = {(row["t"], row["sign_phase"]): row for row in kept["rows"]}
        for row in fresh["rows"]:
            old = by_key[(row["t"], row["sign_phase"])]
            if row["cz"] != old["cz"]:
                failures.append(f"{name} t = {row['t']}: {row['cz']} CZ against {old['cz']}")
            if not np.allclose(row["law"], old["law"], rtol=1e-8, atol=1e-10):
                failures.append(f"{name} t = {row['t']}: law {row['law']} against {old['law']}")
    for failure in failures:
        print(failure)
    print(f"signed kernel noise replay: t = {list(ts)}, {len(failures)} departures")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--t", default="-0.05,0,0.05", help="comma-separated t values for --check")
    args = parser.parse_args()
    if args.check:
        return check(args.check, tuple(float(t) for t in args.t.split(",")))
    if args.out is None:
        parser.error("--out is required without --check")
    result = run(T_GRID, os.environ.get("GOROROBA_AER_DEVICE", "CPU"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(T_GRID)} t values per probe in {result['seconds']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
