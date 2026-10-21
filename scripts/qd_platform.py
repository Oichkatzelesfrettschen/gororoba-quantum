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
  creates, cancels and submits nothing. A processor record the service returns
  without specs.architecture keeps the retained catalogue's copy, named in
  architecture_carried with the time its couplers were last observed.
- check DIR [--agents FILE...] (offline) requires the catalogue to carry its
  schema and no account identifier (FORBIDDEN_KEYS at any depth), one
  processor record per Explorer platform, photon and mode limits that agree
  with each other and with the connected input modes, non-negative per-shot
  prices and complete availability counters, and loads qd_mcp_server.py with
  mcp replaced by recorders to require exactly the tools MCP_TOOLS names,
  every one read-only except MCP_MUTATING. With --agents it renders
  facts_table and requires each FILE's quandela-facts markers to enclose
  exactly that table, so a refreshed snapshot that changes a limit, a
  command set or a price fails until the Quandela README changes
  with it, and a FILE whose table lists qd_ tools must list exactly
  MCP_TOOLS. Status, performance figures, availability statistics, maintenance
  windows and software versions change between reads and stay out of the
  table.
- facts DIR prints the table.
- plan RUN_DIR --platform NAME --max-credits C --expected-seconds S
  --per-job-credits P (network, read-only) runs every check submit makes and
  prints the result: the circuit matches its cases.json sha256, the platform
  is one the case admits, is available and allows the case's max_duration,
  S stays within max_duration, P plus max_shots times the live price per
  shot stays within C, the processor's perfs (HOM and g2 among them) are
  recorded, and a two-photon case on a QPU whose HOM visibility is absent or
  not above 90 % draws a warning on stderr,
  the token has no running or queued job, and Perceval's
  estimate_required_shots for max_samples stays within max_shots. It builds
  the job body through Perceval's own RemoteComputer.prepare_payload and
  communication-layer send with create_job replaced by a recorder, so the
  body is exactly Perceval's and nothing leaves.
- submit RUN_DIR (plan's arguments) --approval TEXT repeats
  plan under an flock beside the token file, writes submission-state.json
  before the request (a lost answer leaves a case submit refuses, never one
  it sends twice), posts the body to /api/jobs with the case's max_duration
  and retains job-body.json and submission.json with the approval, the plan
  and the usage report before the job.
- recover RUN_DIR writes submission.json from a posted checkpoint, which
  carries the returned job id before the receipt is written.
- collect RUN_DIR waits for a terminal status, then retains the result
  answer byte for byte in raw/result.json (written once; a recollection
  must bring the same bytes) and results.json with the scrubbed
  status and job data, the usage report after the job and the counts that
  parse_counts reads from the serialized BSCount: plain Fock states only,
  zipped or not, never through perceval.serialization.deserialize. The
  result must name the submitted job and agree with the status shots; an
  error or canceled job keeps a partial result or records its absence.
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
  oversized zipped result, and that a missing chip architecture raises
  PlatformError, a two-photon case below 90 % HOM warns, and a snapshot keeps
  the retained chip with its observation time.

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
ARCHITECTURE = "architecture"
# strategy.md, "Design rules taken from it", item 1: a block with two photons should wait until HOM visibility is above
# this percent. plan warns on a QPU case below it and does not hold the case.
HOM_FLOOR = 90.0


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


def retained_catalogue(out: Path) -> dict[str, Any] | None:
    """The catalogue an earlier snapshot wrote to out, or None when out holds none."""
    path = out / "catalogue.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def chip_architecture(record: Any) -> str | None:
    """The record's non-empty specs.architecture, or None when the record lacks one or carries it as null."""
    specs = record.get("specs") if isinstance(record, dict) else None
    blob = specs.get(ARCHITECTURE) if isinstance(specs, dict) else None
    return blob if isinstance(blob, str) and blob else None


def architecture_provenance(
    processors: dict[str, dict[str, Any]],
    retained: dict[str, Any] | None,
    stamp: str,
    qpus: frozenset[str] = frozenset(),
) -> tuple[dict[str, str], list[str]]:
    """Stamp each chip architecture with the time its couplers were last read, and return the carried names.

    A record the service omits, or sends as null, keeps the retained copy,
    stamped with the time that copy was observed. The carried names go into
    the catalogue, so a reader sees which couplers this snapshot did not read.
    """
    source = retained or {}
    observed: dict[str, str] = {}
    carried: list[str] = []
    for name, record in processors.items():
        if not isinstance(record.get("specs"), dict):
            record["specs"] = {}
        if chip_architecture(record) is not None:
            observed[name] = stamp
            continue
        kept = chip_architecture(source.get("processors", {}).get(name))
        if kept is None:
            if name in qpus:
                print(f"{name}: no chip architecture live or retained", file=sys.stderr)
            continue
        record["specs"][ARCHITECTURE] = kept
        observed[name] = source.get("architecture_observed_utc", {}).get(name, source["retrieved_utc"])
        carried.append(name)
    return observed, sorted(carried)


def snapshot(out: Path) -> None:
    token()
    rows = get("/api/platforms/public/explorer", auth=False)
    explorer = sorted((platform_row(row) for row in rows), key=lambda p: p["name"])
    public = [
        {"name": row["name"], "type": row["type"], "status": row["status"]}
        for row in get("/api/platforms/public", auth=False)
    ]
    processors = {row["name"]: get(platform_route(row["name"])) for row in explorer}
    stamp = now()
    qpus = frozenset(row["name"] for row in explorer if row["type"] == "qpu")
    observed, carried = architecture_provenance(processors, retained_catalogue(out), stamp, qpus)
    if carried:
        print(f"carried specs.architecture from the retained catalogue for {', '.join(carried)}", file=sys.stderr)
    catalogue = {
        "schema": CATALOGUE_SCHEMA,
        "retrieved_utc": stamp,
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
        "architecture_observed_utc": observed,
        "architecture_carried": carried,
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
CASES_SCHEMAS = ("qd-box-kite-cases-v1", "qd-belenos-mesh-cases-v1", "qd-bdsc-cases-v1")
CIRCUIT_SCHEMA = "qd-circuit-v1"
NUMERIC_CIRCUIT_SCHEMA = "qd-numeric-circuit-v1"
CIRCUIT_SCHEMAS = (CIRCUIT_SCHEMA, "qd-mesh-circuit-v1", NUMERIC_CIRCUIT_SCHEMA)
# A case's processing policy: None leaves the server's default mitigations, an empty list disables them.
MITIGATION_POLICIES: tuple[None, list[str]] = (None, [])
STATE_SCHEMA = "qd-submission-state-v1"
SUBMISSION_SCHEMA = "qd-submission-v1"
COLLECTION_SCHEMA = "qd-collection-v1"
TERMINAL = ("completed", "error", "canceled")
# Perceval 1.3.1 is the client whose payload format the runner captures.
RUNNER_PERCEVAL = "1.3.1"
# POST /api/jobs stores job_name in a varchar(50); a longer name answers
# HTTP 424 "value too long for type character varying(50)".
JOB_NAME_LIMIT = 50
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
    if circuit.get("schema") not in CIRCUIT_SCHEMAS:
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
    expected = numpy.eye(circuit["modes"], dtype=complex)
    phases: list[tuple[int, Any]] = []
    for component in circuit["components"]:
        if "numeric" in component:
            # A numeric component holds complex entries [re, im]; it must be unitary to 1e-12 before Perceval sees it.
            matrix = numpy.array([[complex(re, im) for re, im in row] for row in component["numeric"]], dtype=complex)
            defect = float(numpy.max(numpy.abs(matrix.conj().T @ matrix - numpy.eye(len(matrix)))))
            if defect > 1e-12:
                raise PlatformError(f"a numeric component at {component['at']} deviates from unitary by {defect:.2e}")
        else:
            matrix = numpy.array([[real(x) for x in row] for row in component["unitary"]], dtype=complex)
        at, width = component["at"], len(matrix)
        expected[at : at + width, at : at + width] = matrix
        if manifest.get("gate_form", "unitary") == "native":
            block = pcvl.Circuit(width)
            if "prep_phase" in component:
                # BS.H then PS(phi) on port 1 prepares (|0> + e^{i phi}|1>)/sqrt2 ahead of the block.
                parameter = pcvl.P(component["prep_phase"])
                block.add(0, pcvl.BS.H())
                block.add(1, pcvl.PS(parameter))
                phases.append((at, parameter))
            for op in component["native"]:
                if op[0] == "BS.H":
                    block.add(op[1], pcvl.BS.H())
                elif op[0] == "PS":
                    block.add(op[1], pcvl.PS(math.pi))
                elif op[0] == "PERM":
                    block.add(0, pcvl.PERM(op[1]))
                else:
                    raise PlatformError(f"unknown native op {op!r}")
            chip.add(at, block)
        else:
            chip.add(at, pcvl.Unitary(pcvl.Matrix(matrix)))
    # Perceval's conventions must reproduce the exact case unitary before anything
    # is sent, at every iteration value of a parameterized preparation phase.
    values = [k * math.pi / 4 for k in range(manifest.get("iterations", 1))] if phases else [0.0]
    for value in values:
        target = expected.copy()
        for at, parameter in phases:
            parameter.set_value(value)
            prep = numpy.eye(circuit["modes"], dtype=complex)
            prep[at : at + 2, at : at + 2] = numpy.array([[1, 1], [numpy.exp(1j * value), -numpy.exp(1j * value)]])
            prep[at : at + 2, at : at + 2] /= math.sqrt(2)
            target = expected @ prep
        deviation = float(numpy.max(numpy.abs(numpy.array(chip.compute_unitary()) - target)))
        if deviation > 1e-12:
            raise PlatformError(f"the Perceval circuit deviates from the case unitary by {deviation:.2e} at {value}")
    for _, parameter in phases:
        parameter.reset()
    built = pcvl.Experiment(chip)
    built.with_input(pcvl.BasicState(circuit["input_state"]))
    built.min_detected_photons_filter(manifest["min_detected_photons"])
    return built


def mesh_experiment(manifest: dict[str, Any], circuit: dict[str, Any]) -> tuple[Any, list[dict[str, Any]]]:
    """The Belenos architecture with one Perceval parameter per phase, and one iteration per retained setting.

    Each setting's phases bind the 574 symbols; Perceval's unitary at those
    values must equal qd_belenos_mesh's propagation of the same elements, so
    the BS and PS conventions that designed the phases are the ones sent.
    """
    import numpy
    import perceval as pcvl
    import qd_belenos_mesh as mesh

    arch = mesh.architecture(mesh.load_catalogue())
    spec = circuit["architecture"]
    if spec["symbols"] != [p for k, _, p in arch if k == "ps"] or spec["couplers"] != [
        [m, p[0]] for k, m, p in arch if k == "bs"
    ]:
        raise PlatformError("the case's mesh differs from the retained Belenos architecture")
    # One setting goes out as numbers, the pre-compiled form of the cloud guide;
    # several go out as one parameterized circuit with a setting per iteration.
    numeric = len(circuit["settings"]) == 1
    fixed = dict(zip(spec["symbols"], circuit["settings"][0]["phases"], strict=True))
    chip = pcvl.Circuit(circuit["modes"])
    parameters: dict[str, Any] = {}
    for kind, m, p in arch:
        if kind == "bs":
            chip.add(m, pcvl.BS(theta=p[0]))
        elif numeric:
            chip.add(m, pcvl.PS(fixed[p]))
        else:
            parameters[p] = pcvl.P(p)
            chip.add(m, pcvl.PS(parameters[p]))
    iterations = []
    for setting in circuit["settings"]:
        values = dict(zip(spec["symbols"], setting["phases"], strict=True))
        for symbol, parameter in parameters.items():
            parameter.set_value(values[symbol])
        deviation = float(
            numpy.max(numpy.abs(numpy.array(chip.compute_unitary()) - mesh.unitary(arch, setting["phases"])))
        )
        if deviation > 1e-12:
            raise PlatformError(f"{setting['name']}: Perceval's mesh unitary deviates by {deviation:.2e}")
        state = [0] * circuit["modes"]
        state[setting["input_mode"]] = 1
        iteration = {"name": setting["name"], "circuit_params": values, "input_state": state}
        if "compilation_seed" in setting:
            iteration["compilation_seed"] = seed_value(setting["compilation_seed"], setting["name"])
        iterations.append(iteration)
    for parameter in parameters.values():
        parameter.reset()
    built = pcvl.Experiment(chip)
    built.with_input(pcvl.BasicState(iterations[0]["input_state"]))
    built.min_detected_photons_filter(manifest["min_detected_photons"])
    return built, iterations


def seed_value(seed: Any, owner: str) -> int:
    """A compilation seed as the service takes it: a non-negative integer."""
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise PlatformError(f"{owner}: compilation_seed {seed!r} is not a non-negative integer")
    return seed


def job_seed(manifest: dict[str, Any], settings: list[dict[str, Any]]) -> int | None:
    """The compilation seed of a one-circuit job's computation: its one mesh setting's or its manifest's.

    An iterated job names its seeds per iteration, so a manifest seed on it raises, as does a one-setting
    case whose setting and manifest name different seeds; a case that names none sends none.
    """
    owner = manifest["job"]
    named = manifest.get("compilation_seed")
    if iteration_form(manifest) != "single":
        if named is not None:
            raise PlatformError(f"{owner}: an iterated case names compilation_seed per iteration, not in its manifest")
        return None
    own = settings[0].get("compilation_seed") if settings else None
    if named is not None and own is not None and named != own:
        raise PlatformError(f"{owner}: manifest compilation_seed {named!r} differs from its setting's {own!r}")
    seed = named if own is None else own
    return None if seed is None else seed_value(seed, owner)


def iteration_form(manifest: dict[str, Any]) -> str:
    """How a case's iterations differ: "single" (one computation), "mesh" (each binds its own phases), "seeded"
    (a fixed circuit whose iterations set only their compilation_seed and, optionally, their own budgets) or
    "phase" (phi = k pi/4).

    A one-iteration case is one computation unless its manifest sets "iterator": true, which sends its one
    seeded setting as a ComputationIterator holding one entry, the payload class of every iterated job.

    A non-mesh iterated case with settings is seeded only when every setting names a valid compilation_seed and
    nothing else but its name, and the settings count its iterations. A seeded case names per-iteration
    max_samples and max_shots on every setting or on none; named budgets are positive integers with
    max_shots >= max_samples that sum to the manifest's. Any other settings list raises.
    """
    owner = manifest["job"]
    steps = manifest.get("iterations", 1)
    iterator = manifest.get("iterator", False)
    if iterator is not False and (iterator is not True or steps != 1 or manifest.get("gate_form") == "mesh"):
        raise PlatformError(f"{owner}: iterator is true only on a one-iteration seeded case, not {iterator!r}")
    if steps == 1 and not iterator:
        return "single"
    if iterator and manifest.get("settings") is None:
        raise PlatformError(f"{owner}: a one-entry iterator names its setting")
    if manifest.get("gate_form") == "mesh":
        return "mesh"
    settings = manifest.get("settings")
    if settings is None:
        return "phase"
    if not isinstance(settings, list) or len(settings) != steps:
        raise PlatformError(f"{owner}: {steps} iterations need {steps} settings")
    plain, budgeted = {"name", "compilation_seed"}, {"name", "compilation_seed", "max_samples", "max_shots"}
    keys = {frozenset(setting) if isinstance(setting, dict) else frozenset() for setting in settings}
    if keys not in ({frozenset(plain)}, {frozenset(budgeted)}):
        raise PlatformError(
            f"{owner}: every seeded iteration names its name and compilation_seed, and all or none their budgets"
        )
    for setting in settings:
        seed_value(setting["compilation_seed"], f"{owner}/{setting['name']}")
    if keys == {frozenset(budgeted)}:
        for setting in settings:
            samples, shots = setting["max_samples"], setting["max_shots"]
            if any(isinstance(v, bool) or not isinstance(v, int) or v < 1 for v in (samples, shots)) or shots < samples:
                raise PlatformError(f"{owner}/{setting['name']}: budgets {samples!r} samples, {shots!r} shots")
        for key in ("max_samples", "max_shots"):
            if sum(setting[key] for setting in settings) != manifest[key]:
                raise PlatformError(f"{owner}: per-iteration {key} do not sum to the manifest's {manifest[key]}")
    return "seeded"


def iteration_budgets(manifest: dict[str, Any]) -> list[tuple[int, int]]:
    """(max_samples, max_shots) of every iteration: a seeded setting's own budgets, else an even split."""
    steps = manifest.get("iterations", 1)
    settings = manifest.get("settings") or []
    if iteration_form(manifest) == "seeded" and "max_samples" in settings[0]:
        return [(s["max_samples"], s["max_shots"]) for s in settings]
    return [(manifest["max_samples"] // steps, manifest["max_shots"] // steps)] * steps


def architecture_blob(processor: dict[str, Any], platform: str) -> str:
    """The record's specs.architecture, the field every coupler check decodes; without it no check can run."""
    blob = chip_architecture(processor)
    if blob is None:
        raise PlatformError(f"{platform}: the live record has no specs.architecture, so its couplers cannot be checked")
    return blob


def block_photons(circuit: dict[str, Any]) -> int:
    """The most photons any one interfering block receives: the input modes under each component.

    A mesh setting names one input_mode, so it injects one photon. A circuit
    without components counts as one block spanning its input_state.
    """
    state = circuit.get("input_state")
    if state is None:
        return 1
    spans = [(block["at"], len(block["unitary"])) for block in circuit.get("components", [])] or [(0, len(state))]
    return max(sum(state[at : at + size]) for at, size in spans)


def hom_warning(platform: str, perfs: dict[str, Any], photons: int, case: str) -> str | None:
    """The warning for two photons in one block when the live HOM visibility is absent or not above HOM_FLOOR."""
    hom = perfs.get("HOM (%)")
    if photons < 2 or (isinstance(hom, int | float) and hom > HOM_FLOOR):
        return None
    return (
        f"warning: {case} puts {photons} photons in one interfering block and {platform} reports HOM {hom!r} %, "
        f"not above {HOM_FLOOR:g} %; strategy.md design rule 1 asks that block to wait until HOM recovers"
    )


def live_mesh(processor: dict[str, Any], circuit: dict[str, Any], platform: str) -> None:
    """Refuse a mesh case when the platform's live architecture carries other couplers or symbols than the case."""
    import qd_belenos_mesh as mesh

    live = mesh.decode(architecture_blob(processor, platform))
    spec = circuit["architecture"]
    if [p for k, _, p in live if k == "ps"] != spec["symbols"] or [[m, p[0]] for k, m, p in live if k == "bs"] != spec[
        "couplers"
    ]:
        raise PlatformError("the live architecture differs from the case: regenerate the mesh case after recalibration")


def live_architecture(processor: dict[str, Any], platform: str) -> None:
    """Refuse a case seeded from a retained run on its chip when the live couplers or symbols differ from the
    retained catalogue's, since a comparison with that run then crosses a coupler recalibration."""
    import qd_belenos_mesh as mesh

    if platform != mesh.CHIP:
        return
    live = mesh.decode(architecture_blob(processor, platform))
    retained = mesh.architecture(mesh.load_catalogue())
    if [(k, m, p) for k, m, p in live if k == "bs"] != [(k, m, p) for k, m, p in retained if k == "bs"] or [
        p for k, _, p in live if k == "ps"
    ] != [p for k, _, p in retained if k == "ps"]:
        raise PlatformError(
            "the live architecture differs from the retained catalogue: the seeded case's source ran on other couplers"
        )


def explorer_row(platform: str) -> dict[str, Any]:
    rows = [row for row in get("/api/platforms/public/explorer", auth=False) if row.get("name") == platform]
    if len(rows) != 1:
        raise PlatformError(f"{platform} is not one Explorer platform")
    return platform_row(rows[0])


def payload_version_basis(specs: Any) -> str:
    """Restore specs.commands from available_commands when the record declares a server Perceval of 1.3 or later.

    RPCBasedCommunicationLayer.send builds a version-2 body only when the record carries specs.commands and
    otherwise downgrades it for a worker that predates payload version 2. Version 2 starts at Perceval 1.3
    (PayloadUpdater.update_payload), so a record declaring pcvl_version 1.3 or later names a worker that reads it
    whatever the commands field says; without that declaration the commands stay absent and the body version 1.
    Returns "declared", "restored" or "absent".
    """
    if "commands" in specs:
        return "declared"
    version = str(specs.get("pcvl_version") or "")
    parts = version.split(".")
    if len(parts) < 2 or not all(part.isdigit() for part in parts[:2]) or (int(parts[0]), int(parts[1])) < (1, 3):
        return "absent"
    specs["commands"] = list(specs.commands)
    return "restored"


def payload(case_dir: Path, manifest: dict[str, Any], circuit: dict[str, Any], platform: str) -> dict[str, Any]:
    """Perceval's job body for the case and its live shot estimate, built without sending anything.

    RemoteComputer.prepare_payload and RPCBasedCommunicationLayer.send build
    the body exactly as Perceval sends it; the RPC handler's create_job is
    replaced by a recorder, so the body comes back instead of leaving.
    Perceval reads the platform's processor record with the token to do so.
    """
    from perceval import ExecutionFactory, QuandelaCommunicationLayer, RemoteComputer
    from perceval.utils.constants import KEY_MITIGATIONS

    found = versions()
    if found.get("perceval-quandela") != RUNNER_PERCEVAL:
        raise PlatformError(f"perceval-quandela {found.get('perceval-quandela')} is installed, not {RUNNER_PERCEVAL}")
    import perceval as pcvl

    layer = QuandelaCommunicationLayer(platform, token=token())
    computer = RemoteComputer(layer)
    policy = manifest.get("mitigations")
    if policy not in MITIGATION_POLICIES:
        raise PlatformError(f"{manifest['job']}: mitigations {policy!r} is neither null nor an empty list")
    computer.mitigations = None if policy is None else []
    form = iteration_form(manifest)
    mesh = manifest.get("gate_form") == "mesh"
    built, settings = mesh_experiment(manifest, circuit) if mesh else (experiment(manifest, circuit), [])
    if form == "seeded":
        settings = manifest["settings"]
    steps = manifest.get("iterations", 1)
    # Iterations split the case's sample and shot budgets evenly; a mesh iteration
    # takes its setting's compilation_seed (0 when unnamed), a seeded iteration sets
    # only its own, and a phase case pins 0 and sets phi = k pi/4 per iteration.
    per_samples, per_shots = manifest["max_samples"] // steps, manifest["max_shots"] // steps
    # pcvlar serialization shares one entry per Python object, so an even split reuses per_samples and per_shots
    # themselves: equal integers computed apart would serialize as separate entries and change the body bytes.
    budgeted = form == "seeded" and "max_samples" in manifest["settings"][0]
    budgets = iteration_budgets(manifest) if budgeted else [(per_samples, per_shots)] * steps
    factory = ExecutionFactory(computer, built, max_shots_per_call=max(shots for _, shots in budgets))
    base = factory.build_computation(manifest["command"])
    base.add_params(max_samples=per_samples)
    seed = job_seed(manifest, settings)
    if seed is not None:
        base.add_params(compilation_seed=seed)
    params = settings[0]["circuit_params"] if mesh else ({"phi": 0.0} if form == "phase" else None)
    if len({samples for samples, _ in budgets}) == 1:
        estimate = computer.estimate_required_shots(base, nsamples=per_samples, param_values=params)
        estimate = None if estimate is None else estimate * steps
    else:
        parts = [computer.estimate_required_shots(base, nsamples=n, param_values=params) for n, _ in budgets]
        estimate = None if any(part is None for part in parts) else sum(parts)
    if form != "single":
        for k in range(steps):
            if mesh:
                # A mesh iteration binds all 574 phases and its own input mode.
                factory.add_iteration(
                    circuit_params=settings[k]["circuit_params"],
                    input_state=pcvl.BasicState(settings[k]["input_state"]),
                    max_samples=per_samples,
                    max_shots=per_shots,
                    compilation_seed=settings[k].get("compilation_seed", 0),
                )
                continue
            if form == "seeded":
                factory.add_iteration(
                    max_samples=budgets[k][0],
                    max_shots=budgets[k][1],
                    compilation_seed=settings[k]["compilation_seed"],
                )
                continue
            factory.add_iteration(
                circuit_params={"phi": k * math.pi / 4},
                max_samples=per_samples,
                max_shots=per_shots,
                compilation_seed=0,
            )
        computation = factory.build_computation(manifest["command"])
        computation.add_params(max_samples=per_samples)
    else:
        computation = base
    computation.job_name = f"{manifest['family']}/{manifest['job']}"
    if len(computation.job_name) > JOB_NAME_LIMIT:
        raise PlatformError(f"job name {computation.job_name!r} exceeds the service's {JOB_NAME_LIMIT} characters")
    computer.validate_single(computation)
    captured: dict[str, Any] = {}

    def record(cloud_data: dict[str, Any]) -> str:
        captured["body"] = cloud_data
        return "recorded"

    layer._rpc_handler.create_job = record
    prepared = computer.prepare_payload(computation)
    # send reads the cached specs without refetching, so the basis set here is the one the body is built under.
    basis = payload_version_basis(layer._specs)
    layer.send(prepared)
    body: dict[str, Any] = {**captured["body"], "max_duration": manifest["max_duration"]}
    # RPCBasedCommunicationLayer.send downgrades the body to payload version 1 when the processor record lacks
    # specs.commands; a version-1 worker predates the mitigations key, so a policy case refuses that body.
    if "mitigations" in manifest and "computation" not in body.get("payload", {}):
        raise PlatformError(
            f"{manifest['job']}: Perceval built a version-1 body because the {platform} record lacks specs.commands"
        )
    # Perceval writes the mitigations key only for a non-null list, so the body shows which policy it carries.
    if "mitigations" in manifest and (KEY_MITIGATIONS in json.dumps(body)) != (policy is not None):
        raise PlatformError(f"{manifest['job']}: the job body does not carry the mitigation policy {policy!r}")
    if token() in json.dumps(body):
        raise PlatformError("the job body carries the token")
    return {"body": body, "estimated_shots": estimate, "versions": found, "payload_version_basis": basis}


def plan(
    case_dir: Path, platform: str, max_credits: float, expected_seconds: float, per_job_credits: float
) -> dict[str, Any]:
    """Every check submit makes, read-only: digests, platform, complete cost ceiling, availability and the estimate.

    expected_seconds and per_job_credits are the written case's values: the
    offer's per-job price is visible only in the portal, so the case states
    it, and per-job credits plus max_shots times the live price per shot must
    stay within max_credits.
    """
    for name, value in (
        ("--max-credits", max_credits),
        ("--expected-seconds", expected_seconds),
        ("--per-job-credits", per_job_credits),
    ):
        if not math.isfinite(value) or value < 0:
            raise PlatformError(f"{name} {value} is not a finite, non-negative number")
    manifest, circuit, cases_sha256 = load_case(case_dir)
    if platform not in manifest["platforms"]:
        raise PlatformError(f"cases.json admits {manifest['platforms']}, not {platform}")
    row = explorer_row(platform)
    if row["status"] != "available":
        raise PlatformError(f"{platform} is {row['status']}")
    if manifest["max_duration"] > row["max_duration"]:
        raise PlatformError(f"max_duration {manifest['max_duration']} exceeds the platform's {row['max_duration']}")
    if expected_seconds > manifest["max_duration"]:
        raise PlatformError(f"expected {expected_seconds} s exceed the case's max_duration {manifest['max_duration']}")
    ceiling = row["price_per_shot"] * manifest["max_shots"] + per_job_credits
    if ceiling > max_credits:
        raise PlatformError(
            f"{manifest['max_shots']} shots and the per-job price cost up to {ceiling:g} credits, above {max_credits:g}"
        )
    processor = get(platform_route(platform))
    if processor.get("status") != "available":
        raise PlatformError(f"{platform} processor is {processor.get('status')}")
    perfs = scrub(processor.get("perfs") or {})
    if row["type"] == "qpu":
        message = hom_warning(platform, perfs, block_photons(circuit), case_dir.name)
        if message is not None:
            print(message, file=sys.stderr)
    if manifest.get("gate_form") == "mesh":
        live_mesh(processor, circuit, platform)
    if "seeded_from" in manifest:
        live_architecture(processor, platform)
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
        "perfs_at_plan": perfs,
        "availability_at_plan": counters,
        "expected_seconds": expected_seconds,
        "per_job_credits": per_job_credits,
        "max_samples": manifest["max_samples"],
        "max_shots": manifest["max_shots"],
        "estimated_shots": estimate,
        "credit_ceiling": ceiling,
        "estimated_credits": row["price_per_shot"] * estimate + per_job_credits,
        "max_credits": max_credits,
        "body": built["body"],
        "body_sha256": sha256_bytes(json.dumps(built["body"], sort_keys=True).encode()),
        "versions": built["versions"],
        "payload_version_basis": built["payload_version_basis"],
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


def submit(
    case_dir: Path,
    platform: str,
    approval: str,
    max_credits: float,
    expected_seconds: float,
    per_job_credits: float,
) -> dict[str, Any]:
    """Send one approved case as one job while holding the token's submit lock beside the token file."""
    if not approval.strip():
        raise PlatformError("a nonempty approval is required")
    lock = Path(os.environ.get(TOKEN_ENV, "")).with_name("submit.lock")
    with open(lock, "a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        state_path = case_dir / "submission-state.json"
        if any((case_dir / name).exists() for name in ("submission.json", "submission-state.json", "job-body.json")):
            raise PlatformError(f"{case_dir} was submitted or holds an interrupted submission; never resubmit it")
        checked = plan(case_dir, platform, max_credits, expected_seconds, per_job_credits)
        usage_before = usage_rows(get("/api/tokens/usage/report"))
        receipt = {
            "schema": SUBMISSION_SCHEMA,
            "approval": approval,
            "usage_before": usage_before,
            **{key: value for key, value in checked.items() if key != "body"},
        }
        state = {
            "schema": STATE_SCHEMA,
            "phase": "post_outcome_unknown",
            "started_utc": now(),
            "platform": platform,
            "cases_sha256": checked["cases_sha256"],
            "body_sha256": checked["body_sha256"],
            "receipt": receipt,
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
        # The job id reaches the synced checkpoint before the receipt, so
        # recover can write the receipt of a job whose receipt write was lost.
        state.update(phase="posted", job_id=answer["job_id"], submitted_utc=now())
        write_json(state_path, state)
        return recover(case_dir)


def recover(case_dir: Path) -> dict[str, Any]:
    """Write submission.json from a posted checkpoint; an existing receipt must equal it."""
    state = json.loads((case_dir / "submission-state.json").read_text(encoding="utf-8"))
    if state.get("schema") != STATE_SCHEMA or state.get("phase") != "posted":
        raise PlatformError(f"{case_dir}: the checkpoint is {state.get('phase')}, not posted; nothing to recover")
    record = {**state["receipt"], "job_id": state["job_id"], "submitted_utc": state["submitted_utc"]}
    try:
        write_json(case_dir / "submission.json", record, exclusive=True)
    except FileExistsError:
        if json.loads((case_dir / "submission.json").read_text(encoding="utf-8")) != record:
            raise PlatformError(f"{case_dir}/submission.json differs from the posted checkpoint") from None
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
    # An error or canceled job can still carry partial results; a refused
    # /result is recorded as absent, and only a completed job must have one.
    try:
        result_bytes = request("GET", job_route(job, "result"), raw=True)
    except RefusedError as error:
        if status["status"] == "completed":
            raise
        collected["result_absent"] = str(error)
        result_bytes = None
    else:
        collected["result_sha256"] = sha256_bytes(result_bytes)
        collected.update(result_summary(result_bytes, job, status, complete=status["status"] == "completed"))
    # A recollection is compared before any write, so a result that appears
    # after a recorded absence changes nothing on disk and is reported.
    retained_path = case_dir / "results.json"
    if retained_path.exists():
        retained = json.loads(retained_path.read_text(encoding="utf-8"))
        moving = ("collected_utc", "usage_after")
        if {k: v for k, v in retained.items() if k not in moving} != {
            k: v for k, v in collected.items() if k not in moving
        }:
            raise PlatformError(f"{retained_path} differs from the recollection; nothing was rewritten")
    if result_bytes is not None:
        retain_bytes(raw_dir / "result.json", result_bytes)
    if retained_path.exists():
        return dict(retained)
    write_json(retained_path, collected, exclusive=True)
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


def result_summary(result_bytes: bytes, job: str, status: dict[str, Any], complete: bool = True) -> dict[str, Any]:
    """The counts and scalar fields of a raw /result answer, parsed without Perceval and bound to its job.

    The answer's job_id must be the submitted job and its shots must agree
    with any non-null status shots. A partial result (error or canceled job)
    without serialized counts is summarized as partial with no counts.
    """
    answer = json.loads(result_bytes)
    if not isinstance(answer, dict) or answer.get("job_id") != job:
        raise PlatformError(
            f"the result answers job {answer.get('job_id') if isinstance(answer, dict) else None}, not {job}"
        )
    shots = answer.get("shots")
    if not isinstance(shots, int) or shots < 0:
        raise PlatformError(f"the result of job {job} carries shots {shots!r}")
    if status.get("shots") is not None and status["shots"] != shots:
        raise PlatformError(f"job {job}: status shots {status['shots']} differ from the result's {shots}")
    serialized = answer.get("results")
    inner = json.loads(serialized) if isinstance(serialized, str) and serialized else None
    iterations = None
    if isinstance(inner, dict) and isinstance(inner.get("results_list"), list):
        # An iterated job answers one entry per iteration; counts add up, and
        # each entry keeps its own counts and its iteration's scalar fields.
        iterations = []
        merged: dict[str, int] = {}
        for entry in inner["results_list"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("results"), str):
                raise PlatformError(f"job {job}: an iteration result carries no serialized counts")
            part = parse_counts(entry["results"])
            for state, n in part.items():
                merged[state] = merged.get(state, 0) + n
            iteration = entry.get("iteration") if isinstance(entry.get("iteration"), dict) else {}
            fields = {k: v for k, v in entry.items() if k not in ("results", "iteration")}
            iterations.append(
                {
                    "iteration": scalar_tree(iteration),
                    "counts": part,
                    "samples": sum(part.values()),
                    "result_fields": scalar_tree(fields),
                }
            )
        inner = {**{k: v for k, v in inner.items() if k != "results_list"}, "results": None}
        counts = merged
    elif not isinstance(inner, dict) or not isinstance(inner.get("results"), str):
        if complete:
            raise PlatformError("the result carries no serialized counts")
        return {"shots": shots, "partial": True, "counts": {}, "samples": 0, "result_fields": {}}
    else:
        counts = parse_counts(inner["results"])
    # An iterated answer's top-level shots is one iteration's max_shots; each
    # entry reports the shots it used, and their sum is what the job consumed.
    used = shots
    if iterations is not None:
        per = [entry["result_fields"].get("nb_shots_used") for entry in iterations]
        if not all(isinstance(n, int) and n >= 0 for n in per):
            raise PlatformError(f"job {job}: an iteration reports no nb_shots_used")
        used = sum(per)
        for entry, n in zip(iterations, per, strict=True):
            if entry["samples"] > n:
                raise PlatformError(f"job {job}: an iteration counts {entry['samples']} samples from {n} shots")
    if sum(counts.values()) > used:
        raise PlatformError(f"job {job}: {sum(counts.values())} samples exceed its {used} shots")
    scalars = {k: v for k, v in inner.items() if k != "results" and isinstance(v, int | float | str | None)}
    summary = {
        "shots": shots,
        "shots_used": used,
        "partial": not complete,
        "counts": counts,
        "samples": sum(counts.values()),
        "result_fields": scalars,
    }
    if iterations is not None:
        summary["iterations"] = iterations
    return summary


def scalar_tree(value: Any) -> Any:
    """JSON scalars and nested dicts and lists of them; anything else becomes its type name."""
    if isinstance(value, dict):
        return {str(k): scalar_tree(v) for k, v in value.items()}
    if isinstance(value, list):
        return [scalar_tree(v) for v in value]
    if value is None or isinstance(value, bool | int | float | str):
        return value
    return type(value).__name__


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
    shots = 0
    if status == "completed" or raw.exists():
        if not raw.is_file() or sha256_bytes(raw.read_bytes()) != collected.get("result_sha256"):
            raise PlatformError(f"{owner}: raw/result.json differs from its recorded sha256")
        summary = result_summary(raw.read_bytes(), submission["job_id"], collected["status"], status == "completed")
        # shots_used is derived from the raw bytes; a collection written before
        # the field existed omits it and the raw result supplies it.
        if any(
            collected.get(key) != value
            for key, value in summary.items()
            if not (key == "shots_used" and key not in collected)
        ):
            raise PlatformError(f"{owner}: results.json differs from the raw result")
        modes = json.loads((directory / manifest["circuit"]["file"]).read_text(encoding="utf-8"))["modes"]
        if any(len(state.split(",")) != modes for state in summary["counts"]):
            raise PlatformError(f"{owner}: a counted state has a mode count other than {modes}")
        if summary["samples"] > manifest["max_samples"]:
            raise PlatformError(f"{owner}: {summary['samples']} samples exceed max_samples {manifest['max_samples']}")
        # A count-less partial result carries no per-iteration shots; its top-level shots stand in.
        shots = summary.get("shots_used", summary.get("shots") or 0)
    elif not isinstance(collected.get("result_absent"), str):
        raise PlatformError(f"{owner}: a {status} job records neither a raw result nor its absence")
    else:
        # A result-less terminal job still consumed the shots its status reports.
        reported = collected["status"].get("shots")
        if reported is not None and (not isinstance(reported, int) or reported < 0):
            raise PlatformError(f"{owner}: status shots {reported!r} are not a shot count")
        shots = reported or 0
    return {
        "created_at": submission["submitted_utc"],
        "backends": [submission["platform"]],
        "jobs": 1,
        # A box-kite case counts its blocks and a mesh case its phase settings.
        "circuits": len(manifest["blocks"] if "blocks" in manifest else manifest["settings"]),
        "statuses": {status: 1},
        "charge": charged(submission, collected, shots),
        "detail": f"job {submission['job_id']}, {collected.get('samples', 0)} samples, {shots} shots",
    }


def usage_total(report: Any) -> float | None:
    """credits plus free_credits over every platform row of a token usage report."""
    if not isinstance(report, list):
        return None
    total = 0.0
    for token_row in report:
        for row in token_row.get("usage", []) if isinstance(token_row, dict) else []:
            total += float(row.get("credits") or 0) + float(row.get("free_credits") or 0)
    return total


def charged(submission: dict[str, Any], collected: dict[str, Any], shots: int) -> float:
    """The credits a run consumed: the usage report after collection minus the one before submission.

    Jobs run one at a time on the token, so the difference is this job's
    per-job price plus its shots. The usage report counts the calendar month,
    so a job submitted and collected in different months, a negative
    difference or a receipt without both reports falls back to the recorded
    per-job price plus shots times the price per shot.
    """
    before, after = usage_total(submission.get("usage_before")), usage_total(collected.get("usage_after"))
    same_month = str(submission.get("submitted_utc", ""))[:7] == str(collected.get("collected_utc", ""))[:7]
    if before is not None and after is not None and same_month and after >= before:
        return round(after - before, 6)
    price = submission["platform_at_plan"]["price_per_shot"]
    return round(float(submission.get("per_job_credits", 0)) + shots * price, 6)


def run_directories(runs: Path = RUNS) -> list[Path]:
    return sorted(path for path in runs.iterdir() if path.is_dir()) if runs.is_dir() else []


def zipped(text: str) -> str:
    return ":PCVL:zip:" + base64.b64encode(zlib.compress(text.encode("ascii"))).decode("ascii")


def charge_self_test() -> None:
    """charged() takes the usage delta within one calendar month and the recorded price across a reset."""

    def report(credits: float) -> list[dict[str, Any]]:
        return [{"usage": [{"credits": 0.0, "free_credits": credits, "nb_jobs": 1, "platform_name": "qpu:belenos"}]}]

    submission = {
        "submitted_utc": "2026-10-31T23:59:00+00:00",
        "usage_before": report(12.0),
        "per_job_credits": 1.0,
        "platform_at_plan": {"price_per_shot": 1e-06},
    }
    cases = (
        ("2026-10-31T23:59:30+00:00", report(13.01), 1.01),
        ("2026-11-01T00:00:30+00:00", report(1.01), 1.01),
        ("2026-10-31T23:59:30+00:00", report(11.0), 1.01),
    )
    for collected_utc, after, want in cases:
        got = charged(submission, {"collected_utc": collected_utc, "usage_after": after}, 10000)
        if got != want:
            raise SystemExit(f"self-test: charged() read {got} for a collection at {collected_utc}, not {want}")


def seed_self_test() -> None:
    """seed_value passes non-negative integers and refuses a bool, a negative, a float or a string; job_seed
    takes a one-circuit job's seed from its setting or its manifest and refuses a conflict or an iterated
    case's manifest seed; iteration_form names each case form and refuses a seeded settings list that
    miscounts its iterations, lacks or misstates a seed, or carries circuit parameters."""
    if seed_value(0, "test") != 0 or seed_value(7, "test") != 7:
        raise SystemExit("self-test: seed_value changed a valid seed")
    for bad in (True, -1, 1.0, "1", None):
        try:
            seed_value(bad, "test")
        except PlatformError:
            continue
        raise SystemExit(f"self-test: seed_value accepted {bad!r}")
    one: dict[str, Any] = {"job": "test"}
    many: dict[str, Any] = {"job": "test", "iterations": 2}
    accepted: list[tuple[dict[str, Any], list[dict[str, Any]], int | None]] = [
        (one, [], None),
        (one, [{}], None),
        ({**one, "compilation_seed": 3}, [], 3),
        ({**one, "compilation_seed": 3}, [{}], 3),
        (one, [{"compilation_seed": 4}], 4),
        ({**one, "compilation_seed": 4}, [{"compilation_seed": 4}], 4),
        (many, [{"compilation_seed": 1}, {"compilation_seed": 2}], None),
    ]
    for manifest, settings, want in accepted:
        if job_seed(manifest, settings) != want:
            raise SystemExit(f"self-test: job_seed({manifest}, {settings}) is not {want}")
    refused: list[tuple[dict[str, Any], list[dict[str, Any]]]] = [
        ({**one, "compilation_seed": 3}, [{"compilation_seed": 4}]),
        ({**many, "compilation_seed": 1}, [{}, {}]),
        ({**one, "compilation_seed": -1}, []),
    ]
    for manifest, settings in refused:
        try:
            job_seed(manifest, settings)
        except PlatformError:
            continue
        raise SystemExit(f"self-test: job_seed accepted {manifest} with {settings}")
    seeded = [{"name": "a", "compilation_seed": 0}, {"name": "b", "compilation_seed": 5}]
    forms: list[tuple[dict[str, Any], str]] = [
        (one, "single"),
        ({**one, "settings": seeded}, "single"),
        (many, "phase"),
        ({**many, "gate_form": "mesh", "settings": [{}, {}]}, "mesh"),
        ({**many, "settings": seeded}, "seeded"),
        ({**one, "iterator": True, "settings": seeded[:1]}, "seeded"),
    ]
    for manifest, form in forms:
        if iteration_form(manifest) != form:
            raise SystemExit(f"self-test: iteration_form({manifest}) is not {form}")
    ladder = [{**seeded[0], "max_samples": 10, "max_shots": 20}, {**seeded[1], "max_samples": 30, "max_shots": 60}]
    laddered = {**many, "settings": ladder, "max_samples": 40, "max_shots": 80}
    if iteration_form(laddered) != "seeded" or iteration_budgets(laddered) != [(10, 20), (30, 60)]:
        raise SystemExit("self-test: a budgeted seeded case lost its per-iteration budgets")
    if iteration_budgets({**many, "settings": seeded, "max_samples": 40, "max_shots": 80}) != [(20, 40)] * 2:
        raise SystemExit("self-test: an unbudgeted seeded case lost its even split")
    for bad_ladder in (
        [ladder[0], seeded[1]],
        [{**ladder[0], "max_shots": 5}, ladder[1]],
        [{**ladder[0], "max_samples": 0}, ladder[1]],
        [{**ladder[0], "max_samples": 11, "max_shots": 21}, ladder[1]],
    ):
        try:
            iteration_form({**laddered, "settings": bad_ladder})
        except PlatformError:
            continue
        raise SystemExit(f"self-test: iteration_form accepted ladder {bad_ladder}")
    if job_seed({**one, "iterator": True, "settings": seeded[1:]}, seeded[1:]) is not None:
        raise SystemExit("self-test: a one-entry iterator carried its seed on the base computation")
    for bad_iterator in (
        {**one, "iterator": True},
        {**one, "iterator": 1, "settings": seeded[:1]},
        {**one, "iterator": True, "settings": seeded},
        {**many, "iterator": True, "settings": seeded},
        {**one, "iterator": True, "gate_form": "mesh", "settings": [{}]},
        {**one, "iterator": True, "compilation_seed": 0, "settings": seeded[:1]},
    ):
        try:
            iteration_form(bad_iterator)
            job_seed(bad_iterator, bad_iterator.get("settings") or [])
        except PlatformError:
            continue
        raise SystemExit(f"self-test: accepted iterator case {bad_iterator}")
    for bad_settings in (
        seeded[:1],
        [seeded[0], {"name": "b"}],
        [seeded[0], {"name": "b", "compilation_seed": -1}],
        [seeded[0], {"name": "b", "compilation_seed": 1, "circuit_params": {"phi": 0.0}}],
        [seeded[0], {"name": "b", "compilation_seed": True}],
    ):
        try:
            iteration_form({**many, "settings": bad_settings})
        except PlatformError:
            continue
        raise SystemExit(f"self-test: iteration_form accepted settings {bad_settings}")


def payload_version_self_test() -> None:
    """A 1.3 record without commands gets them back and builds a version-2 body; a 1.2 record keeps version 1."""
    import perceval as pcvl
    from perceval.runtime.payload_generator import PayloadGenerator
    from perceval.runtime.payload_updater import PayloadUpdater
    from perceval.runtime.platform_specs import PlatformSpecs
    from perceval.utils.constants import KEY_COMPUTATION, KEY_MITIGATIONS

    built = pcvl.Experiment(pcvl.BS())
    built.with_input(pcvl.BasicState([1, 0]))
    built.min_detected_photons_filter(1)
    computation = pcvl.ExecutionFactory(pcvl.SimulatedComputer("SLOS"), built).build_computation("sample_count")
    computation.add_params(max_samples=100, max_shots=200)
    for version, expected in (("1.3.0", "restored"), ("1.2.4", "absent"), (None, "absent")):
        specs = PlatformSpecs({"available_commands": ["probs", "sample_count"], "pcvl_version": version})
        basis = payload_version_basis(specs)
        if basis != expected:
            raise PlatformError(f"self-test: pcvl_version {version} reads {basis}, expected {expected}")
        body = PayloadGenerator.from_computation(computation, [], None, None)
        if "commands" not in specs:
            body = PayloadUpdater.update_payload(body, specs, target_payload_version=1)
        if (KEY_COMPUTATION in body) != (expected == "restored"):
            raise PlatformError(f"self-test: pcvl_version {version} built the wrong payload version")
    # A version-1 body round-tripped by PayloadUpdater loses an explicit empty mitigation list.
    v1 = PayloadUpdater.update_payload(
        PayloadGenerator.from_computation(computation, [], None, None), specs, target_payload_version=1
    )
    if KEY_MITIGATIONS in PayloadUpdater.update_payload(v1, pcvl.SimulatedComputer("SLOS"), target_payload_version=2):
        raise PlatformError("self-test: a version-1 round trip kept the mitigation list")


def runner_self_test() -> int:
    """Offline rules of plan, submit, collect and run_facts against a stubbed service; returns the rejections."""
    charge_self_test()
    payload_version_self_test()
    seed_self_test()
    root = Path(__file__).resolve().parent.parent
    case = root / "results/quandela/cases/box_kite_photonic_single/job-00"
    modes = ["0"] * 24
    dark, label = modes.copy(), modes.copy()
    dark[22], label[20] = "1", "1"
    counts = f":PCVL:BSCount:{{|{','.join(dark)}>=9990;|{','.join(label)}>=10}}"
    result = json.dumps(
        {"job_id": "job-a", "results": json.dumps({"results": zipped(counts), "global_perf": 1.0}), "shots": 10012}
    )
    row = {field: None for field in PLATFORM_FIELDS} | {
        "name": "sim:belenos",
        "status": "available",
        "max_duration": 300,
        "price_per_shot": 0.0,
        "maintenance": None,
    }
    idle = dict.fromkeys(AVAILABILITY_KEYS, 0)
    body = {"job_name": "gororoba-job-00", "payload": {"command": "sample_count"}, "platform_name": "sim:belenos"}
    service: dict[str, Any] = {
        "row": row,
        "idle": idle,
        "estimate": 10000,
        "refuse": False,
        "result": result,
        "status": "completed",
        "processor_status": "available",
    }

    def fake_request(method: str, route: str, auth: bool = True, body: Any = None, raw: bool = False) -> Any:
        if (method, route) == ("POST", "/api/jobs"):
            if service["refuse"]:
                raise RefusedError("POST /api/jobs: HTTP 422 unprocessable payload")
            return {"job_id": "job-a"}
        if route.endswith("/status"):
            return {"status": service["status"], "shots": 10012, "token_id": 7}
        if route.endswith("/data"):
            return {"job_id": "job-a", "token_label": "secret-label", "status": "completed"}
        if route.endswith("/result"):
            if service["result"] is None:
                raise RefusedError(f"GET {route}: HTTP 404 no result")
            return str(service["result"]).encode("utf-8")
        if route == platform_route("sim:belenos"):
            return {"status": service["processor_status"], "perfs": {"g2 (%)": 1.0, "HOM (%)": 94.2}, "token_id": 7}
        if route == "/api/tokens/usage/report":
            return [{"total_jobs": 1, "usage": [{"job": "job-a", "token_label": "secret-label"}], "token_id": 7}]
        raise AssertionError(f"unexpected {method} {route}")

    def fake_payload(*_: Any) -> dict[str, Any]:
        return {
            "body": body,
            "estimated_shots": service["estimate"],
            "versions": {"perceval-quandela": "1.3.1"},
            "payload_version_basis": "declared",
        }

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
            refuse("a non-finite credit ceiling", lambda: plan(run, "sim:belenos", math.nan, 10.0, 0.0), "finite")
            refuse("a platform outside the case", lambda: plan(run, "qpu:ascella", 1.0, 10.0, 0.0), "admits")
            refuse("a per-job price above the ceiling", lambda: plan(run, "sim:belenos", 0.0, 10.0, 0.5), "above")
            refuse("expected seconds past max_duration", lambda: plan(run, "sim:belenos", 1.0, 301.0, 0.0), "exceed")
            service["row"] = {**row, "status": "maintenance"}
            refuse("a platform under maintenance", lambda: plan(run, "sim:belenos", 1.0, 10.0, 0.0), "is maintenance")
            service["row"] = row
            service["processor_status"] = "calibration"
            refuse(
                "a processor under calibration",
                lambda: plan(run, "sim:belenos", 1.0, 10.0, 0.0),
                "processor is calibration",
            )
            service["processor_status"] = "available"
            service["row"] = {**row, "price_per_shot": 1e-6}
            refuse("a ceiling above the case's credits", lambda: plan(run, "sim:belenos", 0.0, 10.0, 0.0), "above")
            service["row"], service["idle"] = row, {**idle, "num_jobs_in_queue": 1}
            refuse("a token with a queued job", lambda: plan(run, "sim:belenos", 1.0, 10.0, 0.0), "running or queued")
            service["idle"], service["estimate"] = idle, 10**9
            refuse("an estimate above max_shots", lambda: plan(run, "sim:belenos", 1.0, 10.0, 0.0), "estimates")
            service["estimate"] = 10000
            refuse("an empty approval", lambda: submit(run, "sim:belenos", " ", 1.0, 10.0, 0.0), "approval")
            refused = scratch / "refused"
            shutil.copytree(case, refused)
            service["refuse"] = True
            refuse("a refused POST", lambda: submit(refused, "sim:belenos", "approved", 0.0, 10.0, 0.0), "HTTP 422")
            service["refuse"] = False
            if json.loads((refused / "submission-state.json").read_text(encoding="utf-8"))["phase"] != "refused":
                raise AssertionError("a refused POST left a checkpoint other than refused")
            refuse(
                "a resubmitted refusal",
                lambda: submit(refused, "sim:belenos", "again", 0.0, 10.0, 0.0),
                "never resubmit",
            )
            submit(run, "sim:belenos", "approved in the written case", 0.0, 10.0, 0.0)
            refuse("a second submit", lambda: submit(run, "sim:belenos", "again", 0.0, 10.0, 0.0), "never resubmit")
            collected = collect(run, 0.0, 1.0)
            receipt = json.loads((run / "submission.json").read_text(encoding="utf-8"))
            if receipt["perfs_at_plan"].get("g2 (%)") != 1.0 or receipt["expected_seconds"] != 10.0:
                raise AssertionError("the receipt lacks the processor perfs or the approved seconds")
            for name in ("results.json", "submission.json"):
                if carried := sorted(set(FORBIDDEN_KEYS) & keys(json.loads((run / name).read_text(encoding="utf-8")))):
                    raise AssertionError(f"{name} retained {carried}")
            if collect(run, 0.0, 1.0)["counts"] != collected["counts"]:
                raise AssertionError("a recollection changed the retained counts")
            service["result"] = result.replace("1.0}", "0.5}")
            if service["result"] == result:
                raise AssertionError("the recollection fixture did not change the result bytes")
            refuse("a recollection with other raw bytes", lambda: collect(run, 0.0, 1.0), "nothing was rewritten")
            service["result"] = result
            lost = scratch / "lost-receipt"
            shutil.copytree(run, lost)
            (lost / "submission.json").unlink()
            if recover(lost) != json.loads((run / "submission.json").read_text(encoding="utf-8")):
                raise AssertionError("recover wrote a receipt other than submit's")
            refuse("recovery from a refused checkpoint", functools.partial(recover, refused), "not posted")
            for terminal, partial in (("canceled", None), ("error", result)):
                stopped = scratch / f"stopped-{terminal}"
                shutil.copytree(case, stopped)
                submit(stopped, "sim:belenos", "approved", 0.0, 10.0, 0.0)
                service["status"], service["result"] = terminal, partial
                collect(stopped, 0.0, 1.0)
                facts = run_facts(stopped)
                if (
                    facts["statuses"] != {terminal: 1}
                    or (partial is not None) != (stopped / "raw/result.json").exists()
                ):
                    raise AssertionError(f"a {terminal} job was retained as {facts}")
            if "10012 shots" not in run_facts(scratch / "stopped-canceled")["detail"]:
                raise AssertionError("a result-less canceled job lost its status shots")
            late = scratch / "stopped-canceled"
            service["status"], service["result"] = "canceled", result.replace("job-a", "job-a")
            refuse("a late partial result", lambda: collect(late, 0.0, 1.0), "nothing was rewritten")
            if (late / "raw/result.json").exists():
                raise AssertionError("a refused recollection wrote raw/result.json")
            service["status"], service["result"] = "completed", result
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
                ("a raw result of another job", _foreign_result, "not job-a"),
                ("more samples than shots", _inflated_result, "exceed its"),
                (
                    "status shots off the result",
                    lambda d: _rewrite(d / "results.json", status={"status": "completed", "shots": 5}),
                    "differ from the result",
                ),
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
    iterated = json.dumps(
        {
            "job_id": "job-i",
            "shots": 9,
            "results": json.dumps(
                {
                    "results_list": [
                        {
                            "results": ":PCVL:BSCount:{|1,0>=3;|0,1>=1}",
                            "nb_shots_used": 5,
                            "iteration": {"circuit_params": {"phi": 0.0}},
                        },
                        {
                            "results": zipped(":PCVL:BSCount:{|0,1>=4}"),
                            "nb_shots_used": 4,
                            "iteration": {"circuit_params": {"phi": 3.14}},
                        },
                    ]
                }
            ),
        }
    ).encode()
    summary = result_summary(iterated, "job-i", {"shots": 9})
    if (
        summary["counts"] != {"1,0": 3, "0,1": 5}
        or [it["samples"] for it in summary["iterations"]] != [4, 4]
        or summary["shots_used"] != 9
    ):
        raise AssertionError(f"an iterated result parsed as {summary}")
    overdrawn = iterated.replace(b'"nb_shots_used\\": 4', b'"nb_shots_used\\": 3')
    if overdrawn == iterated:
        raise AssertionError("the overdrawn-iteration fixture did not change the iterated result")
    refuse(
        "an iteration with more samples than shots", functools.partial(result_summary, overdrawn, "job-i", {}), "from"
    )
    broken = iterated.replace(b"|1,0>=3", b"|{_:0},0>=3")
    if broken == iterated:
        raise AssertionError("the annotated-state fixture did not change the iterated result")
    refuse("an iteration with an annotated state", functools.partial(result_summary, broken, "job-i", {}), "")
    for label_text, text in (
        ("a BasicState tag", ":PCVL:BasicState:|1,0>"),
        ("an annotated state", ":PCVL:BSCount:{|{_:0},0>=3}"),
        ("a repeated state", ":PCVL:BSCount:{|1,0>=3;|1,0>=4}"),
        ("an oversized zipped result", zipped(":PCVL:BSCount:{" + "0" * (RESULT_LIMIT + 1) + "}")),
    ):
        refuse(label_text, functools.partial(parse_counts, text), "")
    return rejected


def _inflated_result(directory: Path) -> None:
    """Shrink the result's shots below its sample count and rebind its digest."""
    raw = directory / "raw/result.json"
    data = raw.read_bytes().replace(b'"shots": 10012', b'"shots": 5')
    raw.write_bytes(data)
    status = json.loads((directory / "results.json").read_text(encoding="utf-8"))["status"]
    _rewrite(directory / "results.json", result_sha256=sha256_bytes(data), shots=5, status={**status, "shots": 5})


def _foreign_result(directory: Path) -> None:
    """Replace the raw result with another job's answer and rebind its digest."""
    raw = directory / "raw/result.json"
    data = raw.read_bytes().replace(b'"job-a"', b'"job-b"')
    raw.write_bytes(data)
    _rewrite(directory / "results.json", result_sha256=sha256_bytes(data))


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
    chipped = {name for name, record in catalogue["processors"].items() if chip_architecture(record) is not None}
    if "architecture_observed_utc" not in catalogue or "architecture_carried" not in catalogue:
        raise SystemExit("the catalogue lacks its architecture provenance markers")
    stamped = set(catalogue["architecture_observed_utc"])
    carried_names = set(catalogue["architecture_carried"])
    if "qpu:belenos" not in chipped:
        raise SystemExit("qpu:belenos carries no chip architecture, so the mesh checks cannot run")
    if stamped != chipped or not carried_names <= stamped:
        raise SystemExit("architecture markers do not name exactly the platforms with a chip architecture")
    for name, stamp in catalogue["architecture_observed_utc"].items():
        try:
            datetime.datetime.fromisoformat(stamp)
        except (TypeError, ValueError):
            raise SystemExit(f"{name}: architecture_observed_utc {stamp!r} is not an ISO timestamp") from None
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
    guides = (root / "docs" / "notes" / "quandela" / "README.md",)
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
        "edited table": text("README.md", "| credits per shot |", "| price |"),
        "stale row": text("README.md", END, "| stale | row |\n" + END),
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
        "belenos without architecture": catalogue(lambda c: c["processors"]["qpu:belenos"]["specs"].pop(ARCHITECTURE)),
        "carried name without a chip": catalogue(lambda c: c.update(architecture_carried=["qpu:nonexistent"])),
        "missing provenance markers": catalogue(lambda c: c.pop("architecture_observed_utc")),
        "stamp missing for a chip": catalogue(lambda c: c["architecture_observed_utc"].pop("sim:belenos")),
        "null observation time": catalogue(lambda c: c["architecture_observed_utc"].update({"qpu:belenos": None})),
        "malformed observation time": catalogue(
            lambda c: c["architecture_observed_utc"].update({"qpu:belenos": "yesterday"})
        ),
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
    missing: list[dict[str, Any]] = [{}, {"specs": {}}, {"specs": None}, {"specs": {"architecture": None}}]
    for record in missing:
        try:
            architecture_blob(record, "qpu:belenos")
        except PlatformError:
            continue
        raise AssertionError("architecture_blob accepted a record without a usable specs.architecture")
    if hom_warning("qpu:belenos", {"HOM (%)": 90.0}, 2, "case") is None:
        raise AssertionError("hom_warning is silent at the 90 % floor")
    if hom_warning("qpu:belenos", {"HOM (%)": 90.01}, 2, "case") is not None:
        raise AssertionError("hom_warning fires above the floor")
    if hom_warning("qpu:belenos", {}, 2, "case") is None:
        raise AssertionError("hom_warning is silent on two photons in one block without a HOM figure")
    if hom_warning("qpu:belenos", {"HOM (%)": 88.5}, 1, "case") is not None:
        raise AssertionError("hom_warning fires on one photon per block")
    packed: dict[str, Any] = {
        "input_state": [1, 0, 0, 0, 1, 0, 0, 0],
        "components": [{"at": 0, "unitary": [0] * 4}, {"at": 4, "unitary": [0] * 4}],
    }
    if block_photons(packed) != 1:
        raise AssertionError("block_photons counts photons in disjoint blocks together")
    pair: dict[str, Any] = {"input_state": [0, 0, 0, 0, 1, 1, 0, 0], "components": [{"at": 4, "unitary": [0] * 4}]}
    if block_photons(pair) != 2:
        raise AssertionError("block_photons misses two photons in one block")
    if block_photons({"input_state": [1, 1]}) != 2 or block_photons({"settings": [{"input_mode": 3}]}) != 1:
        raise AssertionError("block_photons misreads a circuit without components or a mesh setting")
    retained: dict[str, Any] = {
        "retrieved_utc": "2026-10-17T17:53:31+00:00",
        "processors": {"qpu:belenos": {"specs": {"architecture": "b"}}},
    }
    records: dict[str, dict[str, Any]] = {"qpu:belenos": {"specs": {}}, "sim:x": {"specs": None}}
    observed, carried = architecture_provenance(records, retained, "2026-10-19T00:00:00+00:00")
    if records["qpu:belenos"]["specs"] != {"architecture": "b"} or carried != ["qpu:belenos"]:
        raise AssertionError("architecture_provenance does not carry the retained chip")
    if observed != {"qpu:belenos": "2026-10-17T17:53:31+00:00"}:
        raise AssertionError("architecture_provenance does not keep the retained observation time")
    chained: dict[str, Any] = {**retained, "architecture_observed_utc": {"qpu:belenos": "2026-10-16T00:00:00+00:00"}}
    chained_observed, _ = architecture_provenance({"qpu:belenos": {"specs": {}}}, chained, "2026-10-19T00:00:00+00:00")
    if chained_observed != {"qpu:belenos": "2026-10-16T00:00:00+00:00"}:
        raise AssertionError("architecture_provenance replaces an earlier observation time with the snapshot time")
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
        p.add_argument("--expected-seconds", type=float, required=True, help="the written case's expected seconds")
        p.add_argument("--per-job-credits", type=float, required=True, help="the offer's per-job price in the case")
        if name == "submit":
            p.add_argument("--approval", required=True, help="the user's approval, quoted, kept in submission.json")
    p = sub.add_parser("recover")
    p.add_argument("case_dir", type=Path)
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
    elif args.command in ("plan", "submit", "recover", "collect", "runs"):
        try:
            if args.command == "plan":
                checked = plan(
                    args.case_dir, args.platform, args.max_credits, args.expected_seconds, args.per_job_credits
                )
                print(json.dumps({k: v for k, v in checked.items() if k != "body"}, indent=1, sort_keys=True))
            elif args.command == "submit":
                record = submit(
                    args.case_dir,
                    args.platform,
                    args.approval,
                    args.max_credits,
                    args.expected_seconds,
                    args.per_job_credits,
                )
                print(f"job {record['job_id']} on {record['platform']}")
            elif args.command == "recover":
                print(f"job {recover(args.case_dir)['job_id']}: submission.json written from the checkpoint")
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
