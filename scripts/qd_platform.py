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
  --per-job-credits P [--admit-status STATUS ...] (network, read-only) runs every check submit makes and
  prints the result: the circuit matches its cases.json sha256, the platform
  is one the case admits, is available and allows the case's max_duration,
  S stays within max_duration, P plus the largest iteration's max_shots times
  the live price per shot stays within C, the processor's perfs (HOM and g2 among them) are
  recorded, and a two-photon case on a QPU whose HOM visibility is absent or
  not above 90 % draws a warning on stderr,
  the token satisfies the case's occupancy policy, and Perceval's
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
  answer byte for byte in raw/result.json (written once, before the answer
  is parsed or the job data and usage are read; a recollection must bring
  the same bytes) and results.json with the scrubbed status and job data,
  the usage report after the job (or usage_absent naming the failed read)
  and the counts that
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
import email.message
import fcntl
import functools
import hashlib
import http.client
import importlib.metadata
import importlib.util
import io
import json
import math
import os
import re
import shutil
import ssl
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
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
    "qd_job_billing",
    "qd_job_result",
    "qd_job_status",
    "qd_plan",
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

    def __init__(self, message: str, code: int | None = None) -> None:
        super().__init__(message)
        self.code = code


class UnansweredError(PlatformError):
    """The request lacks a usable acknowledgment that establishes its outcome."""


# Statuses a read may outlive: the service's own timeouts, throttling and gateway or upstream failures.
TRANSIENT_STATUSES = frozenset({408, 429, 500, 502, 503, 504})


def transient(error: PlatformError) -> bool:
    """A failed read worth repeating: a transient HTTP status, or no answer at all (network or timeout).

    A missing token and other local configuration failures raise at once.
    A malformed or oversized response remains retryable for reads alone.
    """
    if isinstance(error, RefusedError):
        return error.code in TRANSIENT_STATUSES
    return isinstance(error, UnansweredError)


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
        data = json.dumps(body, sort_keys=True).encode("utf-8")
        headers["Content-Type"] = "application/json"
    call = urllib.request.Request(API + route, data=data, headers=headers, method=method)
    try:
        with OPENER.open(call, timeout=60) as response:
            answer = response.read(RESULT_LIMIT + 1)
    except urllib.error.HTTPError as error:
        try:
            detail = error.read(500).decode("utf-8", errors="replace")
        except (OSError, http.client.HTTPException) as interrupted:
            raise UnansweredError(
                f"{method} {route}: HTTP {error.code} response interrupted: {interrupted!r}"
            ) from None
        finally:
            error.close()
        hint = STATUS_HINTS.get(error.code, "redirect refused" if 300 <= error.code < 400 else "")
        if method.upper() not in {"GET", "HEAD", "OPTIONS"} and (error.code == 408 or error.code >= 500):
            raise UnansweredError(f"{method} {route}: HTTP {error.code}; remote mutation outcome is unknown") from None
        raise RefusedError(f"{method} {route}: HTTP {error.code} {detail} {hint}".rstrip(), error.code) from None
    # HTTPError subclasses URLError and is caught above. urlopen wraps only
    # connection setup in URLError; a connection dropped while the answer is
    # read surfaces as http.client.HTTPException (IncompleteRead,
    # RemoteDisconnected), ConnectionError or ssl.SSLEOFError (an OSError that
    # is neither), and is unanswered as well.
    except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException, ssl.SSLEOFError) as error:
        raise UnansweredError(f"{method} {route}: {error!r}") from None
    if len(answer) > RESULT_LIMIT:
        raise UnansweredError(f"{method} {route}: answer exceeds the {RESULT_LIMIT}-byte response limit")
    if raw:
        return answer
    try:
        return json.loads(answer) if answer else None
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise UnansweredError(f"{method} {route}: answer is not usable JSON") from None


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


OBSERVATION_SCHEMA = "qd-observation-v1"
ACCOUNT_API = "https://api.account.quandela.com"
# Every GET route of the retained cloud and account OpenAPI documents
# (docs/notes/quandela/api/) plus the platform routes Perceval reads, except
# routes that return token records (credentials), the QRNG routes (each read
# is a billed provider request that needs an approved case) and the session
# routes (logout, oauth). Job routes belong to collect.
OBSERVED_ROUTES = (
    ("cloud", "/", False),
    ("cloud", "/health", False),
    ("cloud", "/openapi.json", False),
    ("cloud", "/qt-openapi.json", False),
    ("cloud", "/api/platforms/public", False),
    ("cloud", "/api/platforms/public/explorer", False),
    ("cloud", "/api/jobs/availability", True),
    ("cloud", "/api/tokens/usage/report", True),
    ("account", "/", False),
    ("account", "/health", False),
    ("account", "/api/rss-feed", False),
)


def observed(host: str, route: str, auth: bool) -> dict[str, Any]:
    """One route's answer, scrubbed of FORBIDDEN_KEYS when it is JSON, or the refusal that answered it."""
    base = {"cloud": API, "account": ACCOUNT_API}[host]
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {token()}"
    entry: dict[str, Any] = {"host": base, "route": route, "auth": auth, "retrieved_utc": now()}
    try:
        with OPENER.open(urllib.request.Request(base + route, headers=headers), timeout=60) as response:
            answer = response.read(RESULT_LIMIT + 1)
            entry["http_status"] = response.status
            entry["content_type"] = response.headers.get("Content-Type")
    except urllib.error.HTTPError as error:
        error.close()
        return {**entry, "http_status": error.code, "refused": True}
    except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException, ssl.SSLEOFError) as error:
        return {**entry, "unanswered": repr(error)}
    if len(answer) > RESULT_LIMIT:
        return {**entry, "unanswered": f"answer exceeds {RESULT_LIMIT} bytes"}
    try:
        value = json.loads(answer)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # A non-JSON answer (the RSS feed, an HTML home page) is kept as text with its digest.
        return {**entry, "sha256": sha256_bytes(answer), "text": answer.decode("utf-8", errors="replace")}
    cleaned = scrub(value)
    return {**entry, "sha256": sha256_bytes(json.dumps(cleaned, sort_keys=True).encode()), "json": cleaned}


def observe(out: Path) -> None:
    """Write out/observation.json: every observed route, then every platform's processor record, all raw."""
    token()
    routes = [observed(*route) for route in OBSERVED_ROUTES]
    explorer = next(entry for entry in routes if entry["route"] == "/api/platforms/public/explorer")
    names = sorted(row["name"] for row in explorer.get("json") or [] if isinstance(row, dict) and "name" in row)
    for name in names:
        routes.append(observed("cloud", platform_route(name), True))
    record = {
        "schema": OBSERVATION_SCHEMA,
        "retrieved_utc": now(),
        "versions": versions(),
        "excluded": "token records, QRNG reads (billed), session routes; job routes are collect's",
        "routes": routes,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "observation.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    failed = [entry["route"] for entry in routes if "json" not in entry and "text" not in entry]
    print(f"{len(routes)} routes observed; unanswered or refused: {failed or 'none'}")


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
        "mcp.server.fastmcp.server",
        "mcp.server.stdio",
        "mcp.types",
        "pydantic",
    )
    modules = {name: ModuleType(name) for name in names}
    modules["mcp.server.fastmcp"].FastMCP = ToolRecorder  # type: ignore[attr-defined]
    modules["mcp.server.fastmcp.exceptions"].ToolError = RuntimeError  # type: ignore[attr-defined]
    modules["mcp.server.fastmcp.server"].Settings = MagicMock()  # type: ignore[attr-defined]
    modules["mcp.server.stdio"].stdio_server = MagicMock()  # type: ignore[attr-defined]
    modules["mcp.types"].ToolAnnotations = dict  # type: ignore[attr-defined]
    modules["mcp.types"].Tool = MagicMock()  # type: ignore[attr-defined]
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
CASES_SCHEMAS = ("qd-box-kite-cases-v1", "qd-belenos-mesh-cases-v1", "qd-bdsc-cases-v1", "qd-hypercomplex-cases-v1")
CIRCUIT_SCHEMA = "qd-circuit-v1"
TEMPLATE_CIRCUIT_SCHEMA = "qd-template-circuit-v1"
CIRCUIT_SCHEMAS = (CIRCUIT_SCHEMA, "qd-mesh-circuit-v1", TEMPLATE_CIRCUIT_SCHEMA)
# A case's processing policy: None leaves the server's default mitigations, an empty list disables them.
MITIGATION_POLICIES: tuple[None, list[str]] = (None, [])


def body_mitigations(body: Any) -> list[Any] | None:
    """The mitigation policy a job body requests: None when its payload omits the mitigations key, else the list.

    PayloadGenerator.from_computation writes the key at payload.mitigations
    only for a non-null policy, and the sent body serializes the list as a
    Perceval archive string, which deserialize decodes. A mitigations key at
    any other depth, or a value that decodes to anything but a list, is refused.
    """
    from perceval.serialization import deserialize
    from perceval.utils.constants import KEY_MITIGATIONS

    payload = body.get("payload") if isinstance(body, dict) else None
    if not isinstance(payload, dict):
        raise PlatformError("the job body carries no payload")
    elsewhere = {**body, "payload": {k: v for k, v in payload.items() if k != KEY_MITIGATIONS}}
    if KEY_MITIGATIONS in keys(elsewhere):
        raise PlatformError(f"the job body carries {KEY_MITIGATIONS} outside its payload")
    if KEY_MITIGATIONS not in payload:
        return None
    value = payload[KEY_MITIGATIONS]
    try:
        decoded = deserialize(value) if isinstance(value, str) else value
    except Exception as error:  # noqa: BLE001 -- deserialize raises ValueError, binascii.Error and others
        raise PlatformError(f"the job body's {KEY_MITIGATIONS} is no Perceval archive: {error}") from None
    if not isinstance(decoded, list):
        raise PlatformError(f"the job body's {KEY_MITIGATIONS} decodes to {type(decoded).__name__}, not a list")
    return decoded


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


def template_experiment(manifest: dict[str, Any], circuit: dict[str, Any]) -> tuple[Any, list[dict[str, Any]]]:
    """A fixed circuit of BS.Rx and PS components with one Perceval parameter per free angle, and its settings.

    circuit["ops"] lists ["BS", m, k] on modes (m, m + 1) with angle parameter xk (k null for a fixed pi), and
    ["PS", m, k] on mode m. Every setting binds its circuit_params, and Perceval's unitary must carry the source
    photon to the setting's column within 1e-9 before anything is sent.
    """
    import numpy
    import perceval as pcvl

    modes = circuit["modes"]
    chip = pcvl.Circuit(modes)
    parameters: dict[str, Any] = {}
    for kind, m, k in circuit["ops"]:
        if kind == "BS":
            angle = math.pi if k is None else parameters.setdefault(f"x{k}", pcvl.P(f"x{k}"))
            chip.add(m, pcvl.BS.Rx(theta=angle))
        elif kind == "PS":
            chip.add(m, pcvl.PS(parameters.setdefault(f"x{k}", pcvl.P(f"x{k}"))))
        else:
            raise PlatformError(f"unknown template op {kind!r}")
    if len(parameters) != circuit["parameters"]:
        raise PlatformError(f"the template binds {len(parameters)} parameters, not {circuit['parameters']}")
    source = circuit["input_state"].index(1)
    settings = manifest["settings"]
    for setting in settings:
        values = setting["circuit_params"]
        if sorted(values) != sorted(parameters):
            raise PlatformError(f"{setting['name']}: circuit_params do not name the template's parameters")
        for name, parameter in parameters.items():
            parameter.set_value(values[name])
        column = numpy.array([complex(re, im) for re, im in setting["column"]])
        deviation = float(numpy.max(numpy.abs(numpy.array(chip.compute_unitary())[:, source] - column)))
        if deviation > 1e-9:
            raise PlatformError(f"{setting['name']}: the template misses its column by {deviation:.2e}")
        if manifest.get("schema") == "qd-hypercomplex-cases-v1":
            expected = setting["operator"]
            matrix = numpy.asarray(expected["real"]) + 1j * numpy.asarray(expected["imaginary"])
            actual = numpy.asarray(chip.compute_unitary())
            if matrix.shape != actual.shape or not numpy.isfinite(matrix).all():
                raise PlatformError(f"{setting['name']}: full operator needs matching finite dimensions")
            deviation = float(numpy.max(numpy.abs(actual - matrix)))
            if deviation > 1e-9:
                raise PlatformError(f"{setting['name']}: the template misses its full operator by {deviation:.2e}")
        if iteration_form(manifest) != "single":
            for parameter in parameters.values():
                parameter.reset()
    built = pcvl.Experiment(chip)
    built.with_input(pcvl.BasicState(circuit["input_state"]))
    built.min_detected_photons_filter(manifest["min_detected_photons"])
    return built, settings


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
    if manifest.get("gate_form") == "template":
        template_settings = manifest.get("settings")
        if not isinstance(template_settings, list) or len(template_settings) != steps:
            raise PlatformError(f"{owner}: {steps} template iterations need {steps} settings")
        for setting in template_settings:
            if not isinstance(setting.get("circuit_params"), dict) or "column" not in setting:
                raise PlatformError(
                    f"{owner}/{setting.get('name')}: a template setting binds circuit_params and column"
                )
            seed_value(setting.get("compilation_seed", 0), f"{owner}/{setting.get('name')}")
        return "template"
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
    if (
        any(p[1:] != (0.0, 0.0, 0.0, 0.0) for k, _, p in live if k == "bs")
        or [p for k, _, p in live if k == "ps"] != spec["symbols"]
        or [[m, p[0]] for k, m, p in live if k == "bs"] != spec["couplers"]
    ):
        raise PlatformError("the live architecture differs from the case: regenerate the mesh case after recalibration")
    if "ops" in circuit:
        operations = [[kind.upper(), mode, index] for index, (kind, mode, _) in enumerate(live)]
        if operations != circuit["ops"]:
            raise PlatformError("the live architecture operation sequence differs from the case's native template")


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


# Frozen processor records whose server command sets stand in for a live record that omits specs.commands.
RETAINED_RECORDS = (
    ROOT / "docs/evidence/bdsc/inputs/receipt.json",
    ROOT / "docs/evidence/quandela/catalogue.json",
)


def same_worker_version(frozen: dict[str, Any], live: dict[str, Any]) -> bool:
    """Whether a frozen processor record and a live specs share the worker software that fixes Perceval commands.

    Perceval RPC serialization and Command schemas are governed by pcvl_version, pcvl-worker and
    perceval-quandela. Hardware driver patches (such as mosaiq-arcturus or universalchipworker) do not alter
    the client-server RPC Command parameter signatures.
    """
    if frozen.get("pcvl_version") != live.get("pcvl_version"):
        return False
    frozen_sw = frozen.get("software_versions", {})
    live_sw = live.get("software_versions", {})
    if frozen_sw == live_sw:
        return True
    rpc_keys = ("pcvl-worker", "perceval-quandela")
    return all(frozen_sw.get(k) == live_sw.get(k) and live_sw.get(k) is not None for k in rpc_keys)


def retained_commands(platform: str, specs: Any) -> tuple[Any, str] | None:
    """The serialized commands of a frozen record of this platform at the live record's software versions."""
    for path in RETAINED_RECORDS:
        record = json.loads(path.read_text(encoding="utf-8"))
        frozen = record.get("processors", {}).get(platform, {}).get("specs", {})
        if same_worker_version(frozen, specs) and isinstance(frozen.get("commands"), str):
            return frozen["commands"], f"{path.relative_to(ROOT)} retrieved {record.get('retrieved_utc')}"
    return None


def payload_version_basis(specs: Any, platform: str) -> str:
    """Install the server command set when the live record omits specs.commands, from a frozen record of the same
    worker; returns "declared", "restored from <record>" or "absent".

    RemoteComputer builds its command signatures once, at construction, from specs.commands, and without them from
    CommandFactory, whose sample_count lacks compilation_seed; RPCBasedCommunicationLayer.send builds a version-2
    body only when specs.commands is present, and PayloadUpdater's upgrade of a version-1 body drops an explicit
    mitigation list. A frozen record with the same pcvl_version and the same pcvl-worker and perceval-quandela
    versions names the same worker, so its serialized commands are the live server's; without one the commands
    stay absent.
    """
    if "commands" in specs:
        return "declared"
    found = retained_commands(platform, specs)
    if found is None:
        return "absent"
    from perceval.serialization import deserialize

    specs["commands"] = deserialize(found[0])
    return f"restored from {found[1]}"


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
    import perceval as pcvl

    layer = QuandelaCommunicationLayer(platform, token=token())
    # The command set must be in place before RemoteComputer reads it.
    basis = payload_version_basis(layer._specs, platform)
    computer = RemoteComputer(layer)
    policy = manifest.get("mitigations")
    if policy not in MITIGATION_POLICIES:
        raise PlatformError(f"{manifest['job']}: mitigations {policy!r} is neither null nor an empty list")
    computer.mitigations = None if policy is None else []
    form = iteration_form(manifest)
    mesh = manifest.get("gate_form") == "mesh"
    template = manifest.get("gate_form") == "template"
    if mesh:
        built, settings = mesh_experiment(manifest, circuit)
    elif template:
        built, settings = template_experiment(manifest, circuit)
    else:
        built, settings = experiment(manifest, circuit), []
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
    params = settings[0]["circuit_params"] if mesh or template else ({"phi": 0.0} if form == "phase" else None)
    if template:
        # Each template setting routes the photon to its own column, so each is estimated with its own parameters
        # and must fit its own iteration's shot budget.
        parts = [
            computer.estimate_required_shots(base, nsamples=per_samples, param_values=setting["circuit_params"])
            for setting in settings
        ]
        over = [s["name"] for s, part in zip(settings, parts, strict=True) if part is not None and part > per_shots]
        if over:
            raise PlatformError(f"{manifest['job']}: Perceval estimates more than {per_shots} shots for {over}")
        estimate = None if any(part is None for part in parts) else sum(parts)
    elif len({samples for samples, _ in budgets}) == 1:
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
            if template:
                # A template iteration binds its state's angles and phases on the job's fixed circuit.
                factory.add_iteration(
                    circuit_params=settings[k]["circuit_params"],
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
    try:
        computer.validate_single(computation)
    except (TypeError, ValueError) as error:
        raise PlatformError(f"{manifest['job']}: Perceval rejects the computation on {platform}: {error}") from None
    captured: dict[str, Any] = {}

    def record(cloud_data: dict[str, Any]) -> str:
        captured["body"] = cloud_data
        return "recorded"

    layer._rpc_handler.create_job = record
    prepared = computer.prepare_payload(computation)
    # send reads the cached specs without refetching, so the basis set here is the one the body is built under.
    # A refetch since construction replaces the specs, so the command set goes back in before send reads it.
    payload_version_basis(layer._specs, platform)
    layer.send(prepared)
    body: dict[str, Any] = {**captured["body"], "max_duration": manifest["max_duration"]}
    # RPCBasedCommunicationLayer.send downgrades the body to payload version 1 when the processor record lacks
    # specs.commands; a version-1 worker predates the mitigations key, so a policy case refuses that body.
    if "mitigations" in manifest and "computation" not in body.get("payload", {}):
        raise PlatformError(
            f"{manifest['job']}: Perceval built a version-1 body because the {platform} record lacks specs.commands"
        )
    if "mitigations" in manifest and body_mitigations(body) != policy:
        raise PlatformError(f"{manifest['job']}: the job body does not carry the mitigation policy {policy!r}")
    if token() in json.dumps(body):
        raise PlatformError("the job body carries the token")
    return {"body": body, "estimated_shots": estimate, "versions": found, "payload_version_basis": basis}


def require_token_capacity(manifest: dict[str, Any], counters: dict[str, Any]) -> None:
    """Admit the current case when the token has a queue slot; preserve older case policies."""
    if manifest.get("family") != "ascella_predecessor" or manifest.get("job") != "current-schema":
        if counters["num_concurrent_jobs"] or counters["num_jobs_in_queue"]:
            raise PlatformError(f"the token has a running or queued job: {counters}")
        return
    keys = ("max_concurrent_jobs", "max_jobs_in_queue", "num_concurrent_jobs", "num_jobs_in_queue")
    if any(type(counters.get(key)) is not int or counters[key] < 0 for key in keys):
        raise PlatformError("the current case requires non-negative integer token capacity counters")
    if counters["max_concurrent_jobs"] < 1 or counters["num_concurrent_jobs"] > counters["max_concurrent_jobs"]:
        raise PlatformError(f"the token running-job capacity is invalid: {counters}")
    if counters["max_jobs_in_queue"] < 1 or counters["num_jobs_in_queue"] >= counters["max_jobs_in_queue"]:
        raise PlatformError(f"the token has no available queue slot: {counters}")


def plan(
    case_dir: Path,
    platform: str,
    max_credits: float,
    expected_seconds: float,
    per_job_credits: float,
    admit_statuses: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Every check submit makes, read-only: digests, platform, complete cost ceiling, availability and the estimate.

    expected_seconds and per_job_credits are the written case's values: the
    offer's per-job price is visible only in the portal, so the case states
    it, and per-job credits plus the largest iteration's max_shots times the live
    price per shot must stay within max_credits. The platform must read
    available on its Explorer row and processor record; admit_statuses names
    further statuses a written case admits by name, such as running for a test
    of whether a busy platform accepts a job, and the plan records them.
    """
    statuses = ("available", *admit_statuses)
    for name, value in (
        ("--max-credits", max_credits),
        ("--expected-seconds", expected_seconds),
        ("--per-job-credits", per_job_credits),
    ):
        if not math.isfinite(value) or value < 0:
            raise PlatformError(f"{name} {value} is not a finite, non-negative number")
    manifest, circuit, cases_sha256 = load_case(case_dir)
    if "max_credits" in manifest:
        case_ceiling = manifest["max_credits"]
        if (
            isinstance(case_ceiling, bool)
            or not isinstance(case_ceiling, int | float)
            or not math.isfinite(case_ceiling)
            or case_ceiling <= 0
            or max_credits > case_ceiling
        ):
            raise PlatformError(f"--max-credits {max_credits} exceeds or invalidates the case ceiling {case_ceiling!r}")
    if platform not in manifest["platforms"]:
        raise PlatformError(f"cases.json admits {manifest['platforms']}, not {platform}")
    row = explorer_row(platform)
    if row["status"] not in statuses:
        raise PlatformError(f"{platform} is {row['status']}")
    if manifest["max_duration"] > row["max_duration"]:
        raise PlatformError(f"max_duration {manifest['max_duration']} exceeds the platform's {row['max_duration']}")
    if expected_seconds > manifest["max_duration"]:
        raise PlatformError(f"expected {expected_seconds} s exceed the case's max_duration {manifest['max_duration']}")
    # A job bills its largest iteration's max_shots (docs/runbooks/quandela-credit-optimization.md).
    billed_shots = max(shots for _, shots in iteration_budgets(manifest))
    ceiling = row["price_per_shot"] * billed_shots + per_job_credits
    if ceiling > max_credits:
        raise PlatformError(
            f"{billed_shots} billed shots and the per-job price cost up to {ceiling:g} credits, above {max_credits:g}"
        )
    processor = get(platform_route(platform))
    if processor.get("status") not in statuses:
        raise PlatformError(f"{platform} processor is {processor.get('status')}")
    perfs = scrub(processor.get("perfs") or {})
    if row["type"] == "qpu":
        message = hom_warning(platform, perfs, block_photons(circuit), case_dir.name)
        if message is not None:
            print(message, file=sys.stderr)
    if manifest.get("gate_form") == "mesh" or "architecture" in circuit:
        live_mesh(processor, circuit, platform)
    if "seeded_from" in manifest:
        live_architecture(processor, platform)
    counters = availability()
    require_token_capacity(manifest, counters)
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
        "estimated_credits": row["price_per_shot"] * min(billed_shots, estimate) + per_job_credits,
        "max_credits": max_credits,
        "body": built["body"],
        "body_sha256": sha256_bytes(json.dumps(built["body"], sort_keys=True).encode()),
        "admitted_statuses": list(statuses),
        "status_at_plan": {"explorer": row["status"], "processor": processor.get("status")},
        "versions": built["versions"],
        "payload_version_basis": built["payload_version_basis"],
    }


def case_path(text: str) -> Path:
    """The case directory a repository-relative or absolute path names, which must lie under results/quandela/.

    The path resolves symbolic links before the check, so a link out of the
    tree is refused with the same message as a path outside it.
    """
    allowed = (ROOT / "results/quandela").resolve()
    path = (ROOT / text).resolve()
    if path == allowed or allowed not in path.parents:
        raise PlatformError(f"{text!r} is outside results/quandela/")
    if not (path / "cases.json").is_file():
        raise PlatformError(f"{text!r} holds no cases.json")
    return path


def plan_summary(planned: dict[str, Any]) -> dict[str, Any]:
    """The facts of a plan result that decide a submission, without the job body.

    The body's payload carries a "computation" entry only in payload version 2
    (RPCBasedCommunicationLayer.send); version 1 keeps "command". The
    "mitigations" key is the policy the body requests (body_mitigations).
    """
    body = planned["body"]
    payload_part = body.get("payload") if isinstance(body, dict) else None
    if not isinstance(payload_part, dict):
        raise PlatformError("the planned job body carries no payload")
    return {
        **{key: value for key, value in planned.items() if key != "body"},
        "payload_version": 2 if "computation" in payload_part else 1,
        "mitigations_key": "mitigations" in payload_part,
        "mitigations": body_mitigations(body),
        "submitted": False,
    }


def job_billing(data: dict[str, Any], row: dict[str, Any], per_job_credits: float) -> dict[str, Any]:
    """The credits one job's data bills under the measured rule; the cloud reports no per-job charge.

    The rule (docs/runbooks/quandela-credit-optimization.md) is the per-job
    price plus the platform's price per shot times the billed shots: the
    shots used by a one-computation job, the largest iteration's max_shots by
    an iterated one, which the job data does not split out. charge_used
    prices the shots the job data reports and charge_ceiling prices the
    payload's total max_shots; the charge lies between them for an iterated
    job and equals charge_used for a single one. A job canceled before its
    start time ran nothing and bills nothing.
    """
    if not math.isfinite(per_job_credits) or per_job_credits < 0:
        raise PlatformError(f"per_job_credits {per_job_credits} is not a finite, non-negative number")
    price = row["price_per_shot"]
    shots = int(data.get("shots") or 0)
    payload_part = data.get("payload")
    cap = payload_part.get("max_shots") if isinstance(payload_part, dict) else None
    ran = not (
        data.get("status") == "canceled"
        and data.get("start_time") is None
        and not shots
        and data.get("duration") is None
    )
    # A failed job that ran no shots may bill nothing (qpu:ascella job 6fa19f42, results/quandela/runs/
    # ascella-native-input-map-recheck: one job, zero credits) or the per-job price (retained simulator
    # failures), and its job data does not say which, so its used charge is unknown.
    unknown = ran and data.get("status") in ("error", "failed") and not shots
    out: dict[str, Any] = {
        "job_id": data.get("job_id"),
        "platform": data.get("platform_name"),
        "status": data.get("status"),
        "shots": shots,
        "max_shots": cap,
        "duration": data.get("duration"),
        "price_per_shot": price,
        "per_job_credits": per_job_credits,
        "basis": (
            "a failed job without shots bills either nothing or the per-job price; the job data does not say which"
            if unknown
            else "billing rule applied to job data; the cloud reports no per-job charge"
        ),
        "charge_used": (round(per_job_credits + price * shots, 6) if ran else 0.0) if not unknown else None,
        "charge_ceiling": round(per_job_credits + price * cap, 6) if ran and isinstance(cap, int) else None,
    }
    return out


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
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def acquisition_sources(manifest: dict[str, Any]) -> dict[str, str]:
    """Verify every declared analyzer dependency before preparing or sending a reviewed case."""
    expected = manifest.get("analysis_sources")
    required = {
        "scripts/qd_platform.py",
        "scripts/ascella_predecessor_case.py",
        "scripts/ascella_predecessor_analysis.py",
        "scripts/ascella_experiment_analysis.py",
        "scripts/experiment_analysis.py",
        "gororoba_quantum/parallel.py",
    }
    if manifest.get("family") == "ascella_target_slot_drift":
        required |= {"scripts/ascella_target_slot_drift.py", "scripts/ascella_target_slot_drift_analysis.py"}
    if not isinstance(expected, dict) or set(expected) != required:
        raise PlatformError("a reviewed acquisition requires complete constructor/analyzer source identities")
    registered = manifest.get("preregistered", {})
    if not isinstance(registered, dict):
        raise PlatformError("reviewed acquisition preregistration must be an object")
    additional = registered.get("current_case_sources")
    if manifest.get("job") == "current-schema":
        names = {"scripts/ascella_predecessor_current_case.py", "scripts/ascella_predecessor_current_analysis.py"}
        if not isinstance(additional, dict) or set(additional) != names:
            raise PlatformError("the current case requires its builder and analyzer identities")
    elif additional is not None:
        raise PlatformError("current case sources require the current-schema job")
    combined = {**expected, **(additional or {})}
    for name, checksum in combined.items():
        if not isinstance(name, str) or not isinstance(checksum, str):
            raise PlatformError("invalid reviewed source identity")
        path = (ROOT / name).resolve()
        if Path(name).is_absolute() or not path.is_relative_to(ROOT.resolve()):
            raise PlatformError("reviewed source escapes the repository")
        if sha256_bytes(path.read_bytes()) != checksum:
            raise PlatformError(f"reviewed source changed: {name}")
    return combined


def requires_acquisition_review(manifest: dict[str, Any]) -> bool:
    """Recognize the registered diagnostic by family, design or analyzer identity."""
    sources = manifest.get("analysis_sources")
    return (
        manifest.get("family") in {"ascella_predecessor", "ascella_target_slot_drift"}
        or manifest.get("design") == "docs/design/ascella-predecessor-intervention.md"
        or isinstance(sources, dict)
        and "scripts/ascella_predecessor_analysis.py" in sources
    )


def acquisition_policy(
    platform: str, max_credits: float, expected_seconds: float, per_job_credits: float, admit_statuses: tuple[str, ...]
) -> dict[str, Any]:
    return {
        "platform": platform,
        "max_credits": max_credits,
        "expected_seconds": expected_seconds,
        "per_job_credits": per_job_credits,
        "admit_statuses": list(admit_statuses),
    }


def prepare_acquisition_review(
    case_dir: Path,
    platform: str,
    max_credits: float,
    expected_seconds: float,
    per_job_credits: float,
    admit_statuses: tuple[str, ...],
    destination: Path,
) -> dict[str, Any]:
    """Retain the complete submitted-body candidate; perform provider reads only."""
    manifest, _, case_sha = load_case(case_dir)
    sources = acquisition_sources(manifest)
    checked = plan(case_dir, platform, max_credits, expected_seconds, per_job_credits, admit_statuses)
    if checked["cases_sha256"] != case_sha:
        raise PlatformError("the case changed while preparing the review")
    acquisition_sources(manifest)
    packet = {
        "schema": "qd-reviewed-acquisition-v1",
        "prepared_utc": now(),
        "cases_sha256": case_sha,
        "circuit_sha256": manifest["circuit"]["sha256"],
        "analysis_sources": sources,
        "policy": acquisition_policy(platform, max_credits, expected_seconds, per_job_credits, admit_statuses),
        "binding": {
            key: checked[key]
            for key in (
                "body",
                "body_sha256",
                "versions",
                "payload_version_basis",
                "estimated_shots",
                "admitted_statuses",
            )
        },
        "provider_observation": {key: value for key, value in checked.items() if key != "body"},
        "scope": "descriptive target-slot diagnostic; physical predecessor attribution unavailable",
        "authorization": "pending-owner-approval",
        "process_id_policy": "pin reviewed Perceval transport process UUID; compare the complete posted body",
    }
    write_json(destination, packet, exclusive=True)
    return packet


def verify_acquisition_review(
    case_dir: Path, checked: dict[str, Any], packet_path: Path, expected_sha256: str, policy: dict[str, Any]
) -> dict[str, Any]:
    """Bind fresh admission and the exact POST body to an externally retained review digest."""
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise PlatformError("a reviewed acquisition requires an external SHA-256 anchor")
    with packet_path.open("rb") as stream:
        raw = stream.read(20 * 1024 * 1024 + 1)
    if len(raw) > 20 * 1024 * 1024 or sha256_bytes(raw) != expected_sha256:
        raise PlatformError("reviewed acquisition packet differs from its external anchor")
    packet = json.loads(raw)
    if not isinstance(packet, dict) or packet.get("schema") != "qd-reviewed-acquisition-v1":
        raise PlatformError("unsupported reviewed acquisition packet")
    manifest, _, case_sha = load_case(case_dir)
    sources = acquisition_sources(manifest)
    circuit_sha = sha256_bytes((case_dir / manifest["circuit"]["file"]).read_bytes())
    if (
        packet.get("policy") != policy
        or packet.get("cases_sha256") != case_sha
        or checked.get("cases_sha256") != case_sha
        or packet.get("analysis_sources") != sources
        or packet.get("circuit_sha256") != circuit_sha
        or circuit_sha != manifest["circuit"]["sha256"]
    ):
        raise PlatformError("the fresh acquisition changes reviewed policy, case, circuit or sources")
    binding = packet.get("binding")
    if not isinstance(binding, dict) or not isinstance(binding.get("body"), dict):
        raise PlatformError("reviewed acquisition body is absent")
    for key in ("versions", "payload_version_basis", "estimated_shots", "admitted_statuses"):
        if checked.get(key) != binding.get(key):
            raise PlatformError(f"the fresh acquisition changes reviewed {key}")
    body = checked.get("body")
    if not isinstance(body, dict):
        raise PlatformError("the fresh acquisition body is absent")
    try:
        uuid.UUID(body["process_id"])
        uuid.UUID(binding["body"]["process_id"])
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        raise PlatformError("Perceval transport process identity must be a UUID") from error
    # Perceval payload_generator gives process_id a uuid4 at module load. Pin
    # that transport identifier so the actual POST remains byte-bound across processes.
    body["process_id"] = binding["body"]["process_id"]
    body_sha = sha256_bytes(json.dumps(body, sort_keys=True).encode())
    if body != binding["body"] or body_sha != binding.get("body_sha256"):
        raise PlatformError("the fresh acquisition changes the reviewed POST body")
    checked["body_sha256"] = body_sha
    return packet


def submit(
    case_dir: Path,
    platform: str,
    approval: str,
    max_credits: float,
    expected_seconds: float,
    per_job_credits: float,
    admit_statuses: tuple[str, ...] = (),
    verify: Callable[[dict[str, Any]], None] | None = None,
    reviewed_packet: Path | None = None,
    reviewed_sha256: str | None = None,
) -> dict[str, Any]:
    """Send one approved case as one job while holding the token's submit lock beside the token file.

    verify receives the plan whose body is posted, before the checkpoint is
    written, so a caller's own stop conditions bind the request actually sent;
    a PlatformError from it refuses the submission with nothing written.
    """
    if not approval.strip():
        raise PlatformError("a nonempty approval is required")
    manifest, _, gated_case_sha256 = load_case(case_dir)
    if (reviewed_packet is None) != (reviewed_sha256 is None):
        raise PlatformError("reviewed packet and digest must be supplied together")
    if requires_acquisition_review(manifest) and reviewed_packet is None:
        raise PlatformError("Ascella target-slot acquisition requires an externally anchored reviewed packet")
    if manifest.get("acquisition_admission", "ready") != "ready":
        raise PlatformError(f"{manifest['job']}: acquisition admission is {manifest['acquisition_admission']}")
    if manifest.get("draft"):
        raise PlatformError(f"{case_dir} is a draft without frozen seeds and order; rebuild it from its draw")
    lock = Path(os.environ.get(TOKEN_ENV, "")).with_name("submit.lock")
    with open(lock, "a", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        state_path = case_dir / "submission-state.json"
        if any((case_dir / name).exists() for name in ("submission.json", "submission-state.json", "job-body.json")):
            raise PlatformError(f"{case_dir} was submitted or holds an interrupted submission; never resubmit it")
        checked = plan(case_dir, platform, max_credits, expected_seconds, per_job_credits, admit_statuses)
        if checked.get("cases_sha256") != gated_case_sha256:
            raise PlatformError("the acquisition case changed between admission and planning")
        if verify is not None:
            verify(checked)
        reviewed = None
        if reviewed_packet is not None and reviewed_sha256 is not None:
            reviewed = verify_acquisition_review(
                case_dir,
                checked,
                reviewed_packet,
                reviewed_sha256,
                acquisition_policy(platform, max_credits, expected_seconds, per_job_credits, admit_statuses),
            )
        usage_before = usage_rows(get("/api/tokens/usage/report"))
        if reviewed_packet is not None and reviewed_sha256 is not None:
            reviewed = verify_acquisition_review(
                case_dir,
                checked,
                reviewed_packet,
                reviewed_sha256,
                acquisition_policy(platform, max_credits, expected_seconds, per_job_credits, admit_statuses),
            )
        receipt = {
            "schema": SUBMISSION_SCHEMA,
            "approval": approval,
            "usage_before": usage_before,
            **{key: value for key, value in checked.items() if key != "body"},
        }
        if reviewed is not None:
            attempts = lock.parent / "reviewed-acquisition-attempts"
            attempts.mkdir(mode=0o700, exist_ok=True)
            parent_fd = os.open(attempts.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(parent_fd)
            finally:
                os.close(parent_fd)
            try:
                write_json(
                    attempts / f"{reviewed['cases_sha256']}.json",
                    {
                        "cases_sha256": reviewed["cases_sha256"],
                        "reviewed_packet_sha256": reviewed_sha256,
                        "body_sha256": checked["body_sha256"],
                        "consumed_utc": now(),
                    },
                    exclusive=True,
                )
            except FileExistsError:
                raise PlatformError("the reviewed case-wide acquisition attempt is already consumed") from None
            receipt["reviewed_packet_sha256"] = reviewed_sha256
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
        if not stream.eof or stream.unused_data:
            raise PlatformError("a zipped result must contain exactly one complete compressed stream")
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


def expected_iterations(manifest: dict[str, Any]) -> int | None:
    """The iterations an iterated case sends, or None for a one-computation case."""
    return None if iteration_form(manifest) == "single" else int(manifest.get("iterations", 1))


# Count-less partial collections retained before results.json carried failed iterations; their job ids are bound to
# submission.json, and every later collection must carry the iterations field.
ITERATIONS_PREDATING_JOBS = frozenset(
    {
        "03dd195b-b429-4ef1-be96-98005617343c",
        "90712931-1b5a-4c14-bdd0-95e01ac02292",
        "c2edef5d-5e6f-4161-83fc-aadd024171fb",
    }
)


def predates(retained: dict[str, Any], summary: dict[str, Any], key: str) -> bool:
    """Whether a retained collection omits summary[key] because it was written before the field existed.

    shots_used is derived from the raw bytes, so a record without it takes it
    from the raw result. Only the count-less partial records of
    ITERATIONS_PREDATING_JOBS may omit their failed iteration entries.
    """
    if key in retained or key not in summary:
        return False
    if key == "shots_used":
        return True
    return (
        key == "iterations"
        and summary.get("partial") is True
        and not summary.get("counts")
        and retained.get("job_id") in ITERATIONS_PREDATING_JOBS
    )


def patient(read: Callable[[], Any], job: str, what: str, deadline: float, poll: float) -> Any:
    """read() repeated after each transient failure until the deadline; any other failure raises at once.

    Every repeated call is a GET of the existing job, so a repeat never creates a job.
    """
    while True:
        try:
            return read()
        except PlatformError as error:
            if not transient(error) or time.monotonic() > deadline:
                raise
            print(f"job {job}: {what} read failed, retrying: {str(error)[:160]}", file=sys.stderr)
            time.sleep(poll)


def collect(case_dir: Path, poll: float, timeout: float) -> dict[str, Any]:
    """Wait for the job, then retain its status, result and job data; the raw result keeps its bytes."""
    submission = json.loads((case_dir / "submission.json").read_text(encoding="utf-8"))
    manifest, _, cases_sha256 = load_case(case_dir)
    if submission.get("schema") != SUBMISSION_SCHEMA or submission["cases_sha256"] != cases_sha256:
        raise PlatformError("cases.json differs from the submission receipt")
    job = submission["job_id"]
    expected = expected_iterations(manifest)
    deadline = time.monotonic() + timeout
    while True:
        status: dict[str, Any] = patient(
            lambda: request("GET", job_route(job, "status")), job, "status", deadline, poll
        )
        if status.get("status") in TERMINAL:
            break
        if time.monotonic() > deadline:
            raise PlatformError(f"job {job} is still {status.get('status')}")
        time.sleep(poll)
    raw_dir = case_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    retained_path = case_dir / "results.json"
    # An error or canceled job can still carry partial results. Only HTTP 404,
    # the cloud API's "Not found" answer of /api/jobs/{job_id}/result, records
    # the result as absent; any other refusal leaves the run recollectable.
    result_bytes: bytes | None
    absent: str | None = None
    try:
        result_bytes = patient(
            lambda: request("GET", job_route(job, "result"), raw=True), job, "result", deadline, poll
        )
    except RefusedError as error:
        if status["status"] == "completed" or error.code != 404:
            raise
        # An earlier collection already retained an answer, so a refusal now is a changed answer.
        if (raw_dir / "result.json").exists():
            raise PlatformError(f"job {job}: raw/result.json is retained but /result now answers {error}") from None
        absent, result_bytes = str(error), None
    # A first collection keeps the answer before parsing it or reading job data
    # and usage, so a later failure leaves the scientific bytes on disk. A
    # recollection writes only after its comparison below, so a result that
    # appears after a recorded absence changes nothing on disk.
    if result_bytes is not None and not retained_path.exists():
        retain_bytes(raw_dir / "result.json", result_bytes)
    collected: dict[str, Any] = {
        "schema": COLLECTION_SCHEMA,
        "collected_utc": now(),
        "job_id": job,
        "status": scrub(status),
        "data": scrub(patient(lambda: request("GET", job_route(job, "data")), job, "data", deadline, poll)),
    }
    # charged() falls back to the billing rule when usage_after is missing, so
    # an unreadable usage report is recorded and the collection proceeds.
    try:
        collected["usage_after"] = usage_rows(
            patient(lambda: get("/api/tokens/usage/report"), job, "usage", deadline, poll)
        )
    except PlatformError as error:
        collected["usage_absent"] = str(error)
    if result_bytes is None:
        collected["result_absent"] = absent
    else:
        collected["result_sha256"] = sha256_bytes(result_bytes)
        collected.update(
            result_summary(result_bytes, job, status, complete=status["status"] == "completed", expected=expected)
        )
    if retained_path.exists():
        retained = json.loads(retained_path.read_text(encoding="utf-8"))
        moving = ("collected_utc", "usage_after", "usage_absent")
        if {k: v for k, v in retained.items() if k not in moving} != {
            k: v for k, v in collected.items() if k not in moving and not predates(retained, collected, k)
        }:
            raise PlatformError(f"{retained_path} differs from the recollection; nothing was rewritten")
        if result_bytes is not None:
            retain_bytes(raw_dir / "result.json", result_bytes)
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


def result_summary(
    result_bytes: bytes, job: str, status: dict[str, Any], complete: bool = True, expected: int | None = None
) -> dict[str, Any]:
    """The counts and scalar fields of a raw /result answer, parsed without Perceval and bound to its job.

    The answer's job_id must be the submitted job and its shots must agree
    with any non-null status shots. A partial result (error or canceled job)
    without serialized counts is summarized as partial with no counts. A
    partial iterated result keeps every entry at its position: a counted
    iteration as a completed job would, an iteration answered with the
    worker's error text as "error", and an unreadable entry as "malformed".
    When the case expects more iterations than the answer holds, one "missing"
    entry per absent iteration follows the answered ones; the answer names no
    position, so a missing entry carries no attribution. None of these carries
    counts, so a failed iteration never reads as a counted one.
    """
    answer = json.loads(result_bytes)
    if not isinstance(answer, dict) or answer.get("job_id") != job:
        raise PlatformError(
            f"the result answers job {answer.get('job_id') if isinstance(answer, dict) else None}, not {job}"
        )
    shots = answer.get("shots")
    # A job that ended without completing (error, canceled) may answer shots null: no count, kept as null.
    if not (shots is None and not complete) and (not isinstance(shots, int) or shots < 0):
        raise PlatformError(f"the result of job {job} carries shots {shots!r}")
    if status.get("shots") is not None and status["shots"] != shots:
        raise PlatformError(f"job {job}: status shots {status['shots']} differ from the result's {shots}")
    serialized = answer.get("results")
    inner = json.loads(serialized) if isinstance(serialized, str) and serialized else None
    iterations: list[dict[str, Any]] | None = None
    if isinstance(inner, dict) and isinstance(inner.get("results_list"), list):
        # An iterated job answers one entry per iteration; counts add up, and
        # each entry keeps its own counts and its iteration's scalar fields.
        iterations = []
        merged: dict[str, int] = {}
        for entry in inner["results_list"]:
            if not isinstance(entry, dict) or not isinstance(entry.get("results"), str):
                if complete:
                    raise PlatformError(f"job {job}: an iteration result carries no serialized counts")
                malformed = {"malformed": type(entry.get("results") if isinstance(entry, dict) else entry).__name__}
                if isinstance(entry, dict) and isinstance(entry.get("iteration"), dict):
                    malformed["iteration"] = scalar_tree(entry["iteration"])
                iterations.append(malformed)
                continue
            iteration = entry.get("iteration") if isinstance(entry.get("iteration"), dict) else {}
            fields = {k: v for k, v in entry.items() if k not in ("results", "iteration")}
            # A job that ended without completing can answer an iteration with the worker's error text.
            if not complete and not entry["results"].startswith(":PCVL:"):
                iterations.append(
                    {
                        "iteration": scalar_tree(iteration),
                        "error": entry["results"][:2000],
                        "result_fields": scalar_tree(fields),
                    }
                )
                continue
            part = parse_counts(entry["results"])
            for state, n in part.items():
                merged[state] = merged.get(state, 0) + n
            iterations.append(
                {
                    "iteration": scalar_tree(iteration),
                    "counts": part,
                    "samples": sum(part.values()),
                    "result_fields": scalar_tree(fields),
                }
            )
        if expected is not None and complete and len(iterations) != expected:
            raise PlatformError(f"job {job}: a completed job answers {len(iterations)} iterations of {expected}")
        if expected is not None and not complete:
            if len(iterations) > expected:
                raise PlatformError(f"job {job}: {len(iterations)} iterations answer a case of {expected}")
            iterations.extend({"missing": True} for _ in range(expected - len(iterations)))
        inner = {**{k: v for k, v in inner.items() if k != "results_list"}, "results": None}
        counts = merged
    elif not isinstance(inner, dict) or not isinstance(inner.get("results"), str):
        if complete:
            raise PlatformError("the result carries no serialized counts")
        return {"shots": shots, "partial": True, "counts": {}, "samples": 0, "result_fields": {}}
    else:
        if not complete and not inner["results"].startswith(":PCVL:"):
            return {
                "shots": shots,
                "partial": True,
                "counts": {},
                "samples": 0,
                "error": inner["results"][:2000],
                "result_fields": scalar_tree({key: value for key, value in inner.items() if key != "results"}),
            }
        counts = parse_counts(inner["results"])
    # An iterated answer's top-level shots is one iteration's max_shots; each
    # entry reports the shots it used, and their sum is what the job consumed.
    used = shots
    failed = False
    if iterations is not None:
        counted = [entry for entry in iterations if "counts" in entry]
        per = [entry["result_fields"].get("nb_shots_used") for entry in counted]
        if not all(isinstance(n, int) and n >= 0 for n in per):
            raise PlatformError(f"job {job}: an iteration reports no nb_shots_used")
        used = sum(per)
        for entry, n in zip(counted, per, strict=True):
            if entry["samples"] > n:
                raise PlatformError(f"job {job}: an iteration counts {entry['samples']} samples from {n} shots")
        # The shots a failed iteration consumed are unknown unless it reports them,
        # so shots_used is left out and the top-level shots stand in for the charge.
        failed = len(counted) < len(iterations)
        spent = [entry.get("result_fields", {}).get("nb_shots_used") for entry in iterations]
        if failed and all(isinstance(n, int) and n >= 0 for n in spent):
            used, failed = sum(spent), False
    # A partial job may answer shots null, which bounds nothing.
    if used is not None and sum(counts.values()) > used:
        raise PlatformError(f"job {job}: {sum(counts.values())} samples exceed its {used} shots")
    scalars = {k: v for k, v in inner.items() if k != "results" and isinstance(v, int | float | str | None)}
    summary: dict[str, Any] = {
        "shots": shots,
        **({} if failed else {"shots_used": used}),
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
    returned = collected.get("data", {}).get("payload")
    if (
        manifest.get("schema") == "qd-hypercomplex-cases-v1"
        and "logical_modes" in manifest
        and collected.get("status", {}).get("status") == "completed"
        and not isinstance(returned, dict)
    ):
        raise PlatformError(f"{owner}: completed full-output acquisition lacks its returned payload")
    if isinstance(returned, dict):
        echoed = dict(returned)
        # The worker adds its version to the payload; the sent fields retain
        # their exact JSON structures, including compilation parameters.
        if "pcvl_version" not in body["payload"]:
            echoed.pop("pcvl_version", None)
        if echoed != body["payload"]:
            raise PlatformError(f"{owner}: returned payload differs from job-body.json")
    status = collected["status"]["status"]
    if status not in TERMINAL:
        raise PlatformError(f"{owner}: job status {status} is not terminal")
    raw = directory / "raw" / "result.json"
    shots = 0
    if status == "completed" or raw.exists():
        if not raw.is_file() or sha256_bytes(raw.read_bytes()) != collected.get("result_sha256"):
            raise PlatformError(f"{owner}: raw/result.json differs from its recorded sha256")
        summary = result_summary(
            raw.read_bytes(),
            submission["job_id"],
            collected["status"],
            status == "completed",
            expected_iterations(manifest),
        )

        if any(collected.get(key) != value for key, value in summary.items() if not predates(collected, summary, key)):
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
        "charge": charged(submission, collected, shots, manifest, interim_usage(directory, submission, collected)),
        "detail": f"job {submission['job_id']}, {collected.get('samples', 0)} samples, {shots} shots",
    }


def usage_jobs(report: Any) -> int | None:
    """nb_jobs summed over every platform row of a token usage report."""
    if not isinstance(report, list):
        return None
    return sum(
        int(row.get("nb_jobs") or 0)
        for token_row in report
        if isinstance(token_row, dict)
        for row in token_row.get("usage", [])
        if isinstance(row, dict)
    )


def interim_usage(directory: Path, submission: dict[str, Any], collected: dict[str, Any]) -> list[Any]:
    """usage_before reports of sibling runs submitted after this run and before its collection, in time order."""
    start, end = str(submission.get("submitted_utc", "")), str(collected.get("collected_utc", ""))
    reads = []
    for other in run_directories(directory.parent):
        path = other / "submission.json"
        if other == directory or not path.is_file():
            continue
        sibling = json.loads(path.read_text(encoding="utf-8"))
        when = str(sibling.get("submitted_utc", ""))
        if start < when < end:
            reads.append((when, sibling.get("usage_before")))
    return [report for _, report in sorted(reads, key=lambda item: item[0])]


def usage_total(report: Any) -> float | None:
    """credits plus free_credits over every platform row of a token usage report."""
    if not isinstance(report, list):
        return None
    total = 0.0
    for token_row in report:
        for row in token_row.get("usage", []) if isinstance(token_row, dict) else []:
            total += float(row.get("credits") or 0) + float(row.get("free_credits") or 0)
    return total


def charged(
    submission: dict[str, Any],
    collected: dict[str, Any],
    shots: int,
    manifest: dict[str, Any] | None = None,
    interim: list[Any] | None = None,
) -> float:
    """The credits a run consumed: the first later usage report holding exactly one more job, minus the one before.

    The later report is the earliest of interim (sibling runs' usage_before
    reports taken between this submission and its collection) and the
    collection's usage_after whose job counter exceeds the counter before
    submission; the difference is this job's charge only when that counter
    advanced by exactly one. The usage report counts the calendar month, so a
    job submitted and collected in different months, a negative difference, a
    window holding another job or a receipt without both reports falls back to
    the billing rule: the recorded per-job price plus the price per shot times
    the shots used by a one-computation job, or times the largest iteration's
    max_shots of an iterated one.
    """
    first = submission.get("usage_before")
    before, jobs_before = usage_total(first), usage_jobs(first)
    later = next(
        (
            report
            for report in [*(interim or []), collected.get("usage_after")]
            if jobs_before is not None and (usage_jobs(report) or 0) > jobs_before
        ),
        None,
    )
    after, jobs_after = usage_total(later), usage_jobs(later)
    same_month = str(submission.get("submitted_utc", ""))[:7] == str(collected.get("collected_utc", ""))[:7]
    one_job = jobs_before is not None and jobs_after == jobs_before + 1
    if before is not None and after is not None and same_month and after >= before and one_job:
        return round(after - before, 6)
    # A job canceled before its start time ran nothing and is charged nothing (bdsc-acceptance-diagnostics.md).
    # Shots read from a returned result (shots), and a start time or duration in the job data, count as
    # execution even when the status omits them.
    status = collected.get("status") or {}
    data = collected.get("data") or {}
    if (
        status.get("status") == "canceled"
        and status.get("start_time") is None
        and not status.get("shots")
        and not shots
        and data.get("start_time") is None
        and data.get("duration") is None
    ):
        return 0.0
    price = submission["platform_at_plan"]["price_per_shot"]
    billed = shots
    if manifest is not None and iteration_form(manifest) != "single":
        billed = max(budget for _, budget in iteration_budgets(manifest))
    return round(float(submission.get("per_job_credits", 0)) + billed * price, 6)


def run_directories(runs: Path = RUNS) -> list[Path]:
    return sorted(path for path in runs.iterdir() if path.is_dir()) if runs.is_dir() else []


def zipped(text: str) -> str:
    return ":PCVL:zip:" + base64.b64encode(zlib.compress(text.encode("ascii"))).decode("ascii")


def charge_self_test() -> None:
    """charged() takes the usage delta within one calendar month and the recorded price across a reset."""

    def report(credits: float, jobs: int = 2) -> list[dict[str, Any]]:
        return [{"usage": [{"credits": 0.0, "free_credits": credits, "nb_jobs": jobs, "platform_name": "qpu:belenos"}]}]

    submission = {
        "submitted_utc": "2026-10-31T23:59:00+00:00",
        "usage_before": report(12.0, 1),
        "per_job_credits": 1.0,
        "platform_at_plan": {"price_per_shot": 1e-06},
    }
    cases: tuple[tuple[str, Any, list[Any], float], ...] = (
        ("2026-10-31T23:59:30+00:00", report(13.02), [], 1.02),
        ("2026-11-01T00:00:30+00:00", report(1.02), [], 1.01),
        ("2026-10-31T23:59:30+00:00", report(11.0), [], 1.01),
        # A later job ran inside the window: the delta over two jobs is not this job's charge.
        ("2026-10-31T23:59:30+00:00", report(14.0, 3), [], 1.01),
        # A sibling's pre-submission read holding one more job bounds this job's charge, here none.
        ("2026-10-31T23:59:30+00:00", report(13.0, 3), [report(12.0, 2)], 0.0),
    )
    for collected_utc, after, interim, want in cases:
        got = charged(submission, {"collected_utc": collected_utc, "usage_after": after}, 10000, None, interim)
        if got != want:
            raise SystemExit(f"self-test: charged() read {got} for a collection at {collected_utc}, not {want}")
    # An iterated job across a month boundary bills its largest iteration's max_shots, not the shots it used.
    iterated = {"job": "self-test", "gate_form": "mesh", "iterations": 12, "max_samples": 3600000, "max_shots": 7200000}
    got = charged(submission, {"collected_utc": cases[1][0], "usage_after": cases[1][1]}, 3600000, iterated)
    if got != 1.6:
        raise SystemExit(f"self-test: charged() read {got} for an iterated job across a reset, not 1.6")
    # A job canceled before it started costs nothing even when another job shares its usage window; one
    # canceled after its start keeps the billing rule.
    for start, want in ((None, 0.0), (1792667218.0, 1.01)):
        status = {"status": "canceled", "start_time": start, "shots": 0}
        collected = {"collected_utc": cases[3][0], "usage_after": cases[3][1], "status": status}
        got = charged(submission, collected, 0 if start is None else 10000)
        if got != want:
            raise SystemExit(f"self-test: charged() read {got} for a job canceled with start {start}, not {want}")
    # A canceled job whose status omits start and shots but whose result returned shots keeps the billing rule.
    status = {"status": "canceled", "start_time": None}
    got = charged(submission, {"collected_utc": cases[3][0], "usage_after": cases[3][1], "status": status}, 10000)
    if got != 1.01:
        raise SystemExit(f"self-test: charged() read {got} for a canceled job that returned 10000 shots, not 1.01")
    # A canceled status without a start time keeps the billing rule when the job data records one.
    started = {"start_time": "2026-10-22T17:10:00+00:00", "duration": 4.0}
    collected = {"collected_utc": cases[3][0], "usage_after": cases[3][1], "status": status, "data": started}
    got = charged(submission, collected, 0)
    if got != 1.0:
        raise SystemExit(f"self-test: charged() read {got} for a canceled job whose data records a start, not 1.0")


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
    """A record of the frozen worker without commands gets the frozen command set, whose sample_count takes
    compilation_seed; another worker keeps none; a version-1 round trip loses an empty mitigation list."""
    import perceval as pcvl
    from perceval.runtime.payload_generator import PayloadGenerator
    from perceval.runtime.payload_updater import PayloadUpdater
    from perceval.runtime.platform_specs import PlatformSpecs
    from perceval.utils.constants import KEY_MITIGATIONS

    frozen = json.loads(RETAINED_RECORDS[0].read_text(encoding="utf-8"))["processors"]["qpu:belenos"]["specs"]
    same = {key: frozen[key] for key in ("pcvl_version", "software_versions", "available_commands")}
    specs = PlatformSpecs(dict(same))
    if not payload_version_basis(specs, "qpu:belenos").startswith("restored from"):
        raise PlatformError("self-test: the frozen worker's command set was not restored")
    ascella_frozen = json.loads(RETAINED_RECORDS[1].read_text(encoding="utf-8"))["processors"]["qpu:ascella"]["specs"]
    ascella_same = {key: ascella_frozen[key] for key in ("pcvl_version", "software_versions", "available_commands")}
    ascella_specs = PlatformSpecs(dict(ascella_same))
    if not payload_version_basis(ascella_specs, "qpu:ascella").startswith("restored from"):
        raise PlatformError("self-test: qpu:ascella frozen worker command set was not restored")
    ascella_other = PlatformSpecs(
        {**ascella_same, "software_versions": {**ascella_same["software_versions"], "pcvl-worker": "0.0.0"}}
    )
    if payload_version_basis(ascella_other, "qpu:ascella") != "absent" or "commands" in ascella_other:
        raise PlatformError("self-test: another ascella worker record received the frozen command set")
    sample_count = next(c for c in specs.commands if c.name == "sample_count")
    built = pcvl.Experiment(pcvl.BS())
    built.with_input(pcvl.BasicState([1, 0]))
    built.min_detected_photons_filter(1)
    computation = pcvl.ExecutionFactory(pcvl.SimulatedComputer("SLOS"), built).build_computation("sample_count")
    computation.command = sample_count
    computation.add_params(max_samples=100, max_shots=200, compilation_seed=7)
    other = PlatformSpecs({**same, "software_versions": {**same["software_versions"], "pcvl-worker": "0.0.0"}})
    if payload_version_basis(other, "qpu:belenos") != "absent" or "commands" in other:
        raise PlatformError("self-test: another worker's record received the frozen command set")
    v1 = PayloadUpdater.update_payload(
        PayloadGenerator.from_computation(computation, [], None, None), other, target_payload_version=1
    )
    if KEY_MITIGATIONS in PayloadUpdater.update_payload(v1, pcvl.SimulatedComputer("SLOS"), target_payload_version=2):
        raise PlatformError("self-test: a version-1 round trip kept the mitigation list")


def runner_self_test() -> int:
    """Offline rules of plan, submit, collect and run_facts against a stubbed service; returns the rejections."""
    charge_self_test()
    payload_version_self_test()
    seed_self_test()
    for error, want in (
        (RefusedError("x", 502), True),
        (RefusedError("x", 408), True),
        (RefusedError("x", 404), False),
        (RefusedError("x", 401), False),
        (UnansweredError("x: timed out"), True),
        (PlatformError("x: answer is not JSON"), False),
    ):
        if transient(error) != want:
            raise SystemExit(f"self-test: transient() read {error.code if isinstance(error, RefusedError) else None}")
    # request() maps a refusal to its HTTP code and a connection lost at any stage to UnansweredError.
    refusal = urllib.error.HTTPError(API, 503, "unavailable", email.message.Message(), io.BytesIO(b"busy"))
    for raised, want_class in (
        (refusal, RefusedError),
        (urllib.error.URLError("no route"), UnansweredError),
        (TimeoutError("timed out"), UnansweredError),
        (ConnectionResetError("reset"), UnansweredError),
        (http.client.RemoteDisconnected("closed"), UnansweredError),
        (http.client.IncompleteRead(b"par"), UnansweredError),
        (ssl.SSLEOFError(8, "EOF occurred in violation of protocol"), UnansweredError),
    ):
        with patch.object(OPENER, "open", side_effect=raised):
            try:
                request("GET", "/api/jobs/x/status", auth=False)
            except PlatformError as error:
                if type(error) is not want_class or (isinstance(error, RefusedError) and error.code != 503):
                    raise SystemExit(f"self-test: request() mapped {raised!r} to {error!r}") from None
            else:
                raise SystemExit(f"self-test: request() swallowed {raised!r}")
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
        "fail": {},
        "posts": 0,
    }

    def fake_request(method: str, route: str, auth: bool = True, body: Any = None, raw: bool = False) -> Any:
        # service["fail"] maps a route suffix to the errors its next reads raise, in order.
        for suffix, queue in service["fail"].items():
            if route.endswith(suffix) and queue:
                raise queue.pop(0)
        if (method, route) == ("POST", "/api/jobs"):
            service["posts"] += 1
            if service["refuse"]:
                raise RefusedError("POST /api/jobs: HTTP 422 unprocessable payload", 422)
            return {"job_id": "job-a"}
        if route.endswith("/status"):
            return {"status": service["status"], "shots": 10012, "token_id": 7}
        if route.endswith("/data"):
            return {"job_id": "job-a", "token_label": "secret-label", "status": "completed"}
        if route.endswith("/result"):
            if service["result"] is None:
                raise RefusedError(f"GET {route}: HTTP 404 no result", 404)
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

    archived = "pcvlar 0 1 0 list 0"
    policies: tuple[tuple[dict[str, Any], list[str] | None], ...] = (
        ({"payload": {"command": "sample_count"}}, None),
        ({"job_name": "mitigations", "payload": {"command": "sample_count", "note": "mitigations"}}, None),
        ({"payload": {"command": "sample_count", "mitigations": archived}}, []),
        ({"payload": {"command": "sample_count", "mitigations": []}}, []),
    )
    for sent, want_policy in policies:
        if body_mitigations(sent) != want_policy:
            raise SystemExit(f"self-test: body_mitigations read {sent} as {body_mitigations(sent)!r}")
    if body_mitigations({"payload": {"mitigations": ["detector-balancing"]}}) == []:
        raise SystemExit("self-test: a nonempty mitigation list read as the empty policy")
    misplaced: tuple[tuple[str, dict[str, Any]], ...] = (
        ("a top-level mitigations key", {"mitigations": [], "payload": {}}),
        ("a nested mitigations key", {"payload": {"computation": {"mitigations": []}}}),
        ("a mitigations value that is no list", {"payload": {"mitigations": {}}}),
        ("a body without payload", {"mitigations": []}),
        ("an unreadable mitigations archive", {"payload": {"mitigations": "pcvlar garbage"}}),
    )
    for label_text, misplaced_body in misplaced:
        refuse(label_text, functools.partial(body_mitigations, misplaced_body), "")

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

            def submitted(name: str) -> Path:
                directory = scratch / name
                shutil.copytree(case, directory)
                submit(directory, "sim:belenos", "approved", 0.0, 10.0, 0.0)
                return directory

            # Transient failures of every terminal read are outlived without a second POST.
            flaky = submitted("flaky")
            posts = service["posts"]
            service["fail"] = {
                "/status": [RefusedError("GET status: HTTP 503", 503)],
                "/result": [RefusedError("GET result: HTTP 502", 502)],
                "/data": [UnansweredError("GET data: timed out")],
                "/api/tokens/usage/report": [RefusedError("GET usage: HTTP 429", 429)],
            }
            if collect(flaky, 0.0, 1.0)["counts"] != collected["counts"] or service["posts"] != posts:
                raise AssertionError("a collection through transient read failures changed its counts or posted")
            if "usage_absent" in json.loads((flaky / "results.json").read_text(encoding="utf-8")):
                raise AssertionError("a usage read that recovered was recorded as absent")
            # A usage report that stays unreadable is recorded, and the charge falls back to the billing rule.
            unbilled = submitted("unbilled")
            service["fail"] = {"/api/tokens/usage/report": [RefusedError("GET usage: HTTP 401", 401)]}
            if "HTTP 401" not in collect(unbilled, 0.0, 1.0).get("usage_absent", ""):
                raise AssertionError("an unreadable usage report was not recorded as absent")
            run_facts(unbilled)
            # A failed job-data read leaves the raw result on disk and no results.json; a later collect completes.
            interrupted = submitted("interrupted")
            service["fail"] = {"/data": [RefusedError("GET data: HTTP 404", 404)]}
            refuse("a refused job-data read", lambda: collect(interrupted, 0.0, 1.0), "HTTP 404")
            if not (interrupted / "raw/result.json").is_file() or (interrupted / "results.json").exists():
                raise AssertionError("a refused job-data read lost the raw result or wrote results.json")
            collect(interrupted, 0.0, 1.0)
            run_facts(interrupted)
            # A result whose parse fails is still retained byte for byte.
            unparsed = submitted("unparsed")
            service["result"] = result.replace("job-a", "job-z")
            refuse("a result naming another job", lambda: collect(unparsed, 0.0, 1.0), "not job-a")
            if (unparsed / "raw/result.json").read_bytes() != service["result"].encode():
                raise AssertionError("a result that failed to parse was not retained")
            service["result"] = result
            # Two transient failures in a row are outlived inside the deadline; past it the first one raises.
            repeated = submitted("repeated")
            service["fail"] = {
                "/result": [RefusedError("GET result: HTTP 503", 503), RefusedError("GET result: HTTP 503", 503)]
            }
            collect(repeated, 0.0, 1.0)
            # A failure that recurs on every attempt raises at once, inside the deadline.
            garbled = submitted("garbled")
            service["fail"] = {"/data": [PlatformError("GET data: answer is not JSON")]}
            refuse("an answer that is not JSON", lambda: collect(garbled, 0.0, 1.0), "not JSON")
            # Past the deadline a transient failure raises instead of waiting.
            late_read = submitted("late-read")
            service["fail"] = {"/result": [RefusedError("GET result: HTTP 503", 503)]}
            refuse("a transient read past the deadline", lambda: collect(late_read, 0.0, -1.0), "HTTP 503")
            # Only the result route's 404 records an error job's result as absent; a 401 leaves it recollectable.
            not_found = submitted("not-found")
            service["status"], service["fail"] = "error", {"/result": [RefusedError("GET result: HTTP 404", 404)]}
            if "HTTP 404" not in collect(not_found, 0.0, 1.0).get("result_absent", ""):
                raise AssertionError("a 404 result of an error job was not recorded as absent")
            unauthorized = submitted("unauthorized")
            service["fail"] = {"/result": [RefusedError("GET result: HTTP 401", 401)]}
            refuse("a 401 result of an error job", lambda: collect(unauthorized, 0.0, 1.0), "HTTP 401")
            if (unauthorized / "results.json").exists():
                raise AssertionError("a 401 result of an error job was recorded")
            # A refused /result after an earlier collection retained one is a changed answer, not an absence.
            refused_late = submitted("refused-late")
            service["status"], service["fail"] = "error", {"/data": [RefusedError("GET data: HTTP 404", 404)]}
            refuse("a refused job-data read of an error job", lambda: collect(refused_late, 0.0, 1.0), "HTTP 404")
            service["fail"] = {"/result": [RefusedError("GET result: HTTP 404", 404)]}
            refuse(
                "a refused result after its bytes were retained", lambda: collect(refused_late, 0.0, 1.0), "now answers"
            )
            if (refused_late / "results.json").exists():
                raise AssertionError("a refused result after retention wrote results.json")
            service["status"], service["fail"] = "completed", {}
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
    worker_error = json.dumps(
        {
            "job_id": "job-w",
            "results": json.dumps({"results_list": [{"results": "RuntimeError: no input ports", "iteration": {}}]}),
            "shots": 0,
        }
    ).encode()
    summary = result_summary(worker_error, "job-w", {"shots": 0}, complete=False)
    failed_entry = {"iteration": {}, "error": "RuntimeError: no input ports", "result_fields": {}}
    if summary != {
        "shots": 0,
        "partial": True,
        "counts": {},
        "samples": 0,
        "result_fields": {},
        "iterations": [failed_entry],
    }:
        raise AssertionError(f"an errored iteration without counts parsed as {summary}")
    mixed = json.dumps(
        {
            "job_id": "job-x",
            "shots": 5,
            "results": json.dumps(
                {
                    "results_list": [
                        {"results": ":PCVL:BSCount:{|1,0>=3}", "nb_shots_used": 5, "iteration": {"phi": 0.0}},
                        {"results": "RuntimeError: no input ports", "iteration": {"phi": 1.0}},
                        7,
                        {"results": None, "iteration": {"phi": 2.0}},
                    ]
                }
            ),
        }
    ).encode()
    summary = result_summary(mixed, "job-x", {}, complete=False, expected=6)
    kinds = [sorted(entry) for entry in summary["iterations"]]
    if (
        summary["counts"] != {"1,0": 3}
        or kinds
        != [
            ["counts", "iteration", "result_fields", "samples"],
            ["error", "iteration", "result_fields"],
            ["malformed"],
            ["iteration", "malformed"],
            ["missing"],
            ["missing"],
        ]
        or summary["iterations"][1]["iteration"] != {"phi": 1.0}
        or summary["iterations"][3]["iteration"] != {"phi": 2.0}
        or "shots_used" in summary
    ):
        raise AssertionError(f"a partial job with a counted, a failed and a malformed iteration parsed as {summary}")
    refuse("a completed job with a malformed iteration", functools.partial(result_summary, mixed, "job-x", {}), "")
    refuse(
        "a partial answer with more iterations than its case",
        functools.partial(result_summary, mixed, "job-x", {}, False, 3),
        "answer a case of 3",
    )
    try:
        result_summary(worker_error, "job-w", {"shots": 0})
    except PlatformError:
        pass
    else:
        raise AssertionError("a completed job whose iteration carries an error text was accepted")
    errored = json.dumps({"job_id": "job-e", "duration": 55, "results": None, "shots": None}).encode()
    summary = result_summary(errored, "job-e", {"shots": None}, complete=False)
    if summary != {"shots": None, "partial": True, "counts": {}, "samples": 0, "result_fields": {}}:
        raise AssertionError(f"an errored result without a shot count parsed as {summary}")
    try:
        result_summary(errored, "job-e", {"shots": None})
    except PlatformError:
        pass
    else:
        raise AssertionError("a completed result without a shot count was accepted")
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
    countless = {"partial": True, "counts": {}, "iterations": [{"failed": True}]}
    for job_id in ITERATIONS_PREDATING_JOBS:
        if not predates({"job_id": job_id}, countless, "iterations"):
            raise PlatformError(f"self-test: legacy partial record {job_id} must omit iterations")
    if predates({"job_id": "job-a"}, countless, "iterations"):
        raise PlatformError("self-test: a later count-less partial record omitted its failed iterations")

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
    p = sub.add_parser("observe")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("check")
    p.add_argument("directory", type=Path)
    p.add_argument("--agents", type=Path, nargs="+", help="files carrying the quandela-facts section")
    p = sub.add_parser("facts")
    p.add_argument("directory", type=Path)
    for name in ("plan", "review", "submit"):
        p = sub.add_parser(name)
        p.add_argument("case_dir", type=Path)
        p.add_argument("--platform", required=True)
        p.add_argument("--max-credits", type=float, required=True, help="the written case's credit ceiling")
        p.add_argument("--expected-seconds", type=float, required=True, help="the written case's expected seconds")
        p.add_argument("--per-job-credits", type=float, required=True, help="the offer's per-job price in the case")
        p.add_argument(
            "--admit-status",
            action="append",
            default=[],
            help="a platform status besides available that the written case admits by name",
        )
        if name == "submit":
            p.add_argument("--approval", required=True, help="the user's approval, quoted, kept in submission.json")
            p.add_argument("--reviewed-packet", type=Path, help="the externally reviewed acquisition packet")
            p.add_argument("--reviewed-sha256", help="the independently retained packet SHA-256")
        if name == "review":
            p.add_argument("--out", type=Path, required=True, help="write-once complete acquisition review packet")
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
    elif args.command == "observe":
        try:
            observe(args.out)
        except PlatformError as error:
            raise SystemExit(str(error)) from None
    elif args.command == "check":
        check(args.directory, args.agents)
    elif args.command == "facts":
        print(facts_table(load(args.directory)), end="")
    elif args.command in ("plan", "review", "submit", "recover", "collect", "runs"):
        try:
            if args.command == "plan":
                checked = plan(
                    args.case_dir,
                    args.platform,
                    args.max_credits,
                    args.expected_seconds,
                    args.per_job_credits,
                    tuple(args.admit_status),
                )
                print(json.dumps({k: v for k, v in checked.items() if k != "body"}, indent=1, sort_keys=True))
            elif args.command == "review":
                packet = prepare_acquisition_review(
                    args.case_dir,
                    args.platform,
                    args.max_credits,
                    args.expected_seconds,
                    args.per_job_credits,
                    tuple(args.admit_status),
                    args.out,
                )
                print(
                    json.dumps(
                        {
                            "packet_sha256": sha256_bytes(args.out.read_bytes()),
                            "body_sha256": packet["binding"]["body_sha256"],
                        },
                        indent=1,
                    )
                )
            elif args.command == "submit":
                record = submit(
                    args.case_dir,
                    args.platform,
                    args.approval,
                    args.max_credits,
                    args.expected_seconds,
                    args.per_job_credits,
                    tuple(args.admit_status),
                    reviewed_packet=args.reviewed_packet,
                    reviewed_sha256=args.reviewed_sha256,
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
