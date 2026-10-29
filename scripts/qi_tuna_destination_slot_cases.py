"""Build unapproved source alternatives for every Tuna destination-response slot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from qi_projector_compiler_admission import normalized_instructions
from qi_tuna_readout_mapping_cases import ROOT, encoded, measurement_map, physical_stream, sha

PRIOR = ROOT / "results/quantum_inspire/proposals/tuna-readout-destination-sequential"
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
COMPILER_SHA256 = "c61eb8717a017243361e11b4f3179fcf6b3f9beb5b639aa1962b5dc05380ce8d"
BACKEND_SHA256 = "e92dab9819a2c20da16d057373e5025e89f6e22abc34253178cb801ac32e1223"
ARMS = {
    "baseline": (
        "prepared-zero-baseline-before",
        "baseline-before.cq",
        "3ab15a468b5eaa4811a2a06f297754269976f6901dde12370cf3d5fad593f267",
        "b8ec020a157d48b414c10a544b8f692fd26fa721edd4745d2d91da4382f3eabe",
        (17, 18, 19),
    ),
    "rotated": (
        "prepared-zero-rotated-destinations",
        "rotated-destinations.cq",
        "3084eef16a0d32a23d7b3fa41c92f27fa3ce4f3d84791d128a10246728ad6d5d",
        "2396adc9c5eef41452655d41bbc4df7cfb26a76f78e3e6b9a8d2d9e3327a9eb5",
        (19, 17, 18),
    ),
}


def build() -> dict[str, bytes]:
    """Revalidate historical source/compiler bindings and build all 48 alternatives."""
    receipt_path = PRIOR / "compiler-admission.json"
    receipt_bytes = receipt_path.read_bytes()
    if sha(receipt_bytes) != COMPILER_SHA256:
        raise ValueError("historical compiler receipt differs")
    receipt = json.loads(receipt_bytes)
    if receipt.get("schema") != "qi-tuna-destination-sequential-compiler-v1":
        raise ValueError("historical compiler receipt schema differs")
    compiler_rows = receipt.get("circuits")
    if not isinstance(compiler_rows, list):
        raise ValueError("historical compiler receipt lacks circuit rows")
    alternatives: dict[str, dict[str, Any]] = {}
    backend_bytes: bytes | None = None
    for arm, (directory, filename, source_hash, manifest_hash, early_destinations) in ARMS.items():
        manifest_bytes = (PRIOR / directory / "cases.json").read_bytes()
        source_bytes = (PRIOR / directory / filename).read_bytes()
        backend = (PRIOR / directory / "backend.json").read_bytes()
        compiled = (PRIOR / "local-compiled" / directory / filename).read_bytes()
        if sha(manifest_bytes) != manifest_hash or sha(source_bytes) != source_hash or sha(backend) != BACKEND_SHA256:
            raise ValueError("historical source, manifest or backend bytes differ")
        if backend_bytes is not None and backend != backend_bytes:
            raise ValueError("historical backend snapshots differ")
        backend_bytes = backend
        prior_manifest = json.loads(manifest_bytes)
        source = source_bytes.decode("utf-8")
        compiled_text = compiled.decode("utf-8")
        matches = [row for row in compiler_rows if row.get("source") == f"{directory}/{filename}"]
        expected_map = [
            {"qubit": qubit, "classical_bit": bit} for qubit, bit in zip((4, 11, 6), early_destinations, strict=True)
        ] + [{"qubit": bit, "classical_bit": bit} for bit in range(17)]
        if (
            len(matches) != 1
            or matches[0].get("source_sha256") != source_hash
            or matches[0].get("compiled_sha256") != sha(compiled)
            or measurement_map(source) != expected_map
            or measurement_map(compiled_text) != expected_map
            or normalized_instructions(source) != normalized_instructions(compiled_text)
            or matches[0].get("normalized_instructions") != normalized_instructions(source)
            or matches[0].get("measurement_to_bit_map") != expected_map
            or prior_manifest["circuits"][0].get("sha256") != source_hash
            or prior_manifest["circuits"][0].get("file") != filename
        ):
            raise ValueError("historical compiler or destination evidence differs")
        alternatives[arm] = {
            "source": source_bytes,
            "filename": filename,
            "row": prior_manifest["circuits"][0],
            "compiled_sha256": sha(compiled),
            "physical_stream": physical_stream(source),
        }
    if alternatives["baseline"]["physical_stream"] != alternatives["rotated"]["physical_stream"]:
        raise ValueError("source alternatives differ in their physical instruction stream")
    if backend_bytes is None:
        raise ValueError("historical backend snapshot is absent")
    files: dict[str, bytes] = {}
    catalogue_rows = []
    for slot in range(1, 25):
        for arm in ("baseline", "rotated"):
            variant = alternatives[arm]
            directory = f"slot-{slot:02d}/{arm}"
            manifest = {
                "schema": "qi-tuna-destination-slot-alternative-v1",
                "status": "working-unapproved",
                "provider_execution_authorized": False,
                "slot": slot,
                "comparison_arm": arm,
                "backend": "tuna_17",
                "backend_type_id": 7,
                "nqubits": 17,
                "shots": 4096,
                "circuits": [variant["row"]],
                "backend_snapshot": {"file": "backend.json", "sha256": BACKEND_SHA256},
                "compiled_sha256": variant["compiled_sha256"],
                "compiler_receipt_sha256": COMPILER_SHA256,
            }
            manifest_bytes = encoded(manifest).encode("utf-8")
            files[f"{directory}/cases.json"] = manifest_bytes
            files[f"{directory}/{variant['filename']}"] = variant["source"]
            files[f"{directory}/backend.json"] = backend_bytes
            catalogue_rows.append(
                {"slot": slot, "arm": arm, "directory": directory, "cases_sha256": sha(manifest_bytes)}
            )
    files["catalogue.json"] = encoded(
        {
            "schema": "qi-tuna-destination-slot-alternatives-v1",
            "status": "working-unapproved",
            "provider_execution_authorized": False,
            "slots": 24,
            "alternatives": catalogue_rows,
            "compiler_receipt": {"file": receipt_path.relative_to(ROOT).as_posix(), "sha256": COMPILER_SHA256},
            "producer_sha256": sha(Path(__file__).read_bytes()),
            "boundary": (
                "Both alternatives are listed for every slot; no assignments, provider execution "
                "or served schedule are established."
            ),
        }
    ).encode("utf-8")
    return files


def write_proposal(output: Path) -> None:
    """Write a fresh proposal without replacing any existing path."""
    files = build()
    output.mkdir(parents=True, exist_ok=False)
    for relative, content in files.items():
        path = output / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as destination:
            destination.write(content)


def check_proposal(output: Path) -> dict[str, Any]:
    """Require the complete proposal tree to match deterministic reconstruction."""
    expected = build()
    expected_directories = {
        parent.as_posix() for name in expected for parent in Path(name).parents if parent != Path(".")
    }
    entries = list(output.rglob("*"))
    if output.is_symlink() or any(path.is_symlink() for path in entries):
        raise ValueError("slot alternatives proposal differs: symbolic links are inadmissible")
    if any(path.is_file() and path.stat().st_nlink != 1 for path in entries):
        raise ValueError("slot alternatives proposal differs: hard-linked files are inadmissible")
    actual_directories = {path.relative_to(output).as_posix() for path in entries if path.is_dir()}
    actual = {path.relative_to(output).as_posix(): path.read_bytes() for path in entries if path.is_file()}
    if (
        actual != expected
        or actual_directories != expected_directories
        or len(entries) != len(actual) + len(actual_directories)
    ):
        raise ValueError("slot alternatives proposal differs from source-bound reconstruction")
    return json.loads(expected["catalogue.json"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path, nargs="?", const=PROPOSAL)
    args = parser.parse_args()
    if args.check:
        check_proposal(args.check)
        print("All 48 unapproved slot alternatives match historical source and compiler evidence.")
    else:
        write_proposal(args.out)


if __name__ == "__main__":
    main()
