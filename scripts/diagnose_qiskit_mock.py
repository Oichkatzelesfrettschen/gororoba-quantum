"""Locate a Runtime mock-backend lookup failure using read-only SDK calls.

The HTTP observer delegates every request unchanged and records only a known
backend name, endpoint category and response status. Credentials, account
names, CRNs, hosts, headers and response bodies remain outside the report.
Primitive execution is outside this diagnostic's interface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any
from unittest.mock import patch
from urllib.parse import urlsplit

import requests  # type: ignore[import-untyped, unused-ignore]
from qiskit_ibm_runtime import QiskitRuntimeService


def diagnose(backend_name: str) -> dict[str, Any]:
    if re.fullmatch(r"ibm_[a-z0-9]+", backend_name) is None:
        raise ValueError("backend must use the documented ibm_NAME form")
    mock_name = re.sub(r"^[^_]+", "mock", backend_name)
    events: list[dict[str, Any]] = []
    original_send = requests.sessions.Session.send

    def observed_send(session: Any, request: Any, **kwargs: Any) -> Any:
        response = original_send(session, request, **kwargs)
        path = urlsplit(request.url).path
        if "/backends/" in path:
            backend, _, endpoint = path.split("/backends/", 1)[1].partition("/")
            if backend in (backend_name, mock_name):
                events.append(
                    {
                        "method": request.method,
                        "backend": backend,
                        "endpoint": endpoint
                        if endpoint in ("configuration", "status", "properties", "defaults")
                        else "other",
                        "status_code": response.status_code,
                    }
                )
        return response

    report: dict[str, Any] = {
        "schema": "qiskit-mock-backend-diagnosis-v1",
        "observed_at": datetime.now(UTC).isoformat(),
        "runtime_version": version("qiskit-ibm-runtime"),
        "scope": "backend discovery/configuration/status only; zero primitive submissions",
        "diagnostic_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "probes": [],
    }
    logger = logging.getLogger("qiskit_ibm_runtime")
    previous_level = logger.level
    logger.setLevel(logging.CRITICAL)
    try:
        with patch.object(requests.sessions.Session, "send", observed_send):
            service = QiskitRuntimeService()
            instance = service.active_instance()
            if not instance:
                raise ValueError("service has no resolved active instance")
            report["saved_instance_explicit"] = bool((service.active_account() or {}).get("instance"))
            report["instance_sha256_12"] = hashlib.sha256(instance.encode()).hexdigest()[:12]
            report["requested_backend_available"] = any(backend.name == backend_name for backend in service.backends())
            report["discovery_http_events"] = list(events)
            for name, explicit in ((backend_name, True), (mock_name, False), (mock_name, True)):
                entry: dict[str, Any] = {"backend": name, "explicit_instance": explicit}
                before = len(events)
                try:
                    backend = service.backend(name, **({"instance": instance} if explicit else {}))
                except Exception as error:
                    entry.update(found=False, error_type=type(error).__name__)
                else:
                    entry["found"] = True
                    try:
                        status = backend.status()
                        entry["operational"] = bool(status.operational)
                    except Exception as error:
                        entry["status_error_type"] = type(error).__name__
                entry["http_events"] = events[before:]
                report["probes"].append(entry)
    finally:
        logger.setLevel(previous_level)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="ibm_kingston")
    args = parser.parse_args()
    print(json.dumps(diagnose(args.backend), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
