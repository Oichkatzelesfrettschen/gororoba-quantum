"""Evidence navigation keeps observation identity and inference boundaries distinct."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import quantum_ledger


@pytest.mark.parametrize(
    ("pointer", "expected"),
    [
        ("", {"a/b": {"~": [None, 0, 9007199254740993]}}),
        ("/a~1b/~0/0", None),
        ("/a~1b/~0/1", 0),
        ("/a~1b/~0/2", 9007199254740993),
    ],
)
def test_pointer_preserves_source_values(pointer: str, expected: object) -> None:
    found = quantum_ledger.pointer_value({"a/b": {"~": [None, 0, 9007199254740993]}}, pointer)
    if found != expected:
        raise RuntimeError(f"JSON Pointer {pointer} changes {expected!r} into {found!r}")


@pytest.mark.parametrize("pointer", ["relative", "/rows/-1", "/rows/01", "/rows/1", "/~2", "/rows/-"])
def test_pointer_refuses_ambiguous_or_absent_values(pointer: str) -> None:
    with pytest.raises(ValueError):
        quantum_ledger.pointer_value({"rows": [0]}, pointer)


def test_inspection_binds_exact_bytes_and_refuses_escape(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    content = b'{"n": 0, "missing": null, "rows": [{"covariance": -0.02}]}'
    (root / "analysis.json").write_bytes(content)
    observed = quantum_ledger.inspect(root, "analysis.json", "/rows/0")
    if observed["value"] != {"covariance": -0.02} or observed["file_sha256"] != hashlib.sha256(content).hexdigest():
        raise RuntimeError("inspection changes the source value or its byte identity")
    (tmp_path / "outside.json").write_bytes(content)
    (root / "escape.json").symlink_to(tmp_path / "outside.json")
    for path in ("../outside.json", "escape.json", str(tmp_path / "outside.json")):
        with pytest.raises(ValueError, match="leaves the repository"):
            quantum_ledger.inspect(root, path, "")


def test_ledger_census_exposes_gaps_without_inventing_support(tmp_path: Path) -> None:
    source = tmp_path / "analysis.json"
    source.write_text(json.dumps({"schema": "test-analysis-v1", "numpy_version": "test", "n": 0}))
    claim = {
        "id": "descriptive",
        "evidence_class": "exploratory reanalysis",
        "status": "exploratory",
        "statement": "A descriptive conditional response.",
        "boundary": "Dependence remains unresolved.",
        "assumptions": ["trusted decoding"],
        "acquisitions": ["acquired"],
        "evidence": [{"path": "analysis.json", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}],
        "documents": [],
        "gates": {"analysis": "replay"},
    }
    view = quantum_ledger.build(
        tmp_path,
        [claim],
        [{"id": "acquired"}, {"id": "uncited"}],
        [{"path": "results/run", "provider": "ibm", "claims": ["descriptive"]}],
        {"analysis": "replay command"},
        ["analysis.json", "results/run/raw/job/data.json", "results/unclassified.json"],
    )
    if view["gaps"]["unclaimed_acquisitions"] != ["uncited"]:
        raise RuntimeError("an acquisition without a claim disappears")
    if view["gaps"]["artifacts_without_claim_or_run_link"] != ["results/unclassified.json"]:
        raise RuntimeError("the denominator omits an unclassified artifact")
    raw = next(row for row in view["artifacts"] if row["raw_directory_member"])
    if raw["claim_bindings"] or raw["runs"] != ["results/run"]:
        raise RuntimeError("run ownership becomes a direct scientific citation")
    row = view["claims"][0]
    if row["numerical_replay"] != "not-run-by-ledger" or row["status"] != "exploratory":
        raise RuntimeError("a registered command promotes an exploratory observation")
    if view["sources"][0]["provenance"] != {"numpy_version": "test"}:
        raise RuntimeError("the source's library version is lost")
    if "Dependence remains unresolved." not in quantum_ledger.markdown(view):
        raise RuntimeError("the human-readable ledger omits the inference boundary")
