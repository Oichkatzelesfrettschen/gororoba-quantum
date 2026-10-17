"""Quandela Cloud MCP server over stdio: platforms, processor specs, job limits, token usage, jobs, local simulation.

The server calls the Quandela Cloud REST API through qd_platform.request with
the job token from the file QUANDELA_TOKEN_FILE names; that function sends the
token to qd_platform.API only and refuses redirects. It runs under the
interpreter QD_PYTHON names, the build host's system Python, which carries mcp
1.29 (FastMCP) and the perceval-quandela and exqalibur Arch packages, and it
never writes Perceval's persistent configuration. Reads return
JSON-serializable structures; a failed call raises ToolError, so the MCP
result carries isError with the route and the service's message.

The JSON-RPC stream owns a private duplicate of the process's standard
output. File descriptor 1 is pointed at standard error before Perceval loads,
because exqalibur's console logger writes warnings to descriptor 1 from C++,
where a Python-level redirect cannot reach.

qd_cancel_job is the one tool that changes remote state; its annotation says
so and the client's permission rules ask before it. Job submission and the
per-byte-priced QRNG routes are outside this server: a Quandela job,
simulator or QPU, spends Explorer credits and waits for a written case and
the user's approval. qd_platform.check_mcp holds the tool set, the
annotations and the routes each tool may call.

qd_simulate_local takes a unitary as JSON numbers, never a serialized
Perceval object, whose parameter expressions Perceval evaluates through
sympy. It bounds the output space to LOCAL_MAX_OUTPUT_STATES Fock states and
runs in a worker thread, so the server keeps answering while it computes.

Usage: QD_PYTHON=${QD_PYTHON:-/usr/bin/python3}
       QUANDELA_TOKEN_FILE=TOKEN "$QD_PYTHON" -I scripts/qd_mcp_server.py   (stdio; launched by an MCP client)
"""

from __future__ import annotations

import functools
import io
import math
import os
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Annotated, Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import anyio  # noqa: E402
from mcp.server.fastmcp import FastMCP  # noqa: E402
from mcp.server.fastmcp.exceptions import ToolError  # noqa: E402
from mcp.server.stdio import stdio_server  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402
from pydantic import Field  # noqa: E402
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
LOCAL_MAX_OUTPUT_STATES = 1_000_000
LOCAL_MAX_STATES = 256
UNITARY_TOLERANCE = 1e-9
RESULT_CHARACTERS = 8000
LOCAL_BACKENDS = ("SLOS", "Naive")
READ = ToolAnnotations(readOnlyHint=True, openWorldHint=True)
LOCAL = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
MUTATE = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=True)
# Processor fields too large for a routine read: the serialized chip circuit
# and the platform's HTML documentation.
BULK_SPECS = ("architecture", "documentation")

JobId = Annotated[str, Field(description="Job id as the cloud reports it (a UUID)", pattern=r"^[0-9a-fA-F-]{8,64}$")]
PlatformName = Annotated[
    str, Field(description="Platform name, e.g. qpu:belenos, sim:slos", pattern=r"^(qpu|sim):[a-z0-9:_-]{1,48}$")
]
Matrix = Annotated[
    list[list[float]],
    Field(description="Square matrix as rows of numbers; real part, or imaginary part when passed as imag"),
]

server = FastMCP("quandela")


def reported[**P, R](function: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """Re-raise platform and validation failures as ToolError, whose message reaches the client."""

    @functools.wraps(function)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await function(*args, **kwargs)
        except (PlatformError, ValueError, KeyError, TypeError, RuntimeError) as error:
            raise ToolError(f"{function.__name__}: {error}") from error

    return wrapper


async def threaded[R](call: Callable[[], R]) -> R:
    """Run a blocking call in a worker thread so the stdio loop keeps serving."""
    return await anyio.to_thread.run_sync(call)


@server.tool(annotations=READ)
@reported
async def qd_platforms() -> dict[str, Any]:
    """Explorer platforms (status, per-job seconds, credits per shot, availability, maintenance) and the public list."""

    def read() -> dict[str, Any]:
        return {
            "explorer": [platform_row(row) for row in get("/api/platforms/public/explorer", auth=False)],
            "public": [
                {"name": row["name"], "type": row["type"], "status": row["status"]}
                for row in get("/api/platforms/public", auth=False)
            ],
        }

    return await threaded(read)


@server.tool(annotations=READ)
@reported
async def qd_platform(name: PlatformName, include_bulk: bool = False) -> dict[str, Any]:
    """Processor record of one platform: constraints, input modes, commands, perfs, mitigations, versions.

    include_bulk adds the serialized chip architecture and the HTML documentation.
    """
    record: dict[str, Any] = await threaded(lambda: get(platform_route(name)))
    if not include_bulk:
        specs = record.get("specs", {})
        record["specs"] = {k: v for k, v in specs.items() if k not in BULK_SPECS}
    return record


@server.tool(annotations=READ)
@reported
async def qd_availability() -> dict[str, Any]:
    """The token's job limits and occupancy: running, queued and Quantum Toolbox jobs."""
    return await threaded(availability)


@server.tool(annotations=READ)
@reported
async def qd_usage() -> list[dict[str, Any]]:
    """The token usage report (jobs and usage per token, token ids removed)."""
    return await threaded(lambda: usage_rows(get("/api/tokens/usage/report")))


@server.tool(annotations=READ)
@reported
async def qd_job_status(job_id: JobId) -> dict[str, Any]:
    """Status, progress and timing of one job."""
    status: dict[str, Any] = await threaded(lambda: get(job_route(job_id, "status")))
    return status


@server.tool(annotations=READ)
@reported
async def qd_job_result(job_id: JobId, include_raw: bool = False) -> dict[str, Any]:
    """Result of one finished job; each string field truncates at RESULT_CHARACTERS unless include_raw."""
    result: dict[str, Any] = await threaded(lambda: get(job_route(job_id, "result")))
    if include_raw:
        return result
    return {
        k: (v[:RESULT_CHARACTERS] + "...") if isinstance(v, str) and len(v) > RESULT_CHARACTERS else v
        for k, v in result.items()
    }


def simulate(
    real: list[list[float]], imag: list[list[float]] | None, photons: list[int], backend: str
) -> dict[str, Any]:
    import numpy as np
    import perceval as pcvl

    if backend not in LOCAL_BACKENDS:
        raise ValueError(f"backend {backend!r} is not one of {LOCAL_BACKENDS}")
    modes = len(real)
    if not 1 <= modes <= LOCAL_MAX_MODES or any(len(row) != modes for row in real):
        raise ValueError(f"real must be a square matrix of 1 to {LOCAL_MAX_MODES} modes")
    if imag is not None and (len(imag) != modes or any(len(row) != modes for row in imag)):
        raise ValueError("imag must have the shape of real")
    if len(photons) != modes or any(not 0 <= n <= 1 for n in photons):
        raise ValueError("input_photons must give 0 or 1 photon for each mode")
    unitary = np.array(real, dtype=complex) + (1j * np.array(imag) if imag is not None else 0)
    if not np.allclose(unitary.conj().T @ unitary, np.eye(modes), atol=UNITARY_TOLERANCE):
        raise ValueError("the matrix is not unitary within 1e-9")
    count = sum(photons)
    space = math.comb(modes + count - 1, count)
    if space > LOCAL_MAX_OUTPUT_STATES:
        raise ValueError(f"{count} photons in {modes} modes span {space} output states, over {LOCAL_MAX_OUTPUT_STATES}")
    processor = pcvl.Processor(backend, pcvl.Unitary(pcvl.Matrix(unitary)))
    processor.with_input(pcvl.BasicState(photons))
    outcome = processor.probs()
    probabilities = sorted(outcome["results"].items(), key=lambda item: -item[1])[:LOCAL_MAX_STATES]
    return {
        "perceval": pcvl.__version__,
        "backend": backend,
        "output_states": space,
        "probabilities": {str(k): float(v) for k, v in probabilities},
        "physical_perf": float(outcome.get("physical_perf", 1.0)),
    }


@server.tool(annotations=LOCAL)
@reported
async def qd_simulate_local(
    real: Matrix,
    input_photons: Annotated[list[int], Field(description="Photons per input mode, 0 or 1, e.g. [1, 1, 0, 0]")],
    imag: Matrix | None = None,
    backend: Annotated[str, Field(description="Local Perceval backend: SLOS or Naive")] = "SLOS",
) -> dict[str, Any]:
    """Output probabilities of a unitary (real plus i times imag) on single-photon inputs, simulated on this host.

    Spends no credits. Returns the LOCAL_MAX_STATES most probable output Fock
    states, the output-space size and the physical performance.
    """
    return await threaded(lambda: simulate(real, imag, input_photons, backend))


@server.tool(annotations=MUTATE)
@reported
async def qd_cancel_job(job_id: JobId) -> dict[str, Any]:
    """Cancel one waiting or running job."""
    answer = await threaded(lambda: request("POST", job_route(job_id, "cancel")))
    return {"job_id": job_id, "answer": answer}


def serve() -> None:
    """Serve JSON-RPC on a private duplicate of stdout after pointing descriptor 1 at stderr."""
    protocol = os.dup(sys.stdout.fileno())
    sys.stdout.flush()
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())
    stream = anyio.wrap_file(io.TextIOWrapper(os.fdopen(protocol, "wb"), encoding="utf-8"))

    async def run() -> None:
        async with stdio_server(stdout=stream) as (read_stream, write_stream):
            core = server._mcp_server
            await core.run(read_stream, write_stream, core.create_initialization_options())

    anyio.run(run)


if __name__ == "__main__":
    serve()
