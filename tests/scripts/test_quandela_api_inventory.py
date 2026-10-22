"""API traversal preserves every operation while classifying state and credit effects."""

import hashlib
import io
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest
import quandela_api_inventory as api
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


@pytest.mark.parametrize("name", ["cloud", "toolbox", "account"])
def test_historical_raw_capture_rejects_matching_inventory_rewrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    source = Path(__file__).resolve().parents[2] / "docs/evidence/quandela/input-port-api-audit"
    target = tmp_path / "capture"
    shutil.copytree(source, target)
    path = target / f"{name}-openapi.json"
    document = json.loads(path.read_bytes())
    document["info"]["version"] = document["info"].get("version", "") + "-mutated"
    data = (json.dumps(document) + "\n").encode()
    path.write_bytes(data)
    record = api.inventory(document, strict_references=False)
    record.update(source_url=api.DOCUMENTS[name], source_sha256=hashlib.sha256(data).hexdigest())
    (target / f"{name}-inventory.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    monkeypatch.setattr(sys, "argv", ["quandela_api_inventory", str(target)])
    with pytest.raises(ValueError, match="capture.*digest|capture.*bytes"):
        api.main()


def test_successor_capture_admits_new_bundle_and_replays_offline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import capture_qd_docs

    raw = b'{"info":{"version":"successor"},"paths":{}}'

    def response(url: str, timeout: int) -> io.BytesIO:
        if url not in api.DOCUMENTS.values() or timeout != 30:
            raise AssertionError("unexpected public capture request")
        return io.BytesIO(raw)

    monkeypatch.setattr(api.urllib.request, "urlopen", response)
    monkeypatch.setattr(
        capture_qd_docs,
        "bundle",
        lambda url: ("https://cloud.quandela.com/webide/assets/successor.js", b'request$1.get("/api/successor");'),
    )
    target = tmp_path / "successor"
    monkeypatch.setattr(sys, "argv", ["quandela_api_inventory", str(target), "--capture"])
    if api.main() != 0:
        raise AssertionError("fresh public capture failed")
    monkeypatch.setattr(sys, "argv", ["quandela_api_inventory", str(target)])
    if api.main() != 0:
        raise AssertionError("the successor capture failed its offline replay")
    portal = target / "portal-route-map.json"
    retained_portal = portal.read_bytes()
    portal.write_bytes(retained_portal.replace(b"successor.js", b"mutated.js"))
    with pytest.raises(ValueError, match="portal"):
        api.main()
    portal.write_bytes(retained_portal)
    path = target / "cloud-openapi.json"
    path.write_bytes(raw + b" ")
    record = api.inventory(json.loads(path.read_bytes()), strict_references=False)
    record.update(source_url=api.DOCUMENTS["cloud"], source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (target / "cloud-inventory.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="capture.*digest|capture.*bytes"):
        api.main()


def test_capture_requires_fresh_destination_before_network(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "retained.txt").write_text("preserve")

    def forbidden(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("existing capture directory crossed the network boundary")

    monkeypatch.setattr(api.urllib.request, "urlopen", forbidden)
    monkeypatch.setattr(sys, "argv", ["quandela_api_inventory", str(tmp_path), "--capture"])
    with pytest.raises(ValueError, match="new|empty|fresh"):
        api.main()


def test_historical_code_pins_override_a_rewritten_local_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = Path(__file__).resolve().parents[2] / "docs/evidence/quandela/input-port-api-audit"
    target = tmp_path / "capture"
    shutil.copytree(source, target)
    (target / "cloud-openapi.json").write_bytes(b'{"info":{},"paths":{}}')
    digests = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [*target.glob("*-openapi.json"), target / "portal-route-map.json"]
    }
    (target / "capture-sha256.json").write_text(
        json.dumps({"schema": "quandela-api-capture-sha256-v1", "sha256": digests})
    )
    monkeypatch.setattr(api, "HISTORICAL_DIRECTORY", target)
    monkeypatch.setattr(sys, "argv", ["quandela_api_inventory", str(target)])
    with pytest.raises(ValueError, match="capture.*digest|capture.*bytes"):
        api.main()
