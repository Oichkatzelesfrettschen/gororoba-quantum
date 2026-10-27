"""Admit campaign cQASM with local libqasm/OpenSquirrel and preserve its control sequences.

The receipt binds the campaign, every Quantum Inspire manifest and payload,
compiler configurations and the producing sources. Compilation is local and
records no provider execution or sampled outcomes. A host without the pinned
QI stack can check the retained digest chain; a live stack repeats compilation
and requires byte-identical receipts.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import re
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Any

from qi_toolchain_check import compile_circuit, compiler_configs, config_digest, differences, digest, sequences

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import qi_stack  # noqa: E402
from parallel import ordered_map  # noqa: E402

SCHEMA = "quantum-experiment-toolchain-v1"
SOURCE_FILES = (
    "scripts/experiment_toolchain.py",
    "scripts/qi_toolchain_check.py",
    "gororoba_quantum/qi_stack.py",
    "gororoba_quantum/parallel.py",
    "docs/notes/quantum_inspire/requirements-qi.txt",
    "docs/evidence/quantum_inspire/catalogue.json",
)


def _within(path: Path, boundary: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(boundary.resolve()):
        raise ValueError(f"{label} escapes its declared directory")
    return resolved


def inventory(campaign_path: Path) -> tuple[dict[str, Any], dict[str, tuple[str, str]]]:
    """Admit the complete campaign-to-manifest-to-payload digest chain inside this checkout."""
    campaign_path = _within(campaign_path, ROOT, "campaign")
    campaign_bytes = campaign_path.read_bytes()
    campaign = json.loads(campaign_bytes)
    if campaign.get("schema") != "quantum-experiment-campaign-v1" or not isinstance(campaign.get("cases"), list):
        raise ValueError("campaign schema or case inventory differs")
    boundary = campaign_path.parent
    manifests: dict[str, str] = {}
    payloads: dict[str, tuple[str, str]] = {}
    seen_directories: set[Path] = set()
    for entry in campaign["cases"]:
        if entry.get("provider") not in {"qi", "qd"}:
            raise ValueError("campaign case needs an admitted provider")
        if entry["provider"] != "qi":
            continue
        if not isinstance(entry.get("path"), str) or Path(entry["path"]).is_absolute():
            raise ValueError("campaign case path must be relative")
        directory = _within(boundary / entry["path"], boundary, "case")
        if directory in seen_directories:
            raise ValueError("campaign names a Quantum Inspire case twice")
        seen_directories.add(directory)
        manifest_path = _within(directory / "cases.json", directory, "manifest")
        manifest_bytes = manifest_path.read_bytes()
        if digest(manifest_bytes) != entry.get("sha256"):
            raise ValueError(f"case manifest digest differs: {entry['path']}")
        manifest = json.loads(manifest_bytes)
        backend = manifest.get("backend")
        expected = {"tuna": ("tuna_17", 7), "qx": ("QXsinglenodesimulator", 1)}.get(entry.get("backend"))
        if expected is None or (backend, manifest.get("backend_type_id")) != expected:
            raise ValueError("case backend differs from its campaign route")
        rows = manifest.get("circuits")
        if not isinstance(rows, list) or not rows:
            raise ValueError("Quantum Inspire case needs a nonempty circuit inventory")
        manifests[manifest_path.relative_to(ROOT).as_posix()] = digest(manifest_bytes)
        for row in rows:
            filename = row.get("file")
            if not isinstance(filename, str) or Path(filename).is_absolute() or Path(filename).suffix != ".cq":
                raise ValueError("circuit filename must name a relative cQASM payload")
            path = _within(directory / filename, directory, "circuit")
            relative = path.relative_to(ROOT).as_posix()
            if relative in payloads:
                raise ValueError(f"case inventory names a circuit twice: {relative}")
            actual = digest(path.read_bytes())
            if actual != row.get("sha256"):
                raise ValueError(f"circuit digest differs: {relative}")
            payloads[relative] = (actual, backend)
    if not payloads:
        raise ValueError("campaign contains no Quantum Inspire circuit")
    found = {_within(path, boundary, "circuit").relative_to(ROOT).as_posix() for path in boundary.rglob("*.cq")}
    if found != set(payloads):
        raise ValueError("campaign cQASM inventory contains unlisted or missing payloads")
    header = {
        "schema": SCHEMA,
        "campaign": {"path": campaign_path.relative_to(ROOT).as_posix(), "sha256": digest(campaign_bytes)},
        "manifests": dict(sorted(manifests.items())),
        "sources": {name: digest((ROOT / name).read_bytes()) for name in SOURCE_FILES},
        "boundary": (
            "local parse and compile; control order preserved; platform scheduling and hardware execution unobserved"
        ),
    }
    return header, dict(sorted(payloads.items()))


def compile_row(arguments: tuple[str, str, str, dict[str, Any]]) -> dict[str, Any]:
    """One independent parse/compile with the documented narrow SWIG-wrapper warning exclusion."""
    warnings.filterwarnings("ignore", r"builtin type \w+ has no __module__ attribute", DeprecationWarning)
    path, sha256, backend, config = arguments
    payload = (ROOT / path).read_bytes()
    if digest(payload) != sha256:
        raise ValueError(f"circuit bytes changed before compilation: {path}")
    text = payload.decode("utf-8")
    import cqasm.v3x as v3

    analysis = json.loads(v3.Analyzer().analyze_string_to_json(text), strict=False)
    errors = [error["message"] for error in analysis.get("errors", [])]
    row: dict[str, Any] = {
        "case": path,
        "sha256": sha256,
        "backend": backend,
        "compiler_config_sha256": config_digest(config),
        "passes": [step["path"] for stage in config.values() for step in stage],
        "libqasm": "ok" if not errors else errors,
    }
    try:
        compiled = compile_circuit(text, config)
        source_control, source_gates = sequences(text)
        compiled_control, compiled_gates = sequences(compiled)
        control_changes = differences(source_control, compiled_control)
        gate_changes = differences(source_gates, compiled_gates)
        row.update(
            compiled="ok",
            compiled_sha256=digest(compiled.encode()),
            control_sequence_preserved=not control_changes,
            gate_sequence_preserved=not gate_changes,
            control_changes=control_changes,
            gate_changes=gate_changes,
        )
    except Exception as error:
        row["compiled"] = f"error: {type(error).__name__}: {error}"
    return row


def _admitted(row: dict[str, Any]) -> bool:
    return (
        row.get("libqasm") == "ok"
        and row.get("compiled") == "ok"
        and row.get("control_sequence_preserved") is True
        and row.get("control_changes") == {}
        and isinstance(row.get("compiled_sha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", row["compiled_sha256"]) is not None
    )


def generate(campaign_path: Path, out: Path) -> int:
    header, payloads = inventory(campaign_path)
    configs = compiler_configs()
    absent = {backend for _, backend in payloads.values()} - configs.keys()
    if absent:
        raise ValueError(f"retained compiler configuration missing for {sorted(absent)}")
    rows = ordered_map(
        compile_row,
        [(path, sha256, backend, configs[backend]) for path, (sha256, backend) in payloads.items()],
        min_items=1,
    )
    current_header, current_payloads = inventory(campaign_path)
    if current_header != header or current_payloads != payloads:
        raise ValueError("compiler inputs changed during compilation")
    toolchain = {"python": ".".join(map(str, sys.version_info[:3]))}
    toolchain.update({name: importlib.metadata.version(name) for name in ("libqasm", "opensquirrel")})
    record = {**header, "toolchain": toolchain, "circuits": rows}
    out.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(record, indent=1, sort_keys=True) + "\n").encode()
    try:
        with out.open("xb") as stream:
            stream.write(data)
    except FileExistsError:
        if out.read_bytes() != data:
            raise ValueError("toolchain receipt differs; choose a new output path") from None
    failed = sum(not _admitted(row) for row in rows)
    print(f"campaign toolchain: {len(rows)} payloads, {failed} failed parse/compile/control admissions -> {out}")
    return int(failed > 0)


def check(campaign_path: Path, out: Path) -> int:
    expected, payloads = inventory(campaign_path)
    record = json.loads(out.read_bytes())
    for name, value in expected.items():
        if record.get(name) != value:
            raise ValueError(f"toolchain receipt differs in {name}")
    configs = compiler_configs()
    rows = record.get("circuits")
    if not isinstance(rows, list):
        raise ValueError("toolchain receipt needs its circuit rows")
    recorded: dict[str, tuple[str, str]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("case"), str) or row["case"] in recorded:
            raise ValueError("toolchain receipt has malformed or duplicate circuit rows")
        if not _admitted(row):
            raise ValueError(f"toolchain parse/compile/control admission failed: {row['case']}")
        backend = row.get("backend")
        sha256 = row.get("sha256")
        if not isinstance(backend, str) or not isinstance(sha256, str):
            raise ValueError("toolchain source digest or backend mapping is malformed")
        if backend not in configs or row.get("compiler_config_sha256") != config_digest(configs[backend]):
            raise ValueError("toolchain compiler configuration differs")
        recorded[row["case"]] = (sha256, backend)
    if recorded != payloads:
        raise ValueError("toolchain circuit inventory, source bytes or backend mapping differs")
    toolchain = record.get("toolchain", {})
    pins = qi_stack.pins()
    if (
        not isinstance(toolchain, dict)
        or not isinstance(toolchain.get("python"), str)
        or any(toolchain.get(name) != pins[name] for name in ("libqasm", "opensquirrel"))
    ):
        raise ValueError("toolchain receipt versions differ from the pinned stack")
    print(f"campaign toolchain receipt: {len(rows)} payloads match with control preservation")
    if qi_stack.live("campaign libqasm and OpenSquirrel", "validated retained compilation without recompiling"):
        with tempfile.TemporaryDirectory(prefix="experiment-toolchain-") as temporary:
            fresh = Path(temporary) / out.name
            qi_stack.run(
                [
                    "-B",
                    "-W",
                    "error",
                    str(Path(__file__).resolve()),
                    "--campaign",
                    str(campaign_path.resolve()),
                    "--out",
                    str(fresh),
                ]
            )
            if fresh.read_bytes() != out.read_bytes():
                raise ValueError("live campaign toolchain replay differs from the retained receipt")
        print("campaign toolchain live replay matches byte for byte")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return check(args.campaign, args.out) if args.check else generate(args.campaign, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
