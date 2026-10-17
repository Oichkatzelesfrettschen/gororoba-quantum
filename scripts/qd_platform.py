"""Quandela Cloud account reads and the retained catalogue the Quandela guide cites.

Quandela Cloud serves photonic QPUs and simulators through one REST API,
https://api.cloud.quandela.com, which authenticates every job and account read
with a personal job token sent as ``Authorization: Bearer``. The token is
created on the portal's Tokens page; it lives outside every checkout in the
file QUANDELA_TOKEN_FILE names, and nothing here prints, logs or retains it.
Perceval (perceval-quandela 1.3.1 with exqalibur 1.4.2, Arch packages on the
build host) is the SDK; these reads use the documented REST routes directly,
so only the token file and the standard library are needed. check and facts
run offline under the repository's $PYTHON.

Subcommands:

- snapshot --out DIR (network, read-only) writes catalogue.json: the public
  platform list and the Explorer offer's platforms (name, kind, status,
  per-job duration limit, per-shot price, bookable and locked flags, daily
  availability statistic, the next maintenance window), each platform's
  processor record from /api/platforms/{name}/processor (constraints,
  connected photon-source input modes, native commands, detector, mitigations,
  chip architecture, documentation, performance figures, software versions),
  the token's job availability (/api/jobs/availability) and its usage report
  (/api/tokens/usage/report) without token ids, and the cloud API version.
  It refuses to run unless QUANDELA_TOKEN_FILE names the token file, and it
  creates, cancels and submits nothing.
- check DIR [--agents FILE...] (offline) requires the catalogue to carry its
  schema and no account identifier (FORBIDDEN_KEYS at any depth), one
  processor record per Explorer platform, photon and mode limits that agree
  with each other and with the connected input modes, non-negative per-shot
  prices and complete availability counters, and loads qd_mcp_server.py with
  mcp replaced by recorders to require exactly the tools MCP_TOOLS names,
  every one read-only except MCP_MUTATING. With --agents it renders
  facts_table and requires each FILE's quandela-facts markers to enclose
  exactly that table, so a refreshed snapshot that changes a limit, a
  command set or a price fails until AGENTS.md and the Quandela README change
  with it, and a FILE whose table lists qd_ tools must list exactly
  MCP_TOOLS. Status, performance figures, availability statistics, maintenance
  windows and software versions change between reads and stay out of the
  table.
- facts DIR prints the table.
- plan RUN_DIR --platform NAME --max-credits C (network, read-only) runs
  every check submit makes and prints the result: the circuit matches its
  cases.json sha256, the platform is one the case admits, is available and
  allows the case's max_duration, max_shots times the live price per shot
  stays within C, the token has no running or queued job, and Perceval's
  estimate_required_shots for max_samples stays within max_shots. It builds
  the job body through Perceval's own RemoteComputer.prepare_payload and
  communication-layer send with create_job replaced by a recorder, so the
  body is exactly Perceval's and nothing leaves.
- submit RUN_DIR --platform NAME --max-credits C --approval TEXT repeats
  plan under an flock beside the token file, writes submission-state.json
  before the request (a lost answer leaves a case submit refuses, never one
  it sends twice), posts the body to /api/jobs with the case's max_duration
  and retains job-body.json and submission.json with the approval, the plan
  and the usage report before the job.
- collect RUN_DIR waits for a terminal status, then retains the result
  answer byte for byte in raw/result.json (written once; a recollection
  must bring the same bytes) and results.json with the scrubbed
  status and job data, the usage report after the job and the counts that
  parse_counts reads from the serialized BSCount: plain Fock states only,
  zipped or not, never through perceval.serialization.deserialize.
- runs [--runs DIR] prints run_facts of every retained run, the rules
  scripts/research_state.py applies to the quandela provider.
- --self-test proves check rejects a token id, a staff creator id, a missing
  processor record, an input mode outside the chip, a photon limit off the
  connected modes, a negative price, a missing availability counter, an
  edited table, a stale row inside the markers, a tool table missing a tool,
  a server that adds a submit tool, marks cancel read-only or marks a read
  as mutating, on a temporary copy; and, against a stubbed service, that
  plan refuses a platform outside the case, one under maintenance, a ceiling
  above the case's credits, a busy token and an estimate above max_shots,
  submit refuses an empty approval and a second submission and records a
  refused POST as refused, collect drops token fields at any depth and
  refuses a recollection whose bytes differ, run_facts refuses an edited raw result, case or job body, a
  missing approval, a token field, another job id and an uncollected run,
  and parse_counts refuses other tags, annotated or repeated states and an
  oversized zipped result.

Usage: QUANDELA_TOKEN_FILE=TOKEN "$PYTHON" scripts/qd_platform.py snapshot --out DIR
       QUANDELA_TOKEN_FILE=TOKEN "$PYTHON" scripts/qd_platform.py (plan | submit | collect) RUN_DIR ...
       "$PYTHON" scripts/qd_platform.py (check DIR [--agents FILE...] | facts DIR | runs | --self-test)
"""

from __future__ import annotations

import argparse
import ast
import base64
import datetime
import fcntl
import functools
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch

from oq_platform import keys

API = "https://api.cloud.quandela.com"
CATALOGUE_SCHEMA = "qd-catalogue-v1"
TOKEN_ENV = "QUANDELA_TOKEN_FILE"
USER_AGENT = "gororoba-quantum qd_platform"
# Keys that identify the account, its tokens or Quandela staff; the snapshot
# drops them and check refuses a catalogue that carries one at any depth.
FORBIDDEN_KEYS = (
    "token",
    "token_id",
    "token_label",
    "token_value",
    "creator_id",
    "user_id",
    "entity_id",
    "email",
)
AVAILABILITY_KEYS = (
    "max_concurrent_jobs",
    "max_jobs_in_queue",
    "max_running_qt_jobs",
    "num_concurrent_jobs",
    "num_jobs_in_queue",
    "num_running_qt_jobs",
)
PLATFORM_FIELDS = (
    "name",
    "type",
    "status",
    "description",
    "max_duration",
    "price_per_shot",
    "bookable",
    "is_locked",
    "is_offer_platform",
    "statistic",
)
MAINTENANCE_FIELDS = ("maintenance_title", "start_time", "end_time", "time_zone")
PACKAGES = ("perceval-quandela", "exqalibur")
# The MCP server's tools; qd_cancel_job alone changes remote state.
MCP_TOOLS = (
    "qd_availability",
    "qd_cancel_job",
    "qd_job_result",
    "qd_job_status",
    "qd_platform",
    "qd_platforms",
    "qd_simulate_local",
    "qd_usage",
)
MCP_MUTATING = ("qd_cancel_job",)
MCP_SERVER = Path(__file__).with_name("qd_mcp_server.py")
BEGIN = "<!-- quandela-facts:begin -->\n"
END = "<!-- quandela-facts:end -->"


class PlatformError(RuntimeError):
    """A Quandela Cloud read failed; the message carries the route and the service's answer."""


class RefusedError(PlatformError):
    """The service answered with an HTTP error status, so the request took no effect it reported."""


def now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


def token() -> str:
    """The job token from the file QUANDELA_TOKEN_FILE names."""
    path = os.environ.get(TOKEN_ENV)
    if not path or not Path(path).is_file():
        raise PlatformError(f"{TOKEN_ENV} must name the job token file")
    value = Path(path).read_text(encoding="utf-8").strip()
    if not value:
        raise PlatformError(f"the file {TOKEN_ENV} names is empty")
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuses every redirect, so the bearer token reaches API alone."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        return None


OPENER = urllib.request.build_opener(NoRedirect)
# The service's answer to a refused token names no cause; these name the usual ones.
STATUS_HINTS = {
    401: "the token is missing, expired or revoked; create one on the portal's Tokens page",
    403: "the token lacks this platform; grant it on the token's Permissions tab",
    404: "no such platform or job for this token",
}


def request(method: str, route: str, auth: bool = True, body: Any = None, raw: bool = False) -> Any:
    """JSON answer (or raw bytes) of one API call; any failure raises PlatformError naming the route and the cause."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {token()}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    call = urllib.request.Request(API + route, data=data, headers=headers, method=method)
    try:
        with OPENER.open(call, timeout=60) as response:
            answer = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read()[:500].decode("utf-8", errors="replace")
        error.close()
        hint = STATUS_HINTS.get(error.code, "redirect refused" if 300 <= error.code < 400 else "")
        raise RefusedError(f"{method} {route}: HTTP {error.code} {detail} {hint}".rstrip()) from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise PlatformError(f"{method} {route}: {error}") from None
    if raw:
        return answer
    try:
        return json.loads(answer) if answer else None
    except json.JSONDecodeError:
        raise PlatformError(f"{method} {route}: answer is not JSON: {answer[:200]!r}") from None


def get(route: str, auth: bool = True) -> Any:
    return request("GET", route, auth)


def platform_route(name: str) -> str:
    return "/api/platforms/" + urllib.parse.quote_plus(name) + "/processor"


def job_route(job_id: str, part: str) -> str:
    return "/api/jobs/" + urllib.parse.quote(job_id, safe="") + "/" + part


def platform_row(row: dict[str, Any]) -> dict[str, Any]:
    """An Explorer platform row without staff and booking identifiers."""
    record = {field: row.get(field) for field in PLATFORM_FIELDS}
    maintenance = row.get("maintenance")
    record["maintenance"] = (
        {field: maintenance.get(field) for field in MAINTENANCE_FIELDS} if isinstance(maintenance, dict) else None
    )
    return record


def scrub(value: Any) -> Any:
    """A JSON value without FORBIDDEN_KEYS at any depth."""
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items() if k not in FORBIDDEN_KEYS}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def usage_rows(report: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The token usage report without FORBIDDEN_KEYS at any depth."""
    rows: list[dict[str, Any]] = scrub(report)
    return rows


def availability() -> dict[str, Any]:
    record = get("/api/jobs/availability")
    return {key: record.get(key) for key in AVAILABILITY_KEYS}


def versions() -> dict[str, str | None]:
    found: dict[str, str | None] = {}
    for name in PACKAGES:
        try:
            found[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            found[name] = None
    return found


def snapshot(out: Path) -> None:
    token()
    rows = get("/api/platforms/public/explorer", auth=False)
    explorer = sorted((platform_row(row) for row in rows), key=lambda p: p["name"])
    public = [
        {"name": row["name"], "type": row["type"], "status": row["status"]}
        for row in get("/api/platforms/public", auth=False)
    ]
    processors = {row["name"]: get(platform_route(row["name"])) for row in explorer}
    catalogue = {
        "schema": CATALOGUE_SCHEMA,
        "retrieved_utc": now(),
        "api": API,
        "api_version": get("/openapi.json", auth=False)["info"]["version"],
        "versions": versions(),
        "account": {
            "availability": availability(),
            "token_usage": usage_rows(get("/api/tokens/usage/report")),
        },
        "public_platforms": sorted(public, key=lambda p: p["name"]),
        "explorer_platforms": explorer,
        "processors": processors,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "catalogue.json").write_text(json.dumps(scrub(catalogue), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{len(explorer)} Explorer platforms, {len(public)} public platforms")


def span(low: int | None, high: int | None) -> str:
    if low is None and high is None:
        return "-"
    return f"{low}..{high}" if high is not None else f"{low}+"


def facts_table(catalogue: dict[str, Any]) -> str:
    """Markdown table of each Explorer platform's limits, commands and price."""
    lines = [
        "| platform | kind | description | modes | photons | photon-source input modes | native commands "
        "| detector | max s per job | credits per shot |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in catalogue["explorer_platforms"]:
        specs = catalogue["processors"][row["name"]].get("specs", {})
        limits = specs.get("constraints", {})
        modes = specs.get("connected_input_modes")
        lines.append(
            f"| `{row['name']}` | {row['type']} | {row['description']} "
            f"| {span(limits.get('min_mode_count'), limits.get('max_mode_count'))} "
            f"| {span(limits.get('min_photon_count'), limits.get('max_photon_count'))} "
            f"| {', '.join(map(str, modes)) if modes else '-'} "
            f"| {', '.join(specs.get('available_commands', [])) or '-'} "
            f"| {specs.get('detector') or '-'} | {row['max_duration']} | {row['price_per_shot']:g} |"
        )
    limits = catalogue["account"]["availability"]
    retired = [row["name"] for row in catalogue["explorer_platforms"] if row["status"] == "decommissioned"]
    mitigations = sorted(
        {m for p in catalogue["processors"].values() for m in p.get("specs", {}).get("known_mitigations") or []}
    )
    return (
        "\n".join(lines)
        + f"\n\nToken job limits (/api/jobs/availability): {limits['max_concurrent_jobs']} running, "
        + f"{limits['max_jobs_in_queue']} queued, {limits['max_running_qt_jobs']} running Quantum Toolbox jobs."
        + f"\n\nKnown error mitigations: {', '.join(mitigations)}."
        + f"\n\nDecommissioned at the snapshot: {', '.join(f'`{n}`' for n in retired) or 'none'}.\n"
    )


class ToolRecorder:
    """Stands in for FastMCP: records each tool's name and annotations."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.tools: dict[str, dict[str, Any]] = {}

    def tool(self, annotations: dict[str, Any] | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def register(function: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[function.__name__] = dict(annotations or {})
            return function

        return register


def mcp_surface(server: Path = MCP_SERVER) -> dict[str, dict[str, Any]]:
    """Tool names and annotations of the MCP server, loaded with mcp, anyio and pydantic replaced by stand-ins."""
    names = (
        "anyio",
        "mcp",
        "mcp.server",
        "mcp.server.fastmcp",
        "mcp.server.fastmcp.exceptions",
        "mcp.server.stdio",
        "mcp.types",
        "pydantic",
    )
    modules = {name: ModuleType(name) for name in names}
    modules["mcp.server.fastmcp"].FastMCP = ToolRecorder  # type: ignore[attr-defined]
    modules["mcp.server.fastmcp.exceptions"].ToolError = RuntimeError  # type: ignore[attr-defined]
    modules["mcp.server.stdio"].stdio_server = MagicMock()  # type: ignore[attr-defined]
    modules["mcp.types"].ToolAnnotations = dict  # type: ignore[attr-defined]
    modules["pydantic"].Field = MagicMock()  # type: ignore[attr-defined]
    spec = importlib.util.spec_from_file_location("qd_mcp_surface", server)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {server}")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    tools: dict[str, dict[str, Any]] = module.server.tools
    return tools


# Modules through which a tool could reach the network without qd_platform.request.
NETWORK_MODULES = {"http", "httpx", "requests", "socket", "urllib", "urllib3", "aiohttp"}


def check_routes(server: Path) -> None:
    """Binds the server's code to its annotations: only MCP_MUTATING tools call request, no QRNG route
    appears, and no module other than qd_platform reaches the network."""
    tree = ast.parse(server.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import | ast.ImportFrom):
            roots = {
                (alias.name if isinstance(node, ast.Import) else node.module or "").split(".")[0]
                for alias in node.names
            }
            if reached := roots & NETWORK_MODULES:
                raise SystemExit(f"{server.name}: imports {sorted(reached)}; network access goes through qd_platform")
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and "/qt/" in node.value:
            raise SystemExit(f"{server.name}: names the QRNG route {node.value!r}")
    allowed: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef | ast.FunctionDef) and node.name in MCP_MUTATING:
            allowed |= {id(inner) for inner in ast.walk(node)}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "request" and id(node) not in allowed:
            raise SystemExit(f"{server.name}: line {node.lineno} calls request outside {MCP_MUTATING}")


def check_mcp(server: Path = MCP_SERVER) -> None:
    check_routes(server)
    tools = mcp_surface(server)
    if tuple(sorted(tools)) != MCP_TOOLS:
        raise SystemExit(f"MCP tools {sorted(tools)} differ from {MCP_TOOLS}")
    mutating = tuple(sorted(name for name, notes in tools.items() if notes.get("readOnlyHint") is not True))
    if mutating != MCP_MUTATING:
        raise SystemExit(f"MCP tools {mutating} change remote state, expected {MCP_MUTATING}")


def tool_rows(text: str) -> list[str]:
    """Tool names of the Markdown table rows that open with a backquoted qd_ name."""
    return [line.split("`")[1] for line in text.splitlines() if line.startswith("| `qd_")]


def check_agents(catalogue: dict[str, Any], files: list[Path]) -> None:
    table = facts_table(catalogue)
    tables = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        if rows := tool_rows(text):
            if tuple(sorted(rows)) != MCP_TOOLS:
                raise SystemExit(f"{path}: MCP tool table {sorted(rows)} differs from {MCP_TOOLS}")
            tables += 1
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            raise SystemExit(f"{path}: needs one quandela-facts section")
        if text[text.index(BEGIN) + len(BEGIN) : text.index(END)] != table:
            raise SystemExit(f"{path}: the quandela-facts table differs from facts_table of the snapshot")
    # The guide's tool table states each tool's approval rule; a check over the
    # guides requires one file to carry it.
    if not tables:
        raise SystemExit("no --agents file carries the MCP tool table")


# ---------------------------------------------------------------- case runner

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "results/quandela/runs"
CASES_SCHEMAS = ("qd-box-kite-cases-v1",)
CIRCUIT_SCHEMA = "qd-circuit-v1"
STATE_SCHEMA = "qd-submission-state-v1"
SUBMISSION_SCHEMA = "qd-submission-v1"
COLLECTION_SCHEMA = "qd-collection-v1"
TERMINAL = ("completed", "error", "canceled")
# Perceval 1.3.1 is the client whose payload format the runner captures.
RUNNER_PERCEVAL = "1.3.1"
# A decompressed result larger than this is refused rather than parsed.
RESULT_LIMIT = 64 << 20
STATE_PATTERN = re.compile(r"\|(\d+(?:,\d+)*)>=(\d+)")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_case(case_dir: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    """cases.json, circuit.json and the cases.json sha256; raises when the circuit differs from its digest."""
    cases_bytes = (case_dir / "cases.json").read_bytes()
    manifest: dict[str, Any] = json.loads(cases_bytes)
    if manifest.get("schema") not in CASES_SCHEMAS:
        raise PlatformError(f"{case_dir}/cases.json schema {manifest.get('schema')!r} is not a Quandela case")
    circuit_bytes = (case_dir / manifest["circuit"]["file"]).read_bytes()
    if sha256_bytes(circuit_bytes) != manifest["circuit"]["sha256"]:
        raise PlatformError(f"{case_dir}: circuit.json differs from its cases.json sha256")
    circuit: dict[str, Any] = json.loads(circuit_bytes)
    if circuit.get("schema") != CIRCUIT_SCHEMA:
        raise PlatformError(f"{case_dir}: circuit schema {circuit.get('schema')!r}")
    return manifest, circuit, sha256_bytes(cases_bytes)


def real(entry: list[str]) -> float:
    """The float of an exact entry [a, b] = a + b sqrt(2)."""
    return float(Fraction(entry[0])) + float(Fraction(entry[1])) * math.sqrt(2.0)


def experiment(manifest: dict[str, Any], circuit: dict[str, Any]) -> Any:
    """The Perceval Experiment of a case: one Unitary per component, the input state, the photon filter."""
    import numpy
    import perceval as pcvl

    chip = pcvl.Circuit(circuit["modes"])
    for component in circuit["components"]:
        matrix = numpy.array([[real(x) for x in row] for row in component["unitary"]], dtype=complex)
        chip.add(component["at"], pcvl.Unitary(pcvl.Matrix(matrix)))
    built = pcvl.Experiment(chip)
    built.with_input(pcvl.BasicState(circuit["input_state"]))
    built.min_detected_photons_filter(manifest["min_detected_photons"])
    return built


def explorer_row(platform: str) -> dict[str, Any]:
    rows = [row for row in get("/api/platforms/public/explorer", auth=False) if row.get("name") == platform]
    if len(rows) != 1:
        raise PlatformError(f"{platform} is not one Explorer platform")
    return platform_row(rows[0])


def payload(case_dir: Path, manifest: dict[str, Any], circuit: dict[str, Any], platform: str) -> dict[str, Any]:
    """Perceval's job body for the case and its live shot estimate, built without sending anything.

    RemoteComputer.prepare_payload and RPCBasedCommunicationLayer.send build
    the body exactly as Perceval sends it; the RPC handler's create_job is
    replaced by a recorder, so the body comes back instead of leaving.
    Perceval reads the platform's processor record with the token to do so.
    """
    from perceval import ExecutionFactory, QuandelaCommunicationLayer, RemoteComputer

    found = versions()
    if found.get("perceval-quandela") != RUNNER_PERCEVAL:
        raise PlatformError(f"perceval-quandela {found.get('perceval-quandela')} is installed, not {RUNNER_PERCEVAL}")
    layer = QuandelaCommunicationLayer(platform, token=token())
    computer = RemoteComputer(layer)
    factory = ExecutionFactory(computer, experiment(manifest, circuit), max_shots_per_call=manifest["max_shots"])
    computation = factory.build_computation(manifest["command"])
    computation.add_params(max_samples=manifest["max_samples"])
    computation.job_name = f"gororoba-{case_dir.name}"[:64]
    computer.validate_single(computation)
    estimate = computer.estimate_required_shots(computation, nsamples=manifest["max_samples"])
    captured: dict[str, Any] = {}

    def record(cloud_data: dict[str, Any]) -> str:
        captured["body"] = cloud_data
        return "recorded"

    layer._rpc_handler.create_job = record
    layer.send(computer.prepare_payload(computation))
    body: dict[str, Any] = {**captured["body"], "max_duration": manifest["max_duration"]}
    if token() in json.dumps(body):
        raise PlatformError("the job body carries the token")
    return {"body": body, "estimated_shots": estimate, "versions": found}


def plan(case_dir: Path, platform: str, max_credits: float) -> dict[str, Any]:
    """Every check submit makes, read-only: digests, platform, price ceiling, availability and the estimate."""
    manifest, circuit, cases_sha256 = load_case(case_dir)
    if platform not in manifest["platforms"]:
        raise PlatformError(f"cases.json admits {manifest['platforms']}, not {platform}")
    row = explorer_row(platform)
    if row["status"] != "available":
        raise PlatformError(f"{platform} is {row['status']}")
    if manifest["max_duration"] > row["max_duration"]:
        raise PlatformError(f"max_duration {manifest['max_duration']} exceeds the platform's {row['max_duration']}")
    ceiling = row["price_per_shot"] * manifest["max_shots"]
    if ceiling > max_credits:
        raise PlatformError(f"{manifest['max_shots']} shots cost up to {ceiling:g} credits, above {max_credits:g}")
    counters = availability()
    if counters["num_concurrent_jobs"] or counters["num_jobs_in_queue"]:
        raise PlatformError(f"the token has a running or queued job: {counters}")
    built = payload(case_dir, manifest, circuit, platform)
    estimate = built["estimated_shots"]
    if estimate is None or estimate > manifest["max_shots"]:
        raise PlatformError(f"Perceval estimates {estimate} shots for {manifest['max_samples']} samples")
    return {
        "case": case_dir.name,
        "cases_sha256": cases_sha256,
        "platform": platform,
        "platform_at_plan": row,
        "availability_at_plan": counters,
        "max_samples": manifest["max_samples"],
        "max_shots": manifest["max_shots"],
        "estimated_shots": estimate,
        "credit_ceiling": ceiling,
        "estimated_credits": row["price_per_shot"] * estimate,
        "max_credits": max_credits,
        "body": built["body"],
        "body_sha256": sha256_bytes(json.dumps(built["body"], sort_keys=True).encode()),
        "versions": built["versions"],
    }


def write_json(path: Path, value: object, exclusive: bool = False) -> None:
    """Publish a complete JSON file with an atomic rename, or an atomic link when it must not exist."""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        stream.write(json.dumps(value, indent=1, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary = Path(stream.name)
    try:
        if exclusive:
            os.link(temporary, path)
        else:
            os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def submit(case_dir: Path, platform: str, approval: str, max_credits: float) -> dict[str, Any]:
    """Send one approved case as one job while holding the token's submit lock beside the token file."""
    if not approval.strip():
        raise PlatformError("a nonempty approval is required")
    lock = Path(os.environ.get(TOKEN_ENV, "")).with_name("submit.lock")
    with open(lock, "a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        state_path = case_dir / "submission-state.json"
        if any((case_dir / name).exists() for name in ("submission.json", "submission-state.json", "job-body.json")):
            raise PlatformError(f"{case_dir} was submitted or holds an interrupted submission; never resubmit it")
        checked = plan(case_dir, platform, max_credits)
        usage_before = usage_rows(get("/api/tokens/usage/report"))
        state = {
            "schema": STATE_SCHEMA,
            "phase": "post_outcome_unknown",
            "started_utc": now(),
            "platform": platform,
            "cases_sha256": checked["cases_sha256"],
            "body_sha256": checked["body_sha256"],
        }
        # The body and the checkpoint precede the request: a lost answer leaves
        # a case that submit refuses, never one a second invocation sends again.
        write_json(case_dir / "job-body.json", checked["body"], exclusive=True)
        write_json(state_path, state, exclusive=True)
        try:
            answer = request("POST", "/api/jobs", body=checked["body"])
        except RefusedError as error:
            state.update(phase="refused", error=str(error))
            write_json(state_path, state)
            raise
        if not isinstance(answer, dict) or not isinstance(answer.get("job_id"), str):
            raise PlatformError(f"POST /api/jobs answered without a job id: {answer!r}")
        record = {
            "schema": SUBMISSION_SCHEMA,
            "approval": approval,
            "submitted_utc": now(),
            "job_id": answer["job_id"],
            "usage_before": usage_before,
            **{key: value for key, value in checked.items() if key != "body"},
        }
        write_json(case_dir / "submission.json", record, exclusive=True)
        state.update(phase="posted", job_id=answer["job_id"])
        write_json(state_path, state)
        return record


def parse_counts(results: str) -> dict[str, int]:
    """Counts of a serialized Perceval BSCount, ':PCVL:BSCount:{|..>=n;...}', optionally zipped.

    Only plain Fock states with integer counts are accepted; any other tag or
    annotation raises, because perceval.serialization.deserialize evaluates
    parameter expressions through sympy and never sees service data here.
    """
    text = results
    if text.startswith(":PCVL:zip:"):
        stream = zlib.decompressobj()
        raw = stream.decompress(base64.b64decode(text[len(":PCVL:zip:") :], validate=True), RESULT_LIMIT)
        if stream.unconsumed_tail:
            raise PlatformError(f"a zipped result exceeds {RESULT_LIMIT} bytes")
        text = raw.decode("ascii")
    prefix = ":PCVL:BSCount:"
    if not text.startswith(prefix) or not (text.endswith("}") and text[len(prefix)] == "{"):
        raise PlatformError(f"result is not a BSCount: {text[:80]!r}")
    body = text[len(prefix) + 1 : -1]
    counts: dict[str, int] = {}
    for item in body.split(";") if body else []:
        match = STATE_PATTERN.fullmatch(item)
        if match is None or match[1] in counts:
            raise PlatformError(f"result entry {item[:80]!r} is not a unique Fock state count")
        counts[match[1]] = int(match[2])
    return counts


def collect(case_dir: Path, poll: float, timeout: float) -> dict[str, Any]:
    """Wait for the job, then retain its status, result and job data; the raw result keeps its bytes."""
    submission = json.loads((case_dir / "submission.json").read_text(encoding="utf-8"))
    _, _, cases_sha256 = load_case(case_dir)
    if submission.get("schema") != SUBMISSION_SCHEMA or submission["cases_sha256"] != cases_sha256:
        raise PlatformError("cases.json differs from the submission receipt")
    job = submission["job_id"]
    deadline = time.monotonic() + timeout
    while True:
        status = request("GET", job_route(job, "status"))
        if status.get("status") in TERMINAL:
            break
        if time.monotonic() > deadline:
            raise PlatformError(f"job {job} is still {status.get('status')}")
        time.sleep(poll)
    raw_dir = case_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    collected: dict[str, Any] = {
        "schema": COLLECTION_SCHEMA,
        "collected_utc": now(),
        "job_id": job,
        "status": scrub(status),
        "data": scrub(request("GET", job_route(job, "data"))),
        "usage_after": usage_rows(get("/api/tokens/usage/report")),
    }
    if status["status"] == "completed":
        result_bytes = request("GET", job_route(job, "result"), raw=True)
        collected["result_sha256"] = sha256_bytes(result_bytes)
        collected.update(result_summary(result_bytes))
        retain_bytes(raw_dir / "result.json", result_bytes)
    try:
        write_json(case_dir / "results.json", collected, exclusive=True)
    except FileExistsError:
        retained = json.loads((case_dir / "results.json").read_text(encoding="utf-8"))
        moving = ("collected_utc", "usage_after")
        if {k: v for k, v in retained.items() if k not in moving} != {
            k: v for k, v in collected.items() if k not in moving
        }:
            raise PlatformError(
                f"{case_dir}/results.json differs from the recollection; nothing was rewritten"
            ) from None
        return dict(retained)
    return collected


def retain_bytes(path: Path, data: bytes) -> None:
    """Write a raw file once; a later collection must bring the same bytes and rewrites nothing."""
    try:
        with open(path, "xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError:
        if path.read_bytes() != data:
            raise PlatformError(f"{path} differs from the recollected bytes; nothing was rewritten") from None


def result_summary(result_bytes: bytes) -> dict[str, Any]:
    """The counts and scalar fields of a raw /result answer, parsed without Perceval."""
    answer = json.loads(result_bytes)
    inner = json.loads(answer["results"])
    if not isinstance(inner, dict) or not isinstance(inner.get("results"), str):
        raise PlatformError("the result carries no serialized counts")
    counts = parse_counts(inner["results"])
    scalars = {k: v for k, v in inner.items() if k != "results" and isinstance(v, int | float | str | None)}
    return {"counts": counts, "samples": sum(counts.values()), "result_fields": scalars, "shots": answer.get("shots")}


def run_facts(directory: Path) -> dict[str, Any]:
    """Offline rules of one retained run: receipt, digests, approval, collection and raw result bytes."""
    owner = f"Quandela run {directory.name}"
    if not (directory / "submission.json").is_file():
        hint = (
            "; submission-state.json records an interrupted submit"
            if (directory / "submission-state.json").is_file()
            else ""
        )
        raise PlatformError(f"{owner}: no submission.json{hint}")
    submission = json.loads((directory / "submission.json").read_text(encoding="utf-8"))
    manifest, _, cases_sha256 = load_case(directory)
    if submission.get("schema") != SUBMISSION_SCHEMA or submission.get("cases_sha256") != cases_sha256:
        raise PlatformError(f"{owner}: cases.json differs from submission.json")
    if not isinstance(submission.get("approval"), str) or not submission["approval"].strip():
        raise PlatformError(f"{owner}: submission.json records no approval")
    body = json.loads((directory / "job-body.json").read_text(encoding="utf-8"))
    if sha256_bytes(json.dumps(body, sort_keys=True).encode()) != submission["body_sha256"]:
        raise PlatformError(f"{owner}: job-body.json differs from the body the receipt sent")
    if submission["platform"] not in manifest["platforms"]:
        raise PlatformError(f"{owner}: platform {submission['platform']} is outside cases.json")
    if not (directory / "results.json").is_file():
        raise PlatformError(f"{owner}: results.json is missing; collect the run")
    collected = json.loads((directory / "results.json").read_text(encoding="utf-8"))
    if collected.get("schema") != COLLECTION_SCHEMA or collected.get("job_id") != submission["job_id"]:
        raise PlatformError(f"{owner}: results.json names another job or schema")
    if carried := sorted(set(FORBIDDEN_KEYS) & keys(collected)):
        raise PlatformError(f"{owner}: results.json carries {carried}")
    status = collected["status"]["status"]
    if status not in TERMINAL:
        raise PlatformError(f"{owner}: job status {status} is not terminal")
    raw = directory / "raw" / "result.json"
    if status == "completed":
        if not raw.is_file() or sha256_bytes(raw.read_bytes()) != collected.get("result_sha256"):
            raise PlatformError(f"{owner}: raw/result.json differs from its recorded sha256")
        summary = result_summary(raw.read_bytes())
        if any(collected.get(key) != value for key, value in summary.items()):
            raise PlatformError(f"{owner}: results.json differs from the raw result")
        modes = len(json.loads((directory / manifest["circuit"]["file"]).read_text(encoding="utf-8"))["input_state"])
        if any(len(state.split(",")) != modes for state in summary["counts"]):
            raise PlatformError(f"{owner}: a counted state has a mode count other than {modes}")
    elif raw.exists():
        raise PlatformError(f"{owner}: a {status} job holds a raw result")
    shots = collected["status"].get("shots") or 0
    return {
        "created_at": submission["submitted_utc"],
        "backends": [submission["platform"]],
        "jobs": 1,
        "circuits": len(manifest["blocks"]),
        "statuses": {status: 1},
        "charge": shots * submission["platform_at_plan"]["price_per_shot"],
        "detail": f"job {submission['job_id']}, {collected.get('samples', 0)} samples, {shots} shots",
    }


def run_directories(runs: Path = RUNS) -> list[Path]:
    return sorted(path for path in runs.iterdir() if path.is_dir()) if runs.is_dir() else []


def zipped(text: str) -> str:
    return ":PCVL:zip:" + base64.b64encode(zlib.compress(text.encode("ascii"))).decode("ascii")


def runner_self_test() -> int:
    """Offline rules of plan, submit, collect and run_facts against a stubbed service; returns the rejections."""
    root = Path(__file__).resolve().parent.parent
    case = root / "results/quandela/cases/box_kite_photonic_single/job-00"
    modes = ["0"] * 24
    dark, label = modes.copy(), modes.copy()
    dark[22], label[20] = "1", "1"
    counts = f":PCVL:BSCount:{{|{','.join(dark)}>=9990;|{','.join(label)}>=10}}"
    result = json.dumps({"results": json.dumps({"results": zipped(counts), "global_perf": 1.0}), "shots": 10012})
    row = {field: None for field in PLATFORM_FIELDS} | {
        "name": "sim:belenos",
        "status": "available",
        "max_duration": 300,
        "price_per_shot": 0.0,
        "maintenance": None,
    }
    idle = dict.fromkeys(AVAILABILITY_KEYS, 0)
    body = {"job_name": "gororoba-job-00", "payload": {"command": "sample_count"}, "platform_name": "sim:belenos"}
    service: dict[str, Any] = {"row": row, "idle": idle, "estimate": 10000, "refuse": False, "result": result}

    def fake_request(method: str, route: str, auth: bool = True, body: Any = None, raw: bool = False) -> Any:
        if (method, route) == ("POST", "/api/jobs"):
            if service["refuse"]:
                raise RefusedError("POST /api/jobs: HTTP 422 unprocessable payload")
            return {"job_id": "job-a"}
        if route.endswith("/status"):
            return {"status": "completed", "shots": 10012, "token_id": 7}
        if route.endswith("/data"):
            return {"job_id": "job-a", "token_label": "secret-label", "status": "completed"}
        if route.endswith("/result"):
            return str(service["result"]).encode("utf-8")
        if route == "/api/tokens/usage/report":
            return [{"total_jobs": 1, "usage": [{"job": "job-a", "token_label": "secret-label"}], "token_id": 7}]
        raise AssertionError(f"unexpected {method} {route}")

    def fake_payload(*_: Any) -> dict[str, Any]:
        return {"body": body, "estimated_shots": service["estimate"], "versions": {"perceval-quandela": "1.3.1"}}

    rejected = 0

    def refuse(label: str, action: Callable[[], Any], expected: str) -> None:
        nonlocal rejected
        try:
            action()
        except PlatformError as error:
            if expected not in str(error):
                raise AssertionError(f"{label} failed for another reason: {error}") from None
            rejected += 1
            return
        raise AssertionError(f"runner accepted {label}")

    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        (scratch / "token").write_text("token-value\n", encoding="utf-8")
        run = scratch / "run"
        shutil.copytree(case, run)
        stubs = (
            patch.dict(os.environ, {TOKEN_ENV: str(scratch / "token")}),
            patch(f"{__name__}.request", fake_request),
            patch(f"{__name__}.explorer_row", lambda _: service["row"]),
            patch(f"{__name__}.availability", lambda: service["idle"]),
            patch(f"{__name__}.payload", fake_payload),
        )
        for stub in stubs:
            stub.start()
        try:
            refuse("a platform outside the case", lambda: plan(run, "qpu:ascella", 1.0), "admits")
            service["row"] = {**row, "status": "maintenance"}
            refuse("a platform under maintenance", lambda: plan(run, "sim:belenos", 1.0), "is maintenance")
            service["row"] = {**row, "price_per_shot": 1e-6}
            refuse("a ceiling above the case's credits", lambda: plan(run, "sim:belenos", 0.0), "above")
            service["row"], service["idle"] = row, {**idle, "num_jobs_in_queue": 1}
            refuse("a token with a queued job", lambda: plan(run, "sim:belenos", 1.0), "running or queued")
            service["idle"], service["estimate"] = idle, 10**9
            refuse("an estimate above max_shots", lambda: plan(run, "sim:belenos", 1.0), "estimates")
            service["estimate"] = 10000
            refuse("an empty approval", lambda: submit(run, "sim:belenos", " ", 1.0), "approval")
            refused = scratch / "refused"
            shutil.copytree(case, refused)
            service["refuse"] = True
            refuse("a refused POST", lambda: submit(refused, "sim:belenos", "approved", 0.0), "HTTP 422")
            service["refuse"] = False
            if json.loads((refused / "submission-state.json").read_text(encoding="utf-8"))["phase"] != "refused":
                raise AssertionError("a refused POST left a checkpoint other than refused")
            refuse("a resubmitted refusal", lambda: submit(refused, "sim:belenos", "again", 0.0), "never resubmit")
            submit(run, "sim:belenos", "approved in the written case", 0.0)
            refuse("a second submit", lambda: submit(run, "sim:belenos", "again", 0.0), "never resubmit")
            collected = collect(run, 0.0, 1.0)
            for name in ("results.json", "submission.json"):
                if carried := sorted(set(FORBIDDEN_KEYS) & keys(json.loads((run / name).read_text(encoding="utf-8")))):
                    raise AssertionError(f"{name} retained {carried}")
            if collect(run, 0.0, 1.0)["counts"] != collected["counts"]:
                raise AssertionError("a recollection changed the retained counts")
            service["result"] = result.replace("10012", "10013")
            refuse("a recollection with other raw bytes", lambda: collect(run, 0.0, 1.0), "nothing was rewritten")
            service["result"] = result
            if collected["counts"] != {",".join(dark): 9990, ",".join(label): 10}:
                raise AssertionError(f"collect parsed {collected['counts']}")
            run_facts(run)
            mutations: list[tuple[str, Callable[[Path], object], str]] = [
                (
                    "an edited raw result",
                    lambda d: (d / "raw/result.json").write_text("{}", encoding="utf-8"),
                    "sha256",
                ),
                ("a missing approval", lambda d: _rewrite(d / "submission.json", approval=""), "approval"),
                ("an edited case", lambda d: _rewrite(d / "cases.json", max_shots=1), "differs from submission"),
                ("an edited job body", lambda d: _rewrite(d / "job-body.json", job_name="other"), "job-body"),
                ("a retained token id", lambda d: _rewrite(d / "results.json", token_id=7), "carries"),
                ("another job id", lambda d: _rewrite(d / "results.json", job_id="job-b"), "another job"),
                ("an uncollected run", lambda d: (d / "results.json").unlink(), "collect the run"),
            ]
            for number, (label_text, mutate, expected) in enumerate(mutations):
                mutated = scratch / f"mutated-{number}"
                shutil.copytree(run, mutated)
                mutate(mutated)
                refuse(label_text, functools.partial(run_facts, mutated), expected)
        finally:
            for stub in reversed(stubs):
                stub.stop()
    for label_text, text in (
        ("a BasicState tag", ":PCVL:BasicState:|1,0>"),
        ("an annotated state", ":PCVL:BSCount:{|{_:0},0>=3}"),
        ("a repeated state", ":PCVL:BSCount:{|1,0>=3;|1,0>=4}"),
        ("an oversized zipped result", zipped(":PCVL:BSCount:{" + "0" * (RESULT_LIMIT + 1) + "}")),
    ):
        refuse(label_text, functools.partial(parse_counts, text), "")
    return rejected


def _rewrite(path: Path, **fields: Any) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    value.update(fields)
    path.write_text(json.dumps(value), encoding="utf-8")


def load(directory: Path) -> dict[str, Any]:
    value: dict[str, Any] = json.loads((directory / "catalogue.json").read_text(encoding="utf-8"))
    return value


def check(directory: Path, agents: list[Path] | None = None, server: Path = MCP_SERVER) -> None:
    catalogue = load(directory)
    if catalogue["schema"] != CATALOGUE_SCHEMA:
        raise SystemExit(f"unexpected schema {catalogue['schema']}")
    if carried := sorted(set(FORBIDDEN_KEYS) & keys(catalogue)):
        raise SystemExit(f"snapshot carries {carried}")
    counters = catalogue["account"]["availability"]
    if missing := [k for k in AVAILABILITY_KEYS if not isinstance(counters.get(k), int) or counters[k] < 0]:
        raise SystemExit(f"availability lacks {missing}")
    names = [row["name"] for row in catalogue["explorer_platforms"]]
    if len(set(names)) != len(names) or set(catalogue["processors"]) != set(names):
        raise SystemExit("processor records differ from the Explorer platforms")
    for row in catalogue["explorer_platforms"]:
        name = row["name"]
        price, duration = row.get("price_per_shot"), row.get("max_duration")
        if not isinstance(price, int | float) or not isinstance(duration, int) or price < 0 or duration <= 0:
            raise SystemExit(f"{name}: price {price!r} or duration {duration!r}")
        specs = catalogue["processors"][name].get("specs", {})
        limits = specs.get("constraints", {})
        photons = (limits.get("min_photon_count"), limits.get("max_photon_count"))
        if None in photons or photons[0] > photons[1]:
            raise SystemExit(f"{name}: photon limits {photons}")
        modes = specs.get("connected_input_modes")
        if modes is not None:
            high = limits.get("max_mode_count")
            if high is None or not all(0 <= m < high for m in modes) or len(set(modes)) != len(modes):
                raise SystemExit(f"{name}: connected input modes {modes} outside {high} modes")
            # A chip without multi-photon input carries one photon per source-connected mode.
            if not limits.get("support_multi_photon") and photons[1] != len(modes):
                raise SystemExit(f"{name}: {photons[1]} photons over {len(modes)} connected input modes")
    check_mcp(server)
    if agents is not None:
        check_agents(catalogue, agents)
    print(f"qd snapshot: {len(names)} Explorer platforms, {len(catalogue['public_platforms'])} public platforms")


def self_test() -> None:
    root = Path(__file__).resolve().parent.parent
    source = root / "docs" / "evidence" / "quandela"
    guides = (root / "AGENTS.md", root / "docs" / "notes" / "quandela" / "README.md")
    check(source, list(guides))

    def rewrite(path: Path, change: Callable[[Any], None]) -> None:
        value = json.loads(path.read_text(encoding="utf-8"))
        change(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def catalogue(change: Callable[[dict[str, Any]], None]) -> Callable[[Path], None]:
        return lambda scratch: rewrite(scratch / "quandela" / "catalogue.json", change)

    def text(name: str, old: str, new: str) -> Callable[[Path], None]:
        def edit(scratch: Path) -> None:
            path = scratch / name
            body = path.read_text(encoding="utf-8")
            if old not in body:
                raise AssertionError(f"self-test fixture lacks {old!r} in {name}")
            path.write_text(body.replace(old, new, 1), encoding="utf-8")

        return edit

    def drop_tool_rows(scratch: Path) -> None:
        path = scratch / "README.md"
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        path.write_text("".join(line for line in lines if not line.startswith("| `qd_")), encoding="utf-8")

    def qpu(c: dict[str, Any]) -> dict[str, Any]:
        name = next(r["name"] for r in c["explorer_platforms"] if r["type"] == "qpu")
        specs: dict[str, Any] = c["processors"][name]["specs"]
        return specs

    edits: dict[str, Callable[[Path], None]] = {
        "token id": catalogue(lambda c: c["account"]["token_usage"].append({"token_id": 1})),
        "creator id": catalogue(lambda c: c["explorer_platforms"][0].update(maintenance={"creator_id": 1})),
        "missing processor": catalogue(lambda c: c["processors"].pop(c["explorer_platforms"][0]["name"])),
        "input mode outside the chip": catalogue(lambda c: qpu(c)["connected_input_modes"].append(99)),
        "photons off the connected modes": catalogue(lambda c: qpu(c)["constraints"].update(max_photon_count=1)),
        "negative price": catalogue(lambda c: c["explorer_platforms"][0].update(price_per_shot=-1)),
        "missing availability counter": catalogue(lambda c: c["account"]["availability"].pop("max_jobs_in_queue")),
        "edited table": text("AGENTS.md", "| credits per shot |", "| price |"),
        "stale row": text("AGENTS.md", END, "| stale | row |\n" + END),
        "README table drops a tool": text("README.md", "| `qd_usage` |", "| usage |"),
        "README drops the tool table": drop_tool_rows,
        "server adds a submit tool": text(
            "qd_mcp_server.py",
            'if __name__ == "__main__":',
            '@server.tool(annotations=MUTATE)\ndef qd_submit() -> None:\n    pass\n\n\nif __name__ == "__main__":',
        ),
        "server reads a QRNG route": text("qd_mcp_server.py", '"/api/tokens/usage/report"', '"/qt/qrng/bytes?size=8"'),
        "read tool posts": text(
            "qd_mcp_server.py",
            "await threaded(availability)",
            'await threaded(lambda: request("POST", "/api/jobs"))',
        ),
        "server imports urllib": text(
            "qd_mcp_server.py", "import functools\n", "import functools\nimport urllib.request\n"
        ),
        "price missing": catalogue(lambda c: c["explorer_platforms"][0].pop("price_per_shot")),
        "server marks cancel read-only": text(
            "qd_mcp_server.py", "@server.tool(annotations=MUTATE)", "@server.tool(annotations=READ)"
        ),
        "server marks a read as mutating": text(
            "qd_mcp_server.py", "@server.tool(annotations=READ)", "@server.tool(annotations=MUTATE)"
        ),
    }
    for label, edit in edits.items():
        with tempfile.TemporaryDirectory() as tmp:
            scratch = Path(tmp)
            shutil.copytree(source, scratch / "quandela")
            for path in (*guides, MCP_SERVER, Path(__file__)):
                shutil.copy(path, scratch / path.name)
            edit(scratch)
            try:
                check(scratch / "quandela", [scratch / g.name for g in guides], scratch / MCP_SERVER.name)
            except SystemExit:
                continue
            raise AssertionError(f"check accepted {label}")
    print(f"qd_platform self-test: {len(edits)} catalogue rejections, {runner_self_test()} runner rejections")


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("snapshot")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("check")
    p.add_argument("directory", type=Path)
    p.add_argument("--agents", type=Path, nargs="+", help="files carrying the quandela-facts section")
    p = sub.add_parser("facts")
    p.add_argument("directory", type=Path)
    for name in ("plan", "submit"):
        p = sub.add_parser(name)
        p.add_argument("case_dir", type=Path)
        p.add_argument("--platform", required=True)
        p.add_argument("--max-credits", type=float, required=True, help="the written case's credit ceiling")
        if name == "submit":
            p.add_argument("--approval", required=True, help="the user's approval, quoted, kept in submission.json")
    p = sub.add_parser("collect")
    p.add_argument("case_dir", type=Path)
    p.add_argument("--poll", type=float, default=10.0)
    p.add_argument("--timeout", type=float, default=1800.0)
    p = sub.add_parser("runs")
    p.add_argument("--runs", type=Path, default=RUNS)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.command == "snapshot":
        try:
            snapshot(args.out)
        except PlatformError as error:
            raise SystemExit(str(error)) from None
    elif args.command == "check":
        check(args.directory, args.agents)
    elif args.command == "facts":
        print(facts_table(load(args.directory)), end="")
    elif args.command in ("plan", "submit", "collect", "runs"):
        try:
            if args.command == "plan":
                checked = plan(args.case_dir, args.platform, args.max_credits)
                print(json.dumps({k: v for k, v in checked.items() if k != "body"}, indent=1, sort_keys=True))
            elif args.command == "submit":
                record = submit(args.case_dir, args.platform, args.approval, args.max_credits)
                print(f"job {record['job_id']} on {record['platform']}")
            elif args.command == "collect":
                collected = collect(args.case_dir, args.poll, args.timeout)
                print(
                    f"job {collected['job_id']}: {collected['status']['status']}, {collected.get('samples', 0)} samples"
                )
            else:
                for directory in run_directories(args.runs):
                    print(directory.name, json.dumps(run_facts(directory), sort_keys=True))
        except PlatformError as error:
            raise SystemExit(str(error)) from None
    else:
        parser.error("a subcommand or --self-test is required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
