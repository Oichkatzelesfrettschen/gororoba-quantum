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
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

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
    "qbraid": "Documented multi-provider SDK alternative; current cases use the repository's guarded clients.",
    "coheriq": "Documented ecosystem alternative outside the maintained IBM execution workflow.",
    "benchpress": "Documented compiler benchmark alternative; qualification needs the same full-operator oracle.",
    "mapomatic": "Layout-search candidate; admit only against fresh targets and measured layout controls.",
    "qiskit-dynamics": "Continuous-system simulation alternative; the retained note records its archive status.",
    "gmpy2": "Exact integer/rational arithmetic and accelerated symbolic coefficient support.",
    "mpmath": "Arbitrary-precision numerical controls; convergence and precision need explicit error budgets.",
}
ROLES.update(
    {
        "qiskit-addon-mpf": (
            "Optional multiproduct-formula Trotter-error reduction using CVXPY. The 2026-10-16 ecosystem "
            "audit declined the workflow; host CVXPY availability does not establish its admission. "
            "Qualify circuit approximations, solver residuals and error budgets before use."
        ),
        "cuquantum-cu11": (
            "CUDA 11 cuQuantum dependency bundle for the isolated Aer GPU wheel; "
            "shared simulator engine infrastructure."
        ),
        "cutensor-cu11": "CUDA 11 tensor contraction library beneath cuTensorNet in the qualified Aer GPU runtime.",
        "uv": (
            "Pinned environment installer used by Kaggle kernel bootstrap; "
            "records package resolution rather than quantum evidence."
        ),
        "qiskit-aer-gpu-cu13": (
            "Repository-built CUDA 13 Aer wheel for qualified Kaggle GPU simulation; exclusively owns "
            "qiskit_aer in that environment and shares the Aer engine, not an independent witness."
        ),
        "qiskit-aer-gpu-cu11": (
            "CUDA 11 Aer wheel for the isolated Kaggle GPU path; exclusively owns qiskit_aer and shares the "
            "CPU/CUDA 13 Aer engine."
        ),
        "qiskit-aer-gpu": (
            "CUDA 12 Aer alternative remains unused: retained ecosystem audit records release 0.15.1 without "
            "a Python 3.13 wheel; do not coinstall qiskit_aer owners."
        ),
        "custatevec-cu13": (
            "CUDA 13 cuQuantum statevector primitives loaded by the qualified Aer cuStateVec path; shared "
            "simulator infrastructure, not an independent algebra witness."
        ),
        "cutensornet-cu13": (
            "CUDA 13 cuQuantum tensor-network contraction library linked by the Aer GPU wheel; linking does "
            "not establish a selected simulation method or speedup."
        ),
        "cutensor-cu13": (
            "CUDA 13 tensor contraction support beneath cuTensorNet; qualify ABI, device and actual method separately."
        ),
        "nvidia-cuda-runtime": (
            "Pinned CUDA 13 runtime loaded by the repository GPU Aer wheel; verify the driver and device in "
            "each execution environment."
        ),
        "nvidia-cublas": (
            "Pinned CUDA 13 dense GPU linear algebra used by the simulator runtime stack; shared infrastructure."
        ),
        "nvidia-cuda-nvrtc": "Pinned CUDA 13 runtime compilation support in the GPU simulator environment.",
        "nvidia-cusolver": (
            "Pinned CUDA 13 GPU solver library for simulator numerical linear algebra; not a tomography SDP "
            "modeling layer."
        ),
        "nvidia-cusparse": "Pinned CUDA 13 sparse GPU linear algebra support in the simulator environment.",
        "nvidia-nvjitlink": (
            "Pinned CUDA 13 device-code JIT linking support; installation establishes neither GPU execution "
            "nor a numerical result."
        ),
        "cvxpy": (
            "Convex modeling for constrained Qiskit state/process tomography and reconstruction; PSD, trace "
            "and trace-preserving constraints depend on the declared fitter and SDP-compatible solver. "
            "Inspect status, residuals and tolerances; supplies neither an exact algebra witness nor device "
            "proof."
        ),
        "scs": (
            "First-order splitting conic solver supporting PSD tomography through CVXPY; qualify "
            "convergence, constraint residuals and tolerances for the actual fit."
        ),
        "clarabel": (
            "Interior-point conic solver; retained CVXPY interface supports PSD cones. Qualify installed "
            "capabilities and the tomography model before selection; not interchangeable with an "
            "unconstrained fit."
        ),
        "osqp": (
            "Operator-splitting convex quadratic-program solver for QPs with linear constraints; not a "
            "PSD-constrained tomography SDP solver. Qualify the objective and constraint class before use."
        ),
    }
)
DISPATCH_MODULES = ("scripts/kaggle_run.py",)
ROLE_GROUNDING = "docs/state/hypercomplex-libraries/solver-role-grounding.json"


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
    "openquantum-sdk-pennylane",
    "openquantum-sdk-cirq",
    "openquantum-sdk-qrisp",
    "openquantum-mcp",
    "iqm-client",
    "iqm-benchmarks",
    "iqm-error-reduction-tools",
    "qiskit-experiments",
    "qiskit-device-benchmarking",
    "qiskit-serverless",
    "qiskit-ibm-catalog",
    "qiskit-ibm-provider",
    "qiskit-ibm-runtime-mcp-server",
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


def _file_imports(filename: str) -> tuple[str, list[str]]:
    roots: set[str] = set()
    for node in ast.walk(ast.parse((ROOT / filename).read_text())):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            roots.add(node.module.split(".")[0])
    return filename, sorted(roots)


def execution_declarations(root: Path) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    """Read literal pins and referenced pin manifests without importing the dispatcher."""
    declarations: dict[str, dict[str, str]] = {}
    sources: dict[str, str] = {}

    def admit(text: str, source: str) -> None:
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([^ #;]+)", text.strip())
        if match:
            declarations.setdefault(normalized(match[1]), {})[source] = match[2]

    for relative in DISPATCH_MODULES:
        path = root / relative
        sources[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        tree = ast.parse(path.read_text())
        for statement in tree.body:
            if isinstance(statement, ast.Assign):
                targets = statement.targets
            elif isinstance(statement, ast.AnnAssign):
                targets = [statement.target]
            else:
                continue
            constants = [target.id for target in targets if isinstance(target, ast.Name) and target.id.isupper()]
            if not constants:
                continue
            for node in ast.walk(statement.value) if statement.value is not None else ():
                if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                    continue
                provenance = f"{relative}:{node.lineno}:{constants[0]}"
                admit(node.value, provenance)
                if node.value.endswith("-pins.txt"):
                    manifest = root / node.value
                    if not manifest.is_relative_to(root) or not manifest.is_file():
                        raise ValueError(f"dispatcher runtime pin manifest missing: {node.value}")
                    sources[node.value] = hashlib.sha256(manifest.read_bytes()).hexdigest()
                    for line_number, line in enumerate(manifest.read_text().splitlines(), 1):
                        admit(line, f"{node.value}:{line_number}")
    return declarations, sources


def check_execution_coverage(record: dict[str, Any], root: Path) -> None:
    """Every dispatcher/manifest literal pin retains its exact version and source location."""
    expected, sources = execution_declarations(root)
    rows = {row["distribution"]: row for row in record["libraries"]}
    for name, pins in expected.items():
        if name not in rows or any(rows[name]["declared_versions"].get(source) != pin for source, pin in pins.items()):
            raise ValueError(f"execution pin coverage differs: {name}")
    if any(record["sources_sha256"].get(path) != digest for path, digest in sources.items()):
        raise ValueError("execution source hash coverage differs")


def check_inventory_denominator(record: dict[str, Any], root: Path) -> None:
    """Validate unique canonical names and exact integer counts over current execution declarations."""
    names = [row["distribution"] for row in record["libraries"]]
    if any(not isinstance(name, str) or not name for name in names):
        raise ValueError("inventory distribution names must be nonempty strings")
    canonical = [normalized(name) for name in names]
    if len(canonical) != len(set(canonical)):
        raise ValueError("inventory distribution names repeat after normalization")
    if names != canonical:
        raise ValueError("inventory distribution name is not normalized")
    pins, sources = execution_declarations(root)
    expected = {
        "distributions": len(names),
        "execution_pin_distributions": len(pins),
        "execution_pin_declarations": sum(len(versions) for versions in pins.values()),
        "execution_source_files": len(sources),
    }
    counts = record.get("coverage_counts")
    if not isinstance(counts, dict) or set(counts) != set(expected):
        raise ValueError("inventory coverage count fields differ")
    for name, value in expected.items():
        if type(counts[name]) is not int or counts[name] != value:
            raise ValueError(f"inventory coverage count differs: {name}")


def requirement_manifests(root: Path) -> list[Path]:
    """The finite visible requirement-lock discovery surface, excluding hidden environments."""
    return [
        path
        for path in sorted(root.rglob("*requirements*.txt"))
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(root).parts)
    ]


def declared_libraries() -> dict[str, Any]:
    declarations: dict[str, dict[str, str]] = {name: {} for name in ROLES}
    sources: dict[str, str] = {}
    documentary_roles: dict[str, str] = {}
    mentions: dict[str, list[str]] = {}
    for path in sorted((ROOT / "docs/notes").glob("*/pypi/*.json")):
        record = json.loads(path.read_text())
        if not isinstance(record, dict) or not isinstance(record.get("name"), str):
            continue
        name = normalized(record["name"])
        relative = path.relative_to(ROOT).as_posix()
        sources[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        declarations.setdefault(name, {})
        mentions.setdefault(name, []).append(relative)
        documentary_roles[name] = str(record.get("summary", "Provider SDK support dependency"))
    for relative in ("docs/notes/qiskit-ecosystem.md", "docs/notes/packages/candidates.md"):
        path = ROOT / relative
        sources[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        active_table = relative.endswith("candidates.md")
        for line_number, line in enumerate(path.read_text().splitlines(), 1):
            if line.startswith("## Table A"):
                active_table = True
            if line.startswith("## Host import health"):
                active_table = False
            if not active_table:
                continue
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            if not cells:
                continue
            ranked = relative.endswith("candidates.md")
            if ranked and (not cells[0].isdigit() or len(cells) < 4):
                continue
            if not ranked and len(cells) not in (5, 9):
                continue
            first = cells[1] if ranked else cells[0]
            if ranked and first.startswith("PyPI "):
                first = first.removeprefix("PyPI ")
            if ranked and first.startswith("surreal-number packages"):
                first = "surreal"
            candidates = (
                [first] + re.findall(r",\s*([a-z][A-Za-z0-9_.-]+)\s+(?=\d)", first) if ranked else first.split(",")
            )
            for candidate in candidates:
                match = re.match(r"^`?([A-Za-z][A-Za-z0-9_.-]*)(?:`?\s|`?$)", candidate.strip())
                if not match:
                    continue
                name = normalized(match[1])
                if name in {"package", "mcp-server"}:
                    continue
                name = {"python-hypercomplex": "hypercomplex"}.get(name, name)
                declarations.setdefault(name, {})
                mentions.setdefault(name, []).append(f"{relative}:{line_number}")
                if ranked:
                    documentary_roles[name] = f"Documented algebra candidate: {cells[2]}. Decision: {cells[-1]}"
                elif len(cells) == 9:
                    documentary_roles[name] = f"Documented ecosystem candidate: {cells[-1]}"
    for path in requirement_manifests(ROOT):
        relative = path.relative_to(ROOT).as_posix()
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(ROOT).parts):
            sources[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
            for line in path.read_text().splitlines():
                match = re.match(r"^([A-Za-z0-9_.-]+)==([^ #;]+)", line)
                if match:
                    declarations.setdefault(normalized(match[1]), {})[relative] = match[2]
    execution_pins, execution_sources = execution_declarations(ROOT)
    sources.update(execution_sources)
    for name, pins in execution_pins.items():
        declarations.setdefault(name, {}).update(pins)
    for relative in (
        ROLE_GROUNDING,
        "scripts/hypercomplex_libraries.py",
        "docs/notes/quandela/python-stack.md",
        "docs/notes/kaggle/recipes/build_aer_gpu_cu13_wheel.sh",
    ):
        sources[relative] = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
    stack_path = ROOT / "docs/notes/iqm/python-stack-versions.json"
    stack = json.loads(stack_path.read_text())["distributions"]
    stack = {normalized(name): record for name, record in stack.items()}
    sources[stack_path.relative_to(ROOT).as_posix()] = hashlib.sha256(stack_path.read_bytes()).hexdigest()
    for name, record in stack.items():
        declarations.setdefault(name, {})["IQM retained environment"] = record["version"]
    return {
        "declarations": declarations,
        "sources": sources,
        "documentary_roles": documentary_roles,
        "mentions": mentions,
        "stack": stack,
        "execution_pins": execution_pins,
    }


def inventory() -> dict[str, Any]:
    declared = declared_libraries()
    declarations = declared["declarations"]
    sources = declared["sources"]
    documentary_roles = declared["documentary_roles"]
    mentions = declared["mentions"]
    stack = declared["stack"]
    execution_pins = declared["execution_pins"]
    execution_sources = execution_declarations(ROOT)[1]
    package_map = metadata.packages_distributions()
    tracked = subprocess.check_output(["git", "ls-files", "-z", "*.py"], cwd=ROOT).decode().split("\0")
    local_modules = {Path(name).stem for name in tracked if name}
    imports: dict[str, set[str]] = {}
    unresolved: set[str] = set()
    runtime_files = [
        name for name in tracked if name.startswith(("gororoba_quantum/", "scripts/", "ci/", "kaggle_kernel/"))
    ]
    for filename, roots in ordered_map(_file_imports, runtime_files):
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
                "role": ROLES.get(name, documentary_roles.get(name, f"SDK/environment infrastructure: {summary}")),
                "documentation_mentions": sorted(set(mentions.get(name, []))),
                "role_sources": (
                    [ROLE_GROUNDING, "docs/notes/quandela/python-stack.md:63"]
                    if name in {"cvxpy", "scs", "clarabel", "osqp"}
                    else ["docs/notes/qiskit-ecosystem.md:201", ROLE_GROUNDING]
                    if name == "qiskit-addon-mpf"
                    else ["scripts/kaggle_run.py", "docs/notes/qiskit-ecosystem.md"]
                    if name in execution_pins and ("cu13" in name or name.startswith("nvidia-"))
                    else []
                ),
                "independent_algebra_witness": name in INDEPENDENT,
                "hardware_execution": name in EXECUTION,
                "imported_by": sorted(imports.get(name, set())),
                "qualification": "admit only the documented API and declared convention; installation is not a run",
            }
        )
    return {
        "schema": "hypercomplex-library-inventory-v1",
        "coverage_counts": {
            "distributions": len(rows),
            "execution_pin_distributions": len(execution_pins),
            "execution_pin_declarations": sum(len(pins) for pins in execution_pins.values()),
            "execution_source_files": len(execution_sources),
        },
        "libraries": rows,
        "sources_sha256": sources,
        "unresolved_import_roots": sorted(unresolved),
        "execution_flag_scope": "recognized provider dispatch surfaces; false does not prove absence of remote effects",
        "coverage": (
            "all requirements locks, top-level literal pins and referenced runtime pin files in "
            "scripts/kaggle_run.py (without executing dispatch), retained IQM distributions, maintained "
            "scientific roles "
            "and tracked runtime imports; every named package-table entry in the maintained ecosystem "
            "and algebra-candidate notes, plus retained provider PyPI records"
        ),
    }


def markdown(record: dict[str, Any]) -> str:
    lines = [
        "# Python libraries in the hypercomplex campaign",
        "",
        f"The inventory explains {len(record['libraries'])} distributions over the declared source surfaces.",
        "",
        "Each row names a distribution, its scientific or operational role, and the observed host version. "
        "The JSON register retains environment pins and import locations separately. "
        "A missing host distribution may belong to an isolated provider environment.",
        "",
        "Execution pins come from requirement locks and the dispatcher's top-level string literals plus referenced "
        "runtime pin files. The JSON records each pin's file, line and constant, and hashes every source. "
        "Coverage is finite over these named surfaces, not every prose mention or an implicit transitive "
        "resolver closure.",
        "",
        "CPU, CUDA 11 and CUDA 13 Aer distributions share one simulator engine and exclusively own `qiskit_aer` "
        "within an environment. Isolate them; cross-build agreement supplies implementation conformance rather than "
        "independent algebra evidence. CUDA 12 Aer remains unused under the retained Python-wheel "
        "compatibility decision.",
        "",
        "CVXPY models reconstruction constraints; SCS and Clarabel expose conic/PSD capabilities, whereas OSQP "
        "solves quadratic programs with linear constraints. Solver selection requires model, status, residual and "
        "tolerance qualification. [Retained metadata and source observations](solver-role-grounding.json) bind "
        "these roles; the repository's [Quandela stack](../../notes/quandela/python-stack.md) and "
        "[ecosystem audit](../../notes/qiskit-ecosystem.md) supply the operational context.",
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
    parser.add_argument("--check", action="store_true", help="verify retained source pins, roles and rendering")
    arguments = parser.parse_args()
    if arguments.check:
        record = json.loads((arguments.out / "libraries.json").read_text())
        check_inventory_denominator(record, ROOT)
        check_execution_coverage(record, ROOT)
        declared = declared_libraries()
        declarations = declared["declarations"]
        if set(record["sources_sha256"]) != set(declared["sources"]):
            raise ValueError("inventory declared source coverage differs")
        rows = {row["distribution"]: row for row in record["libraries"]}
        for name, pins in declarations.items():
            if name not in rows or any(
                rows[name]["declared_versions"].get(source) != pin for source, pin in pins.items()
            ):
                raise ValueError(f"inventory declared library coverage differs: {name}")
        expected_manifests = {path.relative_to(ROOT).as_posix() for path in requirement_manifests(ROOT)}
        retained_manifests = {path for path in record["sources_sha256"] if "requirements" in Path(path).name}
        if expected_manifests != retained_manifests:
            raise ValueError("inventory requirement manifest coverage differs")
        for relative, digest in record["sources_sha256"].items():
            if hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
                raise ValueError(f"inventory source differs: {relative}")
        for row in record["libraries"]:
            if row["distribution"] in ROLES and row["role"] != ROLES[row["distribution"]]:
                raise ValueError(f"inventory role differs: {row['distribution']}")
        if (arguments.out / "libraries.md").read_text() != markdown(record):
            raise ValueError("inventory Markdown differs")
        print(f"validated {len(record['libraries'])} distributions and every execution pin")
        return 0
    record = inventory()
    prior_path = arguments.out / "libraries.json"
    if prior_path.exists():
        prior = {row["distribution"]: row for row in json.loads(prior_path.read_text())["libraries"]}
        for row in record["libraries"]:
            if row["distribution"] in prior:
                retained = prior[row["distribution"]]
                row["observed_host_version"] = retained["observed_host_version"]
                row["imported_by"] = sorted(set(row["imported_by"]) | set(retained["imported_by"]))
        record["host_observation_policy"] = (
            "existing observations/import locations retained; additions observed by generator interpreter"
        )
    check_inventory_denominator(record, ROOT)
    check_execution_coverage(record, ROOT)
    arguments.out.mkdir(parents=True, exist_ok=True)
    (arguments.out / "libraries.json").write_text(json.dumps(record, indent=1) + "\n")
    (arguments.out / "libraries.md").write_text(markdown(record))
    print(f"explained {len(record['libraries'])} distributions; unresolved imports are explicit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
