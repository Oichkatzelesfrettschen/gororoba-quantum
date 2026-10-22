"""Explain declared, imported and explicitly considered Python distributions.

Inventory construction reads project manifests, maintained manuals, import roots
and the retained IQM stack. Installed metadata describes a host observation;
declared environment pins remain separate and never trigger an installation.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata as metadata
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROLES = {
    "hypercomplex": "Independent recursive CD products; Fraction-based exact witnesses.",
    "hypercomplex-engine": "Fast basis signs and higher-dimensional finite checks.",
    "hypercomplex-algebra": "Expression and tensor notation; shares the hypercomplex-engine implementation.",
    "cayley-calculator": "Independent multiplication reference; qualify each special function before use.",
    "cayley-dickson": "Independent recursive doubling reference; local reading and checks under its license boundary.",
    "octonion": "PyTorch octonion/Fano batches after the certified signed relabeling.",
    "splitoct": "Split-signature negative control; associator agreement does not establish algebra identity.",
    "mathdunders": "Numeric-method plumbing; supplies no independent multiplication evidence.",
    "numpy-quaternion": "Vectorized quaternion fields and products.",
    "quaternionic": "Numba quaternion arrays and independent numerical comparisons.",
    "pyquaternion": "Scalar quaternion and rotation bookkeeping.",
    "clifford": "Associative Clifford envelopes and rotor/spinor controls, not octonion multiplication.",
    "kingdon": "Generated symbolic or batched Clifford operators.",
    "galgebra": "Symbolic geometric calculus in an associative Clifford algebra.",
    "pyoctonion": "Small octonion cross-check; depends on pyquaternion.",
    "octonion-sedenion": "Independent product witness over numpy-quaternion; exclude documented mutating functions.",
    "sagemath": "Exact derivations, Clifford and Albert references through certified convention maps.",
    "hyprat": "Exact rational CD coefficients, generalized signs, annihilators and regular representations.",
    "python-flint": "Exact rational/modular matrix rank and kernel certificates; defines no CD table.",
    "pyadic": "Finite-field and finite-precision p-adic coefficients; a separate arithmetic experiment.",
    "numpy": "Arrays, paired-channel probabilities and FFT reference arithmetic.",
    "scipy": "Matrix exponentiation, linear algebra, integration and uncertainty estimates.",
    "sympy": "Exact operator identities and symbolic certificates.",
    "qiskit": "Circuits, native synthesis, topology placement and operator verification.",
    "qiskit-aer": "Ideal/noise circuit simulation; provider/routing approval rules apply to submitted jobs.",
    "qiskit-ibm-runtime": "IBM execution and result collection through the approved-record runner.",
    "perceval-quandela": "Photonic meshes, local SLOS/Naive checks and approved Quandela execution.",
    "exqalibur": "Compiled photonic simulator and mesh backend; preserve binary distribution constraints.",
    "quantuminspire": "Account and case lifecycle through the existing guarded Quantum Inspire runner.",
    "qi-compute-api-client": "Typed Quantum Inspire compute API transport beneath the guarded runner.",
    "qiskit-quantuminspire": "Circuit conversion in the isolated Quantum Inspire environment.",
    "libqasm": "cQASM parsing and validation before upload.",
    "opensquirrel": "Native decomposition and coupling checks; record scheduling limitations.",
    "qxelarator": "Local QX execution; measurement-register semantics differ from Tuna classical bits.",
    "stim": "Stabilizer controls and Clifford subcircuits; not general quaternion wave evolution.",
    "mthree": "Readout sensitivity analysis with explicit calibration and factorization assumptions.",
    "runningman": "Execution support used by measurement mitigation; provider submission stays guarded.",
    "qiskit-experiments": "Device-characterization circuits and analyses; calibration jobs require approval.",
    "lmfit": "Identifiable device/noise parameter fitting with retained residuals.",
    "quimb": "Tensor-network classical references and marginal/expectation calculations.",
    "cotengra": "Contraction planning for tensor-network references.",
    "autoray": "Array dispatch for qualified tensor-network backends.",
    "pyzx": "ZX circuit simplification followed by exact operator-equivalence checks.",
    "galois": "Finite-field Fano incidence and binary algebra certificates.",
    "rustworkx": "Coupling graphs, placement and disjoint-support candidates.",
    "networkx": "Graph inspection and independent topology controls.",
    "samplomatic": "Runtime circuit preparation; dynamic-circuit restrictions remain binding.",
    "qiskit-mitigation": "Hardware mitigation tasks; invocation can submit and needs the written case.",
    "ibm-quantum-schemas": "Runtime task and option schema conformance.",
    "qiskit-qasm3-import": "Validated OpenQASM interchange between isolated SDK environments.",
    "openqasm3": "OpenQASM syntax and AST support.",
    "antlr4-python3-runtime": "Parser runtime for OpenQASM import.",
    "qiskit-addon-utils": "Supported circuit interchange and utility operations.",
    "torch": "Qualified GPU tensor arithmetic and the octonion package backend.",
    "cupy": "Qualified CUDA array and contraction reference path.",
    "jax": "Differentiable array candidate; record actual devices rather than assuming GPU/TPU access.",
    "numba": "Compiled numeric kernels; compilation speed does not change the arithmetic contract.",
    "matplotlib": "Measured plots and static exports with uncertainty and evidence labels.",
    "pandas": "Tabular evidence joins and summaries.",
    "xarray": "Labeled acquisition arrays and parameter axes.",
    "qutip": "Reference-only Lindblad alternative; qualify a capability gap before adding it.",
    "pennylane": "Documented alternative differentiable circuit stack; not required for current cases.",
    "pennylane-quantuminspire": "Documented optional provider adapter; preserve its separate compatibility caps.",
    "perceval-interop": "Documented converter candidate with Qiskit version constraints.",
    "pymatching": "Error-model decoding when a detector-code experiment requires it.",
    "cirq-core": "IQM circuit interface in its isolated stack.",
    "qrisp": "IQM high-level circuit/QEC interface in its isolated stack.",
    "iqm-client": "IQM circuit jobs, native integrations and calibration reads.",
    "iqm-pulla": "IQM circuit-to-pulse compiler, imported as iqm.cpc.",
    "iqm-pulse": "IQM native gate timing and playlist construction.",
    "iqm-benchmarks": "IQM characterization experiments; device jobs require approval.",
    "iqm-qubit-selector": "Calibration-aware IQM layout selection.",
    "iqm-error-reduction-tools": "IQM readout/twirling workflow with acquisition accounting.",
    "iqm-qaoa": "Optional optimization examples; not evidence of advantage for the present PDE task.",
    "openquantum-sdk": "Read-only native credit quotes and approved brokered execution.",
    "openquantum-sdk-qiskit": "Qiskit adapter for brokered backends; Public upload is a disclosure.",
    "openquantum-mcp": "Broker tool transport; tool auto-approval does not replace repository case approval.",
    "pytest": "Behavioral regressions and mutation checks.",
    "pytest-xdist": "CPU-budgeted independent test execution.",
    "ruff": "Pinned lint and format gate.",
    "mypy": "Pinned static type gate.",
    "threadpoolctl": "Inspect and bound native BLAS/OpenMP threads.",
}
INDEPENDENT = {
    "hypercomplex",
    "hypercomplex-engine",
    "cayley-calculator",
    "cayley-dickson",
    "octonion",
    "numpy-quaternion",
    "quaternionic",
    "pyquaternion",
    "pyoctonion",
    "octonion-sedenion",
    "hyprat",
    "sagemath",
}
EXECUTION = {
    "qiskit-ibm-runtime",
    "quantuminspire",
    "qi-compute-api-client",
    "qiskit-quantuminspire",
    "perceval-quandela",
    "openquantum-sdk",
    "openquantum-sdk-qiskit",
    "iqm-client",
    "qiskit-mitigation",
}
ISOLATED_IMPORTS = {
    "cqasm": "libqasm",
    "openquantum_mcp": "openquantum-mcp",
    "openquantum_sdk": "openquantum-sdk",
    "opensquirrel": "opensquirrel",
    "quantuminspire": "quantuminspire",
    "qxelarator": "qxelarator",
    "sedenion": "octonion-sedenion",
}


def normalized(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def inventory() -> dict[str, Any]:
    declarations: dict[str, dict[str, str]] = {name: {} for name in ROLES}
    sources: dict[str, str] = {}
    for path in sorted(ROOT.rglob("*requirements*.txt")):
        relative = path.relative_to(ROOT).as_posix()
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            sources[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
            for line in path.read_text().splitlines():
                match = re.match(r"^([A-Za-z0-9_.-]+)==([^ #;]+)", line)
                if match:
                    declarations.setdefault(normalized(match[1]), {})[relative] = match[2]
    stack_path = ROOT / "docs/notes/iqm/python-stack-versions.json"
    stack = json.loads(stack_path.read_text())["distributions"]
    stack = {normalized(name): record for name, record in stack.items()}
    sources[stack_path.relative_to(ROOT).as_posix()] = hashlib.sha256(stack_path.read_bytes()).hexdigest()
    for name, record in stack.items():
        declarations.setdefault(name, {})["IQM retained environment"] = record["version"]
    package_map = metadata.packages_distributions()
    tracked = subprocess.check_output(["git", "ls-files", "-z", "*.py"], cwd=ROOT).decode().split("\0")
    local_modules = {Path(name).stem for name in tracked if name}
    imports: dict[str, set[str]] = {}
    unresolved: set[str] = set()
    for filename in tracked:
        if not filename or not filename.startswith(("gororoba_quantum/", "scripts/", "ci/", "kaggle_kernel/")):
            continue
        tree = ast.parse((ROOT / filename).read_text())
        for node in ast.walk(tree):
            roots = (
                [alias.name.split(".")[0] for alias in node.names]
                if isinstance(node, ast.Import)
                else (
                    [node.module.split(".")[0]]
                    if isinstance(node, ast.ImportFrom) and node.module and not node.level
                    else []
                )
            )
            for root in roots:
                if root in sys.stdlib_module_names or root in local_modules:
                    continue
                distributions = package_map.get(root, [])
                if not distributions and root in ISOLATED_IMPORTS:
                    distributions = [ISOLATED_IMPORTS[root]]
                if not distributions:
                    unresolved.add(root)
                for distribution in distributions:
                    name = normalized(distribution)
                    declarations.setdefault(name, {})
                    imports.setdefault(name, set()).add(filename)
    rows = []
    for name, pins in sorted(declarations.items()):
        try:
            installed = metadata.distribution(name)
            observed = installed.version
            summary = installed.metadata.get("Summary", "Runtime dependency")
        except metadata.PackageNotFoundError:
            observed = None
            summary = stack.get(name, {}).get("summary", "Environment support dependency")
        rows.append(
            {
                "distribution": name,
                "declared_versions": pins,
                "observed_host_version": observed,
                "role": ROLES.get(name, f"SDK/environment infrastructure: {summary}"),
                "independent_algebra_witness": name in INDEPENDENT,
                "hardware_execution": name in EXECUTION,
                "imported_by": sorted(imports.get(name, set())),
                "qualification": "admit only the documented API and declared convention; installation is not a run",
            }
        )
    return {
        "schema": "hypercomplex-library-inventory-v1",
        "libraries": rows,
        "sources_sha256": sources,
        "unresolved_import_roots": sorted(unresolved),
        "coverage": (
            "all requirements locks, retained IQM distributions, maintained scientific roles "
            "and tracked runtime imports"
        ),
    }


def markdown(record: dict[str, Any]) -> str:
    lines = [
        "# Python libraries in the hypercomplex campaign",
        "",
        "Each row names a distribution, its scientific or operational role, and the observed host version. "
        "The JSON register retains environment pins and import locations separately. "
        "A missing host distribution may belong to an isolated provider environment.",
        "",
        "| Distribution | Host observation | Role |",
        "|---|---|---|",
    ]
    lines.extend(
        f"| {row['distribution']} | {row['observed_host_version'] or 'separate/unobserved'} | {row['role']} |"
        for row in record["libraries"]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    record = inventory()
    arguments.out.mkdir(parents=True, exist_ok=True)
    (arguments.out / "libraries.json").write_text(json.dumps(record, indent=1) + "\n")
    (arguments.out / "libraries.md").write_text(markdown(record))
    print(f"explained {len(record['libraries'])} distributions; unresolved imports are explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
