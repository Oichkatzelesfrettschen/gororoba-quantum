"""Deterministic sequential-projector circuits and descriptive shot summaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

TRIPLES = ((1, 4, 8), (13, 11, 14), (3, 6, 9))
ANGLES = (0, 45, 90)


def ideal_moments(angle: float, *, mutation: bool = False) -> dict[str, float]:
    """Return unnormalized probabilities for the specified pure input state."""
    radians = math.radians(angle)
    cosine, sine = math.cos(radians), math.sin(radians)
    return {
        "herald": 0.5,
        "z_joint": 0.5 if mutation else (1 + cosine * cosine) / 4,
        "x_signed_joint": 0.0 if mutation else sine * cosine / 2,
    }


def validate_backend(backend: dict[str, Any], triples: tuple[tuple[int, int, int], ...] = TRIPLES) -> None:
    """Validate a normalized snapshot with nqubits, gates and coupling_map fields."""
    width = backend["nqubits"]
    gates = {str(gate).lower() for gate in backend["gates"]}
    if not {"ry", "h", "cz", "x", "measure", "barrier", "wait", "init"} <= gates:
        raise ValueError("backend must support ry, h, cz, x, measure, barrier, wait and init")
    edges = {frozenset(edge) for edge in backend["coupling_map"]}
    flat = [qubit for triple in triples for qubit in triple]
    if len(set(flat)) != len(flat) or any(qubit < 0 or qubit >= width for qubit in flat):
        raise ValueError("physical triples must use distinct in-range qubits")
    if any(frozenset(pair) not in edges for a, c, b in triples for pair in ((a, c), (b, c))):
        raise ValueError("physical triples require supported CZ edges")
    if width < 17:
        raise ValueError("Tuna circuit requires 17 physical qubits")


def circuit(
    *,
    compact: bool = False,
    mode: str = "early",
    endpoint: str = "z",
    mutation: bool = False,
    control: int | None = None,
    wait_cycles: int = 0,
    angles: tuple[int, ...] = ANGLES,
) -> str:
    """Generate cQASM; barriers specify ordering, without asserting physical timing."""
    if mode not in {"early", "simultaneous", "sequential"} or endpoint not in {"z", "x"}:
        raise ValueError("unsupported measurement mode or endpoint")
    if compact and mode != "simultaneous":
        raise ValueError("QX twins support terminal-only measurement")
    if wait_cycles < 0 or not isinstance(wait_cycles, int):
        raise ValueError("wait_cycles must be a nonnegative integer")
    if len(angles) != 3 or any(angle % 5 for angle in angles):
        raise ValueError("three angles on the five-degree grid are required")
    if control not in {None, 0, 1}:
        raise ValueError("control must be zero or one")
    triples = ((0, 1, 2), (3, 4, 5), (6, 7, 8)) if compact else TRIPLES
    width, bits = (9, 9) if compact else (17, 20)
    lines = ["version 3.0", "", f"qubit[{width}] q", f"bit[{bits}] b", "", "init q", ""]
    if control is not None:
        if control:
            lines.extend(f"X q[{qubit}]" for qubit in range(width))
    else:
        for (a, c, b), angle in zip(triples, angles, strict=True):
            lines.extend([f"H q[{b}]", f"Ry({math.radians(-angle):.17g}) q[{a}]", "barrier q"])
            if mutation:
                lines.extend([f"Ry({math.radians(angle):.17g}) q[{a}]", "barrier q"])
            for source in (a, b):
                lines.extend([f"H q[{c}]", f"CZ q[{source}], q[{c}]", f"H q[{c}]"])
            if not mutation:
                lines.append(f"Ry({math.radians(angle):.17g}) q[{a}]")
    lines.append("barrier q")
    if mode == "early":
        lines.extend(f"b[{17 + index}] = measure q[{triple[1]}]" for index, triple in enumerate(triples))
        lines.append("barrier q")
    if wait_cycles:
        lines.extend([f"wait({wait_cycles}) q", "barrier q"])
    if endpoint == "x" and control is None:
        lines.extend(f"H q[{triple[0]}]" for triple in triples)
        lines.append("barrier q")
    if mode == "sequential":
        ancillas = {triple[1] for triple in triples}
        lines.extend(f"b[{qubit}] = measure q[{qubit}]" for qubit in sorted(ancillas))
        lines.append("barrier q")
        lines.extend(f"b[{qubit}] = measure q[{qubit}]" for qubit in range(width) if qubit not in ancillas)
    else:
        lines.append(f"b[0:{width - 1}] = measure q")
    return "\n".join(lines) + "\n"


def shot_metadata(*, compact: bool, endpoint: str = "z") -> dict[str, Any]:
    """Map cQASM bits to string offsets; QX and Tuna return bit zero rightmost."""
    width = 9 if compact else 20
    triples = ((0, 1, 2), (3, 4, 5), (6, 7, 8)) if compact else TRIPLES
    return {
        "width": width,
        "bit_order": "classical bit zero is the rightmost character",
        "index_convention": "zero-based string offsets from the left",
        "source": "docs/notes/quantum_inspire/cqasm.md#bit-and-qubit-order",
        "replicas": [
            {
                "data": width - 1 - a,
                "herald": width - 1 - (c if compact else 17 + index),
                "final_herald": width - 1 - c,
                "endpoint": endpoint,
                "physical_triple_a_c_b": [a, c, b],
                "angle_degrees": ANGLES[index],
            }
            for index, (a, c, b) in enumerate(triples)
        ],
    }


def build_batches(backend: dict[str, Any], *, wait_cycles: int = 0) -> dict[str, str]:
    """Build qualification cases; provider execution remains separately authorized."""
    validate_backend(backend)
    result: dict[str, str] = {}
    batches: dict[str, list[tuple[str, dict[str, Any]]]] = {
        "tuna-qualification": [("readout-zero", {"control": 0}), ("readout-one", {"control": 1}), ("geometry", {})],
        "qx-terminal": [("geometry-z", {}), ("mutation-z", {"mutation": True}), ("geometry-x", {"endpoint": "x"})],
    }
    for batch, specifications in batches.items():
        compact = batch == "qx-terminal"
        entries = []
        for name, options in specifications:
            content = circuit(
                compact=compact, mode="simultaneous" if compact else "early", wait_cycles=wait_cycles, **options
            )
            filename = f"{name}.cq"
            result[f"{batch}/{filename}"] = content
            entries.append(
                {
                    "name": name,
                    "file": filename,
                    "sha256": hashlib.sha256(content.encode()).hexdigest(),
                    "analysis_metadata": shot_metadata(compact=compact, endpoint=options.get("endpoint", "z")),
                    "control": options.get("control"),
                    "mutation": options.get("mutation", False),
                }
            )
        manifest = {
            "backend": backend["qx_identifier"] if compact else backend["identifier"],
            "backend_type_id": backend["qx_backend_type_id"] if compact else backend["id"],
            "nqubits": 9 if compact else 17,
            "shots": 2048 if compact else 4096,
            "provider_execution_authorized": False,
            "producer": {
                "file": "scripts/qi_projector_geometry.py",
                "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            },
            "backend_snapshot": {
                "file": "backend.json",
                "sha256": hashlib.sha256((json.dumps(backend, indent=2, sort_keys=True) + "\n").encode()).hexdigest(),
            },
            "circuits": entries,
            "wait_cycles": wait_cycles,
            "angles_degrees": list(ANGLES),
            "physical_triples_a_c_b": [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
            if compact
            else [list(triple) for triple in TRIPLES],
            "physical_readout_duration": "unknown",
            "limitations": [
                "Physical timing equality is unestablished",
                "Compiler may optimize cancelling mutation rotations",
                "QX terminal twins cannot validate mid-circuit classical-bit retention",
            ],
        }
        result[f"{batch}/backend.json"] = json.dumps(backend, indent=2, sort_keys=True) + "\n"
        result[f"{batch}/cases.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    return result


def write_fresh(directory: Path, files: dict[str, str]) -> None:
    """Refuse an existing destination, including empty directories."""
    directory.mkdir(parents=True, exist_ok=False)
    for relative, content in files.items():
        path = directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def analyze_shots(shots: list[str], metadata: dict[str, Any], *, block_size: int = 256) -> dict[str, Any]:
    """Analyze strings indexed left-to-right as explicitly specified by metadata."""
    width = metadata["width"]
    replicas = metadata["replicas"]
    if not shots or not isinstance(width, int) or width < 1 or block_size < 1 or not replicas:
        raise ValueError("nonempty shots and replicas, positive width and block size required")
    if any(len(shot) != width or set(shot) - {"0", "1"} for shot in shots):
        raise ValueError("shots must be fixed-width binary strings")
    for replica in replicas:
        indices = [replica[key] for key in ("data", "herald", "final_herald")]
        if any(not isinstance(index, int) or index < 0 or index >= width for index in indices):
            raise ValueError("metadata indices must address the shot string")
        if replica.get("endpoint", "z") not in {"z", "x"}:
            raise ValueError("endpoint must be z or x")
    bits = np.array([list(shot) for shot in shots], dtype=np.int8)
    data = bits[:, [replica["data"] for replica in replicas]]
    herald = bits[:, [replica["herald"] for replica in replicas]] == 0
    final = bits[:, [replica["final_herald"] for replica in replicas]] == 0
    joint = herald * (data == 0)
    signed = herald * (1 - 2 * data)
    counts = herald.sum(axis=0)
    entries = []
    for index, replica in enumerate(replicas):
        entries.append(
            {
                "endpoint": replica.get("endpoint", "z"),
                "herald_count": int(counts[index]),
                "data_zero_count": int((data[:, index] == 0).sum()),
                "joint_zero_count": int(joint[:, index].sum()),
                "signed_joint_sum": int(signed[:, index].sum()),
                "herald_disagreement_count": int((herald[:, index] != final[:, index]).sum()),
                "herald": float(herald[:, index].mean()),
                "data_zero": float((data[:, index] == 0).mean()),
                "joint_zero": float(joint[:, index].mean()),
                "signed_joint": float(signed[:, index].mean()),
                "conditional_zero": float(joint[:, index].sum() / counts[index]) if counts[index] else None,
                "conditional_signed": float(signed[:, index].sum() / counts[index]) if counts[index] else None,
                "herald_disagreement": float((herald[:, index] != final[:, index]).mean()),
            }
        )
    blocks = [
        {
            "start": start,
            "stop": min(start + block_size, len(shots)),
            "joint_zero": joint[start : start + block_size].mean(axis=0).tolist(),
            "joint_zero_counts": joint[start : start + block_size].sum(axis=0).tolist(),
            "herald_counts": herald[start : start + block_size].sum(axis=0).tolist(),
            "signed_joint_sums": signed[start : start + block_size].sum(axis=0).tolist(),
        }
        for start in range(0, len(shots), block_size)
    ]
    return {
        "interpretation": "descriptive; no IID p-values",
        "shots": len(shots),
        "replicas": entries,
        "cross_replica_joint_counts": (joint.astype(np.int64).T @ joint.astype(np.int64)).tolist(),
        "cross_replica_joint_moments": (joint.astype(float).T @ joint / len(shots)).tolist(),
        "blocks": blocks,
    }


def analyze_case(case_directory: Path, raw_directory: Path, *, block_size: int = 256) -> dict[str, str]:
    """Bind descriptive analysis to unchanged case sources and collected shot bytes."""
    manifest_bytes = (case_directory / "cases.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    results = {}
    for entry in manifest["circuits"]:
        filename = entry["file"]
        if Path(filename).name != filename:
            raise ValueError("circuit filenames must be basenames")
        if hashlib.sha256((case_directory / filename).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"circuit digest differs: {filename}")
        raw_bytes = (raw_directory / f"{filename}.json").read_bytes()
        shots = json.loads(raw_bytes)
        if not isinstance(shots, list) or len(shots) != manifest["shots"]:
            raise ValueError(f"raw shot count differs from cases.json: {filename}")
        report = analyze_shots(shots, entry["analysis_metadata"], block_size=block_size)
        report["provenance"] = {
            "cases_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "circuit_sha256": entry["sha256"],
            "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "analysis_metadata": entry["analysis_metadata"],
        }
        results[f"{filename}.analysis.json"] = json.dumps(report, indent=2, sort_keys=True) + "\n"
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--backend", type=Path, help="normalized backend snapshot JSON for generation")
    operation.add_argument("--analyze-case", type=Path, help="case directory with cases.json and circuit sources")
    parser.add_argument("--raw", type=Path, help="collected raw directory; defaults to CASE/raw")
    parser.add_argument("--block-size", type=int, default=256)
    parser.add_argument("--out", type=Path, required=True, help="fresh output directory")
    parser.add_argument("--wait-cycles", type=int, default=0)
    arguments = parser.parse_args()
    if arguments.analyze_case:
        files = analyze_case(
            arguments.analyze_case, arguments.raw or arguments.analyze_case / "raw", block_size=arguments.block_size
        )
    else:
        if arguments.raw:
            parser.error("--raw requires --analyze-case")
        files = build_batches(json.loads(arguments.backend.read_text()), wait_cycles=arguments.wait_cycles)
    write_fresh(arguments.out, files)


if __name__ == "__main__":
    main()
