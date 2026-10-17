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
- --self-test proves check rejects a token id, a staff creator id, a missing
  processor record, an input mode outside the chip, a photon limit off the
  connected modes, a negative price, a missing availability counter, an
  edited table, a stale row inside the markers, a tool table missing a tool,
  a server that adds a submit tool, marks cancel read-only or marks a read
  as mutating, on a temporary copy.

Usage: QUANDELA_TOKEN_FILE=TOKEN "$PYTHON" scripts/qd_platform.py snapshot --out DIR
       "$PYTHON" scripts/qd_platform.py (check DIR [--agents FILE...] | facts DIR | --self-test)
"""

from __future__ import annotations

import argparse
import ast
import datetime
import importlib.metadata
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
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
FORBIDDEN_KEYS = ("token", "token_id", "token_value", "creator_id", "user_id", "entity_id", "email")
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


def request(method: str, route: str, auth: bool = True) -> Any:
    """JSON answer of one API call; any failure raises PlatformError naming the route and the cause."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {token()}"
    call = urllib.request.Request(API + route, headers=headers, method=method)
    try:
        with OPENER.open(call, timeout=60) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read()[:500].decode("utf-8", errors="replace")
        error.close()
        hint = STATUS_HINTS.get(error.code, "redirect refused" if 300 <= error.code < 400 else "")
        raise PlatformError(f"{method} {route}: HTTP {error.code} {detail} {hint}".rstrip()) from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise PlatformError(f"{method} {route}: {error}") from None
    try:
        return json.loads(body) if body else None
    except json.JSONDecodeError:
        raise PlatformError(f"{method} {route}: answer is not JSON: {body[:200]!r}") from None


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
    """The token usage report without token ids."""
    return [{k: v for k, v in row.items() if k not in FORBIDDEN_KEYS} for row in report]


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
    for path in files:
        text = path.read_text(encoding="utf-8")
        if (rows := tool_rows(text)) and tuple(sorted(rows)) != MCP_TOOLS:
            raise SystemExit(f"{path}: MCP tool table {sorted(rows)} differs from {MCP_TOOLS}")
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            raise SystemExit(f"{path}: needs one quandela-facts section")
        if text[text.index(BEGIN) + len(BEGIN) : text.index(END)] != table:
            raise SystemExit(f"{path}: the quandela-facts table differs from facts_table of the snapshot")


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
    print(f"qd_platform self-test: {len(edits)} rejections")


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
    else:
        parser.error("a subcommand or --self-test is required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
