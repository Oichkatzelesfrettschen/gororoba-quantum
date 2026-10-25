"""Every checksum ledger that a gate once verified with ``sha256sum -c`` still binds its files' bytes.

A ledger row is ``<64 hex digits>`` followed by two spaces (text mode) or a space and ``*`` (binary mode)
and a file name, which GNU sha256sum resolves against the working directory of the gate that ran it. The
rows below pair each ledger with that directory: the ledger's own directory for a ``SHA256SUMS`` file and
the repository root for a ledger that names repository-relative paths. Linux hashes text and binary mode
alike, so both markers compare the file's raw bytes. Backslash-escaped names, blank lines and comments are
outside the formats the ledgers use and fail loudly instead of passing unverified.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROW = re.compile(r"([0-9a-f]{64}) [ *]([^\\\r\n]+)")

# (working directory, ledger path relative to it), the pair a `sha256sum -c` gate ran.
LEDGERS = [
    ("results/local_compute", "SHA256SUMS"),
    ("results/local_compute/aer_delay_sentinels", "SHA256SUMS"),
    ("results/local_compute/n21_shared_predicate", "SHA256SUMS"),
    ("docs/sources/open_gororoba", "SHA256SUMS"),
    ("results/live/2026-10-12T055624.091217Z", "SHA256SUMS"),
    ("results/local_compute/mixed_pub_client", "SHA256SUMS"),
    ("docs/evidence/four_support_rank", "SHA256SUMS"),
    ("docs/evidence/c5_zero_divisor_code", "SHA256SUMS"),
    (".", "docs/evidence/cd-imaginary-sum-conference/source_hashes.sha256"),
    (".", "docs/evidence/cd-tower-basis-sign/source_hashes.sha256"),
    (".", "docs/evidence/cd-sign-row-anf/source_hashes.sha256"),
    (".", "docs/evidence/cd-associator-anf/source_hashes.sha256"),
    (".", "docs/evidence/cd-associator-census/source_hashes.sha256"),
    (".", "docs/evidence/cd-sign-python-semantics/source_hashes.sha256"),
    ("docs/evidence/four_support_geometry", "SHA256SUMS"),
    ("docs/evidence/four_support_doubling", "SHA256SUMS"),
    ("docs/evidence/four_support_homology", "SHA256SUMS"),
    ("docs/evidence/dimension32_skew_schur", "SHA256SUMS"),
    ("docs/evidence/principal_skew_atlas", "SHA256SUMS"),
    ("docs/evidence/schur_acceleration", "SHA256SUMS"),
    ("docs/evidence/vacuum_models", "SHA256SUMS"),
    ("docs/evidence/vacuum_endpoint_information", "SHA256SUMS"),
    ("docs/evidence/nullity_twelve_locus", "SHA256SUMS"),
    ("docs/evidence/kernel_limits", "SHA256SUMS"),
    ("docs/evidence/complex_skew", "SHA256SUMS"),
    ("docs/evidence/formal_certificates", "SHA256SUMS"),
    (".", "docs/evidence/formal_certificates/source_hashes.sha256"),
    ("docs/evidence/local_schur", "SHA256SUMS"),
    ("docs/evidence/folding_proofs", "SHA256SUMS"),
    ("docs/evidence/kernel_determinant", "SHA256SUMS-ordered-map-cancel"),
    ("docs/evidence/projective_kernel_limits", "SHA256SUMS-ordered-map-cancel"),
    ("docs/evidence/real_frontier_graphs", "SHA256SUMS-ordered-map-cancel"),
    ("results/live/kingston-wide-control-result", "SHA256SUMS"),
    ("docs/evidence/c881_exhaustive", "SHA256SUMS"),
    ("docs/evidence/reviewer_associator_audit", "SHA256SUMS"),
    ("docs/evidence/stiefel_witness", "SHA256SUMS"),
    (".", "docs/evidence/stiefel_witness/repo_sources.sha256"),
    ("docs/evidence/simulation-notebook-audit", "SHA256SUMS"),
    (".", "docs/evidence/cd-associator-point-indicators/source_hashes.sha256"),
    (".", "docs/evidence/cd-sign-python-translation/source_hashes-closure-scopes.sha256"),
]


def ledger_id(entry: tuple[str, str]) -> str:
    cwd, name = entry
    return name if cwd == "." else f"{cwd}/{name}"


def mismatches(cwd: Path, ledger: str) -> list[str]:
    """Rows of cwd/ledger whose file is absent or whose sha256 differs, as sha256sum -c run in cwd reports."""
    found = []
    rows = (cwd / ledger).read_text(encoding="utf-8").split("\n")
    if rows.pop() != "":
        raise AssertionError(f"{ledger} does not end in a newline")
    if not rows:
        raise AssertionError(f"{ledger} lists no file")
    for number, row in enumerate(rows, 1):
        match = ROW.fullmatch(row)
        if match is None:
            raise AssertionError(f"{ledger}:{number}: {row!r} is not a sha256sum row")
        path = cwd / match[2]
        if not path.is_file():
            found.append(f"{match[2]}: missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != match[1]:
            found.append(f"{match[2]}: bytes differ from the ledger")
    return found


@pytest.mark.parametrize("entry", LEDGERS, ids=ledger_id)
@pytest.mark.audit
def test_ledger_binds_its_bytes(entry: tuple[str, str]) -> None:
    cwd, ledger = entry
    found = mismatches(ROOT / cwd, ledger)
    if found:
        raise AssertionError(f"{ledger_id(entry)}: " + "; ".join(found))


@pytest.mark.audit
def test_every_sha256sum_gate_ledger_is_listed() -> None:
    gates = json.loads((ROOT / "ci/gates.json").read_text(encoding="utf-8"))["gates"]
    listed = {(cwd, name) for cwd, name in LEDGERS}
    unlisted = []
    for gate in gates:
        words = gate["cmd"].split()
        if words[:2] == ["sha256sum", "-c"] and len(words) == 3 and (gate["cwd"], words[2]) not in listed:
            unlisted.append(gate["name"])
    if unlisted:
        raise AssertionError(f"sha256sum gates whose ledger LEDGERS omits: {unlisted}")


def test_a_changed_or_missing_byte_fails(tmp_path: Path) -> None:
    """The ledger rule on files built here: a two-space row, a binary-marker row, a flipped byte, a deletion."""
    cwd = tmp_path / "bundle"
    (cwd / "sub").mkdir(parents=True)
    files = {"a.json": b'{"value": 1.25}\n', "sub/b.txt": b"retained bytes\n"}
    for name, data in files.items():
        (cwd / name).write_bytes(data)
    rows = [f"{hashlib.sha256(files['a.json']).hexdigest()}  a.json"]
    rows.append(f"{hashlib.sha256(files['sub/b.txt']).hexdigest()} *sub/b.txt")
    (cwd / "SHA256SUMS").write_text("\n".join(rows) + "\n", encoding="utf-8")
    if mismatches(cwd, "SHA256SUMS"):
        raise AssertionError("an intact bundle fails its ledger")
    target = cwd / "sub/b.txt"
    flipped = bytearray(target.read_bytes())
    flipped[3] ^= 1
    target.write_bytes(bytes(flipped))
    if mismatches(cwd, "SHA256SUMS") != ["sub/b.txt: bytes differ from the ledger"]:
        raise AssertionError("a flipped bit passes the ledger")
    target.unlink()
    if mismatches(cwd, "SHA256SUMS") != ["sub/b.txt: missing"]:
        raise AssertionError("a deleted file passes the ledger")
