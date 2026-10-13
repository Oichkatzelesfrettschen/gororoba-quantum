"""Verify the separate resource-policy receipt without rewriting source ledgers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    bundle = ROOT / "docs/evidence/kernel_determinant"
    receipt = json.loads((bundle / "resource-policy-replay.json").read_text())
    if digest(bundle / "SHA256SUMS") != receipt["original_manifest_sha256"]:
        raise ValueError("Original source ledger changed")
    if digest(ROOT / receipt["resource_policy_source"]) != receipt["resource_policy_source_sha256"]:
        raise ValueError("Resource-policy source changed")
    original = {}
    for line in (bundle / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        original[name] = expected
    refreshed = {}
    for line in (bundle / "SHA256SUMS.resource-policy-replay").read_text().splitlines():
        expected, name = line.split("  ", 1)
        refreshed[name] = expected
    if original.keys() != refreshed.keys():
        raise ValueError("Resource-policy replay changed the artifact denominator")
    changed = {name for name in original if original[name] != refreshed[name]}
    if changed != {"../../../gororoba_quantum/parallel.py"}:
        raise ValueError("Resource-policy replay changed an unrelated artifact identity")
    if original["../../../gororoba_quantum/parallel.py"] != receipt["original_parallel_sha256"]:
        raise ValueError("Original resource-policy identity differs")
    for name, expected in refreshed.items():
        if digest(bundle / name) != expected:
            raise ValueError(f"Revalidated source hash differs: {name}")
    print("Original kernel ledger preserved; half-CPU source and unchanged result denominator verified")


if __name__ == "__main__":
    main()
