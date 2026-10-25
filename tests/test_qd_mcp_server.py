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


def fields(**specs: object) -> dict[str, object]:
    return {"name": "qpu:test", "type": "qpu", "specs": specs}


def test_record_fields_distinguish_absent_from_empty() -> None:
    belenos = qd_mcp_server.with_record_fields(
        fields(available_commands=["a"], constraints={"x": 1}, default_mitigations=[], known_mitigations=None)
    )
    states = belenos["record_fields"]
    check(states["commands"] == "absent", f"{states}")
    check(states["default_mitigations"] == "empty" and states["known_mitigations"] == "empty", f"{states}")
    check(states["available_commands"] == "present", f"{states}")
    check(states["architecture"] == "absent" and states["type"] == "absent", f"{states}")
    check(states["record_type"] == "present", f"{states}")


def test_record_fields_present_when_sent() -> None:
    out = qd_mcp_server.with_record_fields(
        fields(
            commands="c",
            available_commands=["a"],
            default_mitigations=["a"],
            known_mitigations=["a"],
            architecture="x",
            type="qpu",
        )
    )
    check(set(out["record_fields"].values()) == {"present"}, f"{out['record_fields']}")


def test_record_without_specs_reports_every_field_absent() -> None:
    out = qd_mcp_server.with_record_fields({})
    check(set(out["record_fields"].values()) == {"absent"}, f"{out['record_fields']}")


def test_platform_scrubs_forbidden_keys(monkeypatch: object) -> None:
    import asyncio

    leaky = fields(commands="c")
    leaky["creator_id"] = "u"
    leaky["specs"]["nested"] = [{"email": "a@b", "keep": 1}]  # type: ignore[index]
    monkeypatch.setattr(qd_mcp_server, "get", lambda route, auth=True: leaky)  # type: ignore[attr-defined]
    out = asyncio.run(qd_mcp_server.qd_platform("qpu:test"))
    check("creator_id" not in out, "a forbidden top-level key survived")
    check(out["specs"]["nested"] == [{"keep": 1}], f"{out['specs']}")
    check(out["record_fields"]["commands"] == "present", "scrub dropped a record field")


def planned(version_two: bool, basis: str) -> dict[str, object]:
    payload: dict[str, object] = {"computation": "c"} if version_two else {"command": "sample_count"}
    return {
        "case": "bdsc_qualification",
        "platform": "qpu:belenos",
        "payload_version_basis": basis,
        "body": {"payload": payload, "max_duration": 300},
        "body_sha256": "00",
    }


def test_plan_summary_reports_version_two_restored() -> None:
    out = qd_mcp_server.plan_summary(planned(True, "restored from docs/evidence/bdsc/inputs/receipt.json"))
    check(out["payload_version"] == 2 and out["payload_version_basis"].startswith("restored"), f"{out}")
    check("body" not in out and out["submitted"] is False and out["mitigations_key"] is False, f"{out}")


def test_plan_summary_reports_version_one() -> None:
    out = qd_mcp_server.plan_summary(planned(False, "absent"))
    check(out["payload_version"] == 1 and out["payload_version_basis"] == "absent", f"{out}")


def test_qd_plan_runs_plan_only_and_refuses_outside_paths(monkeypatch: object) -> None:
    import asyncio

    import pytest
    from mcp.server.fastmcp.exceptions import ToolError

    calls: list[tuple[object, ...]] = []

    def stub(path: Path, platform: str, *rest: float) -> dict[str, object]:
        calls.append((path, platform, *rest))
        return planned(True, "restored from stub")

    monkeypatch.setattr(qd_mcp_server, "plan", stub)  # type: ignore[attr-defined]
    case = "results/quandela/cases/bdsc_qualification/tc-def-e1"
    out = asyncio.run(qd_mcp_server.qd_plan(case, "qpu:belenos"))
    check(out["payload_version"] == 2 and len(calls) == 1, f"{out} {calls}")
    check(calls[0][0] == (Path(qd_mcp_server.__file__).resolve().parents[1] / case), f"{calls}")
    for outside in ("tests", "results/quandela/../ibm", "/etc", "results/quandela"):
        with pytest.raises(ToolError):
            asyncio.run(qd_mcp_server.qd_plan(outside, "qpu:belenos"))
    check(len(calls) == 1, "plan ran for a refused path")


def test_job_billing_applies_the_rule() -> None:
    row = {"price_per_shot": 1e-6}
    data = {
        "job_id": "j",
        "platform_name": "qpu:belenos",
        "status": "completed",
        "shots": 10000,
        "payload": {"max_shots": 20000},
        "start_time": "t",
        "duration": 13,
    }
    out = qd_mcp_server.job_billing(data, row, 1.0)
    check(out["charge_used"] == 1.01 and out["charge_ceiling"] == 1.02, f"{out}")
    cancelled = {"status": "canceled", "shots": None, "start_time": None, "duration": None}
    check(qd_mcp_server.job_billing(cancelled, row, 1.0)["charge_used"] == 0.0, "a job canceled before start billed")


def test_qd_job_billing_reads_data_and_price(monkeypatch: object) -> None:
    import asyncio

    routes: list[str] = []

    def stub(route: str, auth: bool = True) -> object:
        routes.append(route)
        if route.endswith("/data"):
            return {
                "job_id": "abcdef12",
                "platform_name": "sim:x",
                "status": "completed",
                "shots": 5,
                "creator_id": "u",
            }
        return [{"name": "sim:x", "type": "sim", "status": "available", "price_per_shot": 0.0, "max_duration": 300}]

    monkeypatch.setattr(qd_mcp_server, "get", stub)  # type: ignore[attr-defined]
    out = asyncio.run(qd_mcp_server.qd_job_billing("abcdef12"))
    check(out["charge_used"] == 1.0 and "creator_id" not in out, f"{out}")
    check(all("/cancel" not in r for r in routes), f"{routes}")
