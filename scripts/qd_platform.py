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
  prices and complete availability counters. With --agents it renders
  facts_table and requires each FILE's quandela-facts markers to enclose
  exactly that table, so a refreshed snapshot that changes a limit, a
  command set or a price fails until AGENTS.md and the Quandela README change
  with it. Status, performance figures, availability statistics, maintenance
  windows and software versions change between reads and stay out of the
  table.
- facts DIR prints the table.
- --self-test proves check rejects a token id, a staff creator id, a missing
  processor record, an input mode outside the chip, a photon limit off the
  connected modes, a negative price, a missing availability counter, an
  edited table and a stale row inside the markers, on a temporary copy.

Usage: QUANDELA_TOKEN_FILE=TOKEN "$PYTHON" scripts/qd_platform.py snapshot --out DIR
       "$PYTHON" scripts/qd_platform.py (check DIR [--agents FILE...] | facts DIR | --self-test)
"""

from __future__ import annotations

import argparse
import datetime
import importlib.metadata
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
from typing import Any

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


def request(method: str, route: str, auth: bool = True) -> Any:
    """JSON answer of one API call; an HTTP error raises PlatformError with the service's message."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {token()}"
    call = urllib.request.Request(API + route, headers=headers, method=method)
    try:
        with urllib.request.urlopen(call, timeout=60) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        detail = error.read()[:500].decode("utf-8", errors="replace")
        error.close()
        raise PlatformError(f"{method} {route}: HTTP {error.code} {detail}") from None
    return json.loads(body) if body else None


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
    explorer = [platform_row(row) for row in get("/api/platforms/public/explorer", auth=False)]
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
    (out / "catalogue.json").write_text(json.dumps(catalogue, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{len(explorer)} Explorer platforms, {len(public)} public platforms")


def keys(value: Any) -> set[str]:
    """Every mapping key at any depth of a JSON value."""
    if isinstance(value, dict):
        return set(value) | {k for item in value.values() for k in keys(item)}
    if isinstance(value, list):
        return {k for item in value for k in keys(item)}
    return set()


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


def check_agents(catalogue: dict[str, Any], files: list[Path]) -> None:
    table = facts_table(catalogue)
    for path in files:
        text = path.read_text(encoding="utf-8")
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            raise SystemExit(f"{path}: needs one quandela-facts section")
        if text[text.index(BEGIN) + len(BEGIN) : text.index(END)] != table:
            raise SystemExit(f"{path}: the quandela-facts table differs from facts_table of the snapshot")


def load(directory: Path) -> dict[str, Any]:
    value: dict[str, Any] = json.loads((directory / "catalogue.json").read_text(encoding="utf-8"))
    return value


def check(directory: Path, agents: list[Path] | None = None) -> None:
    catalogue = load(directory)
    if catalogue["schema"] != CATALOGUE_SCHEMA:
        raise SystemExit(f"unexpected schema {catalogue['schema']}")
    for key in FORBIDDEN_KEYS:
        if key in keys(catalogue):
            raise SystemExit(f"snapshot carries {key}")
    counters = catalogue["account"]["availability"]
    if missing := [k for k in AVAILABILITY_KEYS if not isinstance(counters.get(k), int) or counters[k] < 0]:
        raise SystemExit(f"availability lacks {missing}")
    names = [row["name"] for row in catalogue["explorer_platforms"]]
    if len(set(names)) != len(names) or set(catalogue["processors"]) != set(names):
        raise SystemExit("processor records differ from the Explorer platforms")
    for row in catalogue["explorer_platforms"]:
        name = row["name"]
        if row["price_per_shot"] < 0 or row["max_duration"] <= 0:
            raise SystemExit(f"{name}: price {row['price_per_shot']} or duration {row['max_duration']}")
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
    if agents is not None:
        check_agents(catalogue, agents)
    print(f"qd snapshot: {len(names)} Explorer platforms, {len(catalogue['public_platforms'])} public platforms")


def self_test() -> None:
    root = Path(__file__).resolve().parent.parent
    source = root / "docs" / "evidence" / "quandela"
    agents = root / "AGENTS.md"
    check(source, [agents])

    def rewrite(path: Path, change: Callable[[Any], None]) -> None:
        value = json.loads(path.read_text(encoding="utf-8"))
        change(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def catalogue(change: Callable[[dict[str, Any]], None]) -> Callable[[Path, Path], None]:
        return lambda directory, _: rewrite(directory / "catalogue.json", change)

    def qpu(c: dict[str, Any]) -> dict[str, Any]:
        name = next(r["name"] for r in c["explorer_platforms"] if r["type"] == "qpu")
        specs: dict[str, Any] = c["processors"][name]["specs"]
        return specs

    def table(_: Path, copy: Path) -> None:
        text = copy.read_text(encoding="utf-8")
        copy.write_text(text.replace("| credits per shot |", "| price |", 1), encoding="utf-8")

    def stale_row(_: Path, copy: Path) -> None:
        text = copy.read_text(encoding="utf-8")
        copy.write_text(text.replace(END, "| stale | row |\n" + END, 1), encoding="utf-8")

    edits: dict[str, Callable[[Path, Path], None]] = {
        "token id": catalogue(lambda c: c["account"]["token_usage"].append({"token_id": 1})),
        "creator id": catalogue(lambda c: c["explorer_platforms"][0].update(maintenance={"creator_id": 1})),
        "missing processor": catalogue(lambda c: c["processors"].pop(c["explorer_platforms"][0]["name"])),
        "input mode outside the chip": catalogue(lambda c: qpu(c)["connected_input_modes"].append(99)),
        "photons off the connected modes": catalogue(lambda c: qpu(c)["constraints"].update(max_photon_count=1)),
        "negative price": catalogue(lambda c: c["explorer_platforms"][0].update(price_per_shot=-1)),
        "missing availability counter": catalogue(lambda c: c["account"]["availability"].pop("max_jobs_in_queue")),
        "edited table": table,
        "stale row": stale_row,
    }
    for label, edit in edits.items():
        with tempfile.TemporaryDirectory() as scratch:
            directory = Path(scratch) / "quandela"
            shutil.copytree(source, directory)
            copy = Path(scratch) / "AGENTS.md"
            shutil.copy(agents, copy)
            edit(directory, copy)
            try:
                check(directory, [copy])
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
