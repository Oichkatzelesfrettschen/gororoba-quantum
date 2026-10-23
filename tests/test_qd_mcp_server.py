"""Contract for qd_mcp_server.with_bulk_presence: a default read reports each bulk spec as a stripped
marker or as absent, and bulk_fields states presence on every read."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import qd_mcp_server  # noqa: E402

ARCHITECTURE = {"chip": [1, 2, 3]}


def record(*bulk: str) -> dict[str, object]:
    specs: dict[str, object] = {"constraints": {"max_photon_count": 6}}
    if "architecture" in bulk:
        specs["architecture"] = ARCHITECTURE
    if "documentation" in bulk:
        specs["documentation"] = "<p>docs</p>"
    return {"name": "qpu:test", "specs": specs}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_default_read_marks_present_and_leaves_absent_absent() -> None:
    out = qd_mcp_server.with_bulk_presence(record("architecture"), include_bulk=False)
    check(out["bulk_fields"] == {"architecture": "present", "documentation": "absent"}, f"{out['bulk_fields']}")
    specs = out["specs"]
    check(specs["architecture"] == {"stripped": True, "chars": len(json.dumps(ARCHITECTURE))}, f"{specs}")
    check("documentation" not in specs, "an absent field gained a key")
    check(specs["constraints"] == {"max_photon_count": 6}, "a non-bulk spec changed")


def test_include_bulk_keeps_values_and_reports_presence() -> None:
    source = record("architecture", "documentation")
    out = qd_mcp_server.with_bulk_presence(source, include_bulk=True)
    check(out["bulk_fields"] == {"architecture": "present", "documentation": "present"}, f"{out['bulk_fields']}")
    check(out["specs"] == source["specs"], "include_bulk altered specs")


def test_record_without_specs_reports_absent() -> None:
    out = qd_mcp_server.with_bulk_presence({"name": "x"}, include_bulk=False)
    check(out == {"name": "x", "bulk_fields": {"architecture": "absent", "documentation": "absent"}}, f"{out}")


def test_null_architecture_reads_empty() -> None:
    out = qd_mcp_server.with_bulk_presence({"specs": {"architecture": None, "documentation": ""}}, False)
    check(out["bulk_fields"] == {"architecture": "empty", "documentation": "empty"}, f"{out['bulk_fields']}")
    check(out["specs"] == {"architecture": None, "documentation": ""}, "an empty bulk value was replaced by a marker")
