"""Open Quantum account reads and the retained catalogue the Open Quantum guides cite.

Open Quantum (Quantum Rings) brokers IonQ, Rigetti, IQM and AQT processors
through one management API (organizations, providers, backend classes, credit
balances) and one scheduler API (uploads, preparations, quotes, jobs). The
SDK and its MCP server live in their own environment,
OQ_PYTHON=${OQ_PYTHON:-$HOME/.local/share/openquantum/venv/bin/python}, built
from docs/notes/open_quantum/requirements-oq.txt; the SDK key file named by
OPENQUANTUM_SDK_KEY authenticates every read. Only check and facts run under
the repository's own $PYTHON; they import nothing from the Open Quantum stack.

Subcommands:

- snapshot --out DIR (network, read-only) writes catalogue.json: every
  provider, every backend class with its status, its constraint document
  (qubits, limits, native and supported operations, features, topology) and
  its job configuration schema, the job categories, the 13 MCP tools with
  their input schemas, and the organization count, credit balances and job
  count of the organization OPENQUANTUM_ORGANIZATION_ID names, else the first
  membership, the selection the MCP server spends on; every listing
  follows its pagination cursor, and it refuses to run unless
  OPENQUANTUM_SDK_KEY names a key file. Organization ids and names never
  enter the file. It also writes
  estimates.json, the scheduler's circuit-free price estimate
  (POST /v1/pricing/estimate with a backend class and a shot count, the call
  the pricing page's calculator makes) at ESTIMATE_SHOTS and each backend's
  shot bounds: every execution plan's price in credits and every queue
  priority's increase. The snapshot uploads no circuit and creates no
  preparation or job.
- check DIR [--agents FILE...] (offline) requires catalogue.json,
  estimates.json and pricing.json to carry their schema and no organization
  identity; a constraint document and shot schema on every backend whose
  limits agree with each other; exactly one pricing row per catalogue
  backend, each Private rate twice its Public rate; and every estimate to
  equal ceil(per_task + shots * per_shot) of its plan's USD-equivalent
  rates, one credit per USD-equivalent dollar, with exactly the rows the
  catalogue's shot grid names and one queue-priority list per plan across
  them. With --agents it renders
  facts_table and requires each FILE's open-quantum-facts markers to enclose
  exactly that table, so a refreshed catalogue, estimate or price list that
  changes a limit, a rate or the credit rule fails until AGENTS.md and the
  Open Quantum README change with it. Status, accepting_jobs and queue depth
  change between reads and stay out of the table; a fixed shot column a
  backend's bounds exclude renders as a dash.
- facts DIR prints the table.
- --self-test proves check rejects an organization id, a shot limit that
  disagrees with its schema, a missing and an extra pricing row, a Private
  rate off twice Public, an estimate off the credit rule or the grid, a
  quote missing a priority, an edited table
  and a stale row inside the markers, on a temporary copy.

Usage: OPENQUANTUM_SDK_KEY=KEY.json "$OQ_PYTHON" scripts/oq_platform.py snapshot --out DIR
       "$PYTHON" scripts/oq_platform.py (check DIR [--agents FILE...] | facts DIR | --self-test)
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import datetime
import json
import math
import os
import shutil
import sys
import tempfile
from collections.abc import Callable
from decimal import Decimal
from functools import partial
from pathlib import Path
from typing import Any

CATALOGUE_SCHEMA = "oq-catalogue-v1"
ESTIMATES_SCHEMA = "oq-estimates-v1"
PRICING_SCHEMA = "oq-pricing-v1"
MCP_TOOLS = 13
# Keys that name the account's organization; the snapshot drops them and
# check refuses a catalogue whose account, providers, backends or categories
# carry one. The MCP input schemas name organization_id as a parameter.
ORGANIZATION_KEYS = ("organization_id", "organization_name")
# Each 90-day Spark batch and each referral grants 25 credits.
SPARK_GRANT_CREDITS = 25
ESTIMATE_SHOTS = (100, 128, 1000, 1024, 4096)
TABLE_SHOTS = (128, 1024)
PLANS = {"Public Plan": "public", "Private Plan": "private"}
BEGIN = "<!-- open-quantum-facts:begin -->\n"
END = "<!-- open-quantum-facts:end -->"


def now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


def plain(value: Any) -> Any:
    """JSON form of an SDK model: dataclasses become dicts and extra merges into its record."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        record = {f.name: plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
        extra = record.pop("extra", None) or {}
        return {**record, **extra}
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [plain(v) for v in value]
    return value


def mcp_tools() -> list[dict[str, Any]]:
    from openquantum_mcp.server import mcp

    tools = asyncio.run(mcp.list_tools())
    return sorted(
        ({"name": t.name, "description": t.description, "input_schema": t.inputSchema} for t in tools),
        key=lambda t: t["name"],
    )


def shot_bounds(backend: dict[str, Any]) -> tuple[int, int, int]:
    shots = backend["configuration_schema"]["properties"]["shots"]
    return shots["minimum"], shots["default"], shots["maximum"]


def estimate_grid(backend: dict[str, Any]) -> list[int]:
    low, _, high = shot_bounds(backend)
    return sorted({low, high} | {n for n in ESTIMATE_SHOTS if low <= n <= high})


def estimates(scheduler: Any, backends: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for backend in backends:
        for shots in estimate_grid(backend):
            quote = scheduler._request(
                "POST", "/v1/pricing/estimate", json={"backend_class_id": backend["id"], "shots": shots}
            )["quote"]
            plans = {
                plan["name"]: {
                    "price": plan["price"],
                    "queue_priorities": {q["name"]: q["price_increase"] for q in plan["queue_priorities"]},
                }
                for plan in quote
            }
            rows.append({"short_code": backend["short_code"], "shots": shots, "plans": plans})
    return rows


def pages(listing: Callable[..., Any], field: str, *args: Any) -> list[Any]:
    """Every record of a cursor-paginated SDK listing, following pagination.next_cursor to the end."""
    records: list[Any] = []
    cursor = None
    while True:
        page = listing(*args, limit=100, cursor=cursor)
        records += getattr(page, field)
        cursor = page.pagination.next_cursor if page.pagination else None
        if not cursor:
            return records


def snapshot(out: Path) -> None:
    import openquantum_mcp
    import openquantum_sdk
    from openquantum_mcp.auth import build_clients

    # The resolver falls back to OPENQUANTUM_TOKEN and the client-id pair; the
    # snapshot binds its provenance to the named key file alone.
    key = os.environ.get("OPENQUANTUM_SDK_KEY")
    if not key or not Path(key).is_file():
        raise SystemExit("OPENQUANTUM_SDK_KEY must name the SDK key file the snapshot reads")
    clients = build_clients()
    management, scheduler = clients.management, clients.scheduler
    organizations = pages(management.list_user_organizations, "organizations")
    if not organizations:
        raise SystemExit("the SDK key reaches no organization")
    # The MCP server spends on OPENQUANTUM_ORGANIZATION_ID when it is set and
    # on the first membership otherwise; the snapshot reads the same one.
    configured = os.environ.get("OPENQUANTUM_ORGANIZATION_ID")
    chosen = [o for o in organizations if o.id == configured] if configured else organizations[:1]
    if not chosen:
        raise SystemExit("OPENQUANTUM_ORGANIZATION_ID names no organization of this SDK key")
    organization = chosen[0].id
    balance = management.get_credit_balance(organization)
    jobs = len(pages(partial(scheduler.list_jobs, organization_id=organization), "jobs"))
    backends = []
    listed = pages(management.list_backend_classes, "backend_classes")
    for summary in sorted(listed, key=lambda b: b.short_code):
        record = plain(summary)
        detail = scheduler.get_backend_class(summary.short_code)
        record["constraint_data"] = detail["constraint_data"]
        record["configuration_schema"] = detail["configuration_schema"]
        record["constraint_model_id"] = detail["constraint_model_id"]
        backends.append(record)
    categories = [plain(c) for c in pages(scheduler.get_job_categories, "categories")]
    for category in categories:
        subcategories = pages(scheduler.get_job_subcategories, "categories", category["id"])
        category["subcategories"] = [plain(s) for s in subcategories]
    retrieved = now()
    catalogue = {
        "schema": CATALOGUE_SCHEMA,
        "retrieved_utc": retrieved,
        "hosts": {"management": clients.config.management_base, "scheduler": clients.config.scheduler_base},
        "versions": {"openquantum-sdk": openquantum_sdk.__version__, "openquantum-mcp": openquantum_mcp.__version__},
        "account": {
            "organization_count": len(organizations),
            "organization_selection": "OPENQUANTUM_ORGANIZATION_ID" if configured else "first membership",
            "spark_credits": balance.spark_credits,
            "full_credits": balance.full_credits,
            "jobs": jobs,
        },
        "providers": sorted(
            (plain(p) for p in pages(management.list_providers, "providers")), key=lambda p: p["short_code"]
        ),
        "backend_classes": backends,
        "job_categories": sorted(categories, key=lambda c: c["short_code"]),
        "mcp_tools": mcp_tools(),
    }
    quotes = {"schema": ESTIMATES_SCHEMA, "retrieved_utc": retrieved, "rows": estimates(scheduler, backends)}
    out.mkdir(parents=True, exist_ok=True)
    for name, value in (("catalogue.json", catalogue), ("estimates.json", quotes)):
        (out / name).write_text(json.dumps(value, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{len(backends)} backend classes, {len(quotes['rows'])} estimates, {len(catalogue['mcp_tools'])} MCP tools")


def keys(value: Any) -> set[str]:
    """Every mapping key at any depth of a JSON value."""
    if isinstance(value, dict):
        return set(value) | {k for item in value.values() for k in keys(item)}
    if isinstance(value, list):
        return {k for item in value for k in keys(item)}
    return set()


def usd(value: float) -> str:
    return f"{value:g}"


def credits(price: dict[str, Any], plan: str, shots: int) -> int:
    """Credits of one job: the USD-equivalent price rounded up to a whole credit."""
    task, shot = Decimal(str(price[f"per_task_{plan}"])), Decimal(str(price[f"per_shot_{plan}"]))
    return math.ceil(task + shots * shot)


def one_credit_shots(price: dict[str, Any], low: int, high: int) -> str:
    """Largest shot count a 1-credit Public job carries, or a dash below the backend's minimum."""
    task, shot = Decimal(str(price["per_task_public"])), Decimal(str(price["per_shot_public"]))
    shots = min(high, int((1 - task) / shot))
    return str(shots) if shots >= low else "-"


def facts_table(catalogue: dict[str, Any], quotes: dict[str, Any], pricing: dict[str, Any]) -> str:
    """Markdown table of each backend's limits and its measured Public credit cost."""
    prices = {row["short_code"]: row for row in pricing["backends"]}
    measured = {(r["short_code"], r["shots"]): r["plans"]["Public Plan"]["price"] for r in quotes["rows"]}
    lines = [
        "| backend (short code) | provider, modality | qubits (per job) | native ops | shots min / default / max "
        "| circuits per job | Public USD task + per shot | Public credits at 128 / 1024 / max shots "
        "| shots in a 1-credit job | 1024-shot jobs per 25 Spark |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for b in catalogue["backend_classes"]:
        code, data = b["short_code"], b["constraint_data"]
        low, default, high = shot_bounds(b)
        price = prices[code]
        cost = [measured.get((code, n)) for n in (*TABLE_SHOTS, high)]
        native = ", ".join(sorted(op["name"] for op in data["native_ops"] if op["name"] != "barrier"))
        per_job = data["limits"]["max_qubits_per_job"]
        qubits = f"{data['n_qubits']}" if per_job == data["n_qubits"] else f"{data['n_qubits']} ({per_job} per job)"
        lines.append(
            f"| {b['name']} (`{code}`) | {price['provider_name']}, {price['modality']} "
            f"| {qubits} | {native} | {low} / {default} / {high} | {data['limits']['max_circuits']} "
            f"| {usd(price['per_task_public'])} + {usd(price['per_shot_public'])} "
            f"| {' / '.join('-' if c is None else str(c) for c in cost)} | {one_credit_shots(price, low, high)} "
            f"| {'-' if cost[1] is None else SPARK_GRANT_CREDITS // cost[1]} |"
        )
    features = sorted({f for b in catalogue["backend_classes"] for f in b["constraint_data"]["features"]})
    rows = [
        f"{f}: "
        + ", ".join(b["short_code"] for b in catalogue["backend_classes"] if f in b["constraint_data"]["features"])
        for f in features
    ]
    surcharges = sorted(
        {
            f"{plan} {name} +{increase}"
            for r in quotes["rows"]
            for plan, entry in r["plans"].items()
            for name, increase in entry["queue_priorities"].items()
        }
    )
    return (
        "\n".join(lines)
        + "\n\nFeatures by backend: "
        + "; ".join(rows)
        + ".\n\nQueue priority increases in credits: "
        + ", ".join(surcharges)
        + ".\n"
    )


def check_agents(catalogue: dict[str, Any], quotes: dict[str, Any], pricing: dict[str, Any], files: list[Path]) -> None:
    table = facts_table(catalogue, quotes, pricing)
    for path in files:
        text = path.read_text(encoding="utf-8")
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            raise SystemExit(f"{path}: needs one open-quantum-facts section")
        if text[text.index(BEGIN) + len(BEGIN) : text.index(END)] != table:
            raise SystemExit(f"{path}: the open-quantum-facts table differs from facts_table of the snapshot")


def load(directory: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    values = [json.loads((directory / f).read_text(encoding="utf-8")) for f in ("catalogue.json", "estimates.json")]
    pricing = json.loads((directory / "pricing.json").read_text(encoding="utf-8"))
    return values[0], values[1], pricing


def check(directory: Path, agents: list[Path] | None = None) -> None:
    catalogue, quotes, pricing = load(directory)
    schemas = (catalogue["schema"], quotes["schema"], pricing["schema"])
    if schemas != (CATALOGUE_SCHEMA, ESTIMATES_SCHEMA, PRICING_SCHEMA):
        raise SystemExit(f"unexpected schema {schemas}")
    present = keys([catalogue[k] for k in ("account", "providers", "backend_classes", "job_categories")])
    for key in ORGANIZATION_KEYS:
        if key in present or key in keys(quotes):
            raise SystemExit(f"snapshot carries {key}")
    if len(catalogue["mcp_tools"]) != MCP_TOOLS:
        raise SystemExit(f"catalogue lists {len(catalogue['mcp_tools'])} MCP tools, expected {MCP_TOOLS}")
    prices = {row["short_code"]: row for row in pricing["backends"]}
    if len(prices) != len(pricing["backends"]):
        raise SystemExit("pricing.json lists a backend twice")
    listed = {b["short_code"] for b in catalogue["backend_classes"]}
    if set(prices) != listed:
        raise SystemExit(f"pricing rows {sorted(set(prices) ^ listed)} differ from the catalogue's backend classes")
    for code, row in prices.items():
        # The guides read the "$50" grant as 25 credits at the Private rate.
        for part in ("task", "shot"):
            public, private = (Decimal(str(row[f"per_{part}_{plan}"])) for plan in ("public", "private"))
            if private != 2 * public:
                raise SystemExit(f"{code}: Private per_{part} {private} is not twice Public {public}")
    quoted = {(r["short_code"], r["shots"]): r["plans"] for r in quotes["rows"]}
    for b in catalogue["backend_classes"]:
        name, data = b["short_code"], b["constraint_data"]
        low, default, high = shot_bounds(b)
        limits = data["limits"]
        if (low, high) != (limits["min_shots"], limits["max_shots"]):
            raise SystemExit(f"{name}: shot schema {low}..{high} differs from its limits")
        if not low <= default <= high:
            raise SystemExit(f"{name}: default shots {default} outside its schema")
        if data["max_qubits"] != data["n_qubits"] or limits["max_qubits_per_job"] > data["n_qubits"]:
            raise SystemExit(f"{name}: qubit limits disagree")
        for edge in data["topology"]["coupling_map"]:
            if len(edge) != 2 or not all(0 <= q < data["n_qubits"] for q in edge):
                raise SystemExit(f"{name}: coupling edge {edge}")
        for shots in estimate_grid(b):
            plans = quoted.get((name, shots))
            if plans is None or set(plans) != set(PLANS):
                raise SystemExit(f"{name}: no Public and Private estimate at {shots} shots")
            for plan, rate in PLANS.items():
                expected = credits(prices[name], rate, shots)
                if plans[plan]["price"] != expected:
                    raise SystemExit(f"{name} {shots} shots: {plan} {plans[plan]['price']} credits, rule {expected}")
    if len(quoted) != len(quotes["rows"]):
        raise SystemExit("estimates repeat a backend and shot count")
    grid = {(b["short_code"], n) for b in catalogue["backend_classes"] for n in estimate_grid(b)}
    if stray := sorted(set(quoted) - grid):
        raise SystemExit(f"estimate {stray[0]} lies outside the catalogue's shot grid")
    # facts_table states one priority list per plan, so every quote offers it.
    for plan in PLANS:
        offered = {json.dumps(plans[plan]["queue_priorities"], sort_keys=True) for plans in quoted.values()}
        if len(offered) != 1:
            raise SystemExit(f"{plan} queue priorities differ between estimates: {sorted(offered)}")
    if agents is not None:
        check_agents(catalogue, quotes, pricing, agents)
    print(
        f"oq snapshot: {len(catalogue['backend_classes'])} backend classes, "
        f"{len(quotes['rows'])} estimates on the ceil credit rule"
    )


def self_test() -> None:
    root = Path(__file__).resolve().parent.parent
    source = root / "docs" / "evidence" / "open_quantum"
    agents = root / "AGENTS.md"
    check(source, [agents])

    def rewrite(path: Path, change: Callable[[Any], None]) -> None:
        value = json.loads(path.read_text(encoding="utf-8"))
        change(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def organization_id(directory: Path, _: Path) -> None:
        rewrite(directory / "catalogue.json", lambda c: c["account"].update(organization_id="x"))

    def shot_limit(directory: Path, _: Path) -> None:
        def change(catalogue: dict[str, Any]) -> None:
            catalogue["backend_classes"][0]["constraint_data"]["limits"]["max_shots"] = 1

        rewrite(directory / "catalogue.json", change)

    def unpriced(directory: Path, _: Path) -> None:
        rewrite(directory / "pricing.json", lambda p: p["backends"].pop())

    def extra_price(directory: Path, _: Path) -> None:
        rewrite(directory / "pricing.json", lambda p: p["backends"].append({**p["backends"][0], "short_code": "x:y"}))

    def private_rate(directory: Path, _: Path) -> None:
        rewrite(directory / "pricing.json", lambda p: p["backends"][0].update(per_shot_private=1))

    def off_rule(directory: Path, _: Path) -> None:
        def change(quotes: dict[str, Any]) -> None:
            quotes["rows"][0]["plans"]["Public Plan"]["price"] += 1

        rewrite(directory / "estimates.json", change)

    def stray_estimate(directory: Path, _: Path) -> None:
        rewrite(directory / "estimates.json", lambda q: q["rows"].append({**q["rows"][0], "shots": 3}))

    def dropped_priority(directory: Path, _: Path) -> None:
        def change(quotes: dict[str, Any]) -> None:
            quotes["rows"][0]["plans"]["Public Plan"]["queue_priorities"].pop("Priority Queue")

        rewrite(directory / "estimates.json", change)

    def table(_: Path, copy: Path) -> None:
        text = copy.read_text(encoding="utf-8")
        copy.write_text(text.replace("| 1024-shot jobs per 25 Spark |", "| jobs |", 1), encoding="utf-8")

    def stale_row(_: Path, copy: Path) -> None:
        text = copy.read_text(encoding="utf-8")
        copy.write_text(text.replace(END, "| stale | row |\n" + END, 1), encoding="utf-8")

    edits = (
        organization_id,
        shot_limit,
        unpriced,
        extra_price,
        private_rate,
        off_rule,
        stray_estimate,
        dropped_priority,
        table,
        stale_row,
    )
    for edit in edits:
        with tempfile.TemporaryDirectory() as scratch:
            directory = Path(scratch) / "open_quantum"
            shutil.copytree(source, directory)
            copy = Path(scratch) / "AGENTS.md"
            shutil.copy(agents, copy)
            edit(directory, copy)
            try:
                check(directory, [copy])
            except SystemExit:
                continue
            raise AssertionError(f"check accepted {edit.__name__}")
    print(f"oq_platform self-test: {len(edits)} rejections")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("snapshot")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("check")
    p.add_argument("directory", type=Path)
    p.add_argument("--agents", type=Path, nargs="+", help="files carrying the open-quantum-facts section")
    p = sub.add_parser("facts")
    p.add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.command == "snapshot":
        snapshot(args.out)
    elif args.command == "check":
        check(args.directory, args.agents)
    elif args.command == "facts":
        print(facts_table(*load(args.directory)), end="")
    else:
        parser.error("a subcommand or --self-test is required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
