"""Contract for scripts/qi_status.py against a fake compute client and a fake Grafana transport: one link request
per dashboard, sections that fail alone, queue scopes kept apart, and calibration reach classified per dashboard.
"""

from __future__ import annotations

import datetime
import json
import sys
from typing import Any

import pytest
import qi_monitoring as monitoring
import qi_status as status

NOW = datetime.datetime(2026, 11, 15, 16, 31, 20, tzinfo=datetime.UTC)
TOKENS = {name: f"{index:032x}" for index, name in enumerate(monitoring.DASHBOARDS)}


def frame(name: str, stamps: list[int], values: list[float]) -> dict[str, Any]:
    fields = [{"name": "Time", "type": "time"}, {"name": "v", "type": "number", "labels": {"name": name}}]
    return {"schema": {"fields": fields}, "data": {"values": [stamps, values]}}


STATUS_DEFINITION = {
    "dashboard": {
        "version": 2,
        "time": {"from": "now-6h", "to": "now"},
        "panels": [
            {
                "id": 1,
                "type": "stat",
                "fieldConfig": {"defaults": {"mappings": [{"type": "value", "options": {"3": {"text": "Offline"}}}]}},
                "targets": [{"refId": "A", "instant": True}],
            },
            {"id": 2, "type": "timeseries", "targets": [{"refId": "A"}]},
        ],
    },
    "meta": {"updated": "2026-07-24T16:57:27Z"},
}
BACKEND_DEFINITION = {
    "dashboard": {
        "title": "Tuna-17",
        "version": 28,
        "panels": [
            {"id": 1, "type": "text", "options": {"content": "## Updates\n[2026-10-22] Data withheld.\ntext"}},
            {"id": 2, "type": "timeseries", "title": "T1", "targets": [{"refId": "A"}, {"refId": "B"}]},
            {"id": 3, "type": "barchart", "title": "Latest T1", "targets": [{"refId": "A", "instant": True}]},
            {"id": 5, "type": "barchart", "title": "Latest T2R", "targets": [{"refId": "A", "instant": True}]},
        ],
    },
    "meta": {"updated": "2026-10-26T11:54:58Z"},
}
DOWN = {"results": {"A": {"status": 502, "error": "dial tcp 192.0.2.7:443: i/o timeout"}}}


class Response:
    def __init__(self, status_code: int, body: Any = None, location: str = "") -> None:
        self.status_code = status_code
        self.body = body
        self.headers = {"Location": location} if location else {}

    def json(self) -> Any:
        if self.body is None:
            raise ValueError("no JSON")
        return self.body


class Transport:
    """Grafana with a per-dashboard panel answer; `refuse` names dashboards the link service answers with 428."""

    def __init__(self, answers: dict[str, tuple[int, Any]], refuse: tuple[str, ...] = ()) -> None:
        self.answers = answers
        self.refuse = refuse
        self.links: list[str] = []
        self.posted: list[tuple[str, int]] = []

    def get(self, url: str, **_options: Any) -> Response:
        if url.startswith(monitoring.LINKS):
            name = url.rsplit("/", 1)[1] or "status"
            self.links.append(name)
            if name in self.refuse:
                return Response(428)
            return Response(301, location=f"{monitoring.GRAFANA}/public-dashboards/{TOKENS[name]}")
        name = next(key for key, token in TOKENS.items() if url.endswith(token))
        return Response(200, STATUS_DEFINITION if name == "status" else BACKEND_DEFINITION)

    def post(self, url: str, **_options: Any) -> Response:
        name = next(key for key, token in TOKENS.items() if token in url)
        panel = int(url.split("/panels/")[1].split("/")[0])
        self.posted.append((name, panel))
        if name == "status":
            stamps = [1792703520000, 1792703580000, 1792703640000, 1792703700000]
            values = [3.0] if panel == 1 else [2.0, 2.0, 3.0, 3.0]
            return Response(
                200, {"results": {"A": {"status": 200, "frames": [frame("Tuna-9", stamps[: len(values)], values)]}}}
            )
        return Response(*self.answers[name])


class Client:
    def __init__(self) -> None:
        self.asked: list[tuple[str, dict[str, Any]]] = []
        self.gateset = ["CZ"]

    def pages(self, path: str) -> list[dict[str, Any]]:
        self.asked.append((path, {}))
        if path == "/backend_types/":
            backend_type = {"id": 7, "name": "Tuna-17", "identifier": "tuna_17", "is_hardware": True, "nqubits": 17}
            backend_type.update(status="calibrating", enabled=True, messages={}, image_id="withheld")
            backend_type.update(max_number_of_shots=131072, gateset=self.gateset)
            return [backend_type]
        return [
            {
                "id": 7,
                "name": "Tuna-17",
                "backend_type_id": 7,
                "status": "calibrating",
                "message": {"content": ""},
                "last_heartbeat": "2026-11-15T16:31:05.925898Z",
            },  # fmt: skip
            {
                "id": 2,
                "name": "Spin-2+",
                "backend_type_id": 2,
                "status": "offline",
                "last_heartbeat": "2025-12-10T13:01:25Z",
            },
        ]

    def get(self, path: str, **params: Any) -> dict[str, Any]:
        self.asked.append((path, params))
        jobs = 0 if params["user_only"] else 8
        return {"number_of_jobs_in_queue": jobs, "avg_wait_time_in_queue_secs": 5045 * jobs, "extra": 1}


def no_pause(_seconds: float) -> None:
    return None


def test_account_joins_instances_and_both_queue_scopes() -> None:
    client = Client()
    found = status.account(client, NOW)
    row = found["backend_types"][0]
    if row["status"] != "calibrating" or "image_id" in row or row["instances"][0]["heartbeat_age_seconds"] != 14.1:
        raise AssertionError(row)
    if row["queue_all"]["number_of_jobs_in_queue"] != 8 or row["queue_own"]["number_of_jobs_in_queue"] != 0:
        raise AssertionError(row)
    if row["limits"]["max_number_of_shots"] != 131072 or len(row["definition_sha256"]) != 64:
        raise AssertionError(row)
    changed = Client()
    changed.gateset = ["CZ", "X90"]
    if status.account(changed, NOW)["backend_types"][0]["definition_sha256"] == row["definition_sha256"]:
        raise AssertionError("a changed gate set kept the definition digest")
    if "extra" in row["queue_all"] or [(item["name"], item["backend_type_id"]) for item in found["unlisted"]] != [
        ("Spin-2+", 2)
    ]:
        raise AssertionError(found)
    if [params for path, params in client.asked if path.endswith("/queue")] != [
        {"user_only": False},
        {"user_only": True},
    ]:
        raise AssertionError(client.asked)


def test_document_asks_the_link_service_once_per_dashboard_and_stops_at_a_dead_datasource() -> None:
    http = Transport(dict.fromkeys(status.BACKEND_DASHBOARDS, (400, DOWN)))
    pauses: list[float] = []
    found = status.document(Client(), http, pause=pauses.append)
    if http.links != ["status", *status.BACKEND_DASHBOARDS]:
        raise AssertionError(http.links)
    # One "Latest" panel per backend dashboard: the second is skipped once the first names a dead datasource.
    if [call for call in http.posted if call[0] == "tuna-17"] != [("tuna-17", 3)]:
        raise AssertionError(http.posted)
    board = found["dashboards"]["tuna-17"]
    if board["calibration"] != {
        "state": "datasource-error",
        "http_status": 400,
        "error": "dial tcp <address>:443: i/o timeout",
    }:
        raise AssertionError(board)
    if board["notices"] != ["[2026-10-22] Data withheld."] or "latest" in board or board["data_panels"] != 3:
        raise AssertionError(board)
    platform = found["platform"]
    if platform["current"] != {"Tuna-9": {"utc": "2026-10-22T21:12:00+00:00", "value": 3.0}}:
        raise AssertionError(platform)
    if platform["history"] != {"Tuna-9": [["2026-10-22T21:12:00+00:00", 2.0], ["2026-10-22T21:14:00+00:00", 3.0]]}:
        raise AssertionError(platform)
    if platform["window"] != {"from": "now-6h", "to": "now"}:
        raise AssertionError(platform)
    if platform["value_text"] != {"3": "Offline"} or found["schema"] != "qi-status-v1":
        raise AssertionError(found)
    if pauses.count(status.LINK_PAUSE_SECONDS) != len(status.BACKEND_DASHBOARDS):
        raise AssertionError(pauses)


def test_live_calibration_reads_every_latest_panel() -> None:
    live = (200, {"results": {"A": {"status": 200, "frames": [frame("Q0", [1792703520000], [41.5])]}}})
    http = Transport({"tuna-17": live})
    board = status.backend_dashboard("tuna-17", http, no_pause)
    if board["calibration"] != {"state": "data", "http_status": 200} or http.posted != [("tuna-17", 3), ("tuna-17", 5)]:
        raise AssertionError((board, http.posted))
    want = [{"name": "v", "labels": {"name": "Q0"}, "utc": "2026-10-22T21:12:00+00:00", "value": 41.5}]
    if board["latest"] != {"Latest T1": want, "Latest T2R": want}:
        raise AssertionError(board["latest"])


@pytest.mark.parametrize(
    ("answer", "state"),
    [
        ((500, {"message": "Internal Server Error"}), "http-error"),
        ((502, None), "http-error"),
        ((200, {"results": {"A": {"status": 200, "frames": []}}}), "empty"),
    ],
)
def test_calibration_reach_names_the_failing_layer(answer: tuple[int, Any], state: str) -> None:
    board = status.backend_dashboard("tuna-5", Transport({"tuna-5": answer}), no_pause)
    if board["calibration"]["state"] != state or board["calibration"]["http_status"] != answer[0]:
        raise AssertionError(board)


def test_sections_fail_alone() -> None:
    http = Transport(dict.fromkeys(status.BACKEND_DASHBOARDS, (400, DOWN)), refuse=("status", "tuna-9"))
    found = status.document(None, http, pause=no_pause, account_error="PlatformError: no login")
    if found["account"] != {"error": "PlatformError: no login"} or "HTTP 428" not in found["platform"]["error"]:
        raise AssertionError(found)
    if "HTTP 428" not in found["dashboards"]["tuna-9"]["error"] or "calibration" not in found["dashboards"]["tuna-17"]:
        raise AssertionError(found["dashboards"])


def test_transitions_order_points_and_drop_unstamped_or_null_ones() -> None:
    points: list[list[Any]] = [
        ["2026-11-15T10:03:00+00:00", 2],
        [None, 4],
        ["2026-11-15T10:01:00+00:00", 0],
        ["2026-11-15T10:02:00+00:00", None],
        ["2026-11-15T10:03:00+00:00", 3],
        ["2026-11-15T10:02:30.500000+00:00", 0],
    ]
    # Time order, the later of the two 10:03 points, and no row for the repeated 0.
    if status.transitions(points) != [["2026-11-15T10:01:00+00:00", 0], ["2026-11-15T10:03:00+00:00", 3]]:
        raise AssertionError(status.transitions(points))


def test_error_text_carries_no_address_or_token() -> None:
    raw = "Post https://h/api: dial tcp 192.0.2.7:443 via [2001:db8::1]:443 at 10:03:00 from 2001:db8::2 Bearer "
    text = status.redact(raw + "eyJhbGci.eyJzdWIi.c2ln")
    want = "Post https://h/api: dial tcp <address>:443 via <address>:443 at 10:03:00 from <address> Bearer <token>"
    if text != want:
        raise AssertionError(text)
    if len(status.redact("x" * 999)) != status.ERROR_LENGTH:
        raise AssertionError("an error text kept its full length")


def test_a_body_of_another_shape_fails_its_own_section_only() -> None:
    http = Transport(
        {"tuna-17": (200, {"results": ["not", "a", "mapping"]}), "tuna-9": (200, {"results": {"A": None}})}
    )
    found = status.document(None, http, pause=no_pause)
    boards = found["dashboards"]
    shape = boards["tuna-9"]["calibration"]
    if boards["tuna-17"]["calibration"]["state"] != "http-error" or shape["state"] != "unread":
        raise AssertionError(boards)
    # The panel's failure stays with the panel: the dashboard keeps its notices.
    if "AttributeError" not in shape["error"] or boards["tuna-9"]["notices"] != ["[2026-10-22] Data withheld."]:
        raise AssertionError(boards)
    if "current" not in found["platform"]:
        raise AssertionError(found["platform"])


class AuthorisationError(Exception):
    """Shaped like the SDK's error, which derives from Exception alone."""


class Refused:
    def pages(self, path: str) -> list[dict[str, Any]]:
        raise AuthorisationError("Not enough segments")


def test_an_authorization_failure_of_the_client_fails_the_account_section_only() -> None:
    http = Transport(dict.fromkeys(status.BACKEND_DASHBOARDS, (400, DOWN)))
    found = status.document(Refused(), http, pause=no_pause)
    if found["account"] != {"error": "AuthorisationError: Not enough segments"}:
        raise AssertionError(found["account"])
    if "current" not in found["platform"] or len(found["dashboards"]) != len(status.BACKEND_DASHBOARDS):
        raise AssertionError(found)


class Flaky(Transport):
    """The Status history panel and the second "Latest" panel answer a datasource error; the others answer data."""

    def post(self, url: str, **_options: Any) -> Response:
        if "/panels/2/" in url or "/panels/5/" in url:
            self.posted.append(("failed", int(url.split("/panels/")[1].split("/")[0])))
            return Response(502, {"results": {"A": {"status": 502, "error": "datasource timeout"}}})
        return super().post(url, **_options)


def test_a_failed_panel_query_is_named_beside_the_panels_that_read() -> None:
    live = (200, {"results": {"A": {"status": 200, "frames": [frame("Q0", [1792703520000], [41.5])]}}})
    http = Flaky({"tuna-17": live})
    platform = status.platform_status(http, no_pause)
    want = {"state": "datasource-error", "http_status": 502, "error": "datasource timeout"}
    if platform["history"] != {} or platform["history_reach"] != want or "Tuna-9" not in platform["current"]:
        raise AssertionError(platform)
    board = status.backend_dashboard("tuna-17", http, no_pause)
    if board["calibration"]["state"] != "data" or list(board["latest"]) != ["Latest T1"]:
        raise AssertionError(board)
    if board["latest_unread"] != {"Latest T2R": want}:
        raise AssertionError(board["latest_unread"])
    steady = status.platform_status(Transport({}), no_pause)
    if steady["history_reach"] != {"state": "data", "http_status": 200}:
        raise AssertionError(steady["history_reach"])


class Dropped(Transport):
    """The Status history panel and the second "Latest" panel fail in transport after the first reads succeed."""

    def post(self, url: str, **_options: Any) -> Response:
        if "/panels/2/" in url or "/panels/5/" in url:
            raise ConnectionError("read timed out from 192.0.2.7")
        return super().post(url, **_options)


def test_a_transport_failure_on_a_later_panel_keeps_what_was_read() -> None:
    live = (200, {"results": {"A": {"status": 200, "frames": [frame("Q0", [1792703520000], [41.5])]}}})
    http = Dropped({"tuna-17": live})
    platform = status.platform_status(http, no_pause)
    if "Tuna-9" not in platform["current"] or platform["history"] != {}:
        raise AssertionError(platform)
    if platform["history_reach"]["state"] != "unread" or "<address>" not in platform["history_reach"]["error"]:
        raise AssertionError(platform["history_reach"])
    board = status.backend_dashboard("tuna-17", http, no_pause)
    if list(board["latest"]) != ["Latest T1"] or board["latest_unread"]["Latest T2R"]["state"] != "unread":
        raise AssertionError(board)
    if board["notices"] != ["[2026-10-22] Data withheld."]:
        raise AssertionError(board)


def test_an_exit_while_importing_the_client_leaves_the_public_sections(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class Exiting:
        def __getattr__(self, name: str) -> Any:
            raise SystemExit("QI_HARDWARE_PAUSE_SECONDS must be one of 30, 60, 90, 120")

    monkeypatch.setitem(sys.modules, "qi_platform", Exiting())
    monkeypatch.setattr(status, "document", lambda client, account_error="": {"client": client, "why": account_error})
    if status.main([]) != 0:
        raise AssertionError("the command exited nonzero")
    printed = json.loads(capsys.readouterr().out)
    if printed != {"client": None, "why": "SystemExit: QI_HARDWARE_PAUSE_SECONDS must be one of 30, 60, 90, 120"}:
        raise AssertionError(printed)
