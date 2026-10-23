"""The repository adapter preserves backend capacity, filtered pagination and error semantics."""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any

import pytest


def adapter() -> Any:
    try:
        return importlib.import_module("oq_mcp_server")
    except ModuleNotFoundError:
        pytest.fail("the repository-owned Open Quantum adapter is absent")


def test_nested_constraints_keep_nominal_and_usable_capacity_separate() -> None:
    module = adapter()
    constraints = {
        "n_qubits": 108,
        "max_qubits": 108,
        "limits": {"max_qubits_per_job": 107},
        "native_ops": [{"name": "cz"}],
        "features": {"barriers": True},
    }
    forward = module.constraint_summary(constraints)
    backward = module.constraint_summary(dict(reversed(list(constraints.items()))))
    if forward != backward or forward["physical_qubits"] != 108 or forward["max_qubits_per_job"] != 107:
        raise AssertionError("constraint order changed capacity, or nominal width replaced job width")
    if forward["native_ops"] != [{"name": "cz"}] or forward["limits"] != {"max_qubits_per_job": 107}:
        raise AssertionError("the summary discarded nested constraints")


def test_filtered_catalogue_scans_past_a_nonmatching_first_page() -> None:
    module = adapter()
    offline = SimpleNamespace(
        id="a",
        name="offline",
        short_code="a",
        type="QPU",
        status="Offline",
        accepting_jobs=False,
        queue_depth=0,
        provider_id="p",
        description="",
    )
    online = SimpleNamespace(
        id="b",
        name="online",
        short_code="b",
        type="QPU",
        status="Online",
        accepting_jobs=True,
        queue_depth=0,
        provider_id="p",
        description="",
    )

    class Management:
        def list_backend_classes(self, *, limit: int, cursor: str | None) -> Any:
            return SimpleNamespace(
                backend_classes=[offline] if cursor is None else [online],
                pagination=SimpleNamespace(next_cursor="next" if cursor is None else None),
            )

    class Scheduler:
        def get_backend_class(self, code: str) -> dict[str, Any]:
            return {"constraint_data": {"n_qubits": 36, "limits": {"max_qubits_per_job": 36}}}

    service = SimpleNamespace(management=Management(), scheduler=Scheduler())
    result = module.backend_catalogue(service, limit=1)
    if len(result["backends"]) != 1 or result["backends"][0]["short_code"] != "b":
        raise AssertionError("pagination stopped on unfiltered backend count")
    if result["backends"][0]["max_qubits_per_job"] != 36:
        raise AssertionError("the catalogue lost the scheduler constraint document")


def test_unknown_capacity_stays_unknown() -> None:
    result = adapter().constraint_summary({})
    if result["physical_qubits"] is not None or result["max_qubits_per_job"] is not None:
        raise AssertionError("missing capacity became a guessed capacity")


def test_vendor_error_text_becomes_an_exception() -> None:
    with pytest.raises(ValueError, match="permission denied"):
        adapter().decoded_result('{"error": "permission denied", "error_type": "AuthError"}')


def test_vendor_success_is_preserved() -> None:
    if adapter().decoded_result('{"estimated_credits": 5}') != {"estimated_credits": 5}:
        raise AssertionError("the adapter changed a vendor quote")
