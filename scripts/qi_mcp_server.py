"""Quantum Inspire MCP server over stdio: backend catalogue, queues, usage ledger, jobs, results and local emulation.

The server wraps the compute job manager REST API through the Client of
qi_platform.py, so it reads the OAuth tokens that `qi login` stores and runs
under QI_PYTHON, the pinned Quantum Inspire environment that also carries
mcp 2.3.0 and qxelarator. Reads return JSON-serializable structures; a failed
call raises, so the MCP result carries isError instead of an error string
inside a successful payload.

Tools that change remote state are qi_compile (creates a project, algorithm,
commit and file, and runs the remote compiler; no execution) and qi_submit_case
(creates and enqueues a batch job from a retained case directory). Each tool
annotation states which, and the client's permission rules ask before either.
qi_submit_case uses qi_platform.submit's durable submission guard and requires
the user's approval text. The legacy raw-string qi_submit refuses execution
and names the case-directory replacement.

qi_run_local runs cQASM 3.0 on the local qxelarator state-vector emulator,
bounded to LOCAL_MAX_QUBITS qubits and LOCAL_MAX_SHOTS shots.

Usage: "$QI_PYTHON" scripts/qi_mcp_server.py   (stdio; launched by an MCP client)
"""

from __future__ import annotations

import functools
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.mcpserver import MCPServer  # noqa: E402
from mcp.server.mcpserver.exceptions import ToolError  # noqa: E402
from mcp.types import ToolAnnotations  # noqa: E402
from qi_platform import Client, PlatformError, declared_qubits, ledger, submit, utc_now  # noqa: E402

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
        except SystemExit as error:
            # The case-directory CLI rejects invalid or repeated submissions
            # with SystemExit. A tool failure must not terminate stdio serving.
            raise ToolError(f"{function.__name__}: {error}") from error

    return wrapper


def client() -> Client:
    global _client
    if _client is None:
        _client = Client()
    return _client


@server.tool(annotations=READ)
@reported
def qi_backends(user_only: bool = True) -> list[dict[str, Any]]:
    """Fresh backend types and scoped queues; user_only selects account (default) or global queue counts."""
    started = utc_now().isoformat()
    connection = client()
    rows = []
    for backend_type in connection.pages("/backend_types/"):
        row = {key: backend_type[key] for key in LIMIT_FIELDS}
        row["queue"] = connection.get(f"/backend_types/{backend_type['id']}/queue", user_only=user_only)
        row.update(queue_user_only=user_only, request_started_utc=started, retrieved_utc=utc_now().isoformat())
        rows.append(row)
    return rows


@server.tool(annotations=READ)
@reported
def qi_backend(backend_type_id: int, user_only: bool = True) -> dict[str, Any]:
    """Fresh backend type, physical instances and scoped queue; the provider enable flag is separate from status."""
    started = utc_now().isoformat()
    connection = client()
    backend_type: dict[str, Any] = dict(connection.get(f"/backend_types/{backend_type_id}"))
    backend_type["queue"] = connection.get(f"/backend_types/{backend_type_id}/queue", user_only=user_only)
    backend_type["backend_instances"] = [
        row for row in connection.pages("/backends") if row["backend_type_id"] == backend_type_id
    ]
    backend_type.update(queue_user_only=user_only, request_started_utc=started, retrieved_utc=utc_now().isoformat())
    return backend_type


@server.tool(annotations=READ)
@reported
def qi_hardware_status() -> list[dict[str, Any]]:
    """Fresh backend-instance statuses and heartbeats, with the interval of the API reads."""
    started = utc_now().isoformat()
    rows: list[dict[str, Any]] = client().pages("/backends")
    finished = utc_now().isoformat()
    return [dict(row, request_started_utc=started, retrieved_utc=finished) for row in rows]


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

    qubits = declared_qubits(cqasm)
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


COMPILE_STAGES = ("none", "decomposition", "mapping", "optimization", "routing")


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
    # The stage and the backend type are checked before the first mutation, so a
    # rejected value leaves no remote resource.
    if stage not in COMPILE_STAGES:
        raise ValueError(f"stage must be one of {', '.join(COMPILE_STAGES)}, not {stage!r}")
    client().get(f"/backend_types/{backend_type_id}")
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
def qi_submit_case(case_dir: str, backend_type_id: int, approval: str) -> dict[str, Any]:
    """Submit a retained case directory as one batch, recording durable state and enabling raw shots.

    The directory contains cases.json and every cQASM file whose digest it
    names. The manifest supplies the shots. Existing submission state blocks
    another run, including after an uncertain response. Use qi_platform.py
    reconcile for read-only recovery and collect to retain the results.
    """
    return submit(Path(case_dir), backend_type_id, approval)


@server.tool(annotations=MUTATE)
@reported
def qi_submit(cqasm: str, backend_type_id: int, shots: int, approval: str, raw_data: bool = True) -> dict[str, Any]:
    """Legacy raw-string submission: refused; migrate to qi_submit_case with a retained manifest."""
    raise ValueError(
        "raw-string qi_submit no longer executes: retain the cQASM files and their sha256 digests in cases.json, "
        "then call qi_submit_case(case_dir, backend_type_id, approval). The manifest supplies the shots; "
        "raw shot retention is always enabled."
    )


if __name__ == "__main__":
    server.run()
