"""Ascella control of the BDSC six-state linear-effect test: one qpu:ascella job of 12 iterations.

The 12-mode union circuit of bdsc_certificate carries both preparation
templates, with the photon on connected input 4. Two orthogonal states f and g
spread over all 12 modes, drawn from a fixed generator, give the six
consistency states, and the effect is one click on an odd output. Every
template parameterization must reproduce its column and its own template's
unitary to 1e-12, and the ideal effect must satisfy both sum rules, before the
case directory results/quandela/cases/bdsc_ascella_control/job-00 is written.
qpu:ascella's record declares an empty default mitigation list, so the job
carries the explicit empty list and one processing policy covers it.

Usage:
  "$PYTHON" scripts/bdsc_ascella_control.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_certificate as cert  # noqa: E402

import bdsc  # noqa: E402

MODES = 12
SOURCE = 4
SELECTED = [1, 3, 5, 7, 9, 11]
TRIALS = 300000
SEED = 20261021
OUT = ROOT / "results/quandela/cases/bdsc_ascella_control/job-00"
REFERENCE = ROOT / "results/quandela/cases/bdsc_qualification/tc-none-e1/cases.json"
LABEL_TAGS = {"f": "f", "g": "g", "+": "p", "-": "m", "+i": "pi", "-i": "mi"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def pair() -> tuple[np.ndarray, np.ndarray]:
    """Two orthonormal 12-mode states from the fixed generator: g is Gram-Schmidt against f."""
    rng = np.random.default_rng(SEED)
    f = rng.normal(size=MODES) + 1j * rng.normal(size=MODES)
    f /= np.linalg.norm(f)
    g = rng.normal(size=MODES) + 1j * rng.normal(size=MODES)
    g -= (f.conj() @ g) * f
    return f, g / np.linalg.norm(g)


def documents() -> dict[str, bytes]:
    """{"cases.json": bytes, "circuit.json": bytes} of the control job."""
    # The template functions read the chip width from this module constant.
    cert.MODES = MODES
    f, g = pair()
    effect = np.zeros((MODES, MODES))
    effect[SELECTED, SELECTED] = 1
    states = bdsc.consistency_states(f, g)
    ideal = {label: float(np.real(psi.conj() @ effect @ psi)) for label, psi in states.items()}
    for plus, minus in (("+", "-"), ("+i", "-i")):
        require(abs(ideal[plus] + ideal[minus] - ideal["f"] - ideal["g"]) < 1e-12, f"sum rule {plus}{minus} fails")
    ops = cert.union_ops(SOURCE)
    settings: list[dict[str, Any]] = []
    for template in cert.PREPARATION_DESCRIPTIONS:
        own_ops = cert.template_ops(template, SOURCE)
        for label, psi in states.items():
            params = cert.union_params(template, psi, SOURCE)
            union = cert.template_unitary(ops, params)
            own = cert.template_unitary(own_ops, cert.template_params(template, psi, SOURCE))
            require(np.allclose(union[:, SOURCE], psi, rtol=0, atol=1e-12), f"{template} {label}: column missed")
            require(np.allclose(union, own, rtol=0, atol=1e-12), f"{template} {label}: union differs from template")
            settings.append(
                {
                    "name": f"{template[:3]}-{LABEL_TAGS[label]}",
                    "observation_index": len(settings),
                    "preparation": template,
                    "circuit_params": {f"x{k}": float(v) for k, v in enumerate(params)},
                    "column": [[float(z.real), float(z.imag)] for z in psi],
                    "ideal_selected_E0": ideal[label],
                }
            )
    input_state = [0] * MODES
    input_state[SOURCE] = 1
    circuit = {
        "schema": "qd-template-circuit-v1",
        "template": cert.UNION_CIRCUIT,
        "modes": MODES,
        "input_state": input_state,
        "parameters": len(ops),
        "ops": [list(op) for op in ops],
    }
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    # The reference manifest fixes the shared fields and their order; the control's own values replace them below.
    shared = ("schema", "command", "gate_form", "min_detected_photons", "max_duration", "eligibility")
    manifest = {key: reference[key] for key in shared}
    manifest.update(
        {
            "family": "bdsc_ascella_control",
            "job": "job-00",
            "platforms": ["sim:ascella", "qpu:ascella"],
            "iterations": len(settings),
            "max_samples": TRIALS * len(settings),
            "max_shots": 2 * TRIALS * len(settings),
            "mitigations": [],
            "job_spec": {
                "pair": "ascella-control",
                "circuit": cert.UNION_CIRCUIT,
                "processing": "empty-mitigation",
                "epoch": 1,
                "iterations": list(range(len(settings))),
            },
            "settings": settings,
            "selected_modes": SELECTED,
            "circuit": {"file": "circuit.json", "sha256": hashlib.sha256(circuit_bytes).hexdigest()},
            "draft": False,
            "eligibility": "exactly one click among the 12 outputs; selected when that click is on a selected output",
        }
    )
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in documents().items():
        (OUT / name).write_bytes(content)
    print(f"bdsc ascella control: wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
