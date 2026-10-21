"""Re-encode a retained run's dense wide outcome vectors through law_encoding, provably losslessly.

record.json and collect.json written before law_encoding stored every
outcome vector of a wide register densely. RUN_DIR re-encodes both files'
vectors (record: groups[].members[].ideal and .replicas[].noisy,
observable_contracts[].terms[].values; collect: each entry's measured laws)
and writes dense-sha256.json naming each file's original sha256; --check
expands every encoded vector and requires each file, written in live_run's
own format, to hash to that digest, so an approval or prediction-reuse
binding that names an original digest stays verifiable. A written case
removed with --drop-case keeps its original digest in the manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import law_encoding  # noqa: E402

MANIFEST = "dense-sha256.json"
SCHEMA = "dense-run-digests-v1"
CASE = "UNAPPROVED_CASE.md"


def record_text(record: Any) -> str:
    """record.json as live_run writes it."""
    return json.dumps(record, indent=2, default=str) + "\n"


def collect_text(entries: Any) -> str:
    """collect.json as live_run's collect checkpoint writes it."""
    return json.dumps(entries, indent=2) + "\n"


def map_record(record: dict[str, Any], change: Callable[[Any], Any]) -> None:
    for group in record.get("groups", []):
        for member in group.get("members", []):
            member["ideal"] = change(member["ideal"])
            for replica in member.get("replicas", []):
                if "noisy" in replica:
                    replica["noisy"] = change(replica["noisy"])
    for contract in record.get("observable_contracts") or []:
        for term in contract["terms"]:
            term["values"] = change(term["values"])


def map_collect(entries: list[Any], change: Callable[[Any], Any]) -> None:
    for entry in entries:
        if isinstance(entry, dict) and "measured" in entry:
            entry["measured"] = {name: [change(law) for law in laws] for name, laws in entry["measured"].items()}


FILES: dict[str, tuple[Callable[[Any], str], Callable[[Any, Callable[[Any], Any]], None]]] = {
    "record.json": (record_text, map_record),
    "collect.json": (collect_text, map_collect),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_run(run: Path, drop_case: bool) -> dict[str, Any]:
    manifest: dict[str, Any] = {"schema": SCHEMA, "files": {}}
    for name, (text, change) in FILES.items():
        path = run / name
        if not path.exists():
            continue
        raw = path.read_bytes()
        value = json.loads(raw)
        if text(value).encode() != raw:
            raise RuntimeError(f"{path}: the bytes differ from live_run's writer format")
        change(value, law_encoding.encode)
        expanded = json.loads(text(value))
        change(expanded, law_encoding.dense)
        if digest(text(expanded).encode()) != digest(raw):
            raise RuntimeError(f"{path}: the encoded file does not expand to its original bytes")
        path.write_text(text(value))
        manifest["files"][name] = digest(raw)
    if drop_case and (run / CASE).exists():
        manifest["dropped"] = {CASE: digest((run / CASE).read_bytes())}
        (run / CASE).unlink()
    (run / MANIFEST).write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    return manifest


def check_run(run: Path) -> None:
    manifest = json.loads((run / MANIFEST).read_text())
    if manifest.get("schema") != SCHEMA or not manifest.get("files"):
        raise RuntimeError(f"{run / MANIFEST}: not a {SCHEMA} manifest")
    present = sorted(name for name in FILES if (run / name).exists())
    if sorted(manifest["files"]) != present:
        raise RuntimeError(f"{run / MANIFEST} lists {sorted(manifest['files'])}, the run holds {present}")
    for name, original in manifest["files"].items():
        text, change = FILES[name]
        value = json.loads((run / name).read_text())
        change(value, law_encoding.dense)
        if digest(text(value).encode()) != original:
            raise RuntimeError(f"{run / name} expands to another file than sha256 {original}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--drop-case", action="store_true", help="remove a dense written case, keeping its digest")
    args = parser.parse_args(argv)
    for run in args.runs:
        if args.check:
            check_run(run)
        else:
            encode_run(run, args.drop_case)
    return 0


if __name__ == "__main__":
    sys.exit(main())
