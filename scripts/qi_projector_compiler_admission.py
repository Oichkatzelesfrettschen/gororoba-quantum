"""Replay proposal compilation and compare the complete ordered instruction stream.

The comparison expands register operations and rounds rotation arguments through
OpenSquirrel 0.9.1's eight-significant-digit writer convention. It establishes
instruction preservation at that serialization precision, not a physical schedule.
Run with the Quantum Inspire interpreter; --check recompiles all six circuits.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

from qi_toolchain_check import compile_circuit, config_digest, digest, indices

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna-projector-geometry"
RECEIPT = PROPOSAL / "compiler-admission.json"
OBSERVATIONS = {
    "tuna-qualification": ROOT / "docs/evidence/tuna-projector-geometry/backend-observation.json",
    "qx-terminal": ROOT / "docs/evidence/tuna-projector-geometry/qx-backend-observation.json",
}


def normalized_instructions(source: str) -> dict[str, Any]:
    """Parse the proposal's closed instruction grammar; reject unrecognized syntax."""
    qubits = bits = 0
    instructions: list[list[Any]] = []
    version_seen = False
    for raw in source.splitlines():
        line = raw.split("//", 1)[0].strip()
        if not line:
            continue
        if line == "version 3.0" and not version_seen:
            version_seen = True
            continue
        if match := re.fullmatch(r"qubit\[(\d+)\] q", line):
            if qubits or instructions:
                raise ValueError("duplicate or late qubit declaration")
            qubits = int(match[1])
            continue
        if match := re.fullmatch(r"bit\[(\d+)\] b", line):
            if bits or instructions:
                raise ValueError("duplicate or late bit declaration")
            bits = int(match[1])
            continue
        if not version_seen or not qubits or not bits:
            raise ValueError("missing declarations")
        if match := re.fullmatch(r"b(?:\[([\d,:]+)\])? = measure q(?:\[([\d,:]+)\])?", line):
            targets = indices(match[2], qubits)
            destinations = indices(match[1], bits)
            if any(target >= qubits for target in targets) or any(bit >= bits for bit in destinations):
                raise ValueError("measurement operand out of range")
            for target, bit in zip(targets, destinations, strict=True):
                instructions.append(["measure", [target], bit])
            continue
        if match := re.fullmatch(r"(init|barrier|H|X|Ry)(?:\(([^()]*)\))? q(?:\[([\d,:]+)\])?", line):
            name, parameter, specification = match.groups()
            if (name == "Ry") != (parameter is not None):
                raise ValueError("invalid gate parameter")
            argument = None
            if parameter is not None:
                value = float(parameter)
                if not math.isfinite(value):
                    raise ValueError("nonfinite rotation")
                argument = format(0.0 if value == 0 else value, ".8")
            targets = indices(specification, qubits)
            if any(target >= qubits for target in targets):
                raise ValueError("gate operand out of range")
            for target in targets:
                instructions.append([name, [target], argument])
            continue
        if match := re.fullmatch(r"CZ q\[(\d+)\], q\[(\d+)\]", line):
            targets = [int(match[1]), int(match[2])]
            if max(targets) >= qubits or targets[0] == targets[1]:
                raise ValueError("invalid CZ operands")
            instructions.append(["CZ", targets, None])
            continue
        raise ValueError(f"unrecognized instruction: {line}")
    if not version_seen or not qubits or not bits or not instructions:
        raise ValueError("incomplete circuit")
    return {"qubits": qubits, "bits": bits, "instructions": instructions}


def replay_circuit(task: tuple[str, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    batch, row, config = task
    relative = f"{batch}/{row['file']}"
    source = (PROPOSAL / relative).read_bytes()
    if digest(source) != row["sha256"]:
        raise ValueError(f"manifest digest differs: {relative}")
    compiled_path = PROPOSAL / "local-compiled" / relative
    compiled = compile_circuit(source.decode(), config).encode()
    if compiled != compiled_path.read_bytes():
        raise ValueError(f"compiled bytes differ: {relative}")
    normalized = normalized_instructions(source.decode())
    if normalized != normalized_instructions(compiled.decode()):
        raise ValueError(f"ordered instruction stream differs: {relative}")
    return {
        "source": relative,
        "source_sha256": digest(source),
        "compiled_sha256": digest(compiled),
        "compiler_config_sha256": config_digest(config),
        "normalized_instructions": normalized,
    }


def check_retained(path: Path) -> None:
    """Check retained inputs and full streams without claiming a compiler execution."""
    record = json.loads(path.read_text())
    if record["schema"] != "qi-projector-compiler-admission-v1":
        raise ValueError("compiler admission schema differs")
    if record["producer_sha256"] != digest(Path(__file__).read_bytes()):
        raise ValueError("compiler admission producer differs")
    if record["compiler_driver_sha256"] != digest((ROOT / "scripts/qi_toolchain_check.py").read_bytes()):
        raise ValueError("compiler driver differs")
    expected_sources: list[str] = []
    for batch, observation_path in OBSERVATIONS.items():
        observation = json.loads(observation_path.read_text())
        backend = record["backends"][batch]
        manifest_path = PROPOSAL / batch / "cases.json"
        manifest = json.loads(manifest_path.read_text())
        if backend["observation_sha256"] != digest(observation_path.read_bytes()):
            raise ValueError("backend observation differs")
        if backend["manifest_sha256"] != digest(manifest_path.read_bytes()):
            raise ValueError("manifest differs")
        if backend["default_compiler_config"] != observation["default_compiler_config"]:
            raise ValueError("compiler configuration differs")
        if backend["compiler_config_sha256"] != config_digest(backend["default_compiler_config"]):
            raise ValueError("compiler configuration digest differs")
        expected_sources.extend(f"{batch}/{row['file']}" for row in manifest["circuits"])
    if [row["source"] for row in record["circuits"]] != expected_sources:
        raise ValueError("circuit inventory differs")
    for row in record["circuits"]:
        source = (PROPOSAL / row["source"]).read_bytes()
        compiled = (PROPOSAL / "local-compiled" / row["source"]).read_bytes()
        if row["source_sha256"] != digest(source) or row["compiled_sha256"] != digest(compiled):
            raise ValueError("circuit bytes differ")
        if normalized_instructions(source.decode()) != row["normalized_instructions"]:
            raise ValueError("source instruction stream differs")
        if normalized_instructions(compiled.decode()) != row["normalized_instructions"]:
            raise ValueError("compiled instruction stream differs")


def generate() -> dict[str, Any]:
    import opensquirrel
    from opensquirrel.writer.writer import _WriterImpl

    if _WriterImpl.FLOAT_PRECISION != 8:
        raise ValueError("OpenSquirrel writer precision changed")
    package = Path(opensquirrel.__file__).parent
    package_sources = {
        path.relative_to(package).as_posix(): digest(path.read_bytes()) for path in sorted(package.rglob("*.py"))
    }
    configs: dict[str, Any] = {}
    tasks: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    for batch, observation_path in OBSERVATIONS.items():
        observation = json.loads(observation_path.read_text())
        manifest_path = PROPOSAL / batch / "cases.json"
        manifest = json.loads(manifest_path.read_text())
        if manifest["backend_type_id"] != observation["id"] or manifest["backend"] != observation["identifier"]:
            raise ValueError(f"backend identity differs: {batch}")
        config = observation["default_compiler_config"]
        configs[batch] = {
            "backend_type_id": observation["id"],
            "backend_identifier": observation["identifier"],
            "observation": observation_path.relative_to(ROOT).as_posix(),
            "observation_sha256": digest(observation_path.read_bytes()),
            "manifest_sha256": digest(manifest_path.read_bytes()),
            "default_compiler_config": config,
            "compiler_config_sha256": config_digest(config),
        }
        tasks.extend((batch, row, config) for row in manifest["circuits"])
    return {
        "schema": "qi-projector-compiler-admission-v1",
        "command": '"$QI_PYTHON" scripts/qi_projector_compiler_admission.py --check',
        "scope": "local decomposition and cQASM serialization; hardware scheduling is outside the replay",
        "parameter_comparison": "Python float format .8, matching bound OpenSquirrel writer FLOAT_PRECISION=8",
        "producer_sha256": digest(Path(__file__).read_bytes()),
        "compiler_driver_sha256": digest((ROOT / "scripts/qi_toolchain_check.py").read_bytes()),
        "versions": {name: version(name) for name in ("opensquirrel", "libqasm", "numpy")},
        "opensquirrel_python_sources_sha256": package_sources,
        "backends": configs,
        "circuits": ordered_map(replay_circuit, tasks, min_items=1),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", nargs="?", type=Path, const=RECEIPT)
    mode.add_argument("--check-retained", nargs="?", type=Path, const=RECEIPT)
    args = parser.parse_args()
    if args.check_retained:
        check_retained(args.check_retained)
        print("retained compiler evidence: input hashes and complete instruction streams match; compiler unrun")
        return
    encoded = json.dumps(generate(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.check.read_text() != encoded:
            raise SystemExit("compiler admission receipt differs from live local replay")
        print("compiler admission: all six compiled streams and receipt bytes match")
    else:
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(encoded)


if __name__ == "__main__":
    main()
