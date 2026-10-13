"""Verify the separate resource-policy receipt without rewriting source ledgers."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SOURCE = "../../../gororoba_quantum/parallel.py"
BUNDLES = ("kernel_determinant", "projective_kernel_limits", "real_frontier_graphs")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ledger(path: Path, root: Path) -> dict[str, str]:
    entries = {}
    for line in path.read_text().splitlines():
        expected, name = line.split("  ", 1)
        require(bool(re.fullmatch(r"[0-9a-f]{64}", expected)), "Ledger digest shape differs")
        require(name not in entries, "Ledger repeats an artifact identity")
        require(
            not Path(name).is_absolute() and (path.parent / name).resolve().is_relative_to(root.resolve()),
            "Ledger path leaves the repository",
        )
        entries[name] = expected
    require(bool(entries), "Source ledger is empty")
    return entries


def verify(root: Path, bundle_name: str) -> None:
    require(bundle_name in BUNDLES, "Unknown resource-policy bundle")
    bundle = root / "docs/evidence" / bundle_name
    receipt = json.loads((bundle / "resource-policy-replay.json").read_text())
    require(receipt["schema"] == f"{bundle_name.replace('_', '-')}-resource-policy-replay-v1", "Receipt schema differs")
    require(receipt["resource_policy_source"] == "gororoba_quantum/parallel.py", "Resource-policy path differs")
    for key in ("original_manifest_sha256", "resource_policy_source_sha256", "original_parallel_sha256"):
        require(
            isinstance(receipt[key], str) and bool(re.fullmatch(r"[0-9a-f]{64}", receipt[key])),
            "Receipt source digest shape differs",
        )
    require(digest(bundle / "SHA256SUMS") == receipt["original_manifest_sha256"], "Original source ledger changed")
    require(
        digest(root / receipt["resource_policy_source"]) == receipt["resource_policy_source_sha256"],
        "Resource-policy source changed",
    )
    original = ledger(bundle / "SHA256SUMS", root)
    refreshed = ledger(bundle / "SHA256SUMS.resource-policy-replay", root)
    require(original.keys() == refreshed.keys(), "Resource-policy replay changed the artifact denominator")
    require(
        {name for name in original if original[name] != refreshed[name]} == {SOURCE},
        "Resource-policy replay changed an unrelated artifact identity",
    )
    require(original[SOURCE] == receipt["original_parallel_sha256"], "Original resource-policy identity differs")
    for name, expected in refreshed.items():
        require(digest(bundle / name) == expected, f"Revalidated source hash differs: {name}")


def self_test(bundle_name: str) -> None:
    bundle = ROOT / "docs/evidence" / bundle_name
    before = {name: digest(bundle / name) for name in ledger(bundle / "SHA256SUMS.resource-policy-replay", ROOT)}
    for mutation in ("schema", "source_path", "source_digest", "duplicate", "denominator", "data_bytes"):
        with TemporaryDirectory(prefix="kernel-resource-receipt-") as temporary:
            root = Path(temporary)
            copied = root / "docs/evidence" / bundle_name
            copied.mkdir(parents=True)
            for filename in ("SHA256SUMS", "SHA256SUMS.resource-policy-replay", "resource-policy-replay.json"):
                shutil.copyfile(bundle / filename, copied / filename)
            for name in ledger(bundle / "SHA256SUMS.resource-policy-replay", ROOT):
                target = copied / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(bundle / name, target)
            verify(root, bundle_name)
            receipt: dict[str, Any] = json.loads((copied / "resource-policy-replay.json").read_text())
            if mutation == "schema":
                receipt["schema"] = "unknown"
            elif mutation == "source_path":
                receipt["resource_policy_source"] = "outside.py"
            elif mutation == "source_digest":
                receipt["resource_policy_source_sha256"] = "0" * 64
            elif mutation == "duplicate":
                path = copied / "SHA256SUMS.resource-policy-replay"
                path.write_text(path.read_text() + path.read_text().splitlines()[0] + "\n")
            elif mutation == "denominator":
                path = copied / "SHA256SUMS.resource-policy-replay"
                path.write_text("\n".join(path.read_text().splitlines()[1:]) + "\n")
            else:
                (copied / "result.json").write_text("corrupted retained result")
            (copied / "resource-policy-replay.json").write_text(json.dumps(receipt))
            try:
                verify(root, bundle_name)
            except ValueError:
                pass
            else:
                raise RuntimeError(f"Resource-policy mutation admitted: {mutation}")
    after = {name: digest(bundle / name) for name in before}
    require(before == after, "Receipt contract changed a retained input")
    print(f"{bundle_name}: six metadata/denominator/data mutations rejected; source bytes preserved")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    for bundle_name in BUNDLES:
        if arguments.self_test:
            self_test(bundle_name)
        else:
            verify(ROOT, bundle_name)
            print(f"{bundle_name}: original ledger preserved; half-CPU source and unchanged denominator verified")


if __name__ == "__main__":
    main()
