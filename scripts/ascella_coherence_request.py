"""Ascella signed-coherence order request: one qpu:ascella job of 64 template iterations on twelve modes.

docs/design/ascella-signed-coherence-conformance.md fixes the request. For each
theta_k = k pi/5, k = 0..4, a direct, an X and a Y readout block run in that
order, each with arms phi = +pi/4, -pi/4, -pi/4, +pi/4; a direct-readout
mutation block at theta = pi/5, phi = pi/4 follows with generator pairs
(I,J), (I,I), (I,I), (I,J). Every iteration programs the logical operator
H S diag(AB, BA) S on modes 0..3 of a twelve-mode circuit, with H the identity
for direct readout and H_X or H_Y on the ordered pair (0, 3), and the identity
on modes 4..11. The twelve-entry input occupation puts the photon on connected
input 0, so the service's final_mode_number default, the input-state width,
returns all twelve modes and eligible events outside the logical block stay in
the denominator.

The builder decomposes each logical operator into the fixed four-mode
Rx/phase template of hypercomplex_cases.photonic_template. The check rebuilds
the case in memory, compares it with the retained files, validates the
retained bytes, binds every iteration through qd_platform.template_experiment
(Perceval's unitary against the manifest operator), and compares each manifest
operator with the
closed form Q+ = a + bI + cJ, Q- = dK (Q+ = cos(theta+phi) + sin(theta+phi) I,
Q- = 0 for the commuting mutation) and the readout law that form implies. The
check also requires the rejection of a perturbed unitary, an exchanged
analyzer and a four-mode output width.

Usage:
  "$PYTHON" scripts/ascella_coherence_request.py [--check]
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from bdsc_certificate import close  # noqa: E402
from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_platform import PlatformError, iteration_form, template_experiment  # noqa: E402

from hypercomplex_operators import ComplexMatrix, order_interferometer, quaternion_matrix  # noqa: E402

MODES = 12
LOGICAL = 4
SOURCE = 0
ANGLES = 5
READOUTS = ("direct", "x", "y")
ARM_SIGNS = (1, -1, -1, 1)
PHI = math.pi / 4
MUTATION_THETA = math.pi / 5
MUTATION_GENERATORS = ("j", "i", "i", "j")
SAMPLES = 8192
SHOTS = 16384
MAX_DURATION = 300
TOLERANCE = 1e-12
OUT = ROOT / "results/quandela/cases/ascella_signed_coherence/job-00"
DESIGN = "docs/design/ascella-signed-coherence-conformance.md"

UNIT_I = quaternion_matrix([0, 1, 0, 0])
UNIT_J = quaternion_matrix([0, 0, 1, 0])
UNIT_K = quaternion_matrix([0, 0, 0, 1])
ANALYZERS = {
    "direct": np.eye(2, dtype=complex),
    "x": np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2),
    "y": np.array([[1, -1j], [1, 1j]], dtype=complex) / math.sqrt(2),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def order_operator(theta: float, phi: float, generator: str) -> ComplexMatrix:
    """S diag(AB, BA) S with A = cos(theta) + sin(theta) I and B = cos(phi) + sin(phi) G, G = J or I."""
    second_unit = {"j": UNIT_J, "i": UNIT_I}[generator]
    first = math.cos(theta) * np.eye(2) + math.sin(theta) * UNIT_I
    second = math.cos(phi) * np.eye(2) + math.sin(phi) * second_unit
    paths = np.zeros((LOGICAL, LOGICAL), dtype=complex)
    paths[:2, :2], paths[2:, 2:] = first @ second, second @ first
    splitter = np.kron(np.array([[1, 1], [1, -1]]) / math.sqrt(2), np.eye(2))
    matrix = np.asarray(splitter @ paths @ splitter, dtype=np.complex128)
    if generator == "j":
        deviation = float(np.max(np.abs(matrix - order_interferometer(theta, phi))))
        require(deviation <= TOLERANCE, f"the J order operator departs from order_interferometer by {deviation:.2e}")
    return matrix


def analyzer(readout: str) -> ComplexMatrix:
    """The four-mode readout: identity, or H_X or H_Y on the ordered mode pair (0, 3)."""
    matrix = np.eye(LOGICAL, dtype=complex)
    matrix[np.ix_([0, 3], [0, 3])] = ANALYZERS[readout]
    return matrix


def embed(matrix: ComplexMatrix) -> ComplexMatrix:
    """diag(matrix, identity) on the twelve device modes."""
    full = np.eye(MODES, dtype=complex)
    full[:LOGICAL, :LOGICAL] = matrix
    return full


def entries() -> list[dict[str, Any]]:
    """The 64 iterations in submission order, each with its block, readout, arm and angles."""
    rows: list[dict[str, Any]] = []
    for k in range(ANGLES):
        for readout in READOUTS:
            for arm, sign in enumerate(ARM_SIGNS):
                rows.append(
                    {
                        "block": f"theta{k}-{readout}",
                        "readout": readout,
                        "arm": arm,
                        "theta_index": k,
                        "theta": k * math.pi / ANGLES,
                        "phi_sign": sign,
                        "phi": sign * PHI,
                        "generator": "j",
                    }
                )
    for arm, generator in enumerate(MUTATION_GENERATORS):
        rows.append(
            {
                "block": "mutation",
                "readout": "direct",
                "arm": arm,
                "theta_index": 1,
                "theta": MUTATION_THETA,
                "phi_sign": 1,
                "phi": PHI,
                "generator": generator,
            }
        )
    return rows


def closed_form(theta: float, phi: float, generator: str) -> ComplexMatrix:
    """[[Q+, Q-], [Q-, Q+]] from the quaternion coefficients of {A,B}/2 and [A,B]/2."""
    identity = np.eye(2, dtype=complex)
    if generator == "j":
        a, b = math.cos(theta) * math.cos(phi), math.sin(theta) * math.cos(phi)
        c, d = math.cos(theta) * math.sin(phi), math.sin(theta) * math.sin(phi)
        symmetric, antisymmetric = a * identity + b * UNIT_I + c * UNIT_J, d * UNIT_K
    else:
        symmetric = math.cos(theta + phi) * identity + math.sin(theta + phi) * UNIT_I
        antisymmetric = np.zeros((2, 2), dtype=complex)
    return np.asarray(np.block([[symmetric, antisymmetric], [antisymmetric, symmetric]]), dtype=np.complex128)


def ideal(row: dict[str, Any]) -> dict[str, float]:
    """The setting's registered ideal: the dark probability D = d^2, or z = p0 - p3 equal to X or Y.

    Adding 0.0 turns the negative zero of a phi = -pi/4 arm at theta = 0 into 0.0 before serialization."""
    theta, phi = row["theta"], row["phi"]
    if row["readout"] == "direct":
        dark = 0.0 if row["generator"] == "i" else (math.sin(theta) * math.sin(phi)) ** 2
        return {"dark": dark + 0.0}
    if row["readout"] == "x":
        return {"z": math.sin(theta) ** 2 * math.sin(2 * phi) + 0.0}
    return {"z": 0.5 * math.sin(2 * theta) * math.sin(2 * phi) + 0.0}


def documents() -> dict[str, bytes]:
    """{"cases.json": bytes, "circuit.json": bytes} of the request."""
    rows = entries()
    template: dict[str, Any] | None = None
    settings: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        logical = analyzer(row["readout"]) @ order_operator(row["theta"], row["phi"], row["generator"])
        mesh, parameters = photonic_template(logical)
        require(template is None or mesh == template, f"iteration {index} needs another mesh than iteration 0")
        template = mesh
        full = embed(logical)
        name = f"{row['block']}-arm{row['arm']}" + ("-ii" if row["generator"] == "i" else "")
        settings.append(
            {
                "name": name,
                "observation_index": index,
                **row,
                "ideal": ideal(row),
                "circuit_params": parameters,
                "column": [[float(value.real), float(value.imag)] for value in full[:, SOURCE]],
                "operator": encoded(full),
                "compilation_seed": 0,
            }
        )
    if template is None or len(settings) != 64:
        raise ValueError(f"the request holds {len(settings)} iterations, not 64")
    input_state = [0] * MODES
    input_state[SOURCE] = 1
    circuit = {**template, "modes": MODES, "input_state": input_state}
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": "ascella_signed_coherence",
        "job": "job-00",
        "platforms": ["qpu:ascella", "sim:ascella"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
        "max_samples": SAMPLES * len(settings),
        "max_shots": SHOTS * len(settings),
        "max_duration": MAX_DURATION,
        "mitigations": [],
        "output_modes": MODES,
        "logical_modes": list(range(LOGICAL)),
        "eligibility": "occupation sum one across all twelve returned modes",
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": hashlib.sha256(circuit_bytes).hexdigest()},
        "preregistered": {
            "primary_endpoints": 27,
            "family_alpha": 0.01,
            "coefficient_tolerance": 0.05,
            "mutation_difference_tolerance": 0.05,
            "mutation_dark_tolerance": 0.05,
            "interpretation": "complex-encoding conformance of the compiled circuit family",
        },
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def operator_of(setting: dict[str, Any]) -> ComplexMatrix:
    entry = setting["operator"]
    return np.asarray(entry["real"], dtype=float) + 1j * np.asarray(entry["imaginary"], dtype=float)


def validate(manifest: dict[str, Any], circuit: dict[str, Any]) -> None:
    """Require the design's request: fields, entry order, full unitaries, analyzers and twelve-mode output."""
    owner = f"{manifest.get('family')}/{manifest.get('job')}"
    for key, value in (
        ("command", "sample_count"),
        ("gate_form", "template"),
        ("iterations", 64),
        ("min_detected_photons", 1),
        ("max_samples", SAMPLES * 64),
        ("max_shots", SHOTS * 64),
        ("max_duration", MAX_DURATION),
        ("mitigations", []),
        ("output_modes", MODES),
    ):
        require(manifest.get(key) == value, f"{owner}: {key} is {manifest.get(key)!r}, not {value!r}")
    input_state = circuit.get("input_state")
    expected_input = [1 if mode == SOURCE else 0 for mode in range(MODES)]
    require(circuit.get("modes") == MODES, f"{owner}: the circuit spans {circuit.get('modes')} modes, not {MODES}")
    # final_mode_number defaults to the input-state width, so this width is the returned output width.
    require(input_state == expected_input, f"{owner}: input occupation {input_state} is not the twelve-mode source 0")
    require(
        all(LOGICAL > op[1] + (op[0] == "BS") for op in circuit["ops"]), f"{owner}: a template op leaves modes 0..3"
    )
    require(iteration_form(manifest) == "template", f"{owner}: the iterations do not form a template job")
    rows = entries()
    settings = manifest["settings"]
    require(len(settings) == len(rows), f"{owner}: {len(settings)} settings, not {len(rows)}")
    template_experiment(manifest, circuit)
    for index, (setting, row) in enumerate(zip(settings, rows, strict=True)):
        label = f"{owner}/{setting.get('name')}"
        for key, value in row.items():
            require(setting.get(key) == value, f"{label}: {key} is {setting.get(key)!r}, not {value!r} at {index}")
        require(setting.get("compilation_seed") == 0, f"{label}: compilation_seed is not 0")
        require(setting.get("observation_index") == index, f"{label}: observation_index is not {index}")
        full = operator_of(setting)
        require(full.shape == (MODES, MODES), f"{label}: the operator is {full.shape}, not twelve-mode")
        expected = embed(analyzer(row["readout"]) @ closed_form(row["theta"], row["phi"], row["generator"]))
        deviation = float(np.max(np.abs(full - expected)))
        require(deviation <= TOLERANCE, f"{label}: the operator departs from the closed form by {deviation:.2e}")
        probabilities = np.abs(full[:, SOURCE]) ** 2
        require(float(probabilities[LOGICAL:].sum()) <= TOLERANCE, f"{label}: the source leaves the logical block")
        registered = setting.get("ideal")
        observed = (
            {"dark": float(probabilities[2] + probabilities[3])}
            if row["readout"] == "direct"
            else {"z": float(probabilities[0] - probabilities[3])}
        )
        require(
            isinstance(registered, dict)
            and registered.keys() == observed.keys()
            and all(abs(registered[key] - observed[key]) <= TOLERANCE for key in observed),
            f"{label}: ideal {registered} differs from the operator's readout {observed}",
        )
        require(ideal(row) == registered, f"{label}: ideal {registered} differs from the closed-form readout")


def rejections(manifest: dict[str, Any], circuit: dict[str, Any]) -> list[str]:
    """Mutated requests that validate must refuse: a perturbed unitary, an exchanged analyzer, four output modes."""
    perturbed = copy.deepcopy(manifest)
    parameter = sorted(perturbed["settings"][20]["circuit_params"])[0]
    perturbed["settings"][20]["circuit_params"][parameter] += 1e-3
    exchanged = copy.deepcopy(manifest)
    x_setting, y_setting = exchanged["settings"][16], exchanged["settings"][20]
    for key in ("circuit_params", "column", "operator", "ideal"):
        x_setting[key], y_setting[key] = y_setting[key], x_setting[key]
    narrow = {**circuit, "input_state": circuit["input_state"][:LOGICAL]}
    refused = []
    for label, candidate, mesh in (
        ("perturbed unitary", perturbed, circuit),
        ("exchanged X and Y analyzers", exchanged, circuit),
        ("four-mode output width", manifest, narrow),
    ):
        try:
            validate(candidate, mesh)
        except (ValueError, PlatformError):
            refused.append(label)
            continue
        raise ValueError(f"validate accepts the {label}")
    return refused


def check() -> int:
    """Rebuild in memory, require the retained bytes, validate them and require each mutation's refusal."""
    built = documents()
    require(documents() == built, "a second build differs from the first")
    retained = {name: (OUT / name).read_bytes() for name in built}
    # The template angles come from complex matrix products whose last bit can move between BLAS kernels, so the
    # retained manifest, which holds the request bytes, is compared within cert.CHECK_TOLERANCE; the circuit carries
    # no float and stays exact.
    close(json.loads(built["cases.json"]), json.loads(retained["cases.json"]), f"{OUT.relative_to(ROOT)}/cases.json")
    require(retained["circuit.json"] == built["circuit.json"], f"{OUT.relative_to(ROOT)}/circuit.json differs")
    manifest, circuit = json.loads(retained["cases.json"]), json.loads(retained["circuit.json"])
    validate(manifest, circuit)
    refused = rejections(manifest, circuit)
    digest = hashlib.sha256(retained["cases.json"]).hexdigest()
    print(f"ascella signed coherence: 64 iterations validated, cases.json {digest}; refused {', '.join(refused)}")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--check"]:
        return check()
    require(not argv, f"usage: ascella_coherence_request.py [--check], not {argv}")
    built = documents()
    validate(json.loads(built["cases.json"]), json.loads(built["circuit.json"]))
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in built.items():
        path = OUT / name
        # The case directory holds the request bytes, which no rebuild rewrites.
        require(not path.exists() or path.read_bytes() == content, f"{path.relative_to(ROOT)} differs from the rebuild")
        if not path.exists():
            path.write_bytes(content)
    digest = hashlib.sha256(built["cases.json"]).hexdigest()
    print(f"ascella signed coherence: {OUT.relative_to(ROOT)} cases.json {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
