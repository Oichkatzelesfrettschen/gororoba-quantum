"""IQM observations keep related calibration reads on one immutable identity."""

from __future__ import annotations

import asyncio
import datetime
import json
import subprocess
import sys
import warnings
from pathlib import Path
from unittest.mock import patch

import pytest

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import iqm_mcp_server as server

CALIBRATION = "04b7af66-cc83-4e7d-bfaa-28236f5ef1b4"
OTHER = "8fda2f13-a42b-4c8b-86bc-3c0604d20982"


def test_server_import_is_warning_free_with_the_pinned_sdk() -> None:
    scripts = Path(__file__).resolve().parents[2] / "scripts"
    program = f"import sys; sys.path.insert(0, {str(scripts)!r}); import iqm_mcp_server"
    result = subprocess.run([sys.executable, "-I", "-W", "error", "-c", program], capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stderr)


class Reader:
    def __init__(self, documents: dict[str, object]) -> None:
        self.documents = documents
        self.paths: list[str] = []

    def get(self, path: str) -> tuple[int, bytes]:
        self.paths.append(path)
        return 200, json.dumps(self.documents[path]).encode()


def test_architecture_resolves_default_then_reads_pinned_identity() -> None:
    root = "api/v1/calibration-sets/garnet/"
    reader = Reader(
        {
            root + "default": {"observation_set_id": CALIBRATION},
            root + CALIBRATION + "/dynamic-quantum-architecture": {"calibration_set_id": CALIBRATION},
        }
    )
    with patch.object(server, "client", return_value=reader):
        result = asyncio.run(server.iqm_architecture("garnet"))
    if result["calibration_set_id"] != CALIBRATION or reader.paths != list(reader.documents):
        raise AssertionError("architecture did not resolve and pin the calibration")


@pytest.mark.parametrize("identity", [CALIBRATION, CALIBRATION.upper()])
def test_metrics_accepts_the_architectures_explicit_identity(identity: str) -> None:
    path = f"api/v1/calibration-sets/garnet/{CALIBRATION}/metrics"
    reader = Reader(
        {
            path: {
                "describes_id": CALIBRATION,
                "dut_label": "chip",
                "created_timestamp": "stamp",
                "observations": [{"dut_field": "qubit.QB4.t1", "value": 1}],
            }
        }
    )
    with patch.object(server, "client", return_value=reader):
        result = asyncio.run(server.iqm_metrics("garnet", calibration_set_id=identity))
    if result["calibration_set_id"] != CALIBRATION or reader.paths != [path]:
        raise AssertionError("explicit calibration identity was replaced by a moving default")


def test_mismatched_calibration_is_an_mcp_error() -> None:
    path = f"api/v1/calibration-sets/garnet/{CALIBRATION}/dynamic-quantum-architecture"
    reader = Reader({path: {"calibration_set_id": OTHER}})
    with patch.object(server, "client", return_value=reader), pytest.raises(server.ToolError, match="calibration"):
        asyncio.run(server.iqm_architecture("garnet", calibration_set_id=CALIBRATION))


def test_observation_preserves_subsecond_utc_and_request_path() -> None:
    start = datetime.datetime(2026, 10, 22, 20, 0, 0, 123456, tzinfo=datetime.UTC)
    end = start.replace(microsecond=823456)
    reader = Reader({"api/v1/quantum-computers/garnet": {"operational_status": "online"}})
    with (
        patch.object(server, "client", return_value=reader),
        patch.object(server, "utc_now", side_effect=[start, end], create=True),
    ):
        result = asyncio.run(server.iqm_quantum_computer("garnet"))
    observed = result["_observation"]
    if observed != {
        "request_started_utc": start.isoformat(),
        "retrieved_utc": end.isoformat(),
        "path": "api/v1/quantum-computers/garnet",
    }:
        raise AssertionError("the observation discarded time precision or route provenance")


def test_explicit_calibration_rejects_path_injection_before_api_read() -> None:
    reader = Reader({})
    with patch.object(server, "client", return_value=reader), pytest.raises(server.ToolError):
        asyncio.run(server.iqm_architecture("garnet", calibration_set_id="../default"))
    if reader.paths:
        raise AssertionError("an invalid identity reached the provider")
