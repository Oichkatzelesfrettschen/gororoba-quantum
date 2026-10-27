"""Generate deterministic operator-conformance cases without contacting a provider.

Each hardware batch carries its own readout controls. Optical settings use one
connected input and retain all twelve outputs. Unallocated compiler randomness
keeps an optical case outside the remote runner's acquisition boundary.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.metadata
import json
import math
import platform
import re
import sys
from dataclasses import asdict, dataclass
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from hypercomplex_cases import encoded, qi_native, write_files
from qi_zero_divisor_cases import CASES, CATALOGUE, catalogue_check, logical

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from dimension_six_circuits import transition_circuit  # noqa: E402
from experiment_references import (  # noqa: E402
    ACTIVE_INDICES,
    BASIS_NAMES,
    quarter_mass_operators,
    reference_report,
    sedenion_operators,
    transition_matrix,
)
from operator_arithmetic import photonic_template, probabilities  # noqa: E402
from parallel import ordered_map  # noqa: E402
from qrng_seeds import resolve  # noqa: E402

QD_CATALOGUE = ROOT / "docs/evidence/quandela/catalogue.json"
FAMILIES = ("mub-six", "quarter-mass", "sedenion-lcu")
SEED_DRAW = "docs/evidence/anu_qrng/draw-2026-10-26T220128Z.json"
SEED_MAPPING = "docs/evidence/quantum-experiment-conformance/cases/seeds.json"


@cache
def optical_seeds() -> list[dict[str, Any]]:
    """Each static optical acquisition owns one reserved ANU draw index."""
    rows = [
        {"family": "mub-six", "name": f"{preparation}-to-{measurement}-input-{column}"}
        for preparation, measurement, column in _mub_jobs()
    ] + [{"family": "sedenion-lcu", "name": name} for name in CASES]
    allocations = []
    for index, row in enumerate(rows, start=2):
        reference = f"qrng:{SEED_DRAW}#{index}"
        value, source, source_index = resolve(reference, root=ROOT)
        allocations.append(
            {
                "family": row["family"],
                "setting": row["name"],
                "seed": value,
                "source": source,
                "index": source_index,
                "reference": reference,
            }
        )
    return allocations


@dataclass(frozen=True)
class Budgets:
    """Operator-supplied ceilings; these values make no runtime or tariff prediction."""

    tuna_shots: int
    qx_shots: int
    photonic_samples: int
    photonic_shots: int
    execution_seconds: float
    photonic_credits: float

    def validate(self) -> None:
        backend, emulator = catalogue_check()
        for value, ceiling, label in (
            (self.tuna_shots, backend["max_number_of_shots"], "Tuna shots"),
            (self.qx_shots, emulator["max_number_of_shots"], "QX shots"),
            (self.photonic_samples, self.photonic_shots, "photonic samples"),
            (self.photonic_shots, self.photonic_shots, "photonic shots"),
        ):
            if type(value) is not int or not 1 <= value <= ceiling:
                raise ValueError(f"{label} must be a positive integer within the declared ceiling")
        for ceiling_value in (self.execution_seconds, self.photonic_credits):
            if not math.isfinite(ceiling_value) or ceiling_value <= 0:
                raise ValueError("execution and credit ceilings must be finite and positive")
        if self.execution_seconds > 300:
            raise ValueError("execution ceiling exceeds the admitted 300-second envelope")


def _permutation(size: int, target: int) -> Any:
    matrix = np.eye(size, dtype=np.complex128)
    matrix[:, [0, target]] = matrix[:, [target, 0]]
    return matrix


def _mub_jobs() -> list[tuple[str, str, int]]:
    return [
        (preparation, measurement, column)
        for preparation in BASIS_NAMES[:3]
        for measurement in BASIS_NAMES[:3]
        for column in range(6)
    ]


def _mub_setting(arguments: tuple[str, str, int]) -> dict[str, Any]:
    preparation, measurement, column = arguments
    transition = (
        np.eye(6, dtype=np.complex128) if preparation == measurement else transition_matrix(preparation, measurement)
    )
    matrix = np.eye(8, dtype=np.complex128)
    matrix[np.ix_(ACTIVE_INDICES, ACTIVE_INDICES)] = transition
    target = ACTIVE_INDICES[column]
    matrix[:, [0, target]] = matrix[:, [target, 0]]
    optical = transition.copy()
    optical[:, [0, column]] = optical[:, [column, 0]]
    row = {
        "name": f"{preparation}-to-{measurement}-input-{column}",
        "family": "mub-six",
        "preparation_basis": preparation,
        "measurement_basis": measurement,
        "input_column": column,
        "matrix": matrix,
        "optical_matrix": optical,
        "active_outputs": list(ACTIVE_INDICES),
        "optical_active_outputs": list(range(6)),
        "success_outputs": [],
        "optical_success_outputs": [],
        "placement": (11, 13, 14),
    }
    row["source_circuit"] = transition_circuit(preparation, measurement, column)
    return row


def _quarter_mass_setting(arguments: tuple[str, Any]) -> dict[str, Any]:
    from qiskit import QuantumCircuit

    name, matrix = arguments
    circuit = QuantumCircuit(2)
    if name == "direct_target":
        circuit.x([0, 1])
    else:
        circuit.h([0, 1])
        if name != "preparation":
            circuit.barrier()
            if name != "omit_oracle":
                circuit.cz(0, 1)
            circuit.barrier()
            if name != "omit_reflection":
                circuit.h([0, 1])
                circuit.x([0, 1])
                circuit.cz(0, 1)
                circuit.x([0, 1])
                circuit.h([0, 1])
                circuit.global_phase = math.pi
    return {
        "name": name,
        "family": "quarter-mass",
        "matrix": matrix,
        "source_circuit": circuit,
        "optical_matrix": matrix,
        "active_outputs": list(range(4)),
        "optical_active_outputs": list(range(4)),
        "success_outputs": [3],
        "optical_success_outputs": [3],
        "placement": (11, 13),
    }


def _sedenion_setting(name: str) -> dict[str, Any]:
    from qiskit.quantum_info import Operator

    (first, second), phase, _ = CASES[name]
    witness = sedenion_operators()["witness"]
    source = logical(name)
    if phase not in (0.0, math.pi):
        raise ValueError("the signed witness requires relative phase zero or pi")
    relative_sign = 1 if phase == 0 else -1
    columns = np.arange(16)
    difference = first ^ second
    pivot = (difference & -difference).bit_length() - 1
    pivot_mask = 1 << pivot
    lower = columns & ~pivot_mask
    upper = lower | pivot_mask
    preparation_operator = np.zeros((16, 16), dtype=np.complex128)
    inverse_root_two = math.sqrt(0.5)
    preparation_operator[lower ^ first, columns] = inverse_root_two
    preparation_operator[upper ^ (difference ^ pivot_mask) ^ first, columns] = (
        relative_sign * (1 - 2 * ((columns >> pivot) & 1)) * inverse_root_two
    )
    requested = witness @ np.kron(np.eye(2), preparation_operator)
    requested[requested == 0] = 0
    if not np.allclose(Operator(source).data, requested, atol=1e-12, rtol=0):
        raise ValueError("the source circuit differs from the exact signed-pair preparation")
    input_indices = [first, second, first + 16, second + 16]
    outputs = sorted({1 ^ first, 10 ^ first, 1 ^ second, 10 ^ second})
    output_indices = outputs + [index + 16 for index in outputs]
    input_data = {index ^ multiplier for index in outputs for multiplier in (1, 10)}
    complete_inputs = input_data | {index + 16 for index in input_data}
    input_indices += sorted(complete_inputs - set(input_indices))
    restricted = witness[np.ix_(output_indices, input_indices)]
    preparation = np.array([[1, 1], [relative_sign, -relative_sign]]) * inverse_root_two
    complete_preparation = np.eye(len(input_indices), dtype=np.complex128)
    complete_preparation[:4, :4] = np.kron(np.eye(2), preparation)
    optical = restricted @ complete_preparation
    identity = np.eye(len(input_indices))
    if optical.shape != identity.shape or not (
        np.allclose(optical.conj().T @ optical, identity, atol=1e-12, rtol=0)
        and np.allclose(optical @ optical.conj().T, identity, atol=1e-12, rtol=0)
    ):
        raise ValueError("sedenion complete support restriction must be a square unitary")
    if not np.allclose(witness[:, input_indices][[i for i in range(32) if i not in output_indices]], 0):
        raise ValueError("sedenion restriction loses full-space amplitude")
    return {
        "name": name,
        "family": "sedenion-lcu",
        "matrix": requested,
        "source_circuit": source,
        "optical_matrix": optical,
        "active_outputs": list(range(32)),
        "optical_active_outputs": list(range(len(output_indices))),
        "success_outputs": list(range(16)),
        "optical_success_outputs": list(range(len(outputs))),
        "support_isometry": {"input_indices": input_indices, "output_indices": output_indices},
        "placement": (7, 8, 11, 13, 14),
    }


def settings(family: str) -> list[dict[str, Any]]:
    """Logical settings include full operators and explicit observable partitions."""
    if family == "mub-six":
        return ordered_map(_mub_setting, _mub_jobs(), min_items=1)
    if family == "quarter-mass":
        operators = quarter_mass_operators()
        operators["direct_target"] = np.eye(4, dtype=np.complex128)[::-1]
        names = ("preparation", "amplified", "omit_oracle", "omit_reflection", "direct_target")
        return ordered_map(_quarter_mass_setting, [(name, operators[name]) for name in names], min_items=1)
    if family == "sedenion-lcu":
        rows = ordered_map(_sedenion_setting, list(CASES), min_items=1)
        dark, bright, fixture = rows
        sequenced = [
            dark,
            bright,
            {**bright, "name": "bright-repeat", "repeat_of": "bright"},
            {**dark, "name": "dark-repeat", "repeat_of": "dark"},
            fixture,
        ]
        for order, (row, weight) in enumerate(zip(sequenced, (1, -1, -1, 1, 0), strict=True)):
            row["acquisition_order"] = order
            row["contrast_weight"] = weight
        return sequenced
    raise ValueError(f"unknown family {family!r}")


def _metadata(setting: dict[str, Any]) -> dict[str, Any]:
    excluded = {
        "matrix",
        "optical_matrix",
        "source_circuit",
        "placement",
        "optical_active_outputs",
        "optical_success_outputs",
    }
    return {key: value for key, value in setting.items() if key not in excluded}


def _readout(width: int, mapping: list[int], prepared: int) -> str:
    text = ["version 3.0", f"qubit[{width}] q", f"bit[{len(mapping)}] b"]
    if prepared:
        text.extend(f"X q[{physical}]" for physical in mapping)
    text.append("barrier q")
    text.extend(f"b[{logical_index}] = measure q[{physical}]" for logical_index, physical in enumerate(mapping))
    return "\n".join(text) + "\n"


def _qi_cases(setting: dict[str, Any], budgets: Budgets) -> dict[str, str]:
    compiled = qi_native(
        setting["matrix"],
        setting["name"],
        physical_qubits=setting["placement"],
        deterministic=True,
        source_circuit=setting.get("source_circuit"),
    )
    source = compiled.pop("source")
    placement = compiled["placement"]
    physical_to_compact = {physical: compact for compact, physical in enumerate(placement)}
    twin = re.sub(r"q\[(\d+)\]", lambda match: f"q[{physical_to_compact[int(match[1])]}]", source)
    twin = re.sub(r"qubit\[\d+\]", f"qubit[{len(placement)}]", twin)
    files = {}
    for route, backend, backend_id, payload, mapping, shots in (
        ("tuna", "tuna_17", 7, source, compiled["measurement_mapping"], budgets.tuna_shots),
        (
            "qx",
            "QXsinglenodesimulator",
            1,
            twin,
            [physical_to_compact[q] for q in compiled["measurement_mapping"]],
            budgets.qx_shots,
        ),
    ):
        directory = f"{route}/{setting['family']}/{setting['name']}"
        width = max(placement) + 1 if route == "tuna" else len(placement)
        science = {**compiled, **_metadata(setting)}
        science.update(
            kind="science",
            nqubits=width,
            measurement_mapping=mapping,
            register_kind="classical" if route == "tuna" else "qubit",
            register_width=len(placement),
            logical_output_labels=[format(index, f"0{len(placement)}b") for index in range(2 ** len(placement))],
            leakage_outputs=[index for index in range(2 ** len(placement)) if index not in setting["active_outputs"]],
            sha256=hashlib.sha256(payload.encode()).hexdigest(),
        )
        files[f"{directory}/{science['file']}"] = payload
        rows = [science]
        for prepared in (0, 1):
            filename = f"readout-{prepared}.cq"
            text = _readout(width, mapping, prepared)
            files[f"{directory}/{filename}"] = text
            rows.append(
                {
                    "file": filename,
                    "kind": "readout-reference",
                    "prepared": prepared,
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                    "measurement_mapping": mapping,
                    "register_kind": science["register_kind"],
                    "logical_qubits": len(placement),
                    "register_width": len(placement),
                }
            )
        manifest = {
            "schema": "qi-hypercomplex-cases-v1",
            "family": setting["family"],
            "setting": setting["name"],
            "backend": backend,
            "backend_type_id": backend_id,
            "nqubits": width,
            "logical_qubits": len(placement),
            "shots": shots,
            "job_execution_time_limit": budgets.execution_seconds,
            "hardware_pause_seconds": 120,
            "circuits": rows,
            "compiler": {
                "policy": compiled["compiler_policy"],
                "seed_source": compiled["seed_source"],
                "qiskit": importlib.metadata.version("qiskit"),
                "catalogue_sha256": hashlib.sha256(CATALOGUE.read_bytes()).hexdigest(),
                "angle_step_radians": math.pi / 36,
            },
            "preregistered": {
                "primary": "unconditional logical output probabilities",
                "readout_correction": "sensitivity only",
                "minimum_output_readout_contrast": 0.2,
                "confidence": 0.95,
                "claim": "compiled operator conformance; physical mechanism remains device-specific",
            },
            "budget_status": "operator-supplied ceilings; live forecast and written-case approval required",
        }
        files[f"{directory}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
    return files


def _qd_cases(setting: dict[str, Any], budgets: Budgets) -> dict[str, str]:
    import qd_platform

    catalogue = json.loads(QD_CATALOGUE.read_bytes())
    specs = catalogue["processors"]["qpu:ascella"]["specs"]
    if specs["constraints"]["max_mode_count"] != 12 or 0 not in specs["connected_input_modes"]:
        raise ValueError("Ascella requires twelve outputs and connected input zero")
    size = len(setting["optical_matrix"])
    matrix = np.eye(12, dtype=np.complex128)
    matrix[:size, :size] = setting["optical_matrix"]
    circuit, parameters = photonic_template(matrix)
    law = probabilities(matrix)
    row = {
        **_metadata(setting),
        "kind": "science",
        "circuit_params": parameters,
        "operator": encoded(matrix),
        "column": [[float(value.real), float(value.imag)] for value in matrix[:, 0]],
        "requested_probabilities": law,
        "native_probabilities": law,
        "prediction_scope": "logical template; provider compiled mesh remains unobserved",
        "active_outputs": setting["optical_active_outputs"],
        "success_outputs": setting["optical_success_outputs"],
        "leakage_outputs": [index for index in range(12) if index not in setting["optical_active_outputs"]],
        "logical_output_labels": [str(index) for index in range(12)],
        "register_kind": "fock",
    }
    allocation = next(
        row
        for row in optical_seeds()
        if (row["family"], row["setting"]) == (setting["family"], setting.get("repeat_of", setting["name"]))
    )
    mapping_bytes = (ROOT / SEED_MAPPING).read_bytes()
    mapped = [
        row
        for row in json.loads(mapping_bytes)["allocations"]
        if (row["family"], row["setting"]) == (allocation["family"], allocation["setting"])
    ]
    if len(mapped) != 1 or any(
        mapped[0][key] != allocation[original]
        for key, original in (("value", "seed"), ("source", "source"), ("index", "index"))
    ):
        raise ValueError("the reserved seed mapping differs from its registered case identifier")
    text = json.dumps(circuit, indent=1) + "\n"
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": setting["family"],
        "job": setting["name"],
        "platforms": ["qpu:ascella"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": 1,
        "settings": [row],
        "mitigations": [],
        "min_detected_photons": 1,
        "max_samples": budgets.photonic_samples,
        "max_shots": budgets.photonic_shots,
        "max_duration": budgets.execution_seconds,
        "max_credits": budgets.photonic_credits,
        "acquisition_admission": "awaiting-live-budget-review",
        "compilation_seed": allocation["seed"],
        "compilation_seed_allocation": {
            "path": SEED_MAPPING,
            "sha256": hashlib.sha256(mapping_bytes).hexdigest(),
            "family": allocation["family"],
            "setting": allocation["setting"],
            "draw_index": allocation["index"],
            "kind": "reserved-static-case-identifier",
        },
        "compilation_seed_role": "reproduce-base-mesh" if "repeat_of" in setting else "new-mesh",
        "circuit": {"file": "circuit.json", "sha256": hashlib.sha256(text.encode()).hexdigest()},
        "catalogue_sha256": hashlib.sha256(QD_CATALOGUE.read_bytes()).hexdigest(),
        "preregistered": {
            "primary": "all twelve detected-output probabilities",
            "loss": "report detected and attempted denominators separately when supplied",
            "claim": "single-photon transition-operator conformance",
        },
    }
    qd_platform.template_experiment(manifest, circuit)
    directory = f"ascella/{setting['family']}/{setting['name']}"
    return {f"{directory}/circuit.json": text, f"{directory}/cases.json": json.dumps(manifest, indent=1) + "\n"}


def _build_setting(arguments: tuple[dict[str, Any], Budgets, tuple[str, ...]]) -> dict[str, str]:
    setting, budgets, routes = arguments
    files = _qi_cases(setting, budgets) if set(routes) & {"tuna", "qx"} else {}
    files = {name: value for name, value in files.items() if name.split("/")[0] in routes}
    if "ascella" in routes and setting["family"] != "quarter-mass":
        files.update(_qd_cases(setting, budgets))
    return files


def build(
    budgets: Budgets, families: tuple[str, ...] = FAMILIES, routes: tuple[str, ...] = ("tuna", "qx", "ascella")
) -> dict[str, str]:
    budgets.validate()
    if not families or len(set(families)) != len(families) or not set(families) <= set(FAMILIES):
        raise ValueError("families must be a distinct nonempty selection of admitted experiments")
    if not routes or len(set(routes)) != len(routes) or not set(routes) <= {"tuna", "qx", "ascella"}:
        raise ValueError("routes must be a distinct nonempty selection of tuna, qx and ascella")
    if "quarter-mass" in families and not set(routes) & {"tuna", "qx"}:
        raise ValueError("quarter-mass requires at least one admitted route: tuna or qx; Ascella does not cover it")
    # Perceval creates shared local data directories during import. Complete
    # that initialization before spawned workers can race on directory creation.
    if "ascella" in routes:
        importlib.import_module("perceval")
    rows = [row for family in families for row in settings(family)]
    files = {}
    for group in ordered_map(_build_setting, [(row, budgets, routes) for row in rows], min_items=1):
        files.update(group)
    cases = []
    acquisition_schedule = []
    interval_families: dict[str, dict[str, Any]] = {}
    for name, text in sorted(files.items()):
        if name.endswith("/cases.json"):
            route, family, setting, _ = name.split("/")
            manifest = json.loads(text)
            science = manifest["settings"][0] if route == "ascella" else manifest["circuits"][0]
            if family == "sedenion-lcu":
                acquisition_schedule.append(
                    {
                        "path": str(Path(name).parent),
                        "backend": route,
                        "order": science["acquisition_order"],
                        "contrast_weight": science["contrast_weight"],
                        "repeat_of": science.get("repeat_of"),
                    }
                )
            family_key = f"{route}:{family}"
            interval_family = interval_families.setdefault(
                family_key, {"backend": route, "family": family, "endpoint_count": 0, "settings": 0}
            )
            interval_family["endpoint_count"] += len(science["logical_output_labels"]) + bool(
                science["success_outputs"]
            )
            interval_family["settings"] += 1
            cases.append(
                {
                    "path": str(Path(name).parent),
                    "provider": "qd" if route == "ascella" else "qi",
                    "backend": route,
                    "family": family,
                    "setting": setting,
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                }
            )
    index = {
        "schema": "quantum-experiment-campaign-v1",
        "families": list(families),
        "routes": list(routes),
        "budgets": asdict(budgets),
        "cases": cases,
        "acquisition_status": "unsubmitted",
        "interval_families": interval_families,
        "acquisition_schedule": sorted(acquisition_schedule, key=lambda row: (row["backend"], row["order"])),
        "contrast_admission": (
            "requires retained execution order, per-batch readout and matching optical computed meshes"
        ),
        "scope": "MUB overlaps, quarter-mass amplification and certified sedenion support restrictions",
    }
    files["campaign.json"] = json.dumps(index, indent=1) + "\n"
    files["reference.json"] = json.dumps(reference_report(), indent=1, sort_keys=True) + "\n"
    if "ascella" in routes:
        allocations = [
            {**{key: value for key, value in row.items() if key != "seed"}, "value": row["seed"]}
            for row in optical_seeds()
            if row["family"] in families
        ]
        files["seeds.json"] = (
            json.dumps({"schema": "quantum-experiment-seeds-v1", "allocations": allocations}, indent=1) + "\n"
        )
    inputs = (
        "scripts/experiment_cases.py",
        "scripts/hypercomplex_cases.py",
        "scripts/qd_platform.py",
        "scripts/qi_zero_divisor_cases.py",
        "gororoba_quantum/experiment_references.py",
        "gororoba_quantum/cd_core.py",
        "gororoba_quantum/dimension_six_circuits.py",
        "gororoba_quantum/operator_arithmetic.py",
        "docs/evidence/quantum_inspire/catalogue.json",
        "docs/evidence/quandela/catalogue.json",
        SEED_DRAW,
        SEED_MAPPING,
    )
    files["provenance.json"] = (
        json.dumps(
            {
                "schema": "quantum-experiment-provenance-v1",
                "sources": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in inputs},
                "versions": {
                    "python": platform.python_version(),
                    **{
                        name: importlib.metadata.version(name)
                        for name in ("numpy", "scipy", "qiskit", "perceval-quandela", "sympy", "mpmath")
                    },
                },
                "artifacts": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in sorted(files.items())},
                "execution": "deterministic full-operator reconstruction; no sampled outcomes or provider execution",
            },
            indent=1,
            sort_keys=True,
        )
        + "\n"
    )
    return files


def _check_inventory(directory: Path, files: dict[str, str]) -> None:
    actual = {path.relative_to(directory).as_posix() for path in directory.rglob("*") if path.is_file()}
    if actual != set(files):
        raise ValueError("campaign file inventory differs from the regenerated case set")


def replay_receipt(directory: Path, files: dict[str, str]) -> bytes:
    """Bind historical provenance to a full byte-identical regeneration by the executing producer.

    The original producer's provenance remains historical. Every other file
    must agree with both its historical digest and the newly generated bytes.
    The companion receipt names the current sources, runtime and arguments.
    """
    _check_inventory(directory, files)
    historical_bytes = (directory / "provenance.json").read_bytes()
    historical = json.loads(historical_bytes)
    current = json.loads(files["provenance.json"])
    if historical.get("schema") != "quantum-experiment-provenance-v1":
        raise ValueError("historical provenance schema differs")
    artifacts = {
        name: hashlib.sha256(text.encode()).hexdigest() for name, text in files.items() if name != "provenance.json"
    }
    if historical.get("artifacts") != artifacts or current.get("artifacts") != artifacts:
        changed = [name for name, value in artifacts.items() if historical.get("artifacts", {}).get(name) != value]
        details = []
        for name in changed[:4]:
            details.extend(
                list(
                    difflib.unified_diff(
                        (directory / name).read_text().splitlines(),
                        files[name].splitlines(),
                        fromfile=name,
                        tofile="regenerated",
                    )
                )[:16]
            )
        raise ValueError(
            f"historical artifact digests differ from the complete regenerated inventory: {len(changed)} files; "
            f"libc={platform.libc_ver()}; python={platform.python_version()}\n" + "\n".join(details)
        )
    for name, text in files.items():
        if name != "provenance.json" and (directory / name).read_bytes() != text.encode():
            raise ValueError(f"campaign bytes differ: {name}")
    campaign = json.loads(files["campaign.json"])
    receipt = {
        "schema": "quantum-experiment-regeneration-receipt-v1",
        "historical_provenance_sha256": hashlib.sha256(historical_bytes).hexdigest(),
        "current_provenance": current,
        "generation": {key: campaign[key] for key in ("budgets", "families", "routes")},
        "result": "every non-provenance artifact regenerates byte-identically; historical producer provenance retained",
    }
    return (json.dumps(receipt, indent=1, sort_keys=True) + "\n").encode()


def attest_existing(directory: Path, files: dict[str, str], receipt_path: Path) -> None:
    """Publish a companion receipt exclusively, preserving every byte in the historical bundle."""
    if receipt_path.resolve().is_relative_to(directory.resolve()):
        raise ValueError("a replay receipt must live outside the historical bundle")
    receipt = replay_receipt(directory, files)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with receipt_path.open("xb") as stream:
            stream.write(receipt)
    except FileExistsError:
        if receipt_path.read_bytes() != receipt:
            raise ValueError("existing replay receipt differs; choose a new receipt path") from None


def check(directory: Path, files: dict[str, str], receipt_path: Path | None = None) -> None:
    if receipt_path is not None:
        if receipt_path.read_bytes() != replay_receipt(directory, files):
            raise ValueError(
                "replay receipt differs from historical provenance or current sources, runtime or arguments"
            )
        return
    _check_inventory(directory, files)
    changed = [name for name, text in files.items() if (directory / name).read_bytes() != text.encode()]
    if changed:
        first = changed[0]
        details = list(
            difflib.unified_diff(
                (directory / first).read_text().splitlines(),
                files[first].splitlines(),
                fromfile=first,
                tofile="regenerated",
            )
        )[:24]
        raise ValueError(
            f"campaign bytes differ: {first}\n"
            + "\n".join(details)
            + f"\nComplete mismatch inventory ({len(changed)} files): {changed}"
        )


def self_test() -> None:
    if len(settings("mub-six")) != 54:
        raise ValueError("three bases require all 54 ordered input/measurement settings")
    for row in settings("sedenion-lcu"):
        full = np.abs(row["matrix"][:, 0]) ** 2
        restricted = np.abs(row["optical_matrix"][:, 0]) ** 2
        if not np.allclose(full[row["support_isometry"]["output_indices"]], restricted, atol=1e-12):
            raise ValueError("photonic restriction differs from the full five-qubit witness")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--out", type=Path)
    action.add_argument("--check", type=Path)
    action.add_argument("--attest-existing", type=Path)
    action.add_argument("--self-test", action="store_true")
    parser.add_argument("--replay-receipt", type=Path)
    parser.add_argument("--families", nargs="+", choices=FAMILIES, default=list(FAMILIES))
    parser.add_argument("--routes", nargs="+", choices=("tuna", "qx", "ascella"), default=["tuna", "qx", "ascella"])
    parser.add_argument("--tuna-shots", type=int)
    parser.add_argument("--qx-shots", type=int)
    parser.add_argument("--photonic-samples", type=int)
    parser.add_argument("--photonic-shots", type=int)
    parser.add_argument("--execution-seconds", type=float)
    parser.add_argument("--photonic-credits", type=float)
    args = parser.parse_args()
    if args.attest_existing and args.replay_receipt is None:
        parser.error("--attest-existing requires --replay-receipt OUTSIDE_BUNDLE")
    if args.replay_receipt is not None and not (args.attest_existing or args.check):
        parser.error("--replay-receipt accompanies only --check or --attest-existing")
    if args.self_test:
        self_test()
        print("experiment case references pass")
        return 0
    values = [getattr(args, name) for name in Budgets.__dataclass_fields__]
    if any(value is None for value in values):
        parser.error("generation/check requires every explicit shot, sample, execution and credit ceiling")
    files = build(Budgets(*values), tuple(args.families), tuple(args.routes))
    if args.check:
        check(args.check, files, args.replay_receipt)
    elif args.attest_existing:
        attest_existing(args.attest_existing, files, args.replay_receipt)
    else:
        write_files(args.out, files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
