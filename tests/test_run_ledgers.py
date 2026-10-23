"""Every tracked checksum ledger under results/live/ binds the retained bytes it lists.

A run directory's SHA256SUMS lists its files by name relative to the ledger, so a changed byte in a
retained record, QPY circuit or raw result fails here before a merge. The three timestamped directories
under results/live/local-audit-provenance/ keep copies of a run's original manifests, taken before
integration; their rows name files of results/live/<run>/ at their original bytes, so each row is bound
to the original_sha256 that sync-inventory.json records for that path rather than checked in place.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "results/live"
PROVENANCE = LIVE / "local-audit-provenance"
# sha256sum's output line: the digest, a space, then a space (text mode) or "*" (binary mode) and the name.
ROW = re.compile(r"([0-9a-f]{64}) [ *](.+)")


def tracked_ledgers() -> list[Path]:
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", "results/live/**/SHA256SUMS"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout.decode()
    return [ROOT / name for name in listed.split("\0") if name]


def snapshot(ledger: Path) -> bool:
    return ledger.parent.parent == PROVENANCE and (LIVE / ledger.parent.name).is_dir()


def rows(ledger: Path) -> list[tuple[str, str]]:
    parsed = []
    for number, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), 1):
        match = ROW.fullmatch(line)
        if match is None:
            raise AssertionError(f"{ledger}:{number}: {line!r} is not a sha256sum row")
        parsed.append((match[1], match[2]))
    if not parsed:
        raise AssertionError(f"{ledger} lists no file")
    return parsed


def mismatches(ledger: Path) -> list[str]:
    found = []
    for digest, name in rows(ledger):
        path = ledger.parent / name
        if not path.is_file():
            found.append(f"{name}: missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            found.append(f"{name}: bytes differ from the ledger")
    return found


LEDGERS = tracked_ledgers()
IN_PLACE = [ledger for ledger in LEDGERS if not snapshot(ledger)]
SNAPSHOTS = [ledger for ledger in LEDGERS if snapshot(ledger)]


def test_ledgers_split_into_in_place_and_snapshot() -> None:
    if not IN_PLACE or len(SNAPSHOTS) != 3:
        raise AssertionError(f"{len(IN_PLACE)} in-place and {len(SNAPSHOTS)} snapshot ledgers under {LIVE}")


@pytest.mark.parametrize("ledger", IN_PLACE, ids=lambda ledger: str(ledger.parent.relative_to(LIVE)))
def test_run_ledger_binds_its_bytes(ledger: Path) -> None:
    found = mismatches(ledger)
    if found:
        raise AssertionError(f"{ledger.relative_to(ROOT)}: " + "; ".join(found))


@pytest.mark.parametrize("ledger", SNAPSHOTS, ids=lambda ledger: ledger.parent.name)
def test_snapshot_ledger_rows_are_inventoried_originals(ledger: Path) -> None:
    inventory = json.loads((PROVENANCE / "sync-inventory.json").read_text(encoding="utf-8"))
    originals = {(item["path"], item["original_sha256"]) for item in inventory["files"]}
    unbound = [
        name for digest, name in rows(ledger) if (f"results/live/{ledger.parent.name}/{name}", digest) not in originals
    ]
    if unbound:
        raise AssertionError(f"{ledger.relative_to(ROOT)}: rows absent from sync-inventory.json: {unbound}")


def test_a_changed_or_missing_byte_fails(tmp_path: Path) -> None:
    source = min(IN_PLACE, key=lambda ledger: sum(p.stat().st_size for p in ledger.parent.rglob("*") if p.is_file()))
    shutil.copytree(source.parent, tmp_path / "run")
    ledger = tmp_path / "run" / source.name
    if mismatches(ledger):
        raise AssertionError(f"the copy of {source.parent} fails before any edit")
    _, name = rows(ledger)[0]
    target = tmp_path / "run" / name
    data = bytearray(target.read_bytes())
    data[len(data) // 2] ^= 1
    target.write_bytes(bytes(data))
    if mismatches(ledger) != [f"{name}: bytes differ from the ledger"]:
        raise AssertionError(f"a flipped bit in {name} passes the ledger")
    target.unlink()
    if mismatches(ledger) != [f"{name}: missing"]:
        raise AssertionError(f"a deleted {name} passes the ledger")
