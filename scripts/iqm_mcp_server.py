"""IQM Resonance MCP server over stdio: quantum computers, availability, calibration, artifacts, credits, jobs.

The server calls the IQM Server REST and GraphQL APIs through iqm_platform.Client
with the API token of the file IQM_TOKENS_FILE names, reread on every call, so
a token that iqm_platform.py refresh installs serves the next call without a
restart. It runs under the build host's system Python, which carries mcp 1.29
(FastMCP); it imports nothing from the iqm-resonance-stack package. Reads
return JSON-serializable structures; a failed call raises ToolError, so the
MCP result carries isError with the route and the service's message.

iqm_cancel_job is the one tool that changes remote state; its annotation says
so and the client's permission rules ask before it. Job submission and
timeslot booking are outside this server: every IQM job and timeslot spends
credits and waits for a written case and the user's approval.
iqm_platform.check_mcp holds the tool set and the annotations.

Usage: IQM_TOKENS_FILE=TOKENS.json /usr/bin/python3 -I scripts/iqm_mcp_server.py   (stdio; launched by an MCP client)
"""

from __future__ import annotations

import functools
import json
import sys
import urllib.parse
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Annotated, Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import anyio  # noqa: E402
from iqm_platform import API, Client, PlatformError, read_tokens, tokens_path  # noqa: E402
from mcp.server.fastmcp import FastMCP  # noqa: E402
from mcp.server.fastmcp.exceptions import ToolError  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402
from pydantic import Field  # noqa: E402

READ = ToolAnnotations(readOnlyHint=True, openWorldHint=True)
MUTATE = ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=True)
QC_ARTIFACTS = (
    "about",
    "channel-properties",
    "chip-design-records",
    "configuration",
    "duts",
    "settings",
    "static-architecture",
    "static-quantum-architectures",
)
JOB_ARTIFACTS = ("measurement_counts", "measurements", "runtime_estimates", "sweep_results")

Alias = Annotated[
    str,
    Field(
        description="Quantum computer alias, e.g. garnet, emerald, sirius, garnet:mock", pattern=r"^[a-z0-9]+(:mock)?$"
    ),
]
JobId = Annotated[str, Field(description="Job id (a UUID)", pattern=r"^[0-9a-fA-F-]{36}$")]
Locus = Annotated[
    str | None,
    Field(
        description="Keep only observations whose field names this qubit or resonator, e.g. QB4",
        pattern=r"^(QB|COMPR)\d+$",
    ),
]

server = FastMCP("iqm")


def client() -> Client:
    return Client(read_tokens(tokens_path())["access_token"])


def get_json(path: str) -> Any:
    status, body = client().get(path)
    if status != 200:
        raise PlatformError(f"GET {path} answered {status}: {body[:400]!r}")
    return json.loads(body)


def reported[**P, R](function: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    """Re-raise platform and validation failures as ToolError, whose message reaches the client."""

    @functools.wraps(function)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await function(*args, **kwargs)
        except (PlatformError, ValueError, KeyError, TypeError, OSError) as error:
            raise ToolError(f"{function.__name__}: {error}") from error

    return wrapper


async def threaded[R](call: Callable[[], R]) -> R:
    """Run a blocking call in a worker thread so the stdio loop keeps serving."""
    return await anyio.to_thread.run_sync(call)


def qc_path(alias: str, suffix: str = "") -> str:
    return f"{API}/quantum-computers/{urllib.parse.quote(alias)}{suffix}"


@server.tool(annotations=READ)
@reported
async def iqm_quantum_computers() -> Any:
    """Every quantum computer the token reaches: alias, status, health, queue length, station control version."""
    return await threaded(lambda: get_json(f"{API}/quantum-computers"))


@server.tool(annotations=READ)
@reported
async def iqm_quantum_computer(alias: Alias) -> Any:
    """One quantum computer: description, qubit count, job limits, pay-as-you-go and timeslot pricing, health."""
    return await threaded(lambda: get_json(qc_path(alias)))


@server.tool(annotations=READ)
@reported
async def iqm_queue_availability(alias: Alias) -> Any:
    """Pay-as-you-go availability windows (UTC) and queue length; gaps are calibration and maintenance."""
    return await threaded(lambda: get_json(qc_path(alias, "/queue-availability")))


@server.tool(annotations=READ)
@reported
async def iqm_timeslots(alias: Alias) -> Any:
    """Bookable and booked timeslots of one quantum computer."""
    return await threaded(lambda: get_json(qc_path(alias, "/timeslots")))


@server.tool(annotations=READ)
@reported
async def iqm_architecture(alias: Alias) -> Any:
    """Dynamic quantum architecture of the default calibration set: qubits, resonators, gates, loci, implementations."""
    return await threaded(
        lambda: get_json(f"{API}/calibration-sets/{urllib.parse.quote(alias)}/default/dynamic-quantum-architecture")
    )


@server.tool(annotations=READ)
@reported
async def iqm_metrics(alias: Alias, locus: Locus = None) -> Any:
    """Quality metrics of the default calibration set (T1, T2, RB and IRB fidelities, readout), optionally one locus."""

    def read() -> Any:
        document = get_json(f"{API}/calibration-sets/{urllib.parse.quote(alias)}/default/metrics")
        rows = document["observations"]
        if locus:
            rows = [
                row
                for row in rows
                if f".{locus}." in row["dut_field"]
                or f"{locus}__" in row["dut_field"]
                or f"__{locus}." in row["dut_field"]
            ]
        keep = ("dut_field", "value", "unit", "uncertainty", "invalid")
        return {
            "calibration_set_id": document["describes_id"],
            "dut_label": document["dut_label"],
            "created_timestamp": document["created_timestamp"],
            "observations": [{k: row.get(k) for k in keep} for row in rows],
        }

    return await threaded(read)


@server.tool(annotations=READ)
@reported
async def iqm_artifact(alias: Alias, kind: str) -> Any:
    """A configuration artifact of one QC; kind is one of QC_ARTIFACTS."""
    if kind not in QC_ARTIFACTS:
        raise ValueError(f"kind must be one of {QC_ARTIFACTS}")
    return await threaded(lambda: get_json(qc_path(alias, f"/artifacts/{kind}")))


@server.tool(annotations=READ)
@reported
async def iqm_credit() -> dict[str, Any]:
    """Account type, credit balance and credit expiry of the account the token is bound to."""

    def read() -> dict[str, Any]:
        api = client()
        account = api.graphql("{ me { currentAccount { id type } } }")["me"]["currentAccount"]
        credit = api.graphql(
            "query($a: UUID!){ credit(accountId: $a) { currentBalance expiresAt } }", {"a": account["id"]}
        )
        return {"account_type": account["type"], "credit": credit["credit"]}

    return await threaded(read)


@server.tool(annotations=READ)
@reported
async def iqm_tokens() -> list[dict[str, Any]]:
    """Scopes, expiry and refreshability of the account's API tokens."""

    def read() -> list[dict[str, Any]]:
        return [
            {
                "scopes": t["scopes"],
                "expires_at": t["expires_at"],
                "refresh_expires_at": (t.get("refresh_token") or {}).get("expires_at"),
            }
            for t in get_json(f"{API}/tokens")["tokens"]
        ]

    return await threaded(read)


@server.tool(annotations=READ)
@reported
async def iqm_job(job_id: JobId) -> Any:
    """Status, queue position, timeline, errors and billed seconds of one job."""
    return await threaded(lambda: get_json(f"{API}/jobs/{job_id}"))


@server.tool(annotations=READ)
@reported
async def iqm_job_artifact(job_id: JobId, kind: str) -> Any:
    """A job artifact: measurement_counts, measurements, runtime_estimates or sweep_results."""
    if kind not in JOB_ARTIFACTS:
        raise ValueError(f"kind must be one of {JOB_ARTIFACTS}")
    return await threaded(lambda: get_json(f"{API}/jobs/{job_id}/artifacts/{kind}"))


@server.tool(annotations=MUTATE)
@reported
async def iqm_cancel_job(job_id: JobId) -> dict[str, Any]:
    """Cancel one waiting or processing job."""

    def cancel() -> dict[str, Any]:
        status, reply = client().post(f"{API}/jobs/{job_id}/cancel", {})
        if status not in (200, 202, 204):
            raise PlatformError(f"cancel answered {status}: {reply}")
        return {"job_id": job_id, "status": status}

    return await threaded(cancel)


if __name__ == "__main__":
    server.run("stdio")
