"""Retain public Quandela API schemas and recursively inventory their contracts.

Only the three literal public OpenAPI URLs are fetched. Inventoried operations
remain descriptions: the inventory executes neither jobs nor QRNG/token routes.
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
    parser.add_argument("--capture", action="store_true", help="GET only the three public OpenAPI documents")
    parser.add_argument("--portal-map", action="store_true", help="also GET and map the public WebIDE index bundle")
    arguments = parser.parse_args()
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
    if arguments.portal_map:
        from capture_qd_docs import WEBIDE, bundle

        url, data = bundle(WEBIDE)
        retain(
            arguments.directory / "portal-route-map.json",
            (json.dumps(portal_routes(data, url), indent=1, sort_keys=True) + "\n").encode(),
        )
    print(json.dumps(records, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
