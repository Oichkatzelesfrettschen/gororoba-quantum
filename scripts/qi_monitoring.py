"""Quantum Inspire public performance dashboards: per-qubit calibration series and backend-type status.

QuTech publishes one Grafana public dashboard per backend and a Status
dashboard (https://monitoring.qutech.support). The link service
dashboard.quantum-inspire.com redirects each dashboard name to its access
token; resolve() follows that redirect on every call, so a rotated token is
read from the provider rather than from this file. A Grafana public dashboard
serves its definition at GET /api/public/dashboards/TOKEN and one panel's
data at POST /api/public/dashboards/TOKEN/panels/ID/query. Neither needs an
account or credentials, and neither reaches the compute job manager API.

The backend dashboards carry Prometheus series per qubit (T1, T2 Ramsey,
T2 echo, initialization, readout, readout QND, single-qubit gate and Bell-state
error), each as a range panel and an instant "Latest" panel; the Status
dashboard carries platform_backendtypes_status per backend type. A panel whose
datasource fails returns its error per query reference, and a query whose
every reference fails raises, so a provider outage reaches the caller as an
error rather than as an empty series.

Usage: "$QI_PYTHON" scripts/qi_monitoring.py [DASHBOARD [PANEL_ID [HOURS]]]
"""

from __future__ import annotations

import datetime
import importlib
import json
import re
import sys
from typing import Any

LINKS = "https://dashboard.quantum-inspire.com"
GRAFANA = "https://monitoring.qutech.support"
# Each name the link service redirects to its own dashboard; "status" is the service's root link.
DASHBOARDS = {"status": "", "tuna-17": "tuna-17", "tuna-9": "tuna-9", "tuna-5": "tuna-5", "ry_emulator": "ry_emulator"}
TOKEN = re.compile(r"/public-dashboards/([0-9a-f]{32})")
# A dated line of a dashboard's text panel, such as "[2026-10-22] Tuna-17 is temporarily offline ...".
UPDATE = re.compile(r"^\[\d{4}-\d{2}-\d{2}[^\]]*\]\s")
MAX_HOURS = 24 * 30
MAX_POINTS = 1000
TIMEOUT_SECONDS = 30


class MonitoringError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()


def session() -> Any:
    # importlib keeps one typing outcome whether or not requests ships stubs.
    return importlib.import_module("requests").Session()


def resolve(name: str, http: Any) -> str:
    """The access token the link service names for a dashboard; only a redirect ending at the token is one."""
    if name not in DASHBOARDS:
        raise ValueError(f"dashboard must be one of {', '.join(DASHBOARDS)}, not {name!r}")
    response = http.get(f"{LINKS}/{DASHBOARDS[name]}", allow_redirects=False, timeout=TIMEOUT_SECONDS)
    location = response.headers.get("Location", "")
    # The service appends an unknown path to the Status token, so a trailing path names no dashboard.
    match = TOKEN.search(location)
    if response.status_code not in (301, 302, 307, 308) or match is None or location[match.end() :].split("?")[0]:
        raise MonitoringError(f"{LINKS}/{DASHBOARDS[name]} redirects to {location!r} (HTTP {response.status_code})")
    return match.group(1)


def _json(response: Any, what: str) -> Any:
    try:
        body = response.json()
    except ValueError as error:
        raise MonitoringError(f"{what}: HTTP {response.status_code}, not JSON") from error
    return body


def _message(body: Any) -> Any:
    return body.get("message", body) if isinstance(body, dict) else body


def panels_of(definition: dict[str, Any]) -> list[dict[str, Any]]:
    """Every panel of a dashboard definition, rows' nested panels included, in definition order."""
    found = []
    for panel in definition.get("panels") or []:
        found.append(panel)
        found.extend(panel.get("panels") or [])
    return found


def value_text(panel: dict[str, Any]) -> dict[str, str]:
    """The panel's value mappings as value -> text, such as the Status dashboard's 3 -> Offline."""
    mappings = panel.get("fieldConfig", {}).get("defaults", {}).get("mappings") or []
    return {
        value: option["text"]
        for mapping in mappings
        if mapping.get("type") == "value"
        for value, option in mapping.get("options", {}).items()
        if "text" in option
    }


def definition_of(name: str, http: Any) -> tuple[str, dict[str, Any]]:
    """The dashboard's access token and its public definition response."""
    token = resolve(name, http)
    response = http.get(f"{GRAFANA}/api/public/dashboards/{token}", timeout=TIMEOUT_SECONDS)
    body = _json(response, f"dashboard {name}")
    if response.status_code != 200 or not isinstance(body, dict) or "dashboard" not in body:
        raise MonitoringError(f"dashboard {name}: HTTP {response.status_code}: {_message(body)}")
    return token, dict(body)


def dashboard(name: str, http: Any | None = None) -> dict[str, Any]:
    """A dashboard's data panels and dated update notices, with the interval of the reads."""
    http = http or session()
    started = utc_now()
    token, body = definition_of(name, http)
    definition = body["dashboard"]
    data: list[dict[str, Any]] = []
    updates: list[str] = []
    for panel in panels_of(definition):
        if panel.get("type") == "text":
            content = panel.get("options", {}).get("content", "")
            updates.extend(line.strip() for line in content.splitlines() if UPDATE.match(line.strip()))
        elif panel.get("type") != "row":
            data.append(
                {
                    "id": panel["id"],
                    "title": panel.get("title", ""),
                    "type": panel.get("type"),
                    "value_text": value_text(panel),
                    "queries": [
                        {
                            "ref": target.get("refId"),
                            "legend": target.get("legendFormat"),
                            "instant": target.get("instant"),
                        }
                        for target in panel.get("targets", [])
                    ],
                }
            )
    return {
        "dashboard": name,
        "title": definition.get("title"),
        "token": token,
        "version": definition.get("version"),
        "updated": body.get("meta", {}).get("updated"),
        "panels": data,
        "updates": updates,
        "request_started_utc": started,
        "retrieved_utc": utc_now(),
    }


def series(frame: dict[str, Any]) -> list[dict[str, Any]]:
    """One data frame's value fields, each as its labels and (UTC time, value) points."""
    fields = frame["schema"]["fields"]
    values = frame["data"]["values"]
    times = next((column for field, column in zip(fields, values, strict=True) if field.get("type") == "time"), None)
    rows = []
    for field, column in zip(fields, values, strict=True):
        if field.get("type") == "time":
            continue
        stamps = times if times is not None else [None] * len(column)
        rows.append(
            {
                "name": field.get("config", {}).get("displayNameFromDS") or field.get("name"),
                "labels": field.get("labels") or {},
                "points": [
                    [
                        None
                        if stamp is None
                        else datetime.datetime.fromtimestamp(stamp / 1000, datetime.UTC).isoformat(),
                        value,
                    ]
                    for stamp, value in zip(stamps, column, strict=True)
                ],
            }
        )
    return rows


def query(name: str, panel_id: int, hours: float = 6.0, http: Any | None = None) -> dict[str, Any]:
    """One panel's series over the last hours, each query reference with its status and any datasource error."""
    if not 0 < hours <= MAX_HOURS:
        raise ValueError(f"hours must lie in (0, {MAX_HOURS}]")
    http = http or session()
    started = utc_now()
    token, body = definition_of(name, http)
    panel = next((found for found in panels_of(body["dashboard"]) if found.get("id") == panel_id), None)
    if panel is None or panel.get("type") in ("text", "row"):
        raise ValueError(f"dashboard {name} has no data panel {panel_id}")
    request = {
        "intervalMs": max(1000, int(hours * 3_600_000 / MAX_POINTS)),
        "maxDataPoints": MAX_POINTS,
        "timeRange": {"from": f"now-{int(hours * 3600)}s", "to": "now", "timezone": "utc"},
    }
    response = http.post(
        f"{GRAFANA}/api/public/dashboards/{token}/panels/{panel_id}/query", json=request, timeout=TIMEOUT_SECONDS
    )
    body = _json(response, f"panel {panel_id} of {name}")
    if not isinstance(body, dict) or "results" not in body:
        raise MonitoringError(f"panel {panel_id} of {name}: HTTP {response.status_code}: {_message(body)}")
    references = []
    for ref, result in sorted(body["results"].items()):
        frames = result.get("frames") or []
        references.append(
            {
                "ref": ref,
                "status": result.get("status"),
                "error": result.get("error"),
                "series": [row for frame in frames for row in series(frame)],
            }
        )
    if references and all(reference["error"] for reference in references):
        raise MonitoringError(f"panel {panel_id} of {name}: every query failed: {references[0]['error']}")
    return {
        "dashboard": name,
        "panel_id": panel_id,
        "title": panel.get("title", ""),
        "value_text": value_text(panel),
        "hours": hours,
        "references": references,
        "request_started_utc": started,
        "retrieved_utc": utc_now(),
    }


def main(argv: list[str]) -> int:
    name = argv[0] if argv else "status"
    try:
        result = (
            dashboard(name) if len(argv) < 2 else query(name, int(argv[1]), float(argv[2]) if len(argv) > 2 else 6.0)
        )
    except (MonitoringError, ValueError) as error:
        print(f"qi_monitoring: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
