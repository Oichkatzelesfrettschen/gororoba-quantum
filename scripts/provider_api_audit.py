"""Capture read-only provider facts into a new, digest-checked audit directory.

The Open Quantum snapshot includes circuit-free pricing queries; it uploads no
circuit and creates no preparation or job. IQM uses GET and read-only GraphQL.
Quandela uses catalogue, processor and token-usage reads only. Existing source
captures remain unchanged. Capture requires the documented provider credential
environment variables and the Open Quantum interpreter; check is SDK-free.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CAPTURE_FILES = frozenset(
    {"iqm.json", "quandela.json"}
    | {f"open-quantum/{name}.json" for name in ("catalogue", "estimates", "pricing", "pricing-sources")}
)


def digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def stamp() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def capture(out: Path) -> None:
    import capture_oq_docs as sources
    import iqm_platform as iqm
    import oq_platform as oq
    import qd_platform as qd

    if out.exists():
        raise ValueError("capture requires a new directory; retained observations are immutable")
    out.mkdir(parents=True)
    started = stamp()
    connection = iqm.Client(iqm.read_tokens(iqm.tokens_path())["access_token"])
    calls = []

    def read(path: str) -> Any:
        begin = stamp()
        status, body = connection.get(path)
        calls.append(
            {
                "path": path,
                "status": status,
                "request_started_utc": begin,
                "retrieved_utc": stamp(),
                "body_sha256": digest(body),
            }
        )
        if status != 200:
            raise ValueError(f"IQM {path} answered {status}")
        return json.loads(body)

    general = read("api/v1/openapi.json")
    original = json.loads((ROOT / "docs/evidence/iqm/server/openapi.json").read_text())
    computers = read("api/v1/quantum-computers")
    devices = {}
    for alias in ("emerald", "garnet", "sirius"):
        base = "api/v1/quantum-computers/" + alias
        details = read(base)
        schema = read("api/v1/openapi.json?qc=" + alias)
        calibration = read(f"api/v1/calibration-sets/{alias}/default")
        identity = calibration["observation_set_id"]
        architecture = read(f"api/v1/calibration-sets/{alias}/{identity}/dynamic-quantum-architecture")
        metrics = read(f"api/v1/calibration-sets/{alias}/{identity}/metrics")
        if architecture["calibration_set_id"] != identity or metrics["describes_id"] != identity:
            raise ValueError(f"{alias}: calibration identity mismatch")
        devices[alias] = {
            "details": details,
            "calibration_set_id": identity,
            "architecture": architecture,
            "metrics": metrics,
            "openapi": schema,
            "queue_availability": read(base + "/queue-availability"),
        }
    graph = connection.graphql(iqm.GRAPHQL_INTROSPECTION)
    account = connection.graphql("{ me { currentAccount { id type } } }")["me"]["currentAccount"]
    credit = connection.graphql(
        "query($a: UUID!){ credit(accountId: $a) { currentBalance expiresAt } }", {"a": account["id"]}
    )["credit"]
    write(
        out / "iqm.json",
        {
            "request_started_utc": started,
            "retrieved_utc": stamp(),
            "general_openapi": general,
            "general_schema_matches_retained": general == original,
            "graphql_schema": graph,
            "computers": computers,
            "devices": devices,
            "account": {"type": account["type"], "credit": credit},
            "reads": calls,
        },
    )

    oq.snapshot(out / "open-quantum")
    pricing_page = sources.fetch(sources.SITE + "pricing")
    flight = sources.flight_text(pricing_page.decode())
    position = flight.find('{"summary":')
    if position < 0:
        raise ValueError("the live pricing page has no recognized summary")
    table = json.JSONDecoder().raw_decode(flight, position)[0]["summary"]["tableRows"]
    old_price = json.loads((ROOT / "docs/evidence/open_quantum/pricing.json").read_text())
    pricing_sources, findings = sources.pricing_sources(pricing_page.decode(), stamp())
    prices = {
        **old_price,
        "retrieved_utc": stamp(),
        "html_sha256": digest(pricing_page),
        "backends": sorted(
            ({key: row[key] for key in sources.TABLE_FIELDS} for row in table), key=lambda row: row["short_code"]
        ),
        **findings,
    }
    write(out / "open-quantum/pricing.json", prices)
    write(out / "open-quantum/pricing-sources.json", pricing_sources)
    oq.check(out / "open-quantum")

    qd_started = stamp()
    qd_record = {
        "request_started_utc": qd_started,
        "explorer": [qd.platform_row(row) for row in qd.get("/api/platforms/public/explorer", auth=False)],
        "processors": {name: qd.get(qd.platform_route(name)) for name in ("qpu:ascella", "qpu:belenos")},
        "availability": qd.availability(),
        "token_usage": qd.usage_rows(qd.get("/api/tokens/usage/report")),
    }
    qd_record["retrieved_utc"] = stamp()
    write(out / "quandela.json", qd_record)
    files = {str(path.relative_to(out)): digest(path.read_bytes()) for path in sorted(out.rglob("*.json"))}
    write(
        out / "index.json",
        {
            "schema": "provider-api-audit-v1",
            "request_started_utc": started,
            "retrieved_utc": stamp(),
            "files": files,
            "scope": "read-only provider observations and circuit-free estimates; no upload, job or booking",
        },
    )
    check(out)


def check(root: Path) -> None:
    index = json.loads((root / "index.json").read_text())
    if index.get("schema") != "provider-api-audit-v1" or not index.get("files"):
        raise ValueError("invalid provider audit manifest")
    for name in index["files"]:
        path = root / name
        if Path(name).is_absolute() or ".." in Path(name).parts or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("audit manifest path escapes its root")
    if set(index["files"]) != CAPTURE_FILES:
        raise ValueError("audit manifest membership differs from the required capture files")
    actual = {str(path.relative_to(root)) for path in root.rglob("*.json")}
    if actual - {"index.json", "packing.json"} != CAPTURE_FILES:
        raise ValueError("audit directory membership differs from the manifest")
    for name, expected in index["files"].items():
        path = root / name
        if digest(path.read_bytes()) != expected:
            raise ValueError(f"audit digest mismatch: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if (args.capture is None) == (args.check is None):
        parser.error("select exactly one of --capture or --check")
    if args.capture is not None:
        capture(args.capture)
    else:
        check(args.check)


if __name__ == "__main__":
    main()
