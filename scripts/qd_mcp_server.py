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
import json
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
from mcp.server.fastmcp.server import Settings  # noqa: E402
from mcp.server.stdio import stdio_server  # noqa: E402
from mcp.types import Tool, ToolAnnotations  # noqa: E402
from pydantic import Field  # noqa: E402
from qd_platform import (  # noqa: E402
    PlatformError,
    availability,
    case_path,
    get,
    job_billing,
    job_route,
    plan,
    plan_summary,
    platform_route,
    platform_row,
    request,
    scrub,
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
# Fields of the processor record that change Perceval 1.3.1's behavior when absent
# (docs/notes/quandela/calibration.md, "Record fields Perceval reads"); the first five sit in specs.
PERCEVAL_SPECS = ("commands", "available_commands", "default_mitigations", "known_mitigations", "architecture", "type")

JobId = Annotated[str, Field(description="Job id as the cloud reports it (a UUID)", pattern=r"^[0-9a-fA-F-]{8,64}$")]
PlatformName = Annotated[
    str, Field(description="Platform name, e.g. qpu:belenos, sim:slos", pattern=r"^(qpu|sim):[a-z0-9:_-]{1,48}$")
]
Matrix = Annotated[
    list[list[float]],
    Field(description="Square matrix as rows of numbers; real part, or imaginary part when passed as imag"),
]

# MCP 1.29 defines Settings before FastMCP; resolve its lifespan annotation
# after the SDK module has finished loading instead of suppressing warnings.
Settings.model_rebuild(force=True)


class ContractMCP(FastMCP):
    """Reject unadvertised arguments before the SDK's compatibility coercion."""

    async def list_tools(self) -> list[Tool]:
        tools = await super().list_tools()
        for tool in tools:
            tool.inputSchema = {**tool.inputSchema, "additionalProperties": False}
        return tools


server = ContractMCP("quandela")


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


def presence(container: Any, names: tuple[str, ...]) -> dict[str, str]:
    """Each name's state in a mapping: "absent" (no key), "empty" (null or an empty value) or "present"."""
    sent = container if isinstance(container, dict) else {}
    return {name: "absent" if name not in sent else "present" if sent[name] else "empty" for name in names}


def with_bulk_presence(record: dict[str, Any], include_bulk: bool) -> dict[str, Any]:
    """The record plus a bulk_fields presence map; a default read shrinks each present BULK_SPECS value."""
    specs = record.get("specs")
    sent = specs if isinstance(specs, dict) else {}
    out = dict(record)
    # "empty" matches qd_platform.chip_architecture, which treats a null or empty value as no architecture.
    out["bulk_fields"] = presence(sent, BULK_SPECS)
    if not include_bulk and isinstance(specs, dict):
        out["specs"] = {
            key: {"stripped": True, "chars": len(json.dumps(value))} if key in BULK_SPECS and value else value
            for key, value in specs.items()
        }
    return out


def with_record_fields(record: dict[str, Any]) -> dict[str, Any]:
    """The record plus record_fields: presence of each PERCEVAL_SPECS field in specs and of the top-level type."""
    out = dict(record)
    out["record_fields"] = {
        **presence(record.get("specs"), PERCEVAL_SPECS),
        "record_type": presence(record, ("type",))["type"],
    }
    return out


@server.tool(annotations=READ)
@reported
async def qd_platform(name: PlatformName, include_bulk: bool = False) -> dict[str, Any]:
    """Processor record of one platform: constraints, input modes, commands, perfs, mitigations, versions.

    bulk_fields reports "present", "empty" (sent as null or empty) or "absent" for the serialized
    chip architecture and the HTML documentation, as the server sent them. include_bulk keeps their
    values; otherwise a present field is replaced by {"stripped": true, "chars": N}.
    record_fields reports the same three states for the specs fields Perceval 1.3.1 reads (commands,
    available_commands, default_mitigations, known_mitigations, architecture, type) and for the top-level
    type, so an omitted field reads as absent and a null or empty one as empty. Keys named in
    qd_platform.FORBIDDEN_KEYS are removed from the record at any depth.
    """
    record: dict[str, Any] = await threaded(lambda: get(platform_route(name)))
    return with_record_fields(with_bulk_presence(scrub(record), include_bulk))


@server.tool(annotations=READ)
@reported
async def qd_availability() -> dict[str, Any]:
    """Token job limits/occupancy, plus a dashboard link for platform-wide pending jobs.

    Token occupancy is not the platform queue depth or a queue position. The
    dashboard's waiting_jobs requires a browser session; offer its link when
    the caller needs that count. Opening the link requires the client's action.
    """
    occupancy = await threaded(availability)
    return {
        **occupancy,
        "platform_queue": {
            "count": None,
            "status": "requires-dashboard-session",
            "dashboard_url": "https://cloud.quandela.com/webide/",
            "action": "Offer to open the dashboard and read the platform card's pending jobs after sign-in.",
            "source": "GET /api/platform-permissions/users/{user_id}?count_jobs=true; waiting_jobs",
            "boundary": (
                "The job token cannot read this dashboard interface. Token occupancy and cumulative job usage "
                "do not determine platform queue depth or queue position. The dashboard count's user/global "
                "scope requires authenticated verification."
            ),
        },
    }


@server.tool(annotations=READ)
@reported
async def qd_usage() -> list[dict[str, Any]]:
    """The token usage report (jobs and usage per token, token ids removed)."""
    return await threaded(lambda: usage_rows(get("/api/tokens/usage/report")))


@server.tool(annotations=READ)
@reported
async def qd_plan(
    case_dir: Annotated[
        str, Field(description="Case directory under results/quandela/, e.g. results/quandela/cases/bdsc_qualification")
    ],
    platform: PlatformName,
    max_credits: Annotated[float, Field(description="Credit ceiling the plan checks", ge=0)] = 10.0,
    expected_seconds: Annotated[float, Field(description="Expected seconds, checked against max_duration", ge=0)] = 0.0,
    per_job_credits: Annotated[float, Field(description="Per-job price the plan adds to the ceiling", ge=0)] = 1.0,
) -> dict[str, Any]:
    """Read-only plan of one case: the job body's payload version, mitigations key, shot and credit estimates.

    Runs qd_platform.plan, which checks the case's digests, the platform's status and limits and the token's
    occupancy, and builds the job body without sending it; the body itself is left out, its sha256 stays. Submits,
    reserves and uploads nothing. The case directory must lie under results/quandela/. payload_version is 2 when the
    body carries a computation and 1 when it carries a command; payload_version_basis is "declared", "restored from
    RECORD" or "absent" for the processor's command set.
    """
    path = case_path(case_dir)
    planned = await threaded(lambda: plan(path, platform, max_credits, expected_seconds, per_job_credits))
    return plan_summary(planned)


@server.tool(annotations=READ)
@reported
async def qd_job_billing(
    job_id: JobId,
    per_job_credits: Annotated[float, Field(description="Per-job price in credits (1.0 measured)", ge=0)] = 1.0,
) -> dict[str, Any]:
    """Credits one job bills under the measured rule (per-job price plus price per shot times shots), from its job data.

    The cloud reports no per-job charge, so this applies the rule to the job's shots and the platform's Explorer
    price: charge_used prices the reported shots, charge_ceiling the payload's max_shots. Reads only.
    """

    def read() -> dict[str, Any]:
        data: dict[str, Any] = scrub(get(job_route(job_id, "data")))
        rows = [
            row
            for row in get("/api/platforms/public/explorer", auth=False)
            if row.get("name") == data.get("platform_name")
        ]
        if len(rows) != 1:
            raise PlatformError(f"{data.get('platform_name')} is not one Explorer platform")
        return job_billing(data, platform_row(rows[0]), per_job_credits)

    return await threaded(read)


@server.tool(annotations=READ)
@reported
async def qd_job_status(job_id: JobId) -> dict[str, Any]:
    """Status, progress and timing of one job."""
    status: dict[str, Any] = await threaded(lambda: get(job_route(job_id, "status")))
    return status


@server.tool(annotations=READ)
@reported
async def qd_job_result(job_id: JobId, include_raw: bool = False) -> dict[str, Any]:
    """Result of one finished job; every string at any depth truncates at RESULT_CHARACTERS unless include_raw."""
    result: dict[str, Any] = await threaded(lambda: get(job_route(job_id, "result")))
    return result if include_raw else truncated(result)


def truncated(value: Any) -> Any:
    """A JSON value whose strings and keys, at any depth, end after RESULT_CHARACTERS characters."""
    if isinstance(value, str):
        return value[:RESULT_CHARACTERS] + "..." if len(value) > RESULT_CHARACTERS else value
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for index, (key, item) in enumerate(value.items()):
            short = truncated(key) if isinstance(key, str) else key
            # Two long keys sharing a prefix stay distinct through their position.
            out[f"{short}#{index}" if short in out or short != key else short] = truncated(item)
        return out
    if isinstance(value, list):
        return [truncated(v) for v in value]
    return value


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
    if len(photons) != modes or any(type(occupation) is not int or occupation not in (0, 1) for occupation in photons):
        raise ValueError("input_photons must give 0 or 1 photon for each mode")
    for matrix in (real, imag):
        if matrix is not None and any(
            isinstance(entry, bool)
            or not isinstance(entry, (int, float))
            or not -1 - UNITARY_TOLERANCE <= entry <= 1 + UNITARY_TOLERANCE
            for row in matrix
            for entry in row
        ):
            raise ValueError("unitary matrix entries must be finite real numbers bounded by one within 1e-9")
    unitary = np.array(real, dtype=complex) + (1j * np.array(imag) if imag is not None else 0)
    if not np.allclose(unitary.conj().T @ unitary, np.eye(modes), rtol=0, atol=UNITARY_TOLERANCE):
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
        async with stream, stdio_server(stdout=stream) as (read_stream, write_stream):
            core = server._mcp_server
            # FastMCP disables JSON Schema checks to permit string-to-JSON
            # conversion. The advertised JSON types form the server contract.
            core.call_tool(validate_input=True)(server.call_tool)
            await core.run(read_stream, write_stream, core.create_initialization_options())

    anyio.run(run)


if __name__ == "__main__":
    serve()
