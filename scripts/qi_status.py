"""Quantum Inspire status document: backend instances, queues, public status history, notices and calibration reach.

One pass joins the two sources that report on the platform. Every request it sends for data is a read; the one
write it can cause is qi_platform.Client's own token exchange, which runs when the stored access token is within
its refresh margin and which --public-only never reaches.

- the compute API (an account's bearer token, GET only): every backend type with its status and enable flag, each
  physical instance with its status, message and heartbeat, the queue of each type counted over all users and
  over this account, its job limits, and a digest of its published definition (gate set, topology, compiler
  passes) as served, so a changed device definition shows as a changed digest;
- QuTech's public Grafana dashboards (no account, through qi_monitoring.py): the Status dashboard's value per
  backend type with its history, and for each backend dashboard its dated notices and whether its calibration
  datasource answers. While it answers, the document carries the latest per-qubit value of every "Latest"
  panel, and each panel query that fails or holds no value is named with its layer (`history_reach`,
  `latest_unread`).

Each section fails alone: a section that cannot be read holds `{"error": TEXT}` and the others stay. The document
names no team, member or user, and every error text passes redact(), which replaces network addresses and
token-shaped strings.

The link service is asked once per dashboard, LINK_PAUSE_SECONDS apart. Measured 2026-11-15: of 23 link requests
sent inside 5 s the first four were redirected and the other nineteen drew HTTP 428, while requests
3 s and 8 s apart were all redirected; hypothesis: a burst limit. A dashboard whose first "Latest" panel fails is
not asked for the others, since every panel of a backend dashboard names one datasource.

A public dashboard answers over its own stored time range whatever range the request names (measured 2026-11-15
on the Status dashboard, whose definition holds `now-6h` to `now`: requests naming 1 h, 24 h and 720 h each
returned points spanning the same 6 h, and only intervalMs changed their spacing). The status history therefore
covers that window, which the document reports as `window`; a longer record is the union of successive reads.

Usage: "$QI_PYTHON" scripts/qi_status.py [--public-only]
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

# python -I leaves the script directory off sys.path; the sibling modules load from it.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import qi_monitoring as monitoring  # noqa: E402

SCHEMA = "qi-status-v1"
BACKEND_DASHBOARDS = ("tuna-17", "tuna-9", "tuna-5", "ry_emulator")
LINK_PAUSE_SECONDS = 3.0
PANEL_PAUSE_SECONDS = 1.0
# Spacing asked of the status history; the Status datasource answered at 20 s spacing when asked for less.
HISTORY_INTERVAL_MS = 60_000
ERROR_LENGTH = 240
TYPE_FIELDS = (
    "id",
    "name",
    "identifier",
    "is_hardware",
    "nqubits",
    "status",
    "enabled",
    "messages",
    "protocol_version",
)
LIMIT_FIELDS = (
    "default_number_of_shots",
    "max_number_of_shots",
    "job_execution_time_limit",
    "max_jobs_per_batch_job",
    "batchjobs_per_queue_limit",
)
DEFINITION_FIELDS = ("gateset", "topology", "default_compiler_config", "features", "supports_raw_data", "image_id")
QUEUE_FIELDS = (
    "number_of_jobs_in_queue",
    "min_wait_time_in_queue_secs",
    "avg_wait_time_in_queue_secs",
    "max_wait_time_in_queue_secs",
)
# What one section's read can raise: qi_platform.PlatformError and MonitoringError are RuntimeErrors, a transport
# failure of requests is an OSError, and a response body of another shape than the one read here raises one of
# the last five.
READ_ERRORS = (RuntimeError, OSError, KeyError, TypeError, ValueError, AttributeError, IndexError)
# IPv4 addresses, bracketed IPv6 addresses and bare ones of three or more colons (a clock time holds two), and
# JSON web tokens, as they appear in transport and provider errors.
ADDRESS = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b|\[[0-9a-fA-F:.]+\]|\b(?:[0-9a-fA-F]{0,4}:){3,7}[0-9a-fA-F]{0,4}")
TOKEN = re.compile(r"\beyJ[\w-]+\.[\w-]+\.[\w-]+")

Pause = Callable[[float], None]


def redact(text: object) -> str:
    """Error text cut to ERROR_LENGTH with each network address and token-shaped string replaced by a marker."""
    return TOKEN.sub("<token>", ADDRESS.sub("<address>", str(text)))[:ERROR_LENGTH]


def _error(error: BaseException) -> dict[str, str]:
    return {"error": redact(f"{type(error).__name__}: {error}")}


def _instance(row: dict[str, Any], now: datetime.datetime) -> dict[str, Any]:
    beat = datetime.datetime.fromisoformat(row["last_heartbeat"].replace("Z", "+00:00"))
    return {
        "name": row["name"],
        "backend_type_id": row["backend_type_id"],
        "status": row["status"],
        "message": (row.get("message") or {}).get("content", ""),
        "last_heartbeat": row["last_heartbeat"],
        "heartbeat_age_seconds": round((now - beat).total_seconds(), 1),
    }


def account(client: Any, now: datetime.datetime | None = None) -> dict[str, Any]:
    """Backend types with their instances and both queue scopes.

    An instance whose type GET /backend_types/ leaves out is `unlisted` and keeps its backend_type_id: the list
    names the reason for no absence, so the row claims none.
    """
    types = client.pages("/backend_types/")
    instances = client.pages("/backends")
    # The reference time follows the instance read, so a heartbeat written during the reads has a nonnegative age.
    now = now or datetime.datetime.now(datetime.UTC)
    rows = []
    for backend_type in types:
        row = {key: backend_type.get(key) for key in TYPE_FIELDS}
        row["limits"] = {key: backend_type.get(key) for key in LIMIT_FIELDS}
        definition = json.dumps({key: backend_type.get(key) for key in DEFINITION_FIELDS}, sort_keys=True)
        row["definition_sha256"] = hashlib.sha256(definition.encode()).hexdigest()
        for scope, user_only in (("queue_all", False), ("queue_own", True)):
            queue = client.get(f"/backend_types/{backend_type['id']}/queue", user_only=user_only)
            row[scope] = {key: queue.get(key) for key in QUEUE_FIELDS}
        row["instances"] = [_instance(item, now) for item in instances if item["backend_type_id"] == backend_type["id"]]
        rows.append(row)
    listed = {backend_type["id"] for backend_type in types}
    return {
        "backend_types": rows,
        "unlisted": [_instance(item, now) for item in instances if item["backend_type_id"] not in listed],
        "read_utc": now.isoformat(),
    }


def _panel(http: Any, token: str, panel_id: int, interval_ms: int = HISTORY_INTERVAL_MS) -> tuple[int, Any]:
    """One panel query's HTTP status and decoded body; a body that is not JSON decodes to None."""
    # The dashboard's stored range governs the answer; timeRange is sent because the route requires the field.
    request = {
        "intervalMs": interval_ms,
        "maxDataPoints": monitoring.MAX_POINTS,
        "timeRange": {"from": "now-6h", "to": "now", "timezone": "utc"},
    }
    url = f"{monitoring.GRAFANA}/api/public/dashboards/{token}/panels/{panel_id}/query"
    try:
        response = http.post(url, json=request, timeout=monitoring.TIMEOUT_SECONDS)
    except OSError as error:
        raise monitoring.MonitoringError(f"POST {url}: {type(error).__name__}: {error}") from error
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, None


def _series(body: Any) -> list[dict[str, Any]]:
    results = body.get("results", {}) if isinstance(body, dict) else {}
    return [
        row
        for _, result in sorted(results.items())
        for frame in result.get("frames") or []
        for row in monitoring.series(frame)
    ]


def _name(row: dict[str, Any]) -> str:
    return str(row["labels"].get("name") or row["name"])


def _instant(panel: dict[str, Any]) -> bool:
    return any(target.get("instant") for target in panel.get("targets", []))


def _data_panels(definition: dict[str, Any]) -> list[dict[str, Any]]:
    return [panel for panel in monitoring.panels_of(definition) if panel.get("type") not in ("text", "row")]


def transitions(points: list[list[Any]]) -> list[list[Any]]:
    """The points at which the value differs from the point before, so a flat week reads as one row.

    Points are read in time order whatever order the frame holds; a point with no stamp or no value is dropped,
    and of several points at one stamp the last in the frame stands.
    """
    latest: dict[datetime.datetime, list[Any]] = {}
    for stamp, value in points:
        if stamp is not None and value is not None:
            latest[datetime.datetime.fromisoformat(stamp)] = [stamp, value]
    kept: list[list[Any]] = []
    for _, point in sorted(latest.items()):
        if not kept or kept[-1][1] != point[1]:
            kept.append(point)
    return kept


def platform_status(http: Any, pause: Pause = time.sleep) -> dict[str, Any]:
    """The Status dashboard: each backend type's latest value and its value changes over the dashboard's window."""
    token, body = monitoring.definition_of("status", http)
    panels = _data_panels(body["dashboard"])
    latest = next((panel for panel in panels if _instant(panel) or panel.get("type") == "stat"), None)
    ranged = next((panel for panel in panels if panel.get("type") == "timeseries"), None)
    if latest is None:
        raise monitoring.MonitoringError("the Status dashboard holds no instant panel")
    _, answer = _panel(http, token, latest["id"])
    current = {
        _name(row): row["points"][-1] for row in _series(answer) if row["points"] and row["points"][-1][1] is not None
    }
    if not current:
        raise monitoring.MonitoringError(f"Status panel {latest['id']} returned no series")
    history: dict[str, list[list[Any]]] = {}
    history_reach: dict[str, Any] = {"state": "no-panels"}
    if ranged is not None:
        pause(PANEL_PAUSE_SECONDS)
        # A failed history query is no empty history: its layer and error text travel beside the series, and the
        # current values already read stay.
        history_reach, answer = _read_panel(http, token, ranged["id"])
        if history_reach["state"] == "data":
            history = {_name(row): transitions(row["points"]) for row in _series(answer)}
    return {
        "value_text": monitoring.value_text(latest),
        "current": {name: {"utc": point[0], "value": point[1]} for name, point in sorted(current.items())},
        "window": body["dashboard"].get("time"),
        "history": history,
        "history_reach": history_reach,
        "version": body["dashboard"].get("version"),
        "updated": body.get("meta", {}).get("updated"),
    }


def _read_panel(http: Any, token: str, panel_id: int) -> tuple[dict[str, Any], Any]:
    """One panel's reach and body; a transport or shape failure reads as state `unread` with its redacted text."""
    try:
        status, body = _panel(http, token, panel_id)
        return _reach(status, body), body
    except READ_ERRORS as error:
        return {"state": "unread", **_error(error)}, None


def _reach(status: int, body: Any) -> dict[str, Any]:
    """Classify one panel answer: data, empty, datasource-error (Grafana reached, its datasource not) or http-error."""
    results = body.get("results") if isinstance(body, dict) else None
    if not isinstance(results, dict) or not results:
        message = body.get("message") if isinstance(body, dict) else None
        return {"state": "http-error", "http_status": status, "error": redact(message or "no query result")}
    errors = [str(result["error"]) for result in results.values() if result.get("error")]
    if len(errors) == len(results):
        return {"state": "datasource-error", "http_status": status, "error": redact(errors[0])}
    return {"state": "data" if any(row["points"] for row in _series(body)) else "empty", "http_status": status}


def backend_dashboard(name: str, http: Any, pause: Pause = time.sleep) -> dict[str, Any]:
    """One backend dashboard's notices and calibration reach, with every "Latest" panel's values while it has data."""
    token, body = monitoring.definition_of(name, http)
    definition = body["dashboard"]
    notices = [
        line.strip()
        for panel in monitoring.panels_of(definition)
        if panel.get("type") == "text"
        for line in panel.get("options", {}).get("content", "").splitlines()
        if monitoring.UPDATE.match(line.strip())
    ]
    panels = _data_panels(definition)
    latest_panels = [panel for panel in panels if _instant(panel)] or panels
    found: dict[str, Any] = {
        "title": definition.get("title"),
        "version": definition.get("version"),
        "updated": body.get("meta", {}).get("updated"),
        "notices": notices,
        "data_panels": len(panels),
    }
    if not latest_panels:
        return {**found, "calibration": {"state": "no-panels"}}
    latest: dict[str, list[dict[str, Any]]] = {}
    unread: dict[str, dict[str, Any]] = {}
    for index, panel in enumerate(latest_panels):
        if index:
            pause(PANEL_PAUSE_SECONDS)
        reach, answer = _read_panel(http, token, panel["id"])
        title = panel.get("title", str(panel["id"]))
        if index == 0:
            found["calibration"] = reach
            if reach["state"] != "data":
                return found
        elif reach["state"] != "data":
            # A later panel that fails or holds no value is named with its layer, apart from the panels that read.
            unread[title] = reach
            continue
        latest[title] = [
            {"name": row["name"], "labels": row["labels"], "utc": row["points"][-1][0], "value": row["points"][-1][1]}
            for row in _series(answer)
            if row["points"]
        ]
    found["latest"] = latest
    found["latest_unread"] = unread
    return found


def document(
    client: Any | None,
    http: Any | None = None,
    pause: Pause = time.sleep,
    account_error: str = "no account read was requested",
) -> dict[str, Any]:
    """The whole status document; client None leaves the account section as account_error."""
    http = http or monitoring.session()
    found: dict[str, Any] = {"schema": SCHEMA, "request_started_utc": monitoring.utc_now()}
    if client is None:
        found["account"] = {"error": redact(account_error)}
    else:
        try:
            found["account"] = account(client)
        except Exception as error:  # noqa: BLE001 - the SDK's authorization error derives from Exception alone
            found["account"] = _error(error)
    try:
        found["platform"] = platform_status(http, pause)
    except READ_ERRORS as error:
        found["platform"] = _error(error)
    dashboards: dict[str, Any] = {}
    for name in BACKEND_DASHBOARDS:
        pause(LINK_PAUSE_SECONDS)
        try:
            dashboards[name] = backend_dashboard(name, http, pause)
        except READ_ERRORS as error:
            dashboards[name] = _error(error)
    found["dashboards"] = dashboards
    found["retrieved_utc"] = monitoring.utc_now()
    return found


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--public-only", action="store_true", help="read the public dashboards without the account")
    args = parser.parse_args(argv)
    client = None
    reason = "no account read was requested"
    if not args.public_only:
        try:
            from qi_platform import Client  # noqa: PLC0415 - the public read needs no SDK

            client = Client()
        # The SDK's authorization error derives from Exception alone, and importing qi_platform exits on an
        # environment value it rejects (QI_HARDWARE_PAUSE_SECONDS); both leave the public sections readable.
        except (Exception, SystemExit) as error:  # noqa: BLE001
            reason = f"{type(error).__name__}: {error}"
    print(json.dumps(document(client, account_error=reason), indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
