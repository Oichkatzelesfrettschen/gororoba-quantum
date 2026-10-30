"""Build a single-photon optical probe of a two-dimensional A5 kernel slice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sym

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
import anu_qrng  # noqa: E402
from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402

import cd_core  # noqa: E402
from parallel import ordered_map  # noqa: E402

OUTPUT_BASIS = (5, 6, 13, 14)
INPUT_BASIS = (4, 15)
SETTINGS = (
    ("control-dark", 9, 1, -1),
    ("kernel-dark", 10, 1, -1),
    ("mutation-dark", 10, -1, -1),
    ("mutation-bright", 10, -1, 1),
    ("kernel-bright", 10, 1, 1),
    ("control-bright", 9, 1, 1),
)
EXPECTED = (sym.Rational(1, 2), sym.Integer(0), sym.Integer(1), sym.Integer(0), sym.Integer(1), sym.Rational(1, 2))
SAMPLES = 10000
SHOTS = 100000


def exact_operator(second: int, coefficient: int, preparation: int) -> sym.Matrix:
    """Embed the two selected columns of the LCU isometry in eight optical modes."""
    isometry = sym.zeros(8, 2)
    for column, basis in enumerate(INPUT_BASIS):
        for left, weight in ((1, 1), (second, coefficient)):
            output = left ^ basis
            row = OUTPUT_BASIS.index(output)
            sign = cd_core.cd_sign(32, left, basis)
            isometry[row, column] += sym.Rational(weight * sign, 2)
            isometry[row + 4, column] += sym.Rational(sign * (1 if left == 1 else -weight), 2)
    if isometry.T * isometry != sym.eye(2):
        raise ValueError("the selected LCU columns are not an isometry")
    columns = [isometry[:, 0], isometry[:, 1]]
    for index in range(8):
        vector = sym.eye(8)[:, index]
        for previous in columns:
            vector -= previous * (previous.T * vector)[0]
        norm = sym.simplify((vector.T * vector)[0])
        if norm != 0:
            columns.append(vector / sym.sqrt(norm))
        if len(columns) == 8:
            break
    operator = sym.Matrix.hstack(*columns)
    prepare = sym.eye(8)
    prepare[0, 0] = prepare[0, 1] = 1 / sym.sqrt(2)
    prepare[1, 0] = preparation / sym.sqrt(2)
    prepare[1, 1] = -preparation / sym.sqrt(2)
    result = sym.simplify(operator * prepare)
    if sym.simplify(result.T * result) != sym.eye(8):
        raise ValueError("the completed optical operator is not unitary")
    return result


def build_setting(task: tuple[int, tuple, int]) -> dict[str, Any]:
    index, specification, seed = task
    name, second, coefficient, preparation = specification
    exact = exact_operator(second, coefficient, preparation)
    probability = sym.simplify(sum(exact[row, 0] ** 2 for row in range(4)))
    if probability != EXPECTED[index]:
        raise ValueError(f"{name}: the exact branch probability differs")
    matrix = np.asarray(exact, dtype=np.complex128)
    _, parameters = photonic_template(matrix)
    full = np.eye(12, dtype=np.complex128)
    full[:8, :8] = matrix
    return {
        "name": name,
        "observation_index": index,
        "compilation_seed": seed,
        "circuit_params": parameters,
        "column": [[float(v.real), float(v.imag)] for v in full[:, 0]],
        "operator": encoded(full),
        "ideal_success": str(probability),
    }


def documents(draw: Path, job: str, platform: str) -> dict[str, bytes]:
    source = json.loads(draw.read_bytes())
    anu_qrng.admit(source)
    seeds = source["values"]
    if (
        source["type"] != "uint16"
        or len(seeds) != len(SETTINGS)
        or any(type(seed) is not int or not 0 <= seed <= 65535 for seed in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise ValueError("the case needs six distinct uint16 QRNG values")
    settings = ordered_map(build_setting, [(i, item, seeds[i]) for i, item in enumerate(SETTINGS)], min_items=1)
    mesh, _ = photonic_template(np.eye(8, dtype=np.complex128))
    circuit = {**mesh, "modes": 12, "input_state": [1] + [0] * 11}
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": "ascella_a5_kernel_slice",
        "job": job,
        "platforms": [platform],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
        "max_samples": SAMPLES * len(settings),
        "max_shots": SHOTS * len(settings),
        "max_duration": 300,
        "max_credits": 1.1,
        "mitigations": [],
        "output_modes": 12,
        "logical_modes": list(range(8)),
        "eligibility": "single detected photon; success modes 0..3 and failure modes 4..7",
        "seed_source": {
            "script": "scripts/ascella_a5_kernel_slice.py",
            "flag": "--draw",
            "experiment": "ascella-a5-kernel-slice",
            "sources": [f"qrng:{draw.relative_to(ROOT).as_posix()}#{index}" for index in range(len(settings))],
            "usage": "same case settings across simulator and hardware as a matched compilation identifier",
        },
        "analysis_sources": {
            name: sha256_bytes((ROOT / name).read_bytes())
            for name in (
                "scripts/ascella_a5_kernel_slice.py",
                "scripts/hypercomplex_cases.py",
                "scripts/qd_platform.py",
                "gororoba_quantum/cd_core.py",
            )
        },
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "question": "Does the device reproduce the two-dimensional A5 kernel slice and its sign mutation?",
            "inference": "descriptive; report all detected modes and event denominators",
            "success_modes": [0, 1, 2, 3],
            "failure_modes": [4, 5, 6, 7],
            "sentinel_modes": [8, 9, 10, 11],
            "boundary": (
                "Two selected input vectors only; full A5 nullity and physical nonassociativity are not measured."
            ),
        },
    }
    template_experiment(manifest, circuit)
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draw", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--platform", choices=("sim:ascella", "qpu:ascella"), required=True)
    args = parser.parse_args()
    draw = args.draw.resolve()
    payload = documents(draw, "simulator" if args.platform.startswith("sim:") else "hardware", args.platform)
    args.out.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        (args.out / name).write_bytes(data)
    print(
        f"{args.out}: six settings, ideal success 1/2,0,1,0,1,1/2; request sha256 {sha256_bytes(payload['cases.json'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
