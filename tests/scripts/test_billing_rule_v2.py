"""The billing-rule successors differ from their pinned producers only at the superseded fields."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import ascella_predecessor_case as predecessor
import ascella_predecessor_case_v2 as predecessor_v2
import bdsc_case_records_v2 as records_v2
import billing_rule_v2
import pytest
import qd_platform

ROOT = Path(__file__).resolve().parents[2]
# docs/evidence/quandela-billing-rule-successor/README.md records these producer digests.
PINNED_PRODUCERS = {
    "scripts/bdsc_certificate.py": "5dbcd027eb24a303ba5757e00b0123e846bc3c86dab70a24dc1ae1f98b197753",
    "scripts/ascella_predecessor_case.py": "2310aa98d1c0c68812d7edcbd30fd6a0713ca5fb6ab1e1b8c3c96e3d845b197b",
}


def differences(first: Any, second: Any, path: str = "") -> set[str]:
    """JSON pointers at which two decoded documents differ, including keys present on one side only."""
    if isinstance(first, dict) and isinstance(second, dict):
        out: set[str] = set()
        for key in first.keys() | second.keys():
            if key not in first or key not in second:
                out.add(f"{path}/{key}")
            else:
                out |= differences(first[key], second[key], f"{path}/{key}")
        return out
    if isinstance(first, list) and isinstance(second, list) and len(first) == len(second):
        out = set()
        for index, (left, right) in enumerate(zip(first, second, strict=True)):
            out |= differences(left, right, f"{path}/{index}")
        return out
    return set() if first == second else {path}


def flatten(documents: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name, content in documents.items():
        if isinstance(content, dict):
            out |= flatten(content, f"{prefix}{name}/")
        elif name.endswith(".json"):
            out[f"{prefix}{name}"] = json.loads(content)
        else:
            out[f"{prefix}{name}"] = content
    return out


def raw(documents: dict[str, Any], prefix: str = "") -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for name, content in documents.items():
        if isinstance(content, dict):
            out |= raw(content, f"{prefix}{name}/")
        else:
            out[f"{prefix}{name}"] = content.encode() if isinstance(content, str) else content
    return out


def reserialize(original: bytes, value: Any) -> bytes:
    """`value` in the one serialization that reproduces `original` byte for byte from its own parse."""
    parsed = json.loads(original)
    for sort_keys in (False, True):
        form = (json.dumps(parsed, indent=1, sort_keys=sort_keys) + "\n").encode()
        if form == original:
            return (json.dumps(value, indent=1, sort_keys=sort_keys) + "\n").encode()
    raise AssertionError("no indent=1 serialization reproduces the original record")


def changed(original: dict[str, Any], successor: dict[str, Any]) -> dict[str, set[str]]:
    """JSON pointers that differ per record; a record outside them keeps its bytes, and a changed record equals the
    original producer's serialization of its parsed successor value, so formatting cannot drift unseen."""
    before, after = flatten(original), flatten(successor)
    if before.keys() != after.keys():
        raise AssertionError(f"record sets differ: {sorted(before.keys() ^ after.keys())}")
    found = {name: diff for name in before if (diff := differences(before[name], after[name]))}
    old_bytes, new_bytes = raw(original), raw(successor)
    for name in before:
        if name not in found and old_bytes[name] != new_bytes[name]:
            raise AssertionError(f"{name}: bytes differ while its parsed value does not")
        if name in found and new_bytes[name] != reserialize(old_bytes[name], after[name]):
            raise AssertionError(f"{name}: serialization differs from the original producer's")
    return found


def test_pinned_producers_keep_their_recorded_bytes() -> None:
    for name, digest in PINNED_PRODUCERS.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise AssertionError(f"{name} no longer hashes to the digest its successor record names")


def test_supersede_refuses_a_field_that_moved() -> None:
    record = {"resources": {"billing_rule": "another statement"}}
    with pytest.raises(ValueError, match="superseded wording"):
        billing_rule_v2.supersede(record, ("resources", "billing_rule"), "old", "new")
    record = {"resources": {"billing_rule": "old"}}
    billing_rule_v2.supersede(record, ("resources", "billing_rule"), "old", "new")
    if record["resources"]["billing_rule"] != "new":
        raise AssertionError("supersede did not replace the field")


def test_rule_names_the_cap_as_ceiling_and_the_used_shots() -> None:
    for phrase in (
        "smaller of the shots it used",
        "isolated usage report",
        "canceled before its start bills nothing",
        "qd_platform.charged",
        "ceiling",
    ):
        if phrase not in billing_rule_v2.RULE:
            raise AssertionError(f"the successor rule omits {phrase!r}")


# The diagnostic's retained manifests name this ANU draw; the drawn build adds the draw binding and the seeds.
DIAGNOSTIC_DRAW = ROOT / "docs/evidence/anu_qrng/draw-2026-10-22T110545Z.json"


@pytest.mark.parametrize(
    ("family", "draw"), [("diagnostic", None), ("diagnostic", DIAGNOSTIC_DRAW), ("stationarity", None)]
)
def test_bdsc_case_successor_changes_only_billing_and_case_digest(family: str, draw: Path | None) -> None:
    original = records_v2.original(family, draw)
    successor = records_v2.documents(family, draw)
    field = records_v2.CASE_DIGEST[family]
    jobs = sorted(name for name in original if name != "case.json")
    expected = {"case.json": {"/resources/billing_rule"}} | {f"{job}/cases.json": {f"/{field}"} for job in jobs}
    found = changed(original, successor)
    if found != expected:
        raise AssertionError(f"{family}: successor changes {found}, expected {expected}")
    case_bytes = successor["case.json"]
    if not isinstance(case_bytes, bytes):
        raise AssertionError("case.json is not a record")
    digest = hashlib.sha256(case_bytes).hexdigest()
    for job in jobs:
        files = successor[job]
        if not isinstance(files, dict) or json.loads(files["cases.json"])[field] != digest:
            raise AssertionError(f"{job}: {field} does not name the successor case record")


def test_bdsc_case_successor_check_round_trips(tmp_path: Path) -> None:
    records_v2.write("stationarity", tmp_path, None)
    records_v2.check("stationarity", tmp_path, None)
    (tmp_path / "case.json").write_bytes((tmp_path / "case.json").read_bytes() + b" ")
    with pytest.raises(ValueError, match="case.json differs"):
        records_v2.check("stationarity", tmp_path, None)


def test_predecessor_successor_changes_only_credit_basis_and_its_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = predecessor.documents()
    # One build of the original serves every successor call below, which keeps the test inside the call budget.
    monkeypatch.setattr(predecessor, "documents", lambda: dict(original))
    successor = predecessor_v2.documents()
    expected = {
        "cases.json": {"/preregistered/credit_basis", "/preregistered/builder_sha256"},
    }
    found = changed(original, successor)
    if found != expected:
        raise AssertionError(f"successor changes {found}, expected {expected}")
    manifest = json.loads(successor["cases.json"])
    ceiling = predecessor_v2.credit_ceiling(predecessor.SHOTS_PER_ITERATION)
    if manifest["max_credits"] != ceiling or manifest["preregistered"]["expected_credits"] != ceiling:
        raise AssertionError("the credit figures no longer equal the ceiling at the largest iteration's max_shots")
    qd_platform.acquisition_sources(manifest)
    builder = hashlib.sha256((ROOT / predecessor_v2.BUILDER).read_bytes()).hexdigest()
    if manifest["preregistered"]["builder_sha256"] != builder:
        raise AssertionError("the successor request does not name its builder's digest")
    predecessor.publish_case(tmp_path, successor)
    predecessor_v2.check(tmp_path)


@pytest.mark.audit
def test_bdsc_certificate_successor_changes_only_billing_fields() -> None:
    import bdsc_certificate as cert
    import bdsc_certificate_v2 as cert_v2

    found = changed(cert.documents(), cert_v2.documents())
    # The two pointers docs/evidence/quandela-billing-rule-successor/README.md names for bdsc_certificate.py.
    expected = {
        "planning.json": {"/resources_historical/rates/credits"},
        "qualification_case.json": {"/resources/billing_rule"},
    }
    if found != expected:
        raise AssertionError(f"successor changes {found}, expected {expected}")
