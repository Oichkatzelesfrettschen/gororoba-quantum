"""Design study for the census-frequency witness: visibility of compiled sedenion Hadamard tests under device noise.

A Hadamard test of W_ij = L_(e_i e_j)^dagger L_(e_i) L_(e_j), controlled on one
qubit and applied to the basis state |k> of a 4-qubit data register, reads
P(c = 1) = (1 - omega(i, j, k)) / 2 (scripts/algebra_circuit_fixtures.py,
AGENTS.md "Signs, workspace and measurement basis"). Averaged over all
16^3 = 4096 basis triples the ideal frequency is 231/512. Under noise each
triple reads P(c = 1) = 1/2 - V_ijk omega(i, j, k) / 2, so a uniform sample
estimates 1/2 - V (1/2 - 231/512) when the visibility V is common; bright
(omega = +1) and dark (omega = -1) references fix V.

For every ordered pair (i, j), 1 <= i, j <= 15, i != j, the script builds
the controlled W_ij from designs.left_mult_gate and
designs.left_mult_adjoint_gate exactly as the fixture does, compiles the
5-qubit Hadamard test once per pair to the snapshot Target (optimization
level 3, seed 11; the data-state X preparation is outside the compiled block,
so all 16 inputs of a pair share it), and samples every one of its 16 inputs
under calibration_snapshot.noise_simulator. W_ij and W_ji are different
circuits whose signs differ on 336 of the 1680 (i < j, k) triples, so each
order runs its own circuit. Pairs with i = 0, j = 0 or i = j have omega = +1
on every k (their W is the identity up to sign) and enter the census with
their exact ideal value.

Output: per pair the compiled CZ count and per-triple P(c = 1); per-pair
visibility V_ij = sum_k omega (1 - 2 P(c = 1)) / 16; the noisy census
frequency over all 4096 triples against 1/2 - V (1/2 - 231/512) with V the
mean visibility; the bright and dark visibilities V+ (mean 1 - 2P over
omega = +1 triples) and V- (mean 2P - 1 over omega = -1 triples); the census
a two-reference estimator recovers, f = (P - (1 - V+)/2) / ((V+ + V-)/2) over
the simulated triples, when V+ and V- come from all simulated triples and
when they come from the bright and dark triples of one pair alone (the range
over pairs is the reference-mismatch systematic); and the shots a hardware
run needs to resolve the census frequency to +-0.01 at 2 sigma given the
measured visibility.

``--pairs all`` or ``--pairs I,J;I,J``. ``--check FILE`` recomputes FILE's
summary from its records exactly, reruns the named pairs on the CPU and
requires each P(c = 1) within five binomial standard errors and the CZ
counts exactly.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from qiskit import QuantumCircuit, transpile  # noqa: E402

import calibration_snapshot  # noqa: E402
from cd_core import cd_sign  # noqa: E402
from designs import left_mult_adjoint_gate, left_mult_gate  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/calibration/ibm_kingston.json"
DIM = 16
SEED = 11
SHOTS = 4000
CENSUS = Fraction(231, 512)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def omega(i: int, j: int, k: int) -> int:
    return cd_sign(DIM, i, j) * cd_sign(DIM, i ^ j, k) * cd_sign(DIM, j, k) * cd_sign(DIM, i, j ^ k)


def ideal_census() -> Fraction:
    negative = sum(omega(i, j, k) == -1 for i in range(DIM) for j in range(DIM) for k in range(DIM))
    return Fraction(negative, DIM**3)


def hadamard_test(i: int, j: int) -> QuantumCircuit:
    """Controlled W_ij on data qubits 0-3 with control 4, H before and after on the control, control measured."""
    w = QuantumCircuit(4)
    w.append(left_mult_gate(DIM, j), range(4))
    w.append(left_mult_gate(DIM, i), range(4))
    w.append(left_mult_adjoint_gate(DIM, i ^ j), range(4))
    if cd_sign(DIM, i, j) < 0:
        w.global_phase += math.pi
    circuit = QuantumCircuit(5, 1)
    circuit.h(4)
    circuit.append(w.to_gate().control(1), [4, 0, 1, 2, 3])
    circuit.h(4)
    circuit.measure(4, 0)
    return circuit


def prepared(compiled: QuantumCircuit, k: int) -> QuantumCircuit:
    """The compiled test with X on the physical qubits that carry the set bits of k, before everything else."""
    layout = compiled.layout.initial_index_layout()
    prep = QuantumCircuit(compiled.num_qubits, compiled.num_clbits)
    for bit in range(4):
        if (k >> bit) & 1:
            prep.x(layout[bit])
    return prep.compose(compiled)


def pairs_of(text: str) -> list[tuple[int, int]]:
    if text == "all":
        return [(i, j) for i in range(1, DIM) for j in range(1, DIM) if i != j]
    return [tuple(int(v) for v in item.split(",")) for item in text.split(";")]  # type: ignore[misc]


def run(pairs: list[tuple[int, int]], device: str, shots: int) -> dict[str, Any]:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    simulator = calibration_snapshot.noise_simulator(snapshot, device=device)
    target = calibration_snapshot.build_target(snapshot)
    records = []
    for i, j in pairs:
        compiled = transpile(hadamard_test(i, j), target=target, optimization_level=3, seed_transpiler=SEED)
        circuits = [prepared(compiled, k) for k in range(DIM)]
        result = simulator.run(circuits, shots=shots, seed_simulator=SEED + DIM * i + j).result()
        p1 = [result.get_counts(k).get("1", 0) / shots for k in range(DIM)]
        signs = [omega(i, j, k) for k in range(DIM)]
        visibility = sum(s * (1 - 2 * p) for s, p in zip(signs, p1, strict=True)) / DIM
        records.append(
            {
                "pair": [i, j],
                "cz": int(compiled.count_ops().get("cz", 0)),
                "omega": signs,
                "p1": [round(p, 6) for p in p1],
                "visibility": round(visibility, 6),
            }
        )
        print(
            json.dumps({"pair": [i, j], "cz": records[-1]["cz"], "visibility": records[-1]["visibility"]}), flush=True
        )
    return {
        "schema": "census-frequency-design-v2",
        "snapshot": {"path": SNAPSHOT.relative_to(ROOT).as_posix(), "calibration": snapshot["calibration"]},
        "device": device,
        "shots": shots,
        "seed_transpiler": SEED,
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__, "numpy": np.__version__},
        "records": records,
    }


def two_reference(p_mean: float, v_plus: float, v_minus: float) -> float:
    """Fraction of omega = -1 triples from the mean P(c = 1) and the bright and dark visibilities."""
    return (p_mean - (1 - v_plus) / 2) / ((v_plus + v_minus) / 2)


def sided(record: dict[str, Any]) -> tuple[list[float], list[float]]:
    bright = [1 - 2 * p for w, p in zip(record["omega"], record["p1"], strict=True) if w > 0]
    dark = [2 * p - 1 for w, p in zip(record["omega"], record["p1"], strict=True) if w < 0]
    return bright, dark


def summarize(result: dict[str, Any]) -> dict[str, Any]:
    """Noisy census over all 4096 triples, the visibility corrections, and the shots a hardware run needs."""
    census = ideal_census()
    require(census == CENSUS, f"ideal census {census} differs from 231/512")
    by_pair = {tuple(r["pair"]): r for r in result["records"]}
    for (i, j), record in by_pair.items():
        require(record["omega"] == [omega(i, j, k) for k in range(DIM)], f"pair {(i, j)}: recorded signs differ")
    total = Fraction(0)
    noisy = 0.0
    exact_dark = 0
    simulated_p: list[float] = []
    for i in range(DIM):
        for j in range(DIM):
            for k in range(DIM):
                w = omega(i, j, k)
                total += Fraction(1 - w, 2)
                if (i, j) in by_pair:
                    noisy += by_pair[i, j]["p1"][k]
                    simulated_p.append(by_pair[i, j]["p1"][k])
                else:
                    noisy += (1 - w) / 2
                    exact_dark += w < 0
    require(total / DIM**3 == census, "the census sum disagrees with the ideal frequency")
    noisy /= DIM**3
    measured = [r["visibility"] for r in result["records"]]
    mean_v = float(np.mean(measured))
    # Common-visibility prediction: simulated triples read 1/2 - V omega / 2;
    # pairs with an index 0 or i = j carry W = +-identity and keep their ideal value.
    predicted = 0.0
    for i in range(DIM):
        for j in range(DIM):
            for k in range(DIM):
                w = omega(i, j, k)
                predicted += 0.5 - mean_v * w / 2 if (i, j) in by_pair else (1 - w) / 2
    predicted /= DIM**3
    bright = [v for r in result["records"] for v in sided(r)[0]]
    dark = [v for r in result["records"] for v in sided(r)[1]]
    v_plus, v_minus = float(np.mean(bright)), float(np.mean(dark))
    p_mean = float(np.mean(simulated_p))

    def census_from(fraction: float) -> float:
        return (exact_dark + fraction * len(simulated_p)) / DIM**3

    pooled = census_from(two_reference(p_mean, v_plus, v_minus))
    single = []
    for record in result["records"]:
        b, d = sided(record)
        if b and d:
            single.append(census_from(two_reference(p_mean, float(np.mean(b)), float(np.mean(d)))))
    sigma_target = 0.01 / 2
    per_triple = 0.25 / (mean_v**2 * sigma_target**2) if mean_v > 0 else math.inf
    return {
        "ideal_census": str(census),
        "ideal_census_float": round(float(census), 6),
        "noisy_census": round(noisy, 6),
        "common_visibility_prediction": round(predicted, 6),
        "mean_visibility": round(mean_v, 6),
        "visibility_range": [round(min(measured), 6), round(max(measured), 6)],
        "bright_visibility": round(v_plus, 6),
        "dark_visibility": round(v_minus, 6),
        "two_reference_census_pooled": round(pooled, 6),
        "two_reference_census_single_pair_range": [round(min(single), 6), round(max(single), 6)],
        "single_pair_references": len(single),
        "mean_cz": round(float(np.mean([r["cz"] for r in result["records"]])), 2),
        "pairs_simulated": len(by_pair),
        "total_shots_for_0p01_at_2sigma_after_visibility_correction": round(per_triple, 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pairs", default="all")
    parser.add_argument("--shots", type=int, default=SHOTS)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check:
        retained = json.loads(args.check.read_text(encoding="utf-8"))
        require(retained["schema"] == "census-frequency-design-v2", f"{args.check}: unexpected schema")
        require(summarize(retained) == retained["summary"], f"{args.check}: summary differs from its records")
        named = {tuple(r["pair"]): r for r in retained["records"]}
        subset = list(named) if args.pairs == "all" else pairs_of(args.pairs)
        fresh = run(subset, "CPU", retained["shots"])
        for record in fresh["records"]:
            old = named[tuple(record["pair"])]
            require(old["cz"] == record["cz"], f"pair {record['pair']}: CZ count differs")
            for a, b in zip(old["p1"], record["p1"], strict=True):
                bound = 5 * math.sqrt(2 * max(a * (1 - a), 1 / retained["shots"]) / retained["shots"])
                require(abs(a - b) <= bound, f"pair {record['pair']}: P(c=1) {a} against {b}")
        print(f"{args.check}: pairs {subset} reproduced on the CPU")
        return 0
    require(args.out is not None, "--out is required")
    result = run(pairs_of(args.pairs), os.environ.get("GOROROBA_AER_DEVICE", "CPU"), args.shots)
    result["summary"] = summarize(result)
    print(json.dumps(result["summary"]), flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
