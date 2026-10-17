"""Parse, analyze and compile every retained Quantum Inspire case circuit with the platform's own toolchain.

Every .cq under results/quantum_inspire/cases belongs to a batch manifest
(cases.json with a circuit list) that names its backend. Under $QI_PYTHON
(the Quantum Inspire environment, docs/notes/quantum_inspire/setup.md, with
libqasm 1.2.1 and opensquirrel 0.9.1) the script

- analyzes each circuit with libqasm's cQASM 3.0 analyzer, a fresh analyzer
  per circuit since one analyzer keeps the declarations it has seen;
- compiles it with OpenSquirrel through the backend type's
  default_compiler_config from docs/evidence/quantum_inspire/catalogue.json,
  the passes the platform applies for that backend (Tuna: SWAP2CZDecomposer
  then CZDecomposer; QX: none);
- compares, per qubit, the source's and the compiled circuit's sequence of
  waits, barriers and measurements (with each measurement's bit) and of
  gates, and records every difference;

and writes docs/evidence/quantum_inspire/toolchain_check.json. A libqasm
error or a failed compilation fails the run after the record is written; a
changed sequence is reported.

Scheduling: OpenSquirrel 0.9.1 schedules only in QuantifySchedulerExporter
(opensquirrel/passes/exporter/quantify_scheduler_exporter.py). Its
_Scheduler visits the circuit in reverse and ties each operation's end to the
start of the next operation on its qubits; wait(n) adds n cycles of 20 ns and
a run of consecutive barriers aligns its qubits to the latest of them, which
places every operation as late as possible. Every operation lasts one cycle
unless the exporter's operation_cycles assigns it more, so the 800 ns
measurement the Tuna page states needs that table. default_compiler_config
holds decomposition passes only, so the ALAP schedule is built after the
passes this record runs, by the exporter in the platform's control stack;
quantify-scheduler is absent from the Quantum Inspire environment, so the
exporter does not run here and the record states only that it is importable.

--out FILE writes the record to FILE in place of the retained path.

--check runs on the standard library alone: the record must name exactly
the current case files with their current sha256, and every circuit must
have analyzed and compiled, so a regenerated case without a rerun fails.
When qi_stack.live finds the pinned stack under $QI_PYTHON, --check also
regenerates the record into a temporary file and requires its bytes to equal
the retained record's; libqasm's analysis and OpenSquirrel's passes are
deterministic, so any difference is a changed toolchain or a stale record.
Without the stack it prints the replay line and checks the record alone.

Usage: "$QI_PYTHON" scripts/qi_toolchain_check.py [--out FILE]
       "$PYTHON" scripts/qi_toolchain_check.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import qi_stack  # noqa: E402

CASES = ROOT / "results/quantum_inspire/cases"
CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
RECORD = ROOT / "docs/evidence/quantum_inspire/toolchain_check.json"
SCHEMA = "qi-toolchain-check-v1"
EXPORTER = "opensquirrel/passes/exporter/quantify_scheduler_exporter.py"
CONTROL = ("wait", "barrier", "measure")
Sequence = dict[int, list[list[Any]]]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def case_files() -> dict[str, tuple[str, str]]:
    """Repository path of every listed .cq -> (its sha256, its manifest's backend identifier)."""
    out = {}
    for manifest in sorted(CASES.rglob("cases.json")):
        cases = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(cases.get("circuits"), list):
            continue
        for row in cases["circuits"]:
            path = manifest.parent / row["file"]
            out[path.relative_to(ROOT).as_posix()] = (digest(path.read_bytes()), cases["backend"])
    unlisted = sorted(p.relative_to(ROOT).as_posix() for p in CASES.rglob("*.cq"))
    missing = [p for p in unlisted if p not in out]
    if missing:
        raise SystemExit(f"{len(missing)} circuits belong to no batch manifest, first {missing[0]}")
    return out


def indices(spec: str | None, size: int) -> list[int]:
    """Register indices of an operand: the whole register, i, i:j (inclusive) or a comma list of those."""
    if spec is None:
        return list(range(size))
    out: list[int] = []
    for part in spec.split(","):
        low, _, high = part.strip().partition(":")
        out += list(range(int(low), int(high or low) + 1))
    return out


def sequences(text: str) -> tuple[Sequence, Sequence]:
    """Per-qubit control sequence ([kind, argument]) and gate-name sequence of a cQASM 3.0 program."""
    qubit_name, size, bit_name, bits = "q", 0, "b", 0
    control: Sequence = {}
    gates: Sequence = {}
    for raw in text.splitlines():
        line = raw.split("//")[0].strip()
        if not line or line.startswith("version"):
            continue
        if match := re.fullmatch(r"qubit\[(\d+)\]\s+(\w+)", line):
            size, qubit_name = int(match[1]), match[2]
            control = {q: [] for q in range(size)}
            gates = {q: [] for q in range(size)}
            continue
        if match := re.fullmatch(r"bit\[(\d+)\]\s+(\w+)", line):
            bits, bit_name = int(match[1]), match[2]
            continue
        operand = re.compile(rf"\b{qubit_name}(?:\[([^\]]*)\])?")
        if match := re.fullmatch(rf"{bit_name}(?:\[([^\]]*)\])?\s*=\s*measure\w*(?:\([^)]*\))?\s+(.+)", line):
            targets = [q for m in operand.finditer(match[2]) for q in indices(m[1], size)]
            for bit, q in zip(indices(match[1], bits), targets, strict=True):
                control[q].append(["measure", bit])
            continue
        name, _, rest = line.partition(" ")
        targets = [q for m in operand.finditer(rest) for q in indices(m[1], size)]
        for q in targets:
            if name == "barrier":
                control[q].append(["barrier", None])
            elif name.startswith("wait("):
                control[q].append(["wait", int(name[5:-1])])
            else:
                gates[q].append([name])
    return control, gates


def differences(source: Sequence, compiled: Sequence) -> dict[str, dict[str, Any]]:
    return {
        str(q): {"source": source[q], "compiled": compiled.get(q)}
        for q in sorted(source)
        if source[q] != compiled.get(q)
    }


def compiler_configs() -> dict[str, dict[str, Any]]:
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    return {b["identifier"]: b["default_compiler_config"] for b in catalogue["backend_types"]}


def config_digest(config: dict[str, Any]) -> str:
    """sha256 of a backend's default_compiler_config in canonical JSON, the passes compile_circuit applies."""
    return digest(json.dumps(config, sort_keys=True, separators=(",", ":")).encode())


def compile_circuit(text: str, config: dict[str, Any]) -> str:
    from opensquirrel import Circuit

    circuit = Circuit.from_string(text)
    for stage in ("decomposition", "mapping", "optimization", "routing"):
        for step in config.get(stage, []):
            module, _, name = step["path"].rpartition(".")
            instance = getattr(importlib.import_module(module), name)(**step.get("arguments", {}))
            method = {"decompose": "decompose", "map": "map", "merge": "merge", "route": "route"}[step["method"]]
            getattr(circuit, method)(instance)
    return str(circuit)


def generate(out: Path = RECORD) -> int:
    from importlib.metadata import version

    # libqasm 1.2.1's SWIG module warns at import that its builtin types lack
    # __module__; under -W error that warning is raised inside the extension's
    # module initialization and the interpreter segfaults.
    warnings.filterwarnings("ignore", r"builtin type \w+ has no __module__ attribute", DeprecationWarning)
    import cqasm.v3x as v3

    configs = compiler_configs()
    rows = []
    failures = 0
    for path, (sha, backend) in case_files().items():
        text = (ROOT / path).read_text(encoding="utf-8")
        analysis = json.loads(v3.Analyzer().analyze_string_to_json(text), strict=False)
        errors = [e["message"] for e in analysis.get("errors", [])]
        row: dict[str, Any] = {
            "case": path,
            "sha256": sha,
            "backend": backend,
            "compiler_config_sha256": config_digest(configs[backend]),
            "passes": [step["path"] for stage in configs[backend].values() for step in stage],
            "libqasm": "ok" if not errors else errors,
        }
        try:
            compiled = compile_circuit(text, configs[backend])
        except Exception as error:  # OpenSquirrel raises its own and builtin exceptions for a rejected circuit
            row["compiled"] = f"error: {type(error).__name__}: {error}"
            failures += 1
            rows.append(row)
            continue
        source_control, source_gates = sequences(text)
        compiled_control, compiled_gates = sequences(compiled)
        control_changes = differences(source_control, compiled_control)
        gate_changes = differences(source_gates, compiled_gates)
        row |= {
            "compiled": "ok",
            "compiled_sha256": digest(compiled.encode()),
            "control_sequence_preserved": not control_changes,
            "gate_sequence_preserved": not gate_changes,
            "control_changes": control_changes,
            "gate_changes": gate_changes,
        }
        failures += bool(errors)
        rows.append(row)
    import opensquirrel

    exporter = Path(opensquirrel.__file__).parent.parent / EXPORTER
    try:
        importlib.import_module("quantify_scheduler")
        quantify = True
    except ModuleNotFoundError:
        quantify = False
    record = {
        "schema": SCHEMA,
        "toolchain": {
            "python": ".".join(map(str, sys.version_info[:3])),
            "libqasm": version("libqasm"),
            "opensquirrel": version("opensquirrel"),
        },
        "scheduling": {
            "pass": "opensquirrel.passes.exporter.QuantifySchedulerExporter",
            "source": EXPORTER,
            "source_sha256": digest(exporter.read_bytes()),
            "in_default_compiler_config": any(
                "Exporter" in step["path"] for config in configs.values() for stage in config.values() for step in stage
            ),
            "quantify_scheduler_installed": quantify,
        },
        "circuits": rows,
    }
    out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    changed = sum(not r.get("gate_sequence_preserved", True) for r in rows)
    print(
        f"qi toolchain: {len(rows)} circuits, {failures} failing, {changed} with a compiled gate sequence change "
        f"-> {out}"
    )
    return 1 if failures else 0


def check() -> int:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if record.get("schema") != SCHEMA:
        raise SystemExit(f"{RECORD.relative_to(ROOT)}: schema differs")
    # A circuit's compilation evidence holds while its bytes, its manifest's backend and that
    # backend's default_compiler_config all match the record.
    configs = {name: config_digest(config) for name, config in compiler_configs().items()}
    current = {path: (sha, backend, configs.get(backend)) for path, (sha, backend) in case_files().items()}
    recorded = {
        row["case"]: (row["sha256"], row["backend"], row.get("compiler_config_sha256")) for row in record["circuits"]
    }
    if len(recorded) != len(record["circuits"]):
        raise SystemExit("the record names a circuit twice")
    stale = sorted(p for p in current.keys() | recorded.keys() if current.get(p) != recorded.get(p))
    if stale:
        raise SystemExit(
            f"{len(stale)} circuits differ from the record in bytes, backend or compiler configuration, "
            f"first {stale[0]}; rerun under $QI_PYTHON"
        )
    bad = [row["case"] for row in record["circuits"] if row["libqasm"] != "ok" or row["compiled"] != "ok"]
    if bad:
        raise SystemExit(f"{len(bad)} circuits failed analysis or compilation, first {bad[0]}")
    print(f"qi toolchain record: {len(current)} circuits match their bytes, backends and compiler configurations")
    if qi_stack.live("libqasm and OpenSquirrel", "checked the retained record without recompiling"):
        regenerate()
    return 0


def regenerate() -> None:
    """The record rebuilt under $QI_PYTHON into temporary storage must equal the retained bytes."""
    with tempfile.TemporaryDirectory(prefix="qi-toolchain-") as temporary:
        fresh = Path(temporary) / RECORD.name
        qi_stack.run(["-B", "-W", "error", str(Path(__file__).resolve()), "--out", str(fresh)])
        retained, rebuilt = RECORD.read_bytes(), fresh.read_bytes()
    if rebuilt != retained:
        old, new = json.loads(retained), json.loads(rebuilt)
        changed = [row["case"] for row, again in zip(old["circuits"], new["circuits"], strict=True) if row != again]
        detail = f"first changed circuit {changed[0]}" if changed else f"toolchain {new['toolchain']}"
        raise SystemExit(f"{RECORD.relative_to(ROOT)} differs from the record regenerated under $QI_PYTHON: {detail}")
    print(f"qi toolchain live: the record regenerated under $QI_PYTHON equals {RECORD.relative_to(ROOT)} byte for byte")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="compare the record with the cases; recompile when live")
    parser.add_argument("--out", type=Path, default=RECORD, help="where the regenerated record goes")
    args = parser.parse_args()
    return check() if args.check else generate(args.out)


if __name__ == "__main__":
    sys.exit(main())
