"""Retain public Quandela API schemas and recursively inventory their contracts.

Captures fetch the three literal public OpenAPI URLs and the public WebIDE
bundle. Inventoried operations remain descriptions; jobs and QRNG/token
routes are never executed by the inventory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

DOCUMENTS = {
    "cloud": "https://api.cloud.quandela.com/openapi.json",
    "toolbox": "https://api.cloud.quandela.com/qt-openapi.json",
    "account": "https://api.account.quandela.com/openapi.json",
}
METHODS = frozenset({"get", "post", "put", "patch", "delete", "head", "options", "trace"})
PORTAL_MAP_SHA256 = "29842b690e3fd8a48fa3d36286c5f7ec7258ba9639a62f9f5b6410a9f91c7262"
HISTORICAL_DIRECTORY = Path(__file__).resolve().parents[1] / "docs/evidence/quandela/input-port-api-audit"
CAPTURE_LEDGER = "capture-sha256.json"
HISTORICAL_DIGESTS = {
    "cloud-openapi.json": "d444026d3d2735c4eee078410e001efe67863d670b55aaa0696e8f440540ab2f",
    "toolbox-openapi.json": "a1fe41a393a997f6bd764f05043e7a6478fa295806c5aab0b733944896d2d279",
    "account-openapi.json": "eecb463e7e8c53dc2d39b1ce2f3c07a9684210b82757584d0e877f6b4baac65a",
    "portal-route-map.json": PORTAL_MAP_SHA256,
}


def capture_digests(directory: Path) -> dict[str, str]:
    """The reviewed historical source uses code pins; successors use their own retained ledger."""
    ledger = directory / CAPTURE_LEDGER
    if directory.resolve() == HISTORICAL_DIRECTORY.resolve() or not ledger.exists():
        return dict(HISTORICAL_DIGESTS)
    record = json.loads(ledger.read_bytes())
    digests = record.get("sha256")
    if (
        record.get("schema") != "quandela-api-capture-sha256-v1"
        or not isinstance(digests, dict)
        or set(digests) != set(HISTORICAL_DIGESTS)
        or any(not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None for value in digests.values())
    ):
        raise ValueError("the capture digest ledger schema or file set differs")
    return digests


def portal_routes(data: bytes, url: str) -> dict[str, Any]:
    """Map literal request$1 call sites without treating lexical matches as an API contract."""
    source = data.decode("utf-8")
    routes = []
    for match in re.finditer(r'request\$1\.(get|post|put|patch|delete)\((`[^`]+`|"[^"]+")', source):
        method, literal = match.groups()
        if "/api/" in literal:
            routes.append({"method": method.upper(), "literal": literal[1:-1], "offset": match.start()})
    return {
        "schema": "quandela-portal-lexical-routes-v1",
        "source_url": url,
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "source_bytes": len(data),
        "routes": routes,
        "hardware_terms": {
            term: term in source for term in ["hardware_config", "hardware_info", "circuit_input_ports"]
        },
        "boundary": (
            "literal call-site map; does not prove endpoint coverage, authentication scope or runtime reachability"
        ),
    }


def inventory(document: dict[str, Any], strict_references: bool = True) -> dict[str, Any]:
    """Walk every schema node and operation, checking each local JSON reference."""
    references: set[str] = set()
    unresolved: set[str] = set()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            reference = node.get("$ref")
            if reference is not None:
                if not isinstance(reference, str) or not reference.startswith("#/"):
                    raise ValueError(f"external or malformed reference requires separate retrieval: {reference!r}")
                target: Any = document
                try:
                    for token in reference[2:].split("/"):
                        target = target[token.replace("~1", "/").replace("~0", "~")]
                except (KeyError, TypeError) as error:
                    if strict_references:
                        raise ValueError(f"unresolved schema reference: {reference}") from error
                    unresolved.add(reference)
                references.add(reference)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(document)
    operations = []
    for path, entry in sorted(document.get("paths", {}).items()):
        for method, operation in sorted(entry.items()):
            if method not in METHODS:
                continue
            effect = "external-mutation"
            if method in {"get", "head", "options"}:
                effect = "documented-read"
                if path.endswith("/logout"):
                    effect = "session-mutation"
                elif "/qrng/" in path or "notebook" in path:
                    effect = "potentially-charged-read"
                elif "token" in path or "oauth" in path:
                    effect = "credential-read"
            operations.append(
                {
                    "path": path,
                    "method": method.upper(),
                    "effect": effect,
                    "summary": operation.get("summary", ""),
                    "description": operation.get("description", ""),
                    "security": operation.get("security", document.get("security", [])),
                    "parameters": entry.get("parameters", []) + operation.get("parameters", []),
                    "requestBody": operation.get("requestBody"),
                    "responses": operation.get("responses", {}),
                    "executed": False,
                }
            )
    return {
        "schema": "quandela-api-contract-inventory-v1",
        "api_version": document.get("info", {}).get("version"),
        "operations": operations,
        "local_references": sorted(references),
        "unresolved_references": sorted(unresolved),
        "schemas": document.get("components", {}).get("schemas", {}),
        "security_schemes": document.get("components", {}).get("securitySchemes", {}),
        "boundary": "schema traversal and operation classification; operation descriptions are not runtime evidence",
    }


def retain(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"retained bytes differ: {path.name}; choose a new capture directory")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--capture", action="store_true", help="GET the three public schemas and WebIDE bundle")
    parser.add_argument("--portal-map", action="store_true", help="also GET and map the public WebIDE index bundle")
    arguments = parser.parse_args()
    if arguments.capture and arguments.directory.exists() and any(arguments.directory.iterdir()):
        raise ValueError("a fresh capture requires a new or empty destination")
    expected = None if arguments.capture else capture_digests(arguments.directory)
    records = []
    for name, url in DOCUMENTS.items():
        path = arguments.directory / f"{name}-openapi.json"
        if arguments.capture:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = response.read(16 * 1024 * 1024 + 1)
            if len(data) > 16 * 1024 * 1024:
                raise ValueError("OpenAPI response exceeds the capture bound")
            retain(path, data)
        data = path.read_bytes()
        if expected is not None and hashlib.sha256(data).hexdigest() != expected[path.name]:
            raise ValueError(f"the retained capture bytes differ from their digest: {path.name}")
        record = inventory(json.loads(data), strict_references=False)
        record.update(source_url=url, source_sha256=hashlib.sha256(data).hexdigest())
        encoded = (json.dumps(record, indent=1, sort_keys=True) + "\n").encode()
        retain(arguments.directory / f"{name}-inventory.json", encoded)
        records.append(
            {
                "document": name,
                "operations": len(record["operations"]),
                "unresolved_references": record["unresolved_references"],
                "sha256": record["source_sha256"],
            }
        )
    if arguments.portal_map or arguments.capture:
        from capture_qd_docs import WEBIDE, bundle

        url, data = bundle(WEBIDE)
        retain(
            arguments.directory / "portal-route-map.json",
            (json.dumps(portal_routes(data, url), indent=1, sort_keys=True) + "\n").encode(),
        )
    portal = arguments.directory / "portal-route-map.json"
    if arguments.capture:
        digests = {
            name: hashlib.sha256((arguments.directory / name).read_bytes()).hexdigest() for name in HISTORICAL_DIGESTS
        }
        retain(
            arguments.directory / CAPTURE_LEDGER,
            (
                json.dumps({"schema": "quandela-api-capture-sha256-v1", "sha256": digests}, indent=1, sort_keys=True)
                + "\n"
            ).encode(),
        )
    elif expected is not None and hashlib.sha256(portal.read_bytes()).hexdigest() != expected[portal.name]:
        raise ValueError("the retained portal capture bytes differ from their digest")
    print(json.dumps(records, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
