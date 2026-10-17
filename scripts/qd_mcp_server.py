"""Quandela Cloud MCP server over stdio: platforms, processor specs, job limits, token usage, jobs, local simulation.

The server calls the Quandela Cloud REST API through the routes of
qd_platform.py with the job token from the file QUANDELA_TOKEN_FILE names, and
it runs under the build host's system interpreter, which carries mcp 1.29
(FastMCP) and the perceval-quandela and exqalibur Arch packages. It sends the
token to qd_platform.API only and never writes Perceval's persistent
configuration. Reads return JSON-serializable structures; a failed call
raises ToolError, so the MCP result carries isError with the service's message.

qd_cancel_job is the one tool that changes remote state; its annotation says
so and the client's permission rules ask before it. Job submission is outside
this server: a Quandela job, simulator or QPU, spends Explorer credits and
waits for a written case and the user's approval.

qd_simulate_local runs a Perceval-serialized circuit on a local Perceval
backend, bounded to LOCAL_MAX_MODES modes and LOCAL_MAX_PHOTONS photons.

Usage: QUANDELA_TOKEN_FILE=TOKEN /usr/bin/python3 -I scripts/qd_mcp_server.py   (stdio; launched by an MCP client)
"""

from __future__ import annotations

import functools
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP  # noqa: E402
from mcp.server.fastmcp.exceptions import ToolError  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402
from qd_platform import (  # noqa: E402
    PlatformError,
    availability,
    get,
    job_route,
    platform_route,
    platform_row,
    request,
    usage_rows,
)

LOCAL_MAX_MODES = 24
LOCAL_MAX_PHOTONS = 12
LOCAL_MAX_STATES = 256
RESULT_CHARACTERS = 8000
LOCAL_BACKENDS = ("SLOS", "Naive", "MPS")
READ = ToolAnnotations(readOnlyHint=True, openWorldHint=True)
LOCAL = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
MUTATE = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=True)
# Processor fields too large for a routine read: the serialized chip circuit
# and the platform's HTML documentation.
BULK_SPECS = ("architecture", "documentation")

server = FastMCP("quandela")


def reported[**P, R](function: Callable[P, R]) -> Callable[P, R]:
    """Re-raise platform and validation failures as ToolError, whose message reaches the client."""

    @functools.wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return function(*args, **kwargs)
        except (PlatformError, ValueError, KeyError, RuntimeError) as error:
            raise ToolError(f"{function.__name__}: {error}") from error

    return wrapper


@server.tool(annotations=READ)
@reported
def qd_platforms() -> dict[str, Any]:
    """Explorer platforms (status, per-job seconds, credits per shot, availability, maintenance) and the public list."""
    return {
        "explorer": [platform_row(row) for row in get("/api/platforms/public/explorer", auth=False)],
        "public": [
            {"name": row["name"], "type": row["type"], "status": row["status"]}
            for row in get("/api/platforms/public", auth=False)
        ],
    }


@server.tool(annotations=READ)
@reported
def qd_platform(name: str, include_bulk: bool = False) -> dict[str, Any]:
    """Processor record of one platform (e.g. qpu:belenos, sim:slos): constraints, commands, perfs, versions.

    include_bulk adds the serialized chip architecture and the HTML documentation.
    """
    record: dict[str, Any] = get(platform_route(name))
    if not include_bulk:
        specs = record.get("specs", {})
        record["specs"] = {k: v for k, v in specs.items() if k not in BULK_SPECS}
    return record


@server.tool(annotations=READ)
@reported
def qd_availability() -> dict[str, Any]:
    """The token's job limits and occupancy: running, queued and Quantum Toolbox jobs."""
    return availability()


@server.tool(annotations=READ)
@reported
def qd_usage() -> list[dict[str, Any]]:
    """The token usage report (jobs and usage per token, token ids removed)."""
    return usage_rows(get("/api/tokens/usage/report"))


@server.tool(annotations=READ)
@reported
def qd_job_status(job_id: str) -> dict[str, Any]:
    """Status, progress and timing of one job."""
    status: dict[str, Any] = get(job_route(job_id, "status"))
    return status


@server.tool(annotations=READ)
@reported
def qd_job_result(job_id: str, include_raw: bool = False) -> dict[str, Any]:
    """Result of one finished job; each string field truncates at RESULT_CHARACTERS unless include_raw."""
    result: dict[str, Any] = get(job_route(job_id, "result"))
    if include_raw:
        return result
    return {
        k: (v[:RESULT_CHARACTERS] + "...") if isinstance(v, str) and len(v) > RESULT_CHARACTERS else v
        for k, v in result.items()
    }


@server.tool(annotations=LOCAL)
@reported
def qd_simulate_local(circuit: str, input_state: str, backend: str = "SLOS") -> dict[str, Any]:
    """Output probabilities of a circuit from perceval.serialization.serialize on a Fock input such as |1,0,1,0>.

    Runs on this host with perceval-quandela; spends no credits. Returns the
    LOCAL_MAX_STATES most probable output states and the physical performance.
    """
    import perceval as pcvl
    from perceval.serialization import deserialize

    if backend not in LOCAL_BACKENDS:
        raise ValueError(f"backend {backend!r} is not one of {LOCAL_BACKENDS}")
    unitary_circuit = deserialize(circuit)
    state = pcvl.BasicState(input_state)
    if unitary_circuit.m > LOCAL_MAX_MODES or state.n > LOCAL_MAX_PHOTONS or state.m != unitary_circuit.m:
        raise ValueError(
            f"circuit of {unitary_circuit.m} modes and input {input_state} exceed {LOCAL_MAX_MODES} modes, "
            f"{LOCAL_MAX_PHOTONS} photons, or differ in mode count"
        )
    processor = pcvl.Processor(backend, unitary_circuit)
    processor.with_input(state)
    outcome = processor.probs()
    probabilities = sorted(outcome["results"].items(), key=lambda item: -item[1])[:LOCAL_MAX_STATES]
    return {
        "perceval": pcvl.__version__,
        "backend": backend,
        "probabilities": {str(k): float(v) for k, v in probabilities},
        "physical_perf": float(outcome.get("physical_perf", 1.0)),
    }


@server.tool(annotations=MUTATE)
@reported
def qd_cancel_job(job_id: str) -> dict[str, Any]:
    """Cancel one waiting or running job."""
    answer = request("POST", job_route(job_id, "cancel"))
    return {"job_id": job_id, "answer": answer}


if __name__ == "__main__":
    server.run()
