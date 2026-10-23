"""Repository-owned Open Quantum stdio adapter over the pinned vendor SDK/tools.

The adapter preserves vendor submission, credit-cap and confirmation logic. It
repairs catalogue filtering and constraint summaries, adds observation intervals,
and converts vendor JSON error values into MCP errors. Run with OQ_PYTHON;
importing the pure normalization helpers requires neither credentials nor SDK.
"""

from __future__ import annotations

import datetime
import functools
import json
from collections.abc import Callable
from typing import Any

TOOLS = (
    "list_organizations",
    "get_credits",
    "list_backends",
    "get_backend",
    "list_job_categories",
    "list_jobs",
    "get_job",
    "prepare_job",
    "submit_job",
    "wait_for_job",
    "get_job_results",
    "get_job_calibration",
    "cancel_job",
)
WRITES = {"prepare_job", "submit_job", "cancel_job"}


def constraint_summary(constraints: dict[str, Any]) -> dict[str, Any]:
    limits = constraints.get("limits") or {}
    return {
        "physical_qubits": constraints.get("n_qubits"),
        "max_qubits_per_job": limits.get("max_qubits_per_job"),
        "limits": limits,
        "native_ops": constraints.get("native_ops"),
        "features": constraints.get("features"),
        "supported_formats": constraints.get("supported_formats"),
        "timing": constraints.get("timing"),
        "noise": constraints.get("noise"),
        "omitted_fields": sorted(
            set(constraints) - {"n_qubits", "limits", "native_ops", "features", "supported_formats", "timing", "noise"}
        ),
    }


def backend_detail(service: Any, backend_class_id: str) -> dict[str, Any]:
    record = service.scheduler.get_backend_class(backend_class_id)
    constraints = record.get("constraint_data") or record.get("constraints") or {}
    return {
        "backend": {key: value for key, value in record.items() if key not in ("constraint_data", "constraints")},
        "constraint_summary": constraint_summary(constraints),
    }


def backend_catalogue(
    service: Any,
    online_only: bool = True,
    device_type: str | None = None,
    name_contains: str | None = None,
    max_qubits: int | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000")
    results = []
    cursor = None
    visited: set[str] = set()
    while True:
        page = service.management.list_backend_classes(limit=50, cursor=cursor)
        for backend in page.backend_classes:
            status = (backend.status or "").lower()
            if online_only and (backend.accepting_jobs is False or status in ("offline", "unavailable", "maintenance")):
                continue
            if device_type and (backend.type or "").lower() != device_type.lower():
                continue
            if (
                name_contains
                and name_contains.lower() not in f"{backend.name} {backend.short_code} {backend.description}".lower()
            ):
                continue
            summary = backend_detail(service, backend.short_code)["constraint_summary"]
            width = summary["physical_qubits"]
            if max_qubits is not None and width is not None and width > max_qubits:
                continue
            results.append(
                {
                    "id": backend.id,
                    "name": backend.name,
                    "short_code": backend.short_code,
                    "type": backend.type,
                    "status": backend.status,
                    "accepting_jobs": backend.accepting_jobs,
                    "queue_depth": backend.queue_depth,
                    "provider_id": backend.provider_id,
                    "qubits": summary["physical_qubits"],
                    **summary,
                }
            )
            if len(results) == limit:
                return {
                    "backends": results,
                    "count": len(results),
                    "limit_reached": True,
                    "capacity_filter": "physical qubit count where known; unknown counts retained",
                }
        cursor = page.pagination.next_cursor if page.pagination else None
        if not cursor:
            return {
                "backends": results,
                "count": len(results),
                "limit_reached": False,
                "capacity_filter": "physical qubit count where known; unknown counts retained",
            }
        if cursor in visited:
            raise ValueError("backend pagination repeated a cursor")
        visited.add(cursor)


def decoded_result(value: str) -> Any:
    result = json.loads(value)
    if isinstance(result, dict) and "error" in result:
        raise ValueError(str(result["error"]))
    return result


def build_server() -> Any:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.exceptions import ToolError
    from mcp.types import ToolAnnotations
    from openquantum_mcp import server as vendor
    from openquantum_mcp.auth import redact_secrets

    server = FastMCP("openquantum")

    def wrap(name: str, original: Callable[..., str]) -> Callable[..., str]:
        @functools.wraps(original)
        def observed(*args: Any, **kwargs: Any) -> str:
            started = datetime.datetime.now(datetime.UTC).isoformat()
            try:
                if name == "list_backends":
                    result = backend_catalogue(vendor.get_service(), *args, **kwargs)
                elif name == "get_backend":
                    result = backend_detail(vendor.get_service(), *args, **kwargs)
                else:
                    result = decoded_result(original(*args, **kwargs))
                if isinstance(result, dict):
                    result["_observation"] = {
                        "request_started_utc": started,
                        "retrieved_utc": datetime.datetime.now(datetime.UTC).isoformat(),
                        "tool": name,
                    }
                return json.dumps(result, default=str)
            except Exception as error:
                raise ToolError(f"{name}: {redact_secrets(str(error))}") from error

        return observed

    for name in TOOLS:
        server.add_tool(
            wrap(name, getattr(vendor, name)),
            name=name,
            annotations=ToolAnnotations(readOnlyHint=name not in WRITES, openWorldHint=True),
        )
    return server


if __name__ == "__main__":
    build_server().run("stdio")
