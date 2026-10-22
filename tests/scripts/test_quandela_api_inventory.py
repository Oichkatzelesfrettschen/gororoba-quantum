"""API traversal preserves every operation while classifying state and credit effects."""

import shutil
import sys
from pathlib import Path
from typing import Any

import pytest
from quandela_api_inventory import inventory


def test_api_inventory_keeps_charged_gets_separate_from_observations() -> None:
    document: dict[str, Any] = {
        "openapi": "3.0.0",
        "info": {"version": "test"},
        "paths": {
            "/api/jobs": {"post": {"responses": {"200": {"$ref": "#/components/schemas/Receipt"}}}},
            "/api/jobs/{job_id}/status": {"get": {}},
            "/qt/qrng/bytes": {"get": {}},
            "/api/tokens": {"get": {}, "post": {}},
            "/api/logout": {"get": {}},
        },
        "components": {"schemas": {"Receipt": {"type": "object"}}},
    }
    result = inventory(document)
    rows = {(row["method"], row["path"]): row for row in result["operations"]}
    if len(rows) != 6 or rows["GET", "/qt/qrng/bytes"]["effect"] != "potentially-charged-read":
        raise RuntimeError("a GET QRNG operation must remain charged and the inventory must retain every method")
    if rows["GET", "/api/tokens"]["effect"] != "credential-read":
        raise RuntimeError("token enumeration must remain separate from ordinary status reads")
    if rows["POST", "/api/jobs"]["effect"] != "external-mutation":
        raise RuntimeError("job creation must remain an external mutation")
    if rows["GET", "/api/logout"]["effect"] != "session-mutation":
        raise RuntimeError("a GET logout changes the session and must never enter the read-only probe set")
    document["components"]["schemas"] = {}
    with pytest.raises(ValueError, match="reference"):
        inventory(document)


def test_portal_inventory_retains_methods_and_dynamic_route_literals() -> None:
    from quandela_api_inventory import portal_routes

    source = 'request$1.get("/api/jobs/page");request$1.post(`/api/jobs/${id}/cancel`);'
    record = portal_routes(source.encode(), "https://cloud.quandela.com/webide/assets/test.js")
    actual = [(row["method"], row["literal"]) for row in record["routes"]]
    if actual != [("GET", "/api/jobs/page"), ("POST", "/api/jobs/${id}/cancel")]:
        raise RuntimeError("the lexical inventory must preserve each method and the unresolved template literal")


def test_offline_api_replay_rejects_a_changed_portal_map(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from quandela_api_inventory import main

    source = Path(__file__).resolve().parents[2] / "docs/evidence/quandela/input-port-api-audit"
    target = tmp_path / "capture"
    shutil.copytree(source, target)
    portal = target / "portal-route-map.json"
    portal.write_bytes(portal.read_bytes().replace(b'"GET"', b'"PUT"', 1))
    monkeypatch.setattr(sys, "argv", ["quandela_api_inventory", str(target)])
    with pytest.raises(ValueError, match="portal"):
        main()
