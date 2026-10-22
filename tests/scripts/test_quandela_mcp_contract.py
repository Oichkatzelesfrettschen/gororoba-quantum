"""Exercise the Quandela MCP process boundary without contacting a provider."""

import io
import subprocess
import sys
from datetime import timedelta
from pathlib import Path
from typing import cast

import anyio
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def test_mcp_import_completes_settings_with_warnings_as_errors() -> None:
    root = Path(__file__).resolve().parents[2]
    program = f"import sys; sys.path.insert(0, {str(root / 'scripts')!r}); import qd_mcp_server"
    process = subprocess.run(
        [sys.executable, "-I", "-W", "error", "-c", program], capture_output=True, text=True, timeout=30
    )
    if process.returncode:
        raise RuntimeError(f"the MCP server failed its warning-free import: {process.stderr}")


@pytest.mark.parametrize("occupation", [True, False, 0.5, "1", -1, 2])
def test_local_simulation_rejects_non_binary_integer_occupation(occupation: object) -> None:
    import qd_mcp_server

    with pytest.raises(ValueError, match="photon"):
        qd_mcp_server.simulate([[1.0]], None, cast(list[int], [occupation]), "SLOS")


@pytest.mark.parametrize("entry", [float("nan"), float("inf"), -float("inf"), 1e308])
def test_local_simulation_rejects_invalid_unitary_before_numeric_overflow(entry: float) -> None:
    import qd_mcp_server

    with pytest.raises(ValueError, match="matrix|finite|unitary"):
        qd_mcp_server.simulate([[entry]], None, [1], "SLOS")


@pytest.mark.parametrize("raw", [True, False])
def test_http_response_exceeding_result_limit_remains_unanswered(raw: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    import qd_platform

    monkeypatch.setattr(qd_platform, "RESULT_LIMIT", 8)
    monkeypatch.setattr(qd_platform.OPENER, "open", lambda *args, **kwargs: io.BytesIO(b'{"payload":"oversize"}'))
    with pytest.raises(qd_platform.UnansweredError, match="bound|limit"):
        qd_platform.request("GET", "/api/jobs/offline/result", auth=False, raw=raw)


def test_mutating_http_call_with_invalid_json_keeps_unknown_outcome(monkeypatch: pytest.MonkeyPatch) -> None:
    import qd_platform

    monkeypatch.setattr(qd_platform.OPENER, "open", lambda *args, **kwargs: io.BytesIO(b"invalid JSON"))
    with pytest.raises(qd_platform.UnansweredError, match="JSON"):
        qd_platform.request("POST", "/api/jobs/offline/cancel", auth=False)


def test_stdio_enforces_advertised_schema_before_sdk_coercion() -> None:
    root = Path(__file__).resolve().parents[2]
    bootstrap = f"""
import sys
sys.path.insert(0, {str(root / "scripts")!r})
import qd_platform
import qd_mcp_server
def forbid(*args, **kwargs):
    raise RuntimeError('provider access forbidden in transport test')
qd_platform.OPENER.open = forbid
qd_mcp_server.serve()
"""

    async def exercise() -> None:
        parameters = StdioServerParameters(command=sys.executable, args=["-I", "-W", "error", "-c", bootstrap])
        async with stdio_client(parameters) as (reader, writer):
            async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=30)) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                if len(tools) != 8:
                    raise AssertionError(f"expected eight tools, received {[tool.name for tool in tools]}")
                failures = []
                for arguments in (
                    {"real": "[[1.0]]", "input_photons": [1]},
                    {"real": [[1.0]], "input_photons": [True]},
                    {"real": [[1.0]], "input_photons": [1], "hardware_config": {}},
                ):
                    result = await session.call_tool("qd_simulate_local", arguments)
                    if not result.isError:
                        failures.append(arguments)
                if failures:
                    raise AssertionError(f"the MCP transport accepted schema-invalid arguments: {failures}")
                result = await session.call_tool("qd_simulate_local", {"real": [[1.0]], "input_photons": [1]})
                if result.isError or result.structuredContent is None:
                    raise AssertionError(f"valid identity simulation failed: {result}")
                if result.structuredContent["probabilities"] != {"|1>": 1.0}:
                    raise AssertionError(f"identity simulation changed photon state: {result}")

    anyio.run(exercise)
