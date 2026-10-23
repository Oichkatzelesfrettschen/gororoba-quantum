"""Contract for scripts/qi_monitoring.py against a fake transport shaped like QuTech's Grafana public API:
the link redirect names the token, panels and dated notices come from the definition, value mappings travel
with the series, and a query whose every reference fails raises.
"""

from __future__ import annotations

from typing import Any

import pytest
import qi_monitoring as monitoring

TOKEN = "0123456789abcdef0123456789abcdef"
DEFINITION = {
    "dashboard": {
        "title": "Status",
        "version": 3,
        "panels": [
            {
                "id": 9,
                "type": "text",
                "options": {"content": "## Updates\n[2026-10-22] Offline for maintenance.\nlink"},
            },
            {
                "id": 1,
                "type": "stat",
                "title": "Backend types",
                "fieldConfig": {"defaults": {"mappings": [{"type": "value", "options": {"3": {"text": "Offline"}}}]}},
                "targets": [{"refId": "A", "legendFormat": "{{name}}", "instant": True}],
            },
        ],
    },
    "meta": {"updated": "2026-10-22T16:51:40Z"},
}
FRAME = {
    "schema": {
        "fields": [
            {"name": "Time", "type": "time"},
            {"name": "platform_backendtypes_status", "type": "number", "labels": {"name": "Tuna-9"}},
        ]
    },
    "data": {"values": [[1792703520000], [3]]},
}


class Response:
    def __init__(self, status: int, body: Any = None, location: str = "") -> None:
        self.status_code = status
        self.body = body
        self.headers = {"Location": location} if location else {}

    def json(self) -> Any:
        if self.body is None:
            raise ValueError("no JSON")
        return self.body


class Transport:
    def __init__(self, location: str, results: dict[str, Any]) -> None:
        self.location = location
        self.results = results
        self.posted: list[dict[str, Any]] = []

    def get(self, url: str, **_options: Any) -> Response:
        if url.startswith(monitoring.LINKS):
            return Response(301, location=self.location)
        return Response(200, DEFINITION)

    def post(self, url: str, json: dict[str, Any], **_options: Any) -> Response:
        self.posted.append({"url": url, **json})
        return Response(400 if all(r.get("error") for r in self.results.values()) else 200, {"results": self.results})


def test_dashboard_reads_panels_mappings_and_notices() -> None:
    http = Transport(f"{monitoring.GRAFANA}/public-dashboards/{TOKEN}", {})
    found = monitoring.dashboard("status", http)
    if found["token"] != TOKEN or found["updates"] != ["[2026-10-22] Offline for maintenance."]:
        raise AssertionError(found)
    if found["panels"] != [
        {
            "id": 1,
            "title": "Backend types",
            "type": "stat",
            "value_text": {"3": "Offline"},
            "queries": [{"ref": "A", "legend": "{{name}}", "instant": True}],
        }
    ]:
        raise AssertionError(found["panels"])


def test_query_returns_series_with_utc_points() -> None:
    http = Transport(f"{monitoring.GRAFANA}/public-dashboards/{TOKEN}", {"A": {"status": 200, "frames": [FRAME]}})
    found = monitoring.query("status", 1, 2.0, http)
    reference = found["references"][0]
    if reference["series"] != [
        {
            "name": "platform_backendtypes_status",
            "labels": {"name": "Tuna-9"},
            "points": [["2026-10-22T21:12:00+00:00", 3]],
        }
    ]:
        raise AssertionError(reference)
    if found["value_text"] != {"3": "Offline"} or http.posted[0]["timeRange"]["from"] != "now-7200s":
        raise AssertionError(found)
    if not http.posted[0]["url"].endswith(f"/api/public/dashboards/{TOKEN}/panels/1/query"):
        raise AssertionError(http.posted)


def test_outage_unknown_panel_and_foreign_redirect_raise() -> None:
    down = {"A": {"status": 502, "error": "dial tcp: i/o timeout"}}
    with pytest.raises(monitoring.MonitoringError, match="every query failed: dial tcp"):
        monitoring.query("status", 1, http=Transport(f"{monitoring.GRAFANA}/public-dashboards/{TOKEN}", down))
    with pytest.raises(ValueError, match="no data panel 9"):
        monitoring.query("status", 9, http=Transport(f"{monitoring.GRAFANA}/public-dashboards/{TOKEN}", down))
    # The link service appends an unknown path to the Status token; that redirect names no dashboard.
    with pytest.raises(monitoring.MonitoringError, match="redirects to"):
        monitoring.dashboard("tuna-17", Transport(f"{monitoring.GRAFANA}/public-dashboards/{TOKEN}/tuna-17", {}))
    with pytest.raises(ValueError, match="dashboard must be one of"):
        monitoring.dashboard("tuna-99", Transport("", {}))
    with pytest.raises(ValueError, match="hours must lie"):
        monitoring.query("status", 1, 0.0, Transport("", {}))


def test_dashboard_without_panels_reads_empty() -> None:
    if monitoring.panels_of({"panels": None}) != [] or monitoring.panels_of(
        {"panels": [{"id": 1, "panels": None}]}
    ) != [{"id": 1, "panels": None}]:
        raise AssertionError("a null panel list did not read as empty")


class Unreachable:
    def get(self, url: str, **_options: Any) -> Response:
        raise ConnectionError(f"name resolution failed for {url}")

    post = get


def test_transport_failure_raises_monitoring_error_and_cli_exits_1(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(
        monitoring.MonitoringError, match="GET https://dashboard.quantum-inspire.com/tuna-9: ConnectionError"
    ):
        monitoring.dashboard("tuna-9", Unreachable())
    monkeypatch.setattr(monitoring, "session", Unreachable)
    if monitoring.main(["status", "1"]) != 1 or "ConnectionError" not in capsys.readouterr().err:
        raise AssertionError("the CLI did not report a transport failure as its one-line error")
