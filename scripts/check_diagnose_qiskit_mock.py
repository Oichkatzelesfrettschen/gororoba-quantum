"""Check scoped mock diagnostics with synthetic accounts and an in-memory transport.

The service constructor and HTTP send method are replaced before diagnosis.
Fixtures contain deliberately recognizable account and HTTP values so leakage
fails the check without reading credentials or contacting a service.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import logging
import sys
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import diagnose_qiskit_mock as diagnostic

REQUESTED = "ibm_kingston"
OTHER_BACKEND = "ibm_privatecustomerdevice"
ACCOUNT_NAME = "private-account-fixture"
INSTANCE = "crn:v1:fixture:private-account:private-instance"
TOKEN = "secret-token-fixture"
HOST = "private-host-fixture.invalid"
HEADER = "private-header-fixture"
BODY = "private-response-body-fixture"
SECRETS = (OTHER_BACKEND, ACCOUNT_NAME, INSTANCE, TOKEN, HOST, HEADER, BODY)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


class _ProbeFailure(RuntimeError):
    """Synthetic backend lookup failure carrying an intentionally private body."""


class _Service:
    def __init__(self, available: bool, saved_instance: bool) -> None:
        self.available = available
        self.saved_instance = saved_instance
        self.transport_calls: list[tuple[Any, Any, dict[str, Any], Any]] = []
        self.lookup_calls: list[tuple[str, dict[str, Any]]] = []
        self.session = diagnostic.requests.sessions.Session()
        self.logger = logging.getLogger("qiskit_ibm_runtime")

    def send(self, session: Any, request: Any, **kwargs: Any) -> Any:
        require(self.logger.level == logging.CRITICAL, "diagnostic omitted temporary Runtime log suppression")
        response = SimpleNamespace(
            status_code=404 if "/mock_" in request.url else 200,
            headers={HEADER: TOKEN},
            text=BODY + INSTANCE,
            content=(BODY + INSTANCE).encode(),
        )
        self.transport_calls.append((session, request, kwargs, response))
        return response

    def request(self, backend: str, endpoint: str) -> None:
        request = SimpleNamespace(
            method="GET",
            url=f"https://{HOST}/backends/{backend}/{endpoint}?token={TOKEN}",
            headers={"Authorization": TOKEN, HEADER: INSTANCE},
            body=BODY,
        )
        response = self.session.send(request, timeout=7, allow_redirects=False)
        session, observed_request, kwargs, observed_response = self.transport_calls[-1]
        require(session is self.session and observed_request is request, "HTTP observer replaced a request")
        require(kwargs == {"timeout": 7, "allow_redirects": False}, "HTTP observer changed send options")
        require(response is observed_response, "HTTP observer replaced a response")
        require(request.headers[HEADER] == INSTANCE and request.body == BODY, "HTTP observer changed request data")
        require(
            response.text == BODY + INSTANCE and response.headers[HEADER] == TOKEN, "HTTP observer changed response"
        )

    def active_instance(self) -> str:
        return INSTANCE

    def active_account(self) -> dict[str, str]:
        return {"instance": INSTANCE if self.saved_instance else "", "name": ACCOUNT_NAME, "token": TOKEN}

    def backends(self) -> list[Any]:
        self.logger.warning("%s %s", ACCOUNT_NAME, INSTANCE)
        self.request(OTHER_BACKEND, "configuration")
        self.request(REQUESTED, "configuration")
        self.request(REQUESTED, "private-endpoint-" + TOKEN)
        names = [OTHER_BACKEND, ACCOUNT_NAME, TOKEN, INSTANCE]
        if self.available:
            names.append(REQUESTED)
        return [SimpleNamespace(name=name) for name in names]

    def backend(self, name: str, **kwargs: Any) -> Any:
        self.lookup_calls.append((name, kwargs))
        if name.startswith("mock_"):
            self.request(name, "configuration")
            raise _ProbeFailure(" ".join(SECRETS))
        require(name == REQUESTED, "diagnostic looked up an unrelated backend")
        return SimpleNamespace(status=self.status)

    def status(self) -> Any:
        self.request(REQUESTED, "status")
        return SimpleNamespace(operational=True, status_msg=" ".join(SECRETS))


def _check_report(available: bool, saved_instance: bool, cli: bool) -> None:
    fixture = _Service(available, saved_instance)
    logger = logging.getLogger("qiskit_ibm_runtime")
    previous_level = logger.level
    output = io.StringIO()
    errors = io.StringIO()
    transport = fixture.send
    handler = logging.StreamHandler(errors)
    logger.addHandler(handler)
    try:
        logger.setLevel(logging.WARNING)
        with (
            patch.object(diagnostic, "QiskitRuntimeService", return_value=fixture) as constructor,
            patch.object(diagnostic.requests.sessions.Session, "send", transport),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
        ):
            if cli:
                with patch.object(sys, "argv", ["diagnose_qiskit_mock.py", "--backend", REQUESTED]):
                    diagnostic.main()
                report = json.loads(output.getvalue())
            else:
                report = diagnostic.diagnose(REQUESTED)
            require(constructor.call_count == 1, "diagnostic constructed an extra service")
            require(
                diagnostic.requests.sessions.Session.send is transport, "diagnostic left the HTTP observer installed"
            )
        require(logger.level == logging.WARNING, "diagnostic failed to restore the Runtime logger")
    finally:
        logger.setLevel(previous_level)
        logger.removeHandler(handler)
    require(report["requested_backend_available"] is available, "requested availability differs from discovery")
    require("available_backend_names" not in report, "report retained account-wide backend discovery")
    require(report["saved_instance_explicit"] is saved_instance, "saved-instance presence differs")
    require(
        report["instance_sha256_12"] == hashlib.sha256(INSTANCE.encode()).hexdigest()[:12],
        "report lost its bounded instance identity",
    )
    rendered = json.dumps(report) + output.getvalue() + errors.getvalue()
    require(all(secret not in rendered for secret in SECRETS), "diagnostic disclosed an account or HTTP field")
    require(errors.getvalue() == "", "diagnostic leaked an SDK warning")
    require(
        report["discovery_http_events"]
        == [
            {"method": "GET", "backend": REQUESTED, "endpoint": "configuration", "status_code": 200},
            {"method": "GET", "backend": REQUESTED, "endpoint": "other", "status_code": 200},
        ],
        "diagnostic lost scoped discovery events or exposed a private endpoint",
    )
    expected_calls = [
        (REQUESTED, {"instance": INSTANCE}),
        ("mock_kingston", {}),
        ("mock_kingston", {"instance": INSTANCE}),
    ]
    require(fixture.lookup_calls == expected_calls, "diagnostic changed explicit or implicit instance probes")
    probes = report["probes"]
    require(len(probes) == 3, "diagnostic lost a backend probe")
    require(probes[0]["found"] is True and probes[0]["operational"] is True, "physical status evidence changed")
    require("status_msg" not in probes[0], "report retained free-form backend status text")
    for probe, backend, endpoint, status_code in zip(
        probes,
        (REQUESTED, "mock_kingston", "mock_kingston"),
        ("status", "configuration", "configuration"),
        (200, 404, 404),
        strict=True,
    ):
        require(
            probe["http_events"]
            == [{"method": "GET", "backend": backend, "endpoint": endpoint, "status_code": status_code}],
            "diagnostic changed HTTP evidence for a requested probe",
        )
        if backend.startswith("mock_"):
            require(
                probe["found"] is False and probe["error_type"] == "_ProbeFailure", "lookup failure evidence changed"
            )


def _check_failure_restoration() -> None:
    logger = logging.getLogger("qiskit_ibm_runtime")
    level = logger.level
    send = diagnostic.requests.sessions.Session.send
    with patch.object(diagnostic, "QiskitRuntimeService", side_effect=_ProbeFailure(TOKEN)):
        try:
            diagnostic.diagnose(REQUESTED)
        except _ProbeFailure:
            pass
        else:
            raise RuntimeError("diagnostic suppressed service-construction failure")
    require(logger.level == level, "failed diagnosis left the Runtime logger changed")
    require(diagnostic.requests.sessions.Session.send is send, "failed diagnosis left the HTTP observer installed")


def main() -> None:
    for available, saved_instance, cli in ((True, True, False), (False, False, False), (True, False, True)):
        _check_report(available, saved_instance, cli)
    _check_failure_restoration()
    print(json.dumps({"scoped_report_checks": 3, "failure_restoration_checks": 1, "network_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
