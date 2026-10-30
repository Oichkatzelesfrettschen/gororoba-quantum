"""Prepare unapproved Tuna classical-destination invariance controls with local compiler evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

from qi_projector_compiler_admission import normalized_instructions
from qi_toolchain_check import compile_circuit, config_digest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

BASELINE = ROOT / "results/quantum_inspire/proposals/tuna-projector-geometry/tuna-qualification"
OBSERVATION = ROOT / "docs/evidence/tuna-projector-geometry/backend-observation.json"
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna-readout-destination-invariance"
BASELINE_HASHES = {
    "readout-zero.cq": "3ab15a468b5eaa4811a2a06f297754269976f6901dde12370cf3d5fad593f267",
    "readout-one.cq": "33e344c4b6357d7f4d3ad26e37686614731d5d2c7bf41eb1960abc925f18a44f",
}
DESTINATIONS = {17: 19, 18: 17, 19: 18}


def sha(content: str | bytes) -> str:
    return hashlib.sha256(content.encode() if isinstance(content, str) else content).hexdigest()


def encoded(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def physical_stream(source: str) -> dict[str, Any]:
    normalized = normalized_instructions(source)
    normalized["instructions"] = [
        [name, qubits, None if name == "measure" else parameter]
        for name, qubits, parameter in normalized["instructions"]
    ]
    return normalized


def measurement_map(source: str) -> list[dict[str, int]]:
    return [
        {"qubit": targets[0], "classical_bit": destination}
        for name, targets, destination in normalized_instructions(source)["instructions"]
        if name == "measure"
    ]


def rotate_destinations(source: str) -> str:
    changed, count = re.subn(
        r"b\[(17|18|19)\] = measure q\[(4|11|6)\]",
        lambda match: f"b[{DESTINATIONS[int(match[1])]}] = measure q[{match[2]}]",
        source,
    )
    if count != 3 or physical_stream(source) != physical_stream(changed):
        raise ValueError("rotation must alter exactly three destinations and preserve physical instructions")
    return changed


def build() -> dict[str, str]:
    files: dict[str, str] = {}
    observation_bytes = OBSERVATION.read_bytes()
    observation = json.loads(observation_bytes)
    if observation["id"] != 7 or observation["identifier"] != "tuna_17":
        raise ValueError("frozen backend identity differs")
    for filename, expected_hash in BASELINE_HASHES.items():
        source_bytes = (BASELINE / filename).read_bytes()
        if sha(source_bytes) != expected_hash:
            raise ValueError("baseline control source hash differs")
        source = source_bytes.decode()
        prepared = 0 if filename == "readout-zero.cq" else 1
        batch = f"prepared-{'zero' if prepared == 0 else 'one'}"
        entries = []
        for name, content, early_bits in (
            ("baseline-before", source, (17, 18, 19)),
            ("rotated-destinations", rotate_destinations(source), (19, 17, 18)),
            ("baseline-after", source, (17, 18, 19)),
        ):
            circuit_file = f"{name}.cq"
            files[f"{batch}/{circuit_file}"] = content
            mapping = measurement_map(content)
            expected = [
                {"qubit": qubit, "classical_bit": bit} for qubit, bit in zip((4, 11, 6), early_bits, strict=True)
            ]
            expected.extend({"qubit": qubit, "classical_bit": qubit} for qubit in range(17))
            if mapping != expected:
                raise ValueError("measurement map differs from the intended early and terminal destinations")
            entries.append(
                {
                    "name": name,
                    "file": circuit_file,
                    "sha256": sha(content),
                    "prepared_label": prepared,
                    "measurement_to_bit_map": mapping,
                    "analysis_metadata": {
                        "width": 20,
                        "bit_order": "classical bit zero is the rightmost character",
                        "index_convention": "zero-based string offsets from the left",
                        "canonical_early_qubit_order": [4, 11, 6],
                        "canonical_early_classical_bits": list(early_bits),
                        "canonical_early_string_offsets": [19 - bit for bit in early_bits],
                        "terminal_classical_bits": list(range(17)),
                        "decoder_rule": "Read qubits through declared destinations; inverse-permute the rotated arm.",
                    },
                    "physical_instruction_stream_sha256": sha(encoded(physical_stream(content))),
                }
            )
        files[f"{batch}/backend.json"] = observation_bytes.decode()
        files[f"{batch}/cases.json"] = encoded(
            {
                "schema": "qi-tuna-readout-destination-case-v1",
                "backend": "tuna_17",
                "backend_type_id": 7,
                "nqubits": 17,
                "shots": 4096,
                "provider_execution_authorized": False,
                "status": "draft-unapproved",
                "statistical_model_status": "power-and-dependence-unqualified",
                "expected_execution_seconds_decimal": "14.844555" if prepared == 0 else "14.688660",
                "provider_execution_ceiling_seconds": 900,
                "prepared_label": prepared,
                "circuits": entries,
                "requested_circuit_order": [entry["file"] for entry in entries],
                "execution_order_boundary": "Verify provider execution order before treating the batch as A-B-A.",
                "backend_snapshot": {"file": "backend.json", "sha256": sha(observation_bytes)},
                "producer": {
                    "file": Path(__file__).relative_to(ROOT).as_posix(),
                    "sha256": sha(Path(__file__).read_bytes()),
                },
                "baseline": {"file": (BASELINE / filename).relative_to(ROOT).as_posix(), "sha256": expected_hash},
                "required_before_submission": [
                    "Fresh backend/compiler admission, limits, pause, queue and zero-credit terms",
                    "Frozen qualified statistical comparison, dependence model, missingness and stopping rules",
                    "Explicit user approval of the exact written case and circuit manifest",
                ],
                "limits": {"circuits_per_batch": 3, "account_queued_batches": 1, "job_seconds": 300},
            }
        )
    files["proposal.json"] = encoded(
        {
            "schema": "qi-tuna-readout-destination-proposal-v1",
            "status": "draft-unapproved",
            "provider_execution_authorized": False,
            "batches": ["prepared-zero", "prepared-one"],
            "circuits_total": 6,
            "shots_per_circuit": 4096,
            "shots_total": 24576,
            "expected_execution_seconds_decimal": "29.533215",
            "provider_execution_ceiling_seconds": 1800,
            "statistical_model_status": "power-and-dependence-unqualified",
            "estimate_basis": ("3*(4.948185 s + 4.896220 s), from measured control jobs; excludes queue and pause."),
            "expected_credits": 0,
            "pricing_condition": "Requires fresh zero-credit terms and account check.",
            "timing_assumption": "Equal physical workloads suggest similar duration; the estimate is unguaranteed.",
            "timing_reference": {
                "file": "results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/results.json",
                "sha256": sha(
                    (
                        ROOT / "results/quantum_inspire/runs/2026-10-27T170500Z-projector-geometry-tuna/results.json"
                    ).read_bytes()
                ),
                "prepared_zero_job": 1616329,
                "prepared_one_job": 1616330,
            },
            "scope": "Classical destination invariance with the failing zero-gap physical controls.",
            "boundary": "Instruction equality establishes neither provider schedule equality nor a physical mechanism.",
        }
    )
    return files


def compile_one(task: tuple[str, str, dict[str, Any]]) -> tuple[str, str, dict[str, Any]]:
    filename, source, config = task
    compiled = compile_circuit(source, config)
    normalized = normalized_instructions(source)
    if normalized != normalized_instructions(compiled):
        raise ValueError(f"complete source/compiled instruction streams differ: {filename}")
    return (
        filename,
        compiled,
        {
            "source": filename,
            "source_sha256": sha(source),
            "compiled_sha256": sha(compiled),
            "normalized_instructions": normalized,
            "measurement_to_bit_map": measurement_map(compiled),
            "physical_instruction_stream_sha256": sha(encoded(physical_stream(compiled))),
        },
    )


def generate() -> dict[str, str]:
    import opensquirrel
    from opensquirrel.writer.writer import _WriterImpl

    if _WriterImpl.FLOAT_PRECISION != 8:
        raise ValueError("compiler serializer precision changed")
    files = build()
    config = json.loads(OBSERVATION.read_text())["default_compiler_config"]
    tasks = [(name, source, config) for name, source in files.items() if name.endswith(".cq")]
    compiled = ordered_map(compile_one, tasks, min_items=1)
    package = Path(opensquirrel.__file__).parent
    receipt = {
        "schema": "qi-tuna-destination-compiler-replay-v1",
        "command": '"$QI_PYTHON" scripts/qi_tuna_readout_mapping_cases.py --check',
        "scope": "Local decomposition and cQASM equality; provider scheduling and IQ handling unmeasured.",
        "default_compiler_config": config,
        "compiler_config_sha256": config_digest(config),
        "backend_observation_sha256": sha(OBSERVATION.read_bytes()),
        "versions": {name: version(name) for name in ("opensquirrel", "libqasm", "numpy")},
        "source_sha256": {
            name: sha((ROOT / name).read_bytes())
            for name in (
                "scripts/qi_tuna_readout_mapping_cases.py",
                "scripts/qi_projector_compiler_admission.py",
                "scripts/qi_toolchain_check.py",
                "gororoba_quantum/parallel.py",
            )
        },
        "opensquirrel_python_sources_sha256": {
            path.relative_to(package).as_posix(): sha(path.read_bytes()) for path in sorted(package.rglob("*.py"))
        },
        "circuits": [row for _, _, row in compiled],
    }
    for filename, content, _ in compiled:
        files[f"local-compiled/{filename}"] = content
    files["local-compiler-receipt.json"] = encoded(receipt)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", nargs="?", type=Path, const=PROPOSAL)
    args = parser.parse_args()
    files = generate()
    if args.check:
        retained = {
            path.relative_to(args.check).as_posix(): path.read_text()
            for path in args.check.rglob("*")
            if path.is_file()
        }
        if retained != files:
            raise SystemExit("retained mapping proposal differs from deterministic local compiler replay")
        print(
            "Tuna destination proposal: six circuits and compiler evidence replay exactly; execution remains unapproved"
        )
    else:
        args.out.mkdir(parents=True, exist_ok=False)
        for relative, content in files.items():
            path = args.out / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x") as destination:
                destination.write(content)


if __name__ == "__main__":
    main()
