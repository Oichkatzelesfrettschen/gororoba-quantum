"""Mathematical proof origins remain independent of finite and formal evidence."""

from typing import Any

import pytest
import research_state


@pytest.mark.parametrize(
    "status,origin",
    [
        ("established", "repository-written"),
        ("established", "external-source"),
        ("open", "unproved-open"),
        ("superseded", "unproved-open"),
        ("superseded", "repository-written"),
    ],
)
def test_valid_proof_origin(status: str, origin: str) -> None:
    research_state._validate_proof_origin(
        {"id": "fixture", "evidence_class": "mathematical claim", "status": status, "proof_origin": origin}
    )


@pytest.mark.parametrize(
    "kind,status,origin",
    [
        ("mathematical claim", "established", None),
        ("mathematical claim", "established", "unproved-open"),
        ("mathematical claim", "open", "repository-written"),
        ("mathematical claim", "established", "peer-reviewed"),
        ("exact finite certificate", "established", "repository-written"),
        ("machine-checked proof", "established", "external-source"),
    ],
)
def test_invalid_proof_origin(kind: str, status: str, origin: Any) -> None:
    claim = {"id": "fixture", "evidence_class": kind, "status": status}
    if origin is not None:
        claim["proof_origin"] = origin
    with pytest.raises(ValueError, match="proof_origin"):
        research_state._validate_proof_origin(claim)
