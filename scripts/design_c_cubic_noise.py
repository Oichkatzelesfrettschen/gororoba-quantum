"""Noisy Walsh spectra of the dim-32 associator circuits under a retained calibration.

Design C (designs.design_c_associator_spectrum) measures the Walsh
distribution P(y) = |2^-5 sum_x omega(x) (-1)^(x.y)|^2 of W_ij. At dim 32
the 360 degree-3 pairs fall into two spectral classes with collision
probability K = sum_y P(y)^2 equal to 11/32 (234 pairs) or 5/32 (126 pairs)
(DESIGN_NOTES.md). This script asks whether that separation survives the
compiled factorized circuit under the noise live_run would predict, and how
much the two diagonal references (Reed-Muller oracle and CCZ normal form,
scripts/associator_cubic_normal_form.py) retain.

For every selected pair and implementation it compiles the circuit to the
snapshot Target (optimization level 3, seed 11), samples the noisy
distribution with calibration_snapshot.noise_simulator on the device named by
GOROROBA_AER_DEVICE (CPU by default), and records the CZ count, the layout,
the total-variation distance to the ideal distribution, the unbiased
collision estimate sum_y n_y (n_y - 1) / (S (S - 1)) and the ideal K.

``--pairs all`` runs the 360 pairs; ``--pairs I,J;I,J`` names a subset.
``--check FILE`` reruns the ``--pairs`` subset of FILE (every pair with
``--pairs all``) on the CPU, so the replay gate re-derives two class
representatives of a 360-pair Kaggle result, and requires each TV distance and collision estimate to
agree within five standard errors of a difference of two independent
estimates at FILE's shot count: sqrt(2/S) for TV and 2 sqrt(2K/S) for the
collision estimate, so a CPU replay re-derives a GPU result.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import numpy as np  # noqa: E402
import qiskit  # noqa: E402
import qiskit_aer  # noqa: E402
from associator_cubic_normal_form import (  # noqa: E402
    cubic_part,
    factorized_blocks,
    normal_form_circuit,
    rank_one_forms,
)
from qiskit import QuantumCircuit, transpile  # noqa: E402

import calibration_snapshot  # noqa: E402
from predict import associator_phase  # noqa: E402
from select_lcu import phase_oracle_from_truth_table  # noqa: E402

SNAPSHOT = ROOT / "docs/evidence/calibration/ibm_kingston.json"
N = 5
DIM = 32
SEED = 11
SHOTS = 20000
IMPLEMENTATIONS = ("factorized", "reed_muller", "normal_form")
TOLERANCE_SIGMAS = 5.0
# Ideal collision probability of the two spectral classes and their pair counts.
CLASS_SIZES = Counter({0.34375: 234, 0.15625: 126})


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def ideal_distribution(phase: list[int]) -> np.ndarray:
    signs = np.array(phase, dtype=float)
    walsh = np.array([sum(signs[x] * (-1) ** bin(x & y).count("1") for x in range(DIM)) for y in range(DIM)])
    return (walsh / DIM) ** 2


def spectrum_circuit(core: QuantumCircuit) -> QuantumCircuit:
    circuit = QuantumCircuit(N, N)
    circuit.h(range(N))
    circuit.compose(core, range(N), inplace=True)
    circuit.h(range(N))
    circuit.measure(range(N), range(N))
    return circuit


def cores(i: int, j: int, forms_by_part: dict[Any, tuple[int, int, int]]) -> dict[str, QuantumCircuit]:
    truth_table = [1 if s == -1 else 0 for s in associator_phase(DIM, i, j)]
    return {
        "factorized": factorized_blocks(i, j),
        "reed_muller": phase_oracle_from_truth_table(truth_table),
        "normal_form": normal_form_circuit(truth_table, forms_by_part[cubic_part(truth_table)]),
    }


def summarize(counts: dict[str, int], ideal: np.ndarray, shots: int) -> dict[str, float]:
    n = np.zeros(DIM)
    for key, value in counts.items():
        n[int(key, 2)] += value
    p = n / shots
    return {
        "tv": round(float(0.5 * np.abs(p - ideal).sum()), 6),
        "collision": round(float((n * (n - 1)).sum() / (shots * (shots - 1))), 6),
    }


def run(pairs: list[tuple[int, int]], device: str, shots: int) -> dict[str, Any]:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    simulator = calibration_snapshot.noise_simulator(snapshot, device=device)
    target = calibration_snapshot.build_target(snapshot)
    forms_by_part = rank_one_forms()
    records = []
    for i, j in pairs:
        ideal = ideal_distribution(associator_phase(DIM, i, j))
        entry: dict[str, Any] = {"pair": [i, j], "ideal_collision": round(float((ideal**2).sum()), 6)}
        for name, core in cores(i, j, forms_by_part).items():
            compiled = transpile(spectrum_circuit(core), target=target, optimization_level=3, seed_transpiler=SEED)
            layout = compiled.layout.final_index_layout() if compiled.layout else list(range(N))
            counts = simulator.run(compiled, shots=shots, seed_simulator=SEED + i * DIM + j).result().get_counts()
            entry[name] = {
                "cz": int(compiled.count_ops().get("cz", 0)),
                "final_layout": layout,
                **summarize(counts, ideal, shots),
            }
        records.append(entry)
        print(json.dumps(entry), flush=True)
    return {
        "schema": "design-c-cubic-noise-v1",
        "snapshot": {"path": SNAPSHOT.relative_to(ROOT).as_posix(), "calibration": snapshot["calibration"]},
        "device": device,
        "shots": shots,
        "seed_transpiler": SEED,
        "versions": {"qiskit": qiskit.__version__, "qiskit_aer": qiskit_aer.__version__, "numpy": np.__version__},
        "records": records,
    }


def parse_pairs(text: str) -> list[tuple[int, int]]:
    if text == "all":
        return [(i, j) for i in range(1, DIM) for j in range(i + 1, DIM) if j.bit_length() == N]
    pairs = []
    for item in text.split(";"):
        i, j = (int(v) for v in item.split(","))
        pairs.append((i, j))
    return pairs


def check(path: Path, subset: list[tuple[int, int]]) -> int:
    retained = json.loads(path.read_text(encoding="utf-8"))
    shots = retained["shots"]
    pairs_listed = [tuple(r["pair"]) for r in retained["records"]]
    by_pair = dict(zip(pairs_listed, retained["records"], strict=True))
    if len(pairs_listed) > len(subset):
        # A full census backs the claim's extrema and class counts, so it
        # must hold every pair once with the predicted class sizes.
        require(sorted(pairs_listed) == parse_pairs("all"), f"{path} does not hold each dim-32 pair exactly once")
        classes = Counter(r["ideal_collision"] for r in retained["records"])
        require(classes == CLASS_SIZES, f"{path} class sizes {dict(classes)} differ from {CLASS_SIZES}")
    require(all(pair in by_pair for pair in subset), f"{path} lacks one of the pairs {subset}")
    pairs = subset or list(by_pair)
    fresh = run(pairs, "CPU", shots)
    for old, new in zip((by_pair[p] for p in pairs), fresh["records"], strict=True):
        for name in IMPLEMENTATIONS:
            for metric in ("tv", "collision"):
                a, b = old[name][metric], new[name][metric]
                sigma = math.sqrt(2.0 / shots) if metric == "tv" else 2.0 * math.sqrt(2.0 * max(a, 1.0 / DIM) / shots)
                require(
                    abs(a - b) <= TOLERANCE_SIGMAS * sigma,
                    f"pair {old['pair']} {name} {metric}: retained {a} against CPU {b}",
                )
            require(old[name]["cz"] == new[name]["cz"], f"pair {old['pair']} {name} CZ count differs")
            require(
                old[name]["final_layout"] == new[name]["final_layout"],
                f"pair {old['pair']} {name} routes onto different physical qubits",
            )
    print(f"{path}: {len(pairs)} pairs reproduced on the CPU within {TOLERANCE_SIGMAS} sigma")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pairs", default="1,16;9,18")
    parser.add_argument("--shots", type=int, default=SHOTS)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check:
        return check(args.check, parse_pairs(args.pairs) if args.pairs != "all" else [])
    require(args.out is not None, "--out is required")
    result = run(parse_pairs(args.pairs), os.environ.get("GOROROBA_AER_DEVICE", "CPU"), args.shots)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
