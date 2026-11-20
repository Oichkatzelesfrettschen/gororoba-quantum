"""Execute one source-verified closure stage and retain bounded state comparisons."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "docs/evidence/a5-char0-transfer"
MANIFEST_SHA256 = "45c070cc53c55a71c1a9dd044ef74618a4ad2531ab468ec8697cc128824b6f6e"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "input is absent or is a symlink: " + str(path))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_path(name: str, slug: str) -> bool:
    return (
        name == f"docs/evidence/a5-char0-transfer/e8-closure-certificate-{slug}.json"
        or name == f"docs/evidence/a5-char0-transfer/cofactors/e8-closure-{slug}.json.xz"
        or (
            name.startswith("docs/evidence/a5-char0-transfer/logs/e8-closure-")
            and (f"-{slug}." in name or f"-{slug}-" in name)
            and name.endswith((".log", ".time"))
        )
    )


def surfaces(manifest: dict[str, Any]) -> dict[str, str]:
    paths = {entry["path"] for entry in manifest["files"]}
    paths.update(str(path.relative_to(ROOT)) for path in (HERE / "logs").iterdir() if path.is_file())
    return {name: digest(ROOT / name) for name in sorted(paths)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, choices=("e8-nm", "e8-np"))
    parser.add_argument("--mode", required=True, choices=("write", "check"))
    arguments = parser.parse_args()
    manifest_path = ROOT / "transport-manifest.json"
    require(digest(manifest_path) == MANIFEST_SHA256, "the frozen source manifest differs")
    manifest = json.loads(manifest_path.read_bytes())
    require(platform.python_version() == manifest["expected_runtime"]["python"], "the Python runtime differs")
    require(
        all(
            importlib.metadata.version(name) == version
            for name, version in manifest["expected_runtime"]["packages"].items()
        ),
        "the scientific package versions differ",
    )
    before = surfaces(manifest)
    immutable = [
        entry for entry in manifest["files"] if not any(output_path(entry["path"], slug) for slug in ("e8-nm", "e8-np"))
    ]
    for entry in immutable:
        require(before[entry["path"]] == entry["sha256"], "a frozen source/input changed: " + entry["path"])
    sys.path.insert(0, str(ROOT / "gororoba_quantum"))
    sys.path.insert(0, str(HERE))
    import e8_closure_certificate as certificate

    if arguments.mode == "write":
        result = certificate.write(arguments.slug, 4, 24)
        require(result["verdict"] == "i_equals_is", "the generated certificate fails the exact verdict")
        expected = manifest["expected_retained_bindings"][arguments.slug]
        for key in ("producer_script", "header_j_and_g", "slice_rings_qi", "reduction_check", "cofactor_file"):
            require(result["sha256"][key] == expected[key], "the regenerated binding differs: " + key)
        require(
            result["sha256"]["certificate_producer"] == manifest["certificate_producer_sha256"],
            "the generated record binds a different certificate producer",
        )
        summary = {key: result[key] for key in ("slug", "verdict", "wall_seconds", "execution", "sha256", "counts")}
    else:
        with certificate._execution_scope(1, 8):
            result = certificate.check(arguments.slug)
        for kind, expected_bad in (("cofactor", 1), ("generator", 42)):
            mutation = result["mutations"][kind]
            require(
                mutation["status"] == "completed" and mutation["bad_identities"] == expected_bad,
                "the mutation result differs: " + kind,
            )
        summary = result
    after = surfaces(manifest)
    changed = [name for name in sorted(before.keys() | after.keys()) if before.get(name) != after.get(name)]
    if arguments.mode == "write":
        require(all(output_path(name, arguments.slug) for name in changed), "generation changed an undeclared surface")
    else:
        require(before == after, "the exact check changed a transported input or retained generation log")
    receipt = {
        "schema": "a5-e8-closure-source-verified-stage/1",
        "source_commit": manifest["source_commit"],
        "input_manifest_sha256": MANIFEST_SHA256,
        "stage_helper_sha256": digest(Path(__file__)),
        "stage": arguments.mode,
        "slug": arguments.slug,
        "frozen_input_entries_checked": len(immutable),
        "before_sha256": before,
        "after_sha256": after,
        "changed_paths": changed,
        "result": summary,
    }
    target = ROOT / f"docs/local/windows-full-{arguments.slug}-{arguments.mode}-receipt.json"
    target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
