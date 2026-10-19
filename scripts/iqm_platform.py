"""IQM Resonance account reads, token refresh and the retained catalogue the IQM guide cites.

IQM Resonance serves IQM's superconducting QPUs and their mock twins through
the IQM Server REST API at https://resonance.iqm.tech/api/v1 and a GraphQL
API at /api/graphql. Every call carries a workspace-scoped API token as a
Bearer header; IQM_TOKENS_FILE names the JSON file holding it
({"access_token", "refresh_token"}), the file iqm-client 36's
TokensFileReader reads, so this script and the client share one credential.
The client stack lives in the iqm-resonance-stack Arch package
(/opt/iqm-resonance-stack, interpreter iqm-python); this script imports only
the standard library and runs under the repository's $PYTHON.

Subcommands:

- snapshot --out DIR (network, read-only) writes every resource a
  job_execution token reads: the server's about, versions, OpenAPI and
  GraphQL schema; per quantum computer its details, health, limits,
  pay-as-you-go availability, timeslots, per-QC OpenAPI, every configuration
  artifact the per-QC OpenAPI names, and the default calibration set with
  its dynamic quantum architecture and quality metrics; the token's scopes
  and expiry; and the account type with its credit balance and expiry.
  Account, user and token ids, names and emails never enter a file. It
  writes index.json (path, HTTP status, bytes, sha256 per file) and
  hardware.json, the per-QC decomposition derive() computes from the
  retained files.
- notifications --cookie-jar JAR --out DIR retains the dashboard's update
  feed (GET /webapp/api/cms/notification), which only a browser session
  cookie reads, and adds it to index.json.
- check DIR [--agents FILE...] (offline) requires every indexed file to
  exist with its sha256 and no unindexed file, every required resource to
  have answered 200, hardware.json to equal derive(DIR), and, with
  --agents, each FILE's iqm-facts markers to enclose exactly facts_table().
- facts DIR prints the table.
- refresh [--min-days N] [--days D] renews the API token through the
  two-phase protocol of POST /api/v1/tokens/current/refresh: the new token
  is requested with activated=false and written to TOKENS.pending before
  POST /api/v1/tokens/current/activate invalidates the refresh token, so a
  lost response never loses a token; a rerun resumes from the pending file.
  An flock on TOKENS.lock serializes refreshes. It refreshes only when the
  current token expires within N days (default 14).
- --self-test proves check rejects an altered, a removed and an unindexed
  file, a non-200 required resource, an edited hardware.json and a stale
  table, and that refresh writes the pending file before activation and
  resumes from it, on temporary copies with a stubbed transport.

Usage: IQM_TOKENS_FILE=TOKENS.json "$PYTHON" scripts/iqm_platform.py snapshot --out DIR
       "$PYTHON" scripts/iqm_platform.py (check DIR [--agents FILE...] | facts DIR | --self-test)
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import datetime as dt
import fcntl
import hashlib
import http.cookiejar
import json
import os
import re
import shutil
import statistics
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

SERVER = "https://resonance.iqm.tech"
API = "api/v1"
USER_AGENT = "gororoba-quantum-iqm-platform/1"
BEGIN = "<!-- iqm-facts:begin -->\n"
END = "<!-- iqm-facts:end -->\n"
LOW_REMAINING = 300
GRAPHQL_INTROSPECTION = (
    "query IntrospectionQuery { __schema { queryType { name } mutationType { name } types { kind name "
    "description fields(includeDeprecated: true) { name description isDeprecated deprecationReason args "
    "{ name description type { kind name ofType { kind name ofType { kind name ofType { kind name } } } } "
    "defaultValue } type { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } "
    "inputFields { name description type { kind name ofType { kind name ofType { kind name } } } "
    "defaultValue } enumValues(includeDeprecated: true) { name description isDeprecated } } } }"
)
QC_ARTIFACTS_PATH = re.compile(r"^/api/v1/quantum-computers/[^/]+/artifacts/([a-z-]+)$")
LOCUS = re.compile(r"(?:QB\d+|COMPR\d+)")

MCP_SERVER = Path(__file__).resolve().parent / "iqm_mcp_server.py"
MCP_TOOLS = (
    "iqm_architecture",
    "iqm_artifact",
    "iqm_cancel_job",
    "iqm_credit",
    "iqm_job",
    "iqm_job_artifact",
    "iqm_metrics",
    "iqm_quantum_computer",
    "iqm_quantum_computers",
    "iqm_queue_availability",
    "iqm_timeslots",
    "iqm_tokens",
)
MCP_MUTATING = ("iqm_cancel_job",)

Transport = Callable[[str, str, bytes | None, dict[str, str]], tuple[int, dict[str, str], bytes]]


class PlatformError(RuntimeError):
    pass


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def urllib_transport(opener: urllib.request.OpenerDirector | None = None) -> Transport:
    open_url = (opener or urllib.request.build_opener()).open

    def send(method: str, url: str, body: bytes | None, headers: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
        request = urllib.request.Request(url, data=body, method=method, headers=headers)
        for _ in range(6):
            try:
                with open_url(request, timeout=120) as response:
                    reply = dict(response.headers)
                    remaining = reply.get("RateLimit-Remaining") or reply.get("ratelimit-remaining")
                    if remaining is not None and int(remaining) < LOW_REMAINING:
                        time.sleep(10)
                    return response.status, reply, response.read()
            except urllib.error.HTTPError as error:
                if error.code == 429:
                    time.sleep(int(error.headers.get("Retry-After", "30")) + 1)
                    continue
                return error.code, dict(error.headers), error.read()
        raise PlatformError(f"{method} {url}: rate limited six times")

    return send


def tokens_path() -> Path:
    named = os.environ.get("IQM_TOKENS_FILE", "")
    if not named:
        raise PlatformError("IQM_TOKENS_FILE must name the tokens file")
    return Path(named).expanduser()


def read_tokens(path: Path) -> dict[str, str]:
    tokens = json.loads(path.read_text())
    if not isinstance(tokens, dict) or not tokens.get("access_token"):
        raise PlatformError(f"{path} lacks access_token")
    return tokens


def write_private(path: Path, value: dict[str, Any]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.unlink(missing_ok=True)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as handle:
        handle.write(json.dumps(value, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


class Client:
    def __init__(self, token: str, transport: Transport | None = None, server: str = SERVER) -> None:
        self.token = token
        self.send = transport or urllib_transport()
        self.server = server

    def headers(self, token: str | None = None, content: bool = False) -> dict[str, str]:
        out = {"Authorization": f"Bearer {token or self.token}", "Accept": "application/json", "User-Agent": USER_AGENT}
        if content:
            out["Content-Type"] = "application/json"
        return out

    def get(self, path: str) -> tuple[int, bytes]:
        status, _, body = self.send("GET", f"{self.server}/{path}", None, self.headers())
        return status, body

    def post(self, path: str, value: Any, token: str | None = None) -> tuple[int, Any]:
        status, _, body = self.send(
            "POST", f"{self.server}/{path}", json.dumps(value).encode(), self.headers(token, True)
        )
        if not body:
            return status, None
        try:
            return status, json.loads(body)
        except ValueError as error:
            raise PlatformError(f"POST {path} answered {status} with a non-JSON body") from error

    def graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        status, reply = self.post("api/graphql", {"query": query, "variables": variables or {}})
        if status != 200 or reply.get("errors"):
            raise PlatformError(f"GraphQL {status}: {reply}")
        data: dict[str, Any] = reply["data"]
        return data


def snapshot(out: Path, client: Client) -> None:
    out.mkdir(parents=True, exist_ok=True)
    index: dict[str, Any] = {"schema": "iqm-snapshot-v1", "server": SERVER, "captured_at": now(), "files": {}}

    def keep(rel: str, url_path: str, status: int, body: bytes, required: bool = True) -> None:
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
        index["files"][rel] = {
            "path": url_path,
            "status": status,
            "bytes": len(body),
            "sha256": sha256(body),
            "required": required,
        }

    def fetch(rel: str, url_path: str, required: bool = True) -> bytes:
        status, body = client.get(url_path)
        keep(rel, url_path, status, body, required)
        return body

    fetch("server/about.json", "about")
    fetch("server/versions.json", "api/versions")
    fetch("server/openapi.json", f"{API}/openapi.json")
    schema = client.graphql(GRAPHQL_INTROSPECTION)
    keep("server/graphql-schema.json", "api/graphql#introspection", 200, canonical(schema))
    status, body = client.get(f"{API}/tokens")
    tokens = [
        {
            "scopes": sorted(t["scopes"]),
            "expires_at": t["expires_at"],
            "refreshable": t.get("refresh_token") is not None,
        }
        for t in json.loads(body).get("tokens", [])
    ]
    keep("account/tokens.json", f"{API}/tokens", status, canonical(sorted(tokens, key=json.dumps)))
    me = client.graphql("{ me { currentAccount { id type } } }")["me"]["currentAccount"]
    credit = client.graphql("query($a: UUID!){ credit(accountId: $a) { currentBalance expiresAt } }", {"a": me["id"]})
    keep(
        "account/credit.json",
        "api/graphql#credit",
        200,
        canonical({"account_type": me["type"], "credit": credit["credit"]}),
    )

    listing = json.loads(fetch("server/quantum-computers.json", f"{API}/quantum-computers"))
    for qc in sorted(q["alias"] for q in listing["quantum_computers"]):
        base = f"qc/{qc.replace(':', '_')}"
        root = f"{API}/quantum-computers/{qc}"
        for name, suffix in (("details", ""), ("health", "/health"), ("limits", "/limits")):
            fetch(f"{base}/{name}.json", root + suffix)
        fetch(f"{base}/queue-availability.json", f"{root}/queue-availability")
        fetch(f"{base}/timeslots.json", f"{root}/timeslots")
        spec = json.loads(fetch(f"{base}/openapi.json", f"{API}/openapi.json?qc={urllib.parse.quote(qc)}"))
        kinds = sorted({m.group(1) for p in spec["paths"] if (m := QC_ARTIFACTS_PATH.match(p))})
        for kind in kinds:
            fetch(f"{base}/artifacts/{kind}.json", f"{root}/artifacts/{kind}")
        # The default set moves with every calibration, so the architecture
        # and metrics are read by the id the default resolved to.
        calibration_set = json.loads(fetch(f"{base}/calibration/set.json", f"{API}/calibration-sets/{qc}/default"))
        pinned = f"{API}/calibration-sets/{qc}/{calibration_set['observation_set_id']}"
        fetch(f"{base}/calibration/dynamic-quantum-architecture.json", f"{pinned}/dynamic-quantum-architecture")
        fetch(f"{base}/calibration/metrics.json", f"{pinned}/metrics")
    carry_feed(out, index)
    prune(out, index)
    (out / "index.json").write_bytes(canonical(index))
    (out / "hardware.json").write_bytes(canonical(derive(out)))


NOTIFICATIONS = "server/notifications.json"


def carry_feed(out: Path, index: dict[str, Any]) -> None:
    """Keep the retained update feed: it needs the browser session, which a token snapshot lacks."""
    previous = out / "index.json"
    if previous.is_file():
        feed = json.loads(previous.read_text())["files"].get(NOTIFICATIONS)
        if feed and (out / NOTIFICATIONS).is_file():
            index["files"][NOTIFICATIONS] = feed


def prune(out: Path, index: dict[str, Any]) -> None:
    """Remove every file the new index omits, so a QC or artifact the service dropped leaves nothing behind."""
    for stale in sorted(p for p in out.rglob("*") if p.is_file()):
        if stale.relative_to(out).as_posix() not in {*index["files"], "index.json", "hardware.json"}:
            stale.unlink()


def notifications(out: Path, jar_path: Path) -> None:
    jar = http.cookiejar.MozillaCookieJar(str(jar_path))
    jar.load(ignore_discard=True, ignore_expires=True)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    url_path = "webapp/api/cms/notification"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
    }
    status, _, body = urllib_transport(opener)("GET", f"{SERVER}/{url_path}", None, headers)
    if status != 200:
        raise PlatformError(f"notifications answered {status}")
    rel = NOTIFICATIONS
    (out / rel).write_bytes(body)
    index = json.loads((out / "index.json").read_text())
    index["files"][rel] = {
        "path": url_path,
        "status": status,
        "bytes": len(body),
        "sha256": sha256(body),
        "required": True,
    }
    (out / "index.json").write_bytes(canonical(index))


def load_json(directory: Path, rel: str) -> Any:
    return json.loads((directory / rel).read_text())


def observations(document: dict[str, Any]) -> dict[str, float]:
    return {o["dut_field"]: o["value"] for o in document["observations"] if not o.get("invalid")}


def median(values: list[float]) -> float | None:
    return float(f"{statistics.median(values):.6g}") if values else None


def pick(values: dict[str, Any], pattern: str) -> dict[str, Any]:
    rule = re.compile(pattern)
    return {m.group(1): v for k, v in values.items() if (m := rule.fullmatch(k))}


def derive_qc(directory: Path, base: str) -> dict[str, Any]:
    details = load_json(directory, f"{base}/details.json")
    static = load_json(directory, f"{base}/artifacts/static-architecture.json")
    dqa = load_json(directory, f"{base}/calibration/dynamic-quantum-architecture.json")
    metrics = load_json(directory, f"{base}/calibration/metrics.json")
    calibration = load_json(directory, f"{base}/calibration/set.json")
    chip = load_json(directory, f"{base}/artifacts/chip-design-records.json")[0]
    config = load_json(directory, f"{base}/artifacts/configuration.json")
    channels = load_json(directory, f"{base}/artifacts/channel-properties.json")
    about = load_json(directory, f"{base}/artifacts/about.json")
    m = observations(metrics)
    c = observations(calibration)
    measure = dqa["gates"]["measure"]["default_implementation"]
    prx = dqa["gates"]["prx"]["default_implementation"]
    qubits = {}
    driven = set().union(*(set(locus) for locus in dqa["gates"]["prx"]["implementations"][prx]["loci"]))
    for qb in dqa["qubits"]:
        if qb not in driven:
            continue
        qubits[qb] = {
            "t1_s": m.get(f"characterization.model.{qb}.t1_time"),
            "t2_s": m.get(f"characterization.model.{qb}.t2_time"),
            "t2_echo_s": m.get(f"characterization.model.{qb}.t2_echo_time"),
            "prx_fidelity": next(
                (v for k, v in m.items() if k.startswith(f"metrics.rb.prx.{prx}.{qb}.fidelity")), None
            ),
            "readout_fidelity": m.get(f"metrics.ssro.measure.{measure}.{qb}.fidelity"),
            "readout_error_0_to_1": m.get(f"metrics.ssro.measure.{measure}.{qb}.error_0_to_1"),
            "readout_error_1_to_0": m.get(f"metrics.ssro.measure.{measure}.{qb}.error_1_to_0"),
            "drive_frequency_hz": c.get(f"controllers.{qb}.drive.frequency"),
            "readout_frequency_hz": c.get(f"gates.measure.{measure}.{qb}.frequency"),
            "prx_duration_s": c.get(f"gates.prx.{prx}.{qb}.duration"),
            "measure_duration_s": c.get(f"gates.measure.{measure}.{qb}.duration"),
        }
    cz = dqa["gates"].get("cz", {})
    pairs: dict[str, dict[str, Any]] = {}
    for impl, spec in cz.get("implementations", {}).items():
        # Only loci the DQA lists for an implementation are operational pairs.
        loci = {"__".join(locus) for locus in spec["loci"]}
        for k, v in pick(m, rf"metrics\.irb\.cz\.{re.escape(impl)}\.(.+?)\.fidelity(?::.*)?").items():
            if k in loci:
                pairs.setdefault(k, {})["cz_irb_fidelity"] = v
                pairs[k]["implementation"] = impl
        for k, v in pick(c, rf"gates\.cz\.{re.escape(impl)}\.(.+?)\.duration").items():
            if k in loci:
                pairs.setdefault(k, {})["cz_duration_s"] = v
    awg = sorted(
        {
            (p.get("sampling_rate"), p.get("instruction_duration_granularity"), p.get("instruction_duration_min"))
            for p in channels.values()
        },
        key=str,
    )

    def col(key: str) -> list[float]:
        return [float(value) for q in qubits.values() if isinstance(value := q[key], int | float)]

    return {
        "alias": details["alias"],
        "display_name": details["display_name"],
        "backend_type": details["backend_type"],
        "description": details["description"].strip(),
        "station_control_version": about["version"],
        "station_label": config.get("label"),
        "dut_label": static["dut_label"],
        "mask_set": chip.get("mask_set_name"),
        "variant": chip.get("variant"),
        "chip_components": {kind: len(items) for kind, items in sorted(chip["content"]["components"].items())},
        "qubits": details["number_of_qubits"],
        "static_architecture_qubits": len([q for q in static["qubits"] if q.startswith("QB")]),
        "computational_resonators": static["computational_resonators"],
        "connectivity": static["connectivity"],
        "limits": details["limits"],
        "pricing": details["pricing"],
        "pulla_enabled": details["pulla_enabled"],
        "calibration_set_id": dqa["calibration_set_id"],
        "metrics_created": metrics["created_timestamp"],
        "gates": {
            name: {
                "default": gate["default_implementation"],
                "loci": {impl: len(spec["loci"]) for impl, spec in sorted(gate["implementations"].items())},
                "overrides": dict(sorted(gate.get("override_default_implementation", {}).items())),
            }
            for name, gate in sorted(dqa["gates"].items())
        },
        "awg_channels": [{"sampling_rate_hz": a[0], "granularity_samples": a[1], "min_samples": a[2]} for a in awg],
        "medians": {
            "t1_s": median(col("t1_s")),
            "t2_s": median(col("t2_s")),
            "t2_echo_s": median(col("t2_echo_s")),
            "prx_fidelity": median(col("prx_fidelity")),
            "readout_fidelity": median(col("readout_fidelity")),
            "cz_irb_fidelity": median([p["cz_irb_fidelity"] for p in pairs.values() if "cz_irb_fidelity" in p]),
            "cz_duration_s": median([p["cz_duration_s"] for p in pairs.values() if "cz_duration_s" in p]),
            "prx_duration_s": median(col("prx_duration_s")),
            "measure_duration_s": median(col("measure_duration_s")),
        },
        "per_qubit": qubits,
        "per_pair": dict(sorted(pairs.items())),
    }


def derive(directory: Path) -> dict[str, Any]:
    index = load_json(directory, "index.json")
    bases = sorted({rel.split("/")[1] for rel in index["files"] if rel.startswith("qc/")})
    computers = [derive_qc(directory, f"qc/{base}") for base in bases]
    return {
        "schema": "iqm-hardware-v1",
        "captured_at": index["captured_at"],
        "server_version": load_json(directory, "server/about.json")["server_version"],
        "api_versions": load_json(directory, "server/versions.json"),
        "account": load_json(directory, "account/credit.json"),
        "tokens": load_json(directory, "account/tokens.json"),
        "quantum_computers": computers,
    }


def gate_list(qc: dict[str, Any]) -> str:
    return ", ".join(f"{name} ({gate['default']})" for name, gate in qc["gates"].items())


def facts_table(hardware: dict[str, Any]) -> str:
    rows = [
        "| QC (alias) | type | QPU chip (mask, variant) | qubits | resonators | couplings "
        "| gates (default implementation) | shots / circuits / instructions max | PAYG credits/s | timeslot "
        "| IQM station control |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for qc in hardware["quantum_computers"]:
        limits = qc["limits"]
        slot = qc["pricing"].get("timeslot")
        chip = f"{qc['dut_label']} ({qc['mask_set']}, {qc['variant']})"
        resonators = ", ".join(qc["computational_resonators"]) or "-"
        maxima = " / ".join(
            str(limits.get(key, "-"))
            for key in ("max_shots_per_circuit", "max_circuits_per_job", "max_instructions_per_circuit")
        )
        timeslot = f"{slot['slot_price']} per {slot['slot_duration']}" if slot else "-"
        cells = (
            f"{qc['display_name']} (`{qc['alias']}`)",
            qc["backend_type"],
            chip,
            str(qc["qubits"]),
            resonators,
            str(len(qc["connectivity"])),
            gate_list(qc),
            maxima,
            qc["pricing"]["payg_price_per_second"],
            timeslot,
            qc["station_control_version"],
        )
        rows.append("| " + " | ".join(cells) + " |")
    account = hardware["account"]
    rows.append("")
    rows.append(
        f"Account: {account['account_type']} with {account['credit']['currentBalance']} credits expiring "
        f"{account['credit']['expiresAt']}; IQM Server {hardware['server_version']}, API "
        f"{', '.join(v['version'] for v in hardware['api_versions'])}; token scopes "
        f"{'; '.join(', '.join(t['scopes']) for t in hardware['tokens'])}."
    )
    return "\n".join(rows) + "\n"


def check_agents(hardware: dict[str, Any], files: list[Path]) -> None:
    table = facts_table(hardware)
    for path in files:
        text = path.read_text()
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            raise PlatformError(f"{path}: needs exactly one iqm-facts marker pair")
        if text[text.index(BEGIN) + len(BEGIN) : text.index(END)] != table:
            raise PlatformError(f"{path}: iqm-facts table differs from the snapshot")


def check(directory: Path, agents: list[Path] | None = None) -> None:
    index = load_json(directory, "index.json")
    if index.get("schema") != "iqm-snapshot-v1":
        raise PlatformError("index.json schema")
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(index["files"]) | {"index.json", "hardware.json"}
    if present != expected:
        raise PlatformError(
            f"file set differs: missing {sorted(expected - present)}, unindexed {sorted(present - expected)}"
        )
    for rel, row in sorted(index["files"].items()):
        if sha256((directory / rel).read_bytes()) != row["sha256"]:
            raise PlatformError(f"{rel}: sha256 differs from index.json")
        if row["required"] and row["status"] != 200:
            raise PlatformError(f"{rel}: {row['path']} answered {row['status']}")
    for rel in index["files"]:
        if rel.startswith("account/") and re.search(r'"(id|email|name|accountId)"', (directory / rel).read_text()):
            raise PlatformError(f"{rel}: carries an account identity field")
    for rel in sorted(r for r in index["files"] if r.endswith("/calibration/set.json")):
        base = rel.removesuffix("set.json")
        ids = {
            load_json(directory, rel)["observation_set_id"],
            load_json(directory, base + "dynamic-quantum-architecture.json")["calibration_set_id"],
            load_json(directory, base + "metrics.json")["describes_id"],
        }
        if len(ids) != 1:
            raise PlatformError(f"{base}: set, architecture and metrics name calibration sets {sorted(ids)}")
    check_mcp()
    hardware = derive(directory)
    if (directory / "hardware.json").read_bytes() != canonical(hardware):
        raise PlatformError("hardware.json differs from derive()")
    if agents:
        check_agents(hardware, agents)


def mcp_surface(server: Path = MCP_SERVER) -> dict[str, str]:
    """Tool name to annotation constant of every @server.tool function, read from the source."""
    tools = {}
    for node in ast.walk(ast.parse(server.read_text())):
        if isinstance(node, ast.AsyncFunctionDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and ast.unparse(decorator.func) == "server.tool":
                    notes = {k.arg: ast.unparse(k.value) for k in decorator.keywords}
                    tools[node.name] = notes.get("annotations", "")
    return tools


def check_mcp(server: Path = MCP_SERVER) -> None:
    tools = mcp_surface(server)
    if tuple(sorted(tools)) != MCP_TOOLS:
        raise PlatformError(f"MCP tools {sorted(tools)} differ from {MCP_TOOLS}")
    mutating = tuple(sorted(name for name, notes in tools.items() if notes != "READ"))
    if mutating != MCP_MUTATING:
        raise PlatformError(f"MCP tools {mutating} change remote state, expected {MCP_MUTATING}")
    text = server.read_text()
    if "/jobs/{qc}" in text or 'timeslots", {' in text or text.count(".post(") != 1:
        raise PlatformError("the MCP server names a submission or booking route")


@contextlib.contextmanager
def locked(path: Path) -> Iterator[None]:
    with open(path.with_name(path.name + ".lock"), "a") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def current_expiry(client: Client) -> dt.datetime:
    status, body = client.get(f"{API}/tokens")
    if status != 200:
        raise PlatformError(f"tokens listing answered {status}")
    suffixes = [
        t
        for t in json.loads(body)["tokens"]
        if t.get("last_characters") and client.token.endswith(t["last_characters"])
    ]
    if len(suffixes) != 1:
        raise PlatformError("the tokens listing names the current token zero or several times")
    return dt.datetime.fromisoformat(suffixes[0]["expires_at"].replace("Z", "+00:00"))


def refresh(path: Path, min_days: float, days: int, transport: Transport | None = None, force: bool = False) -> str:
    pending = path.with_name(path.name + ".pending")
    with locked(path):
        tokens = read_tokens(path)
        client = Client(tokens["access_token"], transport)
        if not pending.exists():
            if not force and current_expiry(client) - dt.datetime.now(dt.UTC) > dt.timedelta(days=min_days):
                return "current token outlives the margin; no refresh"
            if not tokens.get("refresh_token"):
                raise PlatformError(f"{path} lacks refresh_token")
            seconds = days * 86400
            body = {
                "new_token_properties": {
                    "expires_in_seconds": seconds,
                    "refreshing_expires_in_seconds": seconds,
                    "activated": False,
                }
            }
            status, created = client.post(f"{API}/tokens/current/refresh", body, token=tokens["refresh_token"])
            if status != 200 or not isinstance(created, dict) or created.get("activated") or not created.get("token"):
                raise PlatformError(f"refresh answered {status}")
            write_private(
                pending,
                {
                    "access_token": created["token"],
                    "refresh_token": created["refresh_token"],
                    "used_refresh_token": tokens["refresh_token"],
                },
            )
        staged = read_tokens(pending)
        installed = (staged.get("access_token"), staged.get("refresh_token"))
        if installed == (tokens.get("access_token"), tokens.get("refresh_token")):
            # The install wrote the live file and stopped before removing the pending one.
            pending.unlink()
            return "refreshed"
        if staged.get("used_refresh_token") != tokens.get("refresh_token"):
            raise PlatformError(
                f"{pending} was staged from another refresh token than {path} holds; inspect it by hand"
            )
        status, _ = client.post(
            f"{API}/tokens/current/activate", {"api_token": staged["access_token"]}, token=staged["used_refresh_token"]
        )
        # Activation invalidates the refresh token, so a lost success reply
        # leaves a rerun unable to activate; the staged token then answers.
        if status != 200 and Client(staged["access_token"], transport).get(f"{API}/tokens")[0] != 200:
            raise PlatformError(f"activate answered {status}; {pending} keeps the new token for a rerun")
        write_private(path, {"access_token": staged["access_token"], "refresh_token": staged["refresh_token"]})
        pending.unlink()
    return "refreshed"


def expect_failure(label: str, action: Callable[[], object]) -> None:
    try:
        action()
    except PlatformError:
        return
    raise PlatformError(f"self-test: check accepted {label}")


def self_test(evidence: Path) -> None:
    agents = evidence.parent.parent.parent / "AGENTS.md"
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch) / "iqm"
        shutil.copytree(evidence, root)
        check(root)
        index_path = root / "index.json"
        original = index_path.read_bytes()

        def mutate(label: str, change: Callable[[], object], restore: Callable[[], object]) -> None:
            change()
            expect_failure(label, lambda: check(root))
            restore()
            check(root)

        target = root / "server/about.json"
        saved = target.read_bytes()
        mutate("an altered file", lambda: target.write_bytes(saved + b" "), lambda: target.write_bytes(saved))
        mutate("a removed file", target.unlink, lambda: target.write_bytes(saved))
        extra = root / "server/extra.json"
        mutate("an unindexed file", lambda: extra.write_text("{}"), extra.unlink)
        index = json.loads(original)
        index["files"]["server/about.json"]["status"] = 503
        mutate(
            "a non-200 resource",
            lambda: index_path.write_bytes(canonical(index)),
            lambda: index_path.write_bytes(original),
        )
        hardware = root / "hardware.json"
        kept = hardware.read_bytes()
        mutate(
            "an edited hardware.json",
            lambda: hardware.write_bytes(kept.replace(b'"qubits": 20', b'"qubits": 21', 1)),
            lambda: hardware.write_bytes(kept),
        )
        metrics = root / "qc/garnet/calibration/metrics.json"
        measured = metrics.read_bytes()
        document = json.loads(measured)
        document["describes_id"] = "00000000-0000-0000-0000-000000000000"
        mixed = canonical(document)
        index = json.loads(original)
        index["files"]["qc/garnet/calibration/metrics.json"]["sha256"] = sha256(mixed)

        def mix() -> None:
            metrics.write_bytes(mixed)
            index_path.write_bytes(canonical(index))

        def unmix() -> None:
            metrics.write_bytes(measured)
            index_path.write_bytes(original)

        mutate("metrics of another calibration set", mix, unmix)
        index = json.loads(original)
        del index["files"]["server/about.json"]
        del index["files"][NOTIFICATIONS]
        carry_feed(root, index)
        prune(root, index)
        if not (root / NOTIFICATIONS).exists() or NOTIFICATIONS not in index["files"]:
            raise PlatformError("self-test: a token snapshot dropped the retained update feed")
        if target.exists() or not (root / "server/versions.json").exists():
            raise PlatformError("self-test: prune kept a dropped file or removed an indexed one")
        target.write_bytes(saved)
        check(root)
        stale = Path(scratch) / "AGENTS.md"
        text = agents.read_text()
        start = text.index(BEGIN) + len(BEGIN)
        stale.write_text(text[:start] + "| stale |\n" + text[text.index(END) :])
        expect_failure("a stale table", lambda: check(root, [stale]))
        self_test_refresh(Path(scratch))


class StubServer:
    """Token endpoints of IQM Server: refresh stages, activate installs, /tokens authenticates active tokens."""

    def __init__(self, activate_replies: list[int], apply_on_failure: bool) -> None:
        self.active = {"old-access-AAAAA"}
        self.refresh_valid = True
        self.replies = activate_replies
        self.apply_on_failure = apply_on_failure
        self.calls: list[str] = []

    def __call__(
        self, method: str, url: str, body: bytes | None, headers: dict[str, str]
    ) -> tuple[int, dict[str, str], bytes]:
        bearer = headers["Authorization"].removeprefix("Bearer ")
        self.calls.append(url.rsplit("/", 1)[-1])
        if url.endswith("/tokens"):
            if bearer not in self.active:
                return 401, {}, b"{}"
            soon = (dt.datetime.now(dt.UTC) + dt.timedelta(days=1)).isoformat()
            return 200, {}, json.dumps({"tokens": [{"last_characters": "AAAAA", "expires_at": soon}]}).encode()
        if url.endswith("/refresh"):
            request = json.loads(body or b"{}")
            if bearer != "old-refresh" or not self.refresh_valid or request["new_token_properties"]["activated"]:
                return 400, {}, b"{}"
            reply = {"token": "new-access", "refresh_token": "new-refresh", "activated": False}
            return 200, {}, json.dumps(reply).encode()
        if url.endswith("/activate"):
            if bearer != "old-refresh" or not self.refresh_valid:
                return 401, {}, b"{}"
            status = self.replies.pop(0) if self.replies else 200
            if status == 200 or self.apply_on_failure:
                self.active.add("new-access")
                self.refresh_valid = False
            return status, {}, b'{"activated_at": "now"}' if status == 200 else b""
        return 404, {}, b""


def self_test_refresh(scratch: Path) -> None:
    path = scratch / "tokens.json"
    pending = path.with_name(path.name + ".pending")
    installed = {"access_token": "new-access", "refresh_token": "new-refresh"}

    def reset() -> None:
        pending.unlink(missing_ok=True)
        write_private(path, {"access_token": "old-access-AAAAA", "refresh_token": "old-refresh"})

    # An activation the server rejected keeps the pending token; the rerun activates it.
    reset()
    server = StubServer([502], apply_on_failure=False)
    expect_failure("a rejected activation", lambda: refresh(path, 14, 30, server))
    if not pending.exists() or read_tokens(path)["access_token"] != "old-access-AAAAA":
        raise PlatformError("self-test: refresh lost the pending token or replaced the live one early")
    if refresh(path, 14, 30, server) != "refreshed" or server.calls.count("refresh") != 1:
        raise PlatformError(f"self-test: refresh did not resume from the pending token: {server.calls}")
    if read_tokens(path) != installed or pending.exists():
        raise PlatformError("self-test: refresh did not install the activated token")
    if os.stat(path).st_mode & 0o077:
        raise PlatformError("self-test: tokens file is readable beyond its owner")

    # An activation that succeeded with a lost reply installs the staged token at once.
    reset()
    server = StubServer([502], apply_on_failure=True)
    if refresh(path, 14, 30, server) != "refreshed" or read_tokens(path) != installed or pending.exists():
        raise PlatformError("self-test: refresh lost a token the server had already activated")

    # A pending file staged from another refresh token is refused, and the live pair is kept.
    reset()
    write_private(pending, {"access_token": "x", "refresh_token": "y", "used_refresh_token": "other-refresh"})
    expect_failure("a stale pending file", lambda: refresh(path, 14, 30, StubServer([], apply_on_failure=False)))
    if read_tokens(path)["access_token"] != "old-access-AAAAA":
        raise PlatformError("self-test: a stale pending file replaced the live token")

    # A pending pair already installed, interrupted before its removal, completes without a server call.
    reset()
    write_private(path, installed)
    write_private(pending, {**installed, "used_refresh_token": "old-refresh"})
    server = StubServer([], apply_on_failure=False)
    if refresh(path, 14, 30, server) != "refreshed" or pending.exists() or server.calls:
        raise PlatformError(f"self-test: an installed pending pair blocked refresh: {server.calls}")

    # A leftover world-readable temporary file never lends its mode to the tokens file.
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text("{}")
    tmp.chmod(0o644)
    reset()
    if os.stat(path).st_mode & 0o077:
        raise PlatformError("self-test: a leftover temporary file widened the tokens file mode")


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    snap = sub.add_parser("snapshot")
    snap.add_argument("--out", type=Path, required=True)
    note = sub.add_parser("notifications")
    note.add_argument("--cookie-jar", type=Path, required=True)
    note.add_argument("--out", type=Path, required=True)
    chk = sub.add_parser("check")
    chk.add_argument("directory", type=Path)
    chk.add_argument("--agents", type=Path, nargs="*")
    facts = sub.add_parser("facts")
    facts.add_argument("directory", type=Path)
    ref = sub.add_parser("refresh")
    ref.add_argument("--min-days", type=float, default=14)
    ref.add_argument("--days", type=int, default=90)
    args = parser.parse_args()
    evidence = Path(__file__).resolve().parent.parent / "docs/evidence/iqm"
    try:
        if args.self_test:
            self_test(evidence)
            print("iqm_platform self-test passed")
        elif args.command == "snapshot":
            snapshot(args.out, Client(read_tokens(tokens_path())["access_token"]))
        elif args.command == "notifications":
            notifications(args.out, args.cookie_jar)
        elif args.command == "check":
            check(args.directory, args.agents)
            print(f"iqm snapshot {args.directory} verified")
        elif args.command == "facts":
            sys.stdout.write(facts_table(derive(args.directory)))
        elif args.command == "refresh":
            print(refresh(tokens_path(), args.min_days, args.days))
        else:
            parser.error("a subcommand or --self-test is required")
    except PlatformError as error:
        print(f"iqm_platform: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
