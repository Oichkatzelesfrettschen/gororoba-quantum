"""Offline probes of the Qiskit-adjacent packages documented beside this file.

Each probe imports a package on the system interpreter and, where the package
computes locally, checks one exact result. No probe constructs a service,
reads a credential or contacts a network endpoint. qiskit-connector is read
from its metadata only, because importing it loads ``.env`` files into the
process environment. The isolated stacks are checked by their own package
``check()`` functions and by the launcher calls in ``--stacks``.

Usage: "$PYTHON" probe_packages.py [--stacks]
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from collections.abc import Callable
from importlib.metadata import version

DISTRIBUTIONS = {
    "qiskit": "qiskit",
    "qiskit-aer": "qiskit_aer",
    "qiskit-ibm-runtime": "qiskit_ibm_runtime",
    "ibm-quantum-schemas": "ibm_quantum_schemas",
    "qiskit-noise-learning": "qiskit_noise_learning",
    "pauli-prop": "pauli_prop",
    "qiskit-addon-slc": "qiskit_addon_slc",
    "qiskit-serverless": "qiskit_serverless",
    "qiskit-ibm-catalog": "qiskit_ibm_catalog",
    "perceval-quandela": "perceval",
    "perceval-interop": "perceval_interop",
    "qiskit-resume": "qiskit_resume",
    "qiskit-waveform-sim": "qiskit_waveform_sim",
    "qcog": "qcog",
    "qubasic": "qubasic_core",
    "eigenkit": "eigenkit",
    "quantum-al": "quantum_al",
}
METADATA_ONLY = ("qiskit-connector",)
STACK_LAUNCHERS = {
    "qi-stack-python": ["qiskit", "qiskit-quantuminspire", "pennylane-quantuminspire", "quantuminspire"],
    "qiskit-debugger-python": ["qiskit", "qiskit-terra", "qiskit-aer", "qiskit-debugger"],
    "quantum-pipeline-python": ["qiskit", "qiskit-aer", "qiskit-ibm-runtime", "quantum-pipeline"],
}


def probe_pauli_prop() -> str:
    from pauli_prop import propagate_through_circuit
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import SparsePauliOp

    circuit = QuantumCircuit(1)
    circuit.h(0)
    operator, discarded = propagate_through_circuit(SparsePauliOp("Z"), circuit, max_terms=8, atol=1e-12, frame="h")
    if operator != SparsePauliOp("X") or discarded != 0.0:
        raise RuntimeError(f"H^dagger Z H gave {operator} with discarded weight {discarded}")
    return "H^dagger Z H = X, discarded weight 0.0"


def probe_waveform_sim() -> str:
    from qiskit import QuantumCircuit
    from qiskit.transpiler import generate_preset_pass_manager
    from qiskit_ibm_runtime.fake_provider import FakeFez
    from qiskit_waveform_sim import TargetWaveformSimulator

    target = FakeFez().target
    circuit = QuantumCircuit(1)
    circuit.x(0)
    manager = generate_preset_pass_manager(
        optimization_level=0, target=target, initial_layout=[0], scheduling_method="alap"
    )
    snippet = TargetWaveformSimulator(target).compile(manager.run(circuit)).get_snippet("d0")
    duration = target["x"][(0,)].duration
    if target.dt is None or duration is None:
        raise RuntimeError("FakeFez target lacks dt or the X duration")
    samples = round(duration / target.dt)
    if len(snippet.wave) != samples:
        raise RuntimeError(f"X waveform has {len(snippet.wave)} samples, Target duration is {samples} dt")
    event = snippet.events[0]
    return f"X on q0: {samples} samples at dt {target.dt:g} s; placeholder {event.shape} amp {event.amp.real:g}"


def probe_perceval_interop() -> str:
    from perceval_interop import QiskitConverter
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    processor = QiskitConverter().convert(circuit)
    return f"H-CX circuit -> {processor.m}-mode processor"


def probe_aer_devices() -> str:
    from qiskit_aer import AerSimulator

    return f"devices {AerSimulator().available_devices()}"


FUNCTIONAL: dict[str, Callable[[], str]] = {
    "pauli-prop": probe_pauli_prop,
    "qiskit-waveform-sim": probe_waveform_sim,
    "perceval-interop": probe_perceval_interop,
    "qiskit-aer": probe_aer_devices,
}


def run_stacks() -> dict[str, dict[str, str]]:
    script = (
        "import json, sys\n"
        "from importlib.metadata import version\n"
        "print(json.dumps({d: version(d) for d in sys.argv[1:]}))"
    )
    out: dict[str, dict[str, str]] = {}
    for launcher, dists in STACK_LAUNCHERS.items():
        done = subprocess.run([launcher, "-I", "-c", script, *dists], capture_output=True, text=True, check=True)
        out[launcher] = json.loads(done.stdout)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stacks", action="store_true", help="also read versions through the /opt stack launchers")
    args = parser.parse_args()
    failures = 0
    report: dict[str, object] = {"python": sys.version.split()[0]}
    for dist, module in DISTRIBUTIONS.items():
        entry: dict[str, str] = {"version": version(dist)}
        try:
            importlib.import_module(module)
            if dist in FUNCTIONAL:
                entry["probe"] = FUNCTIONAL[dist]()
        except Exception as exc:  # noqa: BLE001 - every failure is reported and counted
            entry["error"] = f"{type(exc).__name__}: {exc}"
            failures += 1
        report[dist] = entry
    for dist in METADATA_ONLY:
        report[dist] = {"version": version(dist), "probe": "metadata only; import loads .env files"}
    if args.stacks:
        report["stacks"] = run_stacks()
    print(json.dumps(report, indent=1))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
