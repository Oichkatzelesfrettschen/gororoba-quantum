"""Verify that the corrected rollback package preserves the pinned CPU payload."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

SOURCE_SHA256 = "c58d8c8c22c64d924b48ba6b4b770d9c4a26f99755e907f518fa6f608f0ce123"
METADATA = frozenset((".PKGINFO", ".BUILDINFO", ".MTREE"))
EXTENSION = "usr/lib/python3.14/site-packages/qiskit_aer/backends/controller_wrappers.cpython-314-x86_64-linux-gnu.so"
DEPENDENCIES = frozenset(
    ("openblas", "python-dateutil", "python-numpy", "python-psutil", "python-qiskit", "python-sympy")
)


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def inspect(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    payload: dict[str, dict[str, Any]] = {}
    metadata: dict[str, list[str]] = {}
    names: set[str] = set()
    with tarfile.open(path) as archive:
        for member in archive:
            name = member.name.removesuffix("/")
            if name in names:
                raise ValueError(f"duplicate archive member: {name}")
            names.add(name)
            if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts:
                raise ValueError(f"unsafe archive member: {name}")
            if name == ".PKGINFO":
                handle = archive.extractfile(member)
                if handle is None:
                    raise ValueError("package metadata is unreadable")
                for line in handle.read().decode().splitlines():
                    if line and not line.startswith("#"):
                        key, value = line.split(" = ", 1)
                        metadata.setdefault(key, []).append(value)
            if name in METADATA:
                continue
            if not (member.isfile() or member.isdir() or member.issym() or member.islnk()):
                raise ValueError(f"unsupported payload member type: {name}")
            digest = None
            if member.isfile():
                handle = archive.extractfile(member)
                if handle is None:
                    raise ValueError(f"payload file is unreadable: {name}")
                digest = hashlib.sha256(handle.read()).hexdigest()
            payload[name] = {
                "type": member.type.decode("ascii"),
                "mode": member.mode,
                "uid": member.uid,
                "gid": member.gid,
                "mtime": member.mtime,
                "linkname": member.linkname,
                "size": member.size,
                "sha256": digest,
            }
    if not METADATA <= names:
        raise ValueError("package metadata members are incomplete")
    return payload, metadata


def verify(source: Path, rollback: Path, installed_root: Path | None = None) -> dict[str, Any]:
    source_digest = sha256(source)
    if source_digest != SOURCE_SHA256:
        raise ValueError("CPU source archive differs from the pinned checksum")
    original, original_metadata = inspect(source)
    rebuilt, rebuilt_metadata = inspect(rollback)
    if original != rebuilt:
        differing = sorted(name for name in original.keys() | rebuilt.keys() if original.get(name) != rebuilt.get(name))
        raise ValueError(f"rollback payload differs at {differing}")
    required = {
        "pkgname": ["python-qiskit-aer"],
        "pkgver": ["0.17.2-4"],
        "arch": ["x86_64"],
        "conflict": ["python-qiskit-aer-cuda"],
    }
    for key, expected in required.items():
        if rebuilt_metadata.get(key) != expected:
            raise ValueError(f"rollback metadata differs at {key}")
    if set(rebuilt_metadata.get("depend", ())) != DEPENDENCIES:
        raise ValueError("rollback dependencies differ from the corrected contract")
    if original_metadata.get("pkgver") != ["0.17.2-3"]:
        raise ValueError("unexpected original CPU package version")
    extension_digest = rebuilt[EXTENSION]["sha256"]
    installed_digest = None
    if installed_root is not None:
        installed_digest = sha256(installed_root / EXTENSION)
        if installed_digest != extension_digest:
            raise ValueError("installed CPU extension differs from the retained rollback extension")
    canonical = json.dumps(rebuilt, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return {
        "status": "verified",
        "source_archive_sha256": source_digest,
        "rollback_archive_sha256": sha256(rollback),
        "payload_entries": len(rebuilt),
        "payload_files": sum(item["sha256"] is not None for item in rebuilt.values()),
        "payload_manifest_sha256": hashlib.sha256(canonical).hexdigest(),
        "compared": ["names", "types", "bytes", "permissions", "uid", "gid", "timestamps", "link_targets"],
        "regenerated_archive_metadata": sorted(METADATA),
        "extension_sha256": extension_digest,
        "installed_extension_sha256": installed_digest,
        "rollback_metadata": {key: rebuilt_metadata[key] for key in (*required, "depend")},
    }


def mutation_checks(source: Path, rollback: Path) -> list[str]:
    """Reject a changed payload, missing member, duplicate, and dependency drift."""
    rejected: list[str] = []
    with tempfile.TemporaryDirectory(prefix="aer-rollback-verifier-") as temporary:
        directory = Path(temporary)
        selected = "usr/lib/python3.14/site-packages/qiskit_aer/VERSION.txt"
        for action in ("payload_bytes", "missing_member", "duplicate_member", "stale_dependency"):
            changed = directory / f"{action}.tar.zst"
            with tarfile.open(rollback) as original, tarfile.open(changed, "w:zst") as output:
                for entry in original:
                    entry = copy.copy(entry)
                    handle = original.extractfile(entry) if entry.isfile() else None
                    contents = handle.read() if handle is not None else None
                    if entry.name == selected:
                        if action == "missing_member":
                            continue
                        if action == "payload_bytes":
                            if not contents:
                                raise AssertionError("mutation fixture needs a nonempty version file")
                            contents = bytes((contents[0] ^ 1,)) + contents[1:]
                    if action == "stale_dependency" and entry.name == ".PKGINFO":
                        if contents is None or b"depend = openblas\n" not in contents:
                            raise AssertionError("mutation fixture lacks the corrected dependency")
                        contents = contents.replace(b"depend = openblas\n", b"depend = blas-openblas\n")
                    if contents is not None:
                        entry.size = len(contents)
                    output.addfile(entry, io.BytesIO(contents) if contents is not None else None)
                    if action == "duplicate_member" and entry.name == selected:
                        output.addfile(entry, io.BytesIO(contents) if contents is not None else None)
            try:
                verify(source, changed)
            except ValueError:
                rejected.append(action)
            else:
                raise AssertionError(f"verifier accepts {action}")
        try:
            verify(rollback, rollback)
        except ValueError:
            rejected.append("source_checksum")
        else:
            raise AssertionError("verifier accepts the wrong source archive")
        installed_root = directory / "installed"
        installed_extension = installed_root / EXTENSION
        installed_extension.parent.mkdir(parents=True)
        installed_extension.write_bytes(b"changed extension")
        try:
            verify(source, rollback, installed_root)
        except ValueError:
            rejected.append("installed_extension")
        else:
            raise AssertionError("verifier accepts a different installed extension")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("rollback", type=Path)
    parser.add_argument("--installed-root", type=Path)
    parser.add_argument("--check", action="store_true", help="exercise six rejection cases in temporary storage")
    args = parser.parse_args()
    report = verify(args.source, args.rollback, args.installed_root)
    if args.check:
        report["mutation_checks"] = mutation_checks(args.source, args.rollback)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
