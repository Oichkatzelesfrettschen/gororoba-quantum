"""Quantum Inspire MCP server over stdio: backend catalogue, queues, usage ledger, jobs, results and local emulation.

The server wraps the compute job manager REST API through the Client of
qi_platform.py, so it reads the OAuth tokens that `qi login` stores and runs
under QI_PYTHON, the pinned Quantum Inspire environment that also carries
mcp 2.3.0 and qxelarator. Reads return JSON-serializable structures; a failed
call raises, so the MCP result carries isError instead of an error string
inside a successful payload.

Tools that change remote state are qi_compile (creates a project, algorithm,
commit and file, and runs the remote compiler; no execution) and qi_submit
(creates and enqueues a batch job, which executes on the backend). Each tool
annotation states which, and the client's permission rules ask before either.
qi_submit takes the user's approval text and refuses an empty one.

qi_run_local runs cQASM 3.0 on the local qxelarator state-vector emulator,
bounded to LOCAL_MAX_QUBITS qubits and LOCAL_MAX_SHOTS shots.

Usage: "$QI_PYTHON" scripts/qi_mcp_server.py   (stdio; launched by an MCP client)
"""

from __future__ import annotations

import functools
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.mcpserver import MCPServer  # noqa: E402
from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402
from qi_platform import Client, PlatformError, ledger  # noqa: E402

LOCAL_MAX_QUBITS = 24
LOCAL_MAX_SHOTS = 100_000
READ = ToolAnnotations(readOnlyHint=True, openWorldHint=True)
LOCAL = ToolAnnotations(readOnlyHint=True, openWorldHint=False)
MUTATE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=True)
LIMIT_FIELDS = (
    "id",
    "name",
    "identifier",
    "is_hardware",
    "nqubits",
    "status",
    "enabled",
    "default_number_of_shots",
    "max_number_of_shots",
    "job_execution_time_limit",
    "max_jobs_per_batch_job",
    "batchjobs_per_queue_limit",
    "supports_raw_data",
    "messages",
)

server = MCPServer("quantum-inspire")
_client: Client | None = None


def reported[**P, R](function: Callable[P, R]) -> Callable[P, R]:
    """Re-raise platform and validation failures as ToolError, whose message reaches the client."""

    @functools.wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return function(*args, **kwargs)
        except (PlatformError, ValueError, RuntimeError) as error:
            raise ToolError(f"{function.__name__}: {error}") from error

    return wrapper


def client() -> Client:
    global _client
    if _client is None:
        _client = Client()
    return _client


@server.tool(annotations=READ)
@reported
def qi_backends() -> list[dict[str, Any]]:
    """Every backend type this account can use, with qubit count, status, shot and time limits, and its queue."""
    rows = []
    for backend_type in client().pages("/backend_types/"):
        row = {key: backend_type[key] for key in LIMIT_FIELDS}
        row["queue"] = client().get(f"/backend_types/{backend_type['id']}/queue")
        rows.append(row)
    return rows


@server.tool(annotations=READ)
@reported
def qi_backend(backend_type_id: int) -> dict[str, Any]:
    """One backend type in full: gate set, topology (coupling edges), compiler passes, limits and queue."""
    backend_type: dict[str, Any] = client().get(f"/backend_types/{backend_type_id}")
    backend_type["queue"] = client().get(f"/backend_types/{backend_type_id}/queue")
    return backend_type


@server.tool(annotations=READ)
@reported
def qi_hardware_status() -> list[dict[str, Any]]:
    """Every physical and emulated backend instance with its status, message and last heartbeat."""
    rows: list[dict[str, Any]] = client().pages("/backends")
    return rows


@server.tool(annotations=READ)
@reported
def qi_usage() -> dict[str, Any]:
    """The account's transaction ledger aggregated by domain and backend type, beside each job's shots and seconds."""
    return ledger(client())


@server.tool(annotations=READ)
@reported
def qi_jobs(latest: int = 20) -> list[dict[str, Any]]:
    """The account's most recent jobs (status, batch, shots, queue and finish times), newest first."""
    jobs = client().pages("/jobs")
    return sorted(jobs, key=lambda job: job["id"], reverse=True)[:latest]


@server.tool(annotations=READ)
@reported
def qi_job(job_id: int) -> dict[str, Any]:
    """One job: its record, result metadata (shots done, execution seconds) and, unless completed, its logs."""
    job: dict[str, Any] = client().get(f"/jobs/{job_id}")
    results = client().get(f"/results/job/{job_id}", page=1, size=100)["items"]
    job["results"] = [{k: v for k, v in r.items() if k not in ("results", "raw_data")} for r in results]
    if job["status"] != "completed":
        job["logs"] = client().get(f"/jobs/{job_id}/logs")
    return job


@server.tool(annotations=READ)
@reported
def qi_results(job_id: int, include_raw: bool = False) -> list[dict[str, Any]]:
    """A job's results: outcome counts keyed by bit string and, on request, every shot.

    QX and the Tuna backends put qubit 0 at the rightmost character; the Ry emulator puts it at the leftmost.
    """
    results = client().get(f"/results/job/{job_id}", page=1, size=100)["items"]
    if not include_raw:
        for result in results:
            result.pop("raw_data", None)
    rows: list[dict[str, Any]] = results
    return rows


@server.tool(annotations=LOCAL)
@reported
def qi_run_local(cqasm: str, shots: int = 1024) -> dict[str, Any]:
    """Run cQASM 3.0 on the local qxelarator emulator (no account, no queue); returns outcome counts."""
    import qxelarator

    match = re.search(r"qubit\[(\d+)\]", cqasm)
    qubits = int(match.group(1)) if match else 1
    if qubits > LOCAL_MAX_QUBITS:
        raise ValueError(f"{qubits} qubits exceed the local bound of {LOCAL_MAX_QUBITS}")
    if not 1 <= shots <= LOCAL_MAX_SHOTS:
        raise ValueError(f"shots must lie in 1..{LOCAL_MAX_SHOTS}")
    try:
        result = qxelarator.execute_string(cqasm, iterations=shots)
    except Exception as error:  # qxelarator raises bare exceptions for parse and analysis failures
        raise ValueError(str(error)) from error
    if isinstance(result, qxelarator.SimulationError):
        raise ValueError(str(result))
    return {"shots": result.shots_done, "counts": dict(result.results)}


def _commit(name: str) -> dict[str, Any]:
    owner = client().member_id
    project = client().post("/projects", {"owner_id": owner, "name": name, "description": name, "starred": False})
    algorithm = client().post(
        "/algorithms", {"project_id": project["id"], "type": "quantum", "shared": "private", "name": name}
    )
    commit: dict[str, Any] = client().post("/commits", {"description": name, "algorithm_id": algorithm["id"]})
    return commit


def _language() -> int:
    for language in client().pages("/languages"):
        if language["name"] == "cQASM" and language["version"] == "3.0":
            return int(language["id"])
    raise RuntimeError("the platform lists no cQASM 3.0 language")


@server.tool(annotations=MUTATE)
@reported
def qi_compile(cqasm: str, backend_type_id: int, stage: str = "decomposition") -> dict[str, Any]:
    """Compile cQASM 3.0 remotely for a backend up to stage (decomposition, mapping, optimization or routing).

    Creates a project, algorithm, commit and file in the account; executes nothing.
    """
    commit = _commit("mcp-compile")
    client().post(
        "/files",
        {
            "commit_id": commit["id"],
            "content": cqasm,
            "language_id": _language(),
            "compile_stage": "none",
            "compile_properties": {},
            "name": "input.cq",
        },
    )
    client().post(f"/commits/{commit['id']}/compile", {"compile_stage": stage, "backend_type_id": backend_type_id})
    files = client().pages("/files", commit_id=commit["id"])
    return {"commit": commit["id"], "files": [{"name": f["name"], "content": f["content"]} for f in files]}


@server.tool(annotations=MUTATE)
@reported
def qi_submit(cqasm: str, backend_type_id: int, shots: int, approval: str, raw_data: bool = True) -> dict[str, Any]:
    """Submit one cQASM 3.0 circuit as a batch job; it executes on the backend and counts against its queue limits.

    approval is the user's own approval of this run, quoted; an empty approval is refused.
    """
    if not approval.strip():
        raise ValueError("qi_submit needs the user's approval text")
    backend_type = client().get(f"/backend_types/{backend_type_id}")
    if backend_type["status"] == "offline":
        raise RuntimeError(f"{backend_type['name']} is offline")
    if not 1 <= shots <= backend_type["max_number_of_shots"]:
        raise ValueError(f"shots must lie in 1..{backend_type['max_number_of_shots']}")
    commit = _commit("mcp-submit")
    file = client().post(
        "/files",
        {
            "commit_id": commit["id"],
            "content": cqasm,
            "language_id": _language(),
            "compile_stage": "none",
            "compile_properties": {},
            "name": "input.cq",
        },
    )
    batch = client().post("/batch_jobs", {"backend_type_id": backend_type_id})
    job = client().post(
        "/jobs",
        {"file_id": file["id"], "batch_job_id": batch["id"], "number_of_shots": shots, "raw_data_enabled": raw_data},
    )
    client().patch(f"/batch_jobs/{batch['id']}/enqueue")
    return {"batch_job": batch["id"], "job": job["id"], "backend": backend_type["name"], "approval": approval}


if __name__ == "__main__":
    server.run()
