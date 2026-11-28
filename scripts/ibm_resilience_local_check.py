"""Raw versus mitigated <Z> of one retained experiment row on the local noise model, for the EstimatorV2 design note.

The row is the design_a associator readout (docs/notes/ibm_quantum/native-sdk-opt-ins.md, section "EstimatorV2
resilience"). The check builds the two mitigation families the client Estimator offers from first principles on
the Target's noise model:

- readout inversion, the construction behind measure mitigation (TREX): live_run.readout_corrected inverts each
  measured bit's confusion channel (without the twirl of the service implementation);
- zero-noise extrapolation by global gate folding at noise factors 1, 3 and 5 (ZneOptions defaults), extrapolated to
  zero with a linear and an exponential fit.

It is an equivalent construction of the technique on a simulated channel, never the service implementation, and it
sends nothing anywhere. The noise model acts on gates, delays and readout. Folding repeats the gate body only: the
final measurement stays single, so one readout channel acts at every noise factor and the fit sees gate and idle
attenuation scaled by the factor on top of a fixed readout channel. The report states the factors, the fit
assumptions and the scheduled-duration ratio as separate fields; the ratio sums circuit durations and leaves out the
repetition delay that the submission planner charges.

Usage:
    "$PYTHON" scripts/ibm_resilience_local_check.py --backend fake:fez \\
        --seed-transpiler qrng:REF --seed-simulator qrng:REF
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ibm_dd_compare as dd  # noqa: E402

NOISE_FACTORS = (1, 3, 5)
DEFAULT_SHOTS = 20000
FOLDING_SCOPE = "global gate folding of the compiled body at odd factors; the final measurement is not folded"
FIT_ASSUMPTIONS = (
    "linear: z is affine in the factor; exponential: z = A exp(-b factor), which holds when gate and idle attenuation "
    "multiply and a fixed readout channel is absent or already inverted; the unfolded readout channel breaks a pure "
    "exponential on raw counts"
)


def z_of(law: np.ndarray) -> float:
    """<Z> of the single measured bit: P(0) - P(1)."""
    return float(law[0] - law[1])


def fold(circuit: QuantumCircuit, target: Any, factor: int) -> QuantumCircuit:
    """circuit with its body folded to the odd noise factor, U (U^dagger U)^k with k = (factor - 1) / 2."""
    if factor < 1 or factor % 2 == 0:
        raise ValueError("global folding needs an odd noise factor")
    measures = [
        (circuit.find_bit(i.qubits[0]).index, circuit.find_bit(i.clbits[0]).index)
        for i in circuit.data
        if i.operation.name == "measure"
    ]
    body = circuit.remove_final_measurements(inplace=False)
    inverse = transpile(
        body.inverse(), target=target, initial_layout=list(range(body.num_qubits)), optimization_level=0
    )
    out = QuantumCircuit(body.num_qubits, circuit.num_clbits)
    out.compose(body, inplace=True)
    for _ in range((factor - 1) // 2):
        out.barrier()
        out.compose(inverse, inplace=True)
        out.barrier()
        out.compose(body, inplace=True)
    for qubit, clbit in measures:
        out.measure(qubit, clbit)
    return out


def extrapolate(factors: tuple[int, ...], values: list[float]) -> dict[str, float]:
    """Zero-noise values of z(lambda): a line through the points and an exponential A exp(-b lambda)."""
    x = np.asarray(factors, dtype=float)
    y = np.asarray(values, dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    out = {"linear": float(intercept)}
    if np.all(y > 0) or np.all(y < 0):
        sign = 1.0 if y[0] > 0 else -1.0
        log_slope, log_intercept = np.polyfit(x, np.log(np.abs(y)), 1)
        out["exponential"] = float(sign * math.exp(log_intercept))
    return out


def run_check(
    name: str, target: Any, props: Any, *, shots: int, seed_transpiler: int | None, seed_simulator: int | None
) -> dict[str, Any]:
    import live_run

    case = dd.cases_from_group("design_a")[0]
    isa = dd.compile_cases([case], target, seed_transpiler, None)[0]
    view = live_run.TargetView(name, target)
    scheduler = dd.baseline_manager(view)
    folded = [scheduler.run(fold(isa, target, factor)) for factor in NOISE_FACTORS]
    simulator = live_run.noise_simulator(name, target, props)
    kwargs: dict[str, Any] = {"shots": shots}
    if seed_simulator is not None:
        kwargs["seed_simulator"] = seed_simulator
    result = simulator.run(folded, **kwargs).result()
    ideal_z = z_of(case.ideal)
    raw, corrected = [], []
    for position, circuit in enumerate(folded):
        law = dd.distribution(result.get_counts(position), circuit.num_clbits)
        raw.append(z_of(law))
        corrected.append(z_of(live_run.readout_corrected(law, circuit, props)))
    durations = [c.estimate_duration(target, unit="dt") for c in folded]
    return {
        "row": case.name,
        "backend": name,
        "shots_per_factor": shots,
        "noise_factors": list(NOISE_FACTORS),
        "ideal_z": ideal_z,
        "raw_z": raw,
        "readout_corrected_z": corrected,
        "zne_of_raw": extrapolate(NOISE_FACTORS, raw),
        "zne_of_readout_corrected": extrapolate(NOISE_FACTORS, corrected),
        "duration_dt": durations,
        "scheduled_duration_ratio": sum(durations) / durations[0],
        "repetition_delay_included": False,
        "folding": FOLDING_SCOPE,
        "fit_assumptions": FIT_ASSUMPTIONS,
        "seed_transpiler": seed_transpiler,
        "seed_simulator": seed_simulator,
    }


def format_report(report: dict[str, Any]) -> str:
    rows = [
        f"{report['row']} on {report['backend']}  ideal <Z> {report['ideal_z']:+.4f}  "
        f"shots/factor {report['shots_per_factor']}",
        "  factor  raw <Z>  readout-corrected <Z>  duration dt",
    ]
    for factor, raw, corrected, duration in zip(
        report["noise_factors"], report["raw_z"], report["readout_corrected_z"], report["duration_dt"], strict=True
    ):
        rows.append(f"  {factor:6d}  {raw:+.4f}  {corrected:+.4f}  {duration}")
    rows.append(f"  ZNE of raw {report['zne_of_raw']}")
    rows.append(f"  ZNE of readout-corrected {report['zne_of_readout_corrected']}")
    rows.append(
        f"  scheduled-duration ratio against one unmitigated circuit {report['scheduled_duration_ratio']:.2f} "
        "(circuit durations only, repetition delay omitted)"
    )
    rows.append(f"  folding: {report['folding']}")
    rows.append(f"  fits: {report['fit_assumptions']}")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    import qrng_seeds

    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--backend", default="fake:fez")
    parser.add_argument("--shots", type=int, default=DEFAULT_SHOTS)
    qrng_seeds.add_seed_argument(parser, "--seed-transpiler", help="transpiler seed, qrng:<draw>#<index>")
    qrng_seeds.add_seed_argument(parser, "--seed-simulator", help="Aer seed, qrng:<draw>#<index>")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.seed_transpiler is None or args.seed_simulator is None:
        parser.error("--seed-transpiler and --seed-simulator take qrng:<draw>#<index> values")
    name, target, props = dd.load_target(args.backend)
    report = run_check(
        name, target, props, shots=args.shots, seed_transpiler=args.seed_transpiler, seed_simulator=args.seed_simulator
    )
    print(format_report(report))
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
