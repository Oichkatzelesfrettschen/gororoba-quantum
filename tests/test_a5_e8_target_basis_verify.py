"""Bounded admission mutations for the E8 standard-monomial basis source bindings."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any

import pytest
from flint import nmod_mpoly_ctx

ROOT = Path(__file__).resolve().parents[1]
LADDER = ROOT / "docs/evidence/a5-exceptional-fibers/monomial-ladder"
sys.path.insert(0, str(LADDER))

import e8_target_basis_v2 as producer  # noqa: E402
import e8_target_basis_verify as admission  # noqa: E402


@pytest.fixture
def bound_basis(monkeypatch: pytest.MonkeyPatch) -> tuple[dict[str, Any], list[str]]:
    engine = producer.T
    context = nmod_mpoly_ctx.get(("y1", "y2"), modulus=101)
    first, _ = context.gens()
    normal = [first * first] * 3
    record = {
        "schema": engine.BASIS_SCHEMA,
        "target": "fixture",
        "prime": 101,
        "root": 10,
        "degree": 2,
        "nvars": 2,
        "monomials": [[2, 0], [1, 1], [0, 2]],
        "radical_normal_forms": [engine.encode_polynomial(polynomial) for polynomial in normal],
        "target_rows": engine.kernel_rows(normal, 101),
        "base_dimension": 1,
        "upper_dimension": 3,
        "target_dimension": 2,
        "sources": {"fixture": "bound-input"},
        "producer_sha256": engine.digest(Path(producer.__file__)),
        "base_producer_sha256": engine.digest(Path(engine.__file__)),
    }
    record["payload_sha256"] = engine.payload_digest(record)
    target = producer.Target("fixture", "synthetic fiber", 101, 10, 1, "header", "relations", "generators")
    monkeypatch.setattr(producer.targets, "TARGETS", {"fixture": target})
    monkeypatch.setattr(producer.targets, "NGEN", 2)
    monkeypatch.setattr(engine, "bound_inputs", lambda _target: {"fixture": "bound-input"})
    solver_entries: list[str] = []

    def export(_target: Any, _degree: int, _singular: str, _timeout: int, _output: Path) -> tuple[Any, Any, Any]:
        solver_entries.append("entered")
        return record["monomials"], normal, {}

    monkeypatch.setattr(engine, "export_basis", export)
    return record, solver_entries


def test_current_basis_admission_replays_the_valid_bounded_map(
    bound_basis: tuple[dict[str, Any], list[str]], tmp_path: Path
) -> None:
    record, solver_entries = bound_basis
    result = admission.replay(record, "controlled-solver", 1, tmp_path / "fresh.json")
    if result != {"target": "fixture", "degree": 2, "monomials": 3, "status": "replayed"}:
        raise AssertionError(result)
    if solver_entries != ["entered"]:
        raise AssertionError(solver_entries)


@pytest.mark.parametrize(
    "field,expected",
    [
        ("producer_sha256", "producer"),
        ("base_producer_sha256", "base producer"),
        ("sources", "inputs|source"),
        ("root", "field|target"),
        ("prime", "field|target"),
        ("payload_sha256", "payload"),
    ],
)
def test_current_basis_admission_rejects_changed_bindings_before_solver_entry(
    field: str, expected: str, bound_basis: tuple[dict[str, Any], list[str]], tmp_path: Path
) -> None:
    """Refreshing a payload digest must not admit a false producer, field or source identity."""
    record, solver_entries = bound_basis
    changed = copy.deepcopy(record)
    changes: dict[str, Any] = {"sources": {"fixture": "changed"}, "root": 91, "prime": 103}
    changed[field] = changes.get(field, "0" * 64)
    if field != "payload_sha256":
        changed["payload_sha256"] = producer.T.payload_digest(changed)
    with pytest.raises(ValueError, match=expected):
        admission.replay(changed, "controlled-solver", 1, tmp_path / "unused.json")
    if solver_entries:
        raise AssertionError("a rejected source binding reached the solver")


@pytest.mark.parametrize("field", ["producer_sha256", "base_producer_sha256"])
def test_current_basis_admission_requires_each_producer_binding(
    field: str, bound_basis: tuple[dict[str, Any], list[str]], tmp_path: Path
) -> None:
    record, solver_entries = bound_basis
    changed = copy.deepcopy(record)
    changed.pop(field)
    changed["payload_sha256"] = producer.T.payload_digest(changed)
    with pytest.raises(ValueError, match="producer"):
        admission.replay(changed, "controlled-solver", 1, tmp_path / "unused.json")
    if solver_entries:
        raise AssertionError("an absent producer binding reached the solver")


@pytest.mark.parametrize("sources", [{}, {"fixture": "bound-input", "extra": "unbound-input"}])
def test_current_basis_admission_compares_the_complete_input_map(
    sources: dict[str, str], bound_basis: tuple[dict[str, Any], list[str]], tmp_path: Path
) -> None:
    record, solver_entries = bound_basis
    changed = copy.deepcopy(record)
    changed["sources"] = sources
    changed["payload_sha256"] = producer.T.payload_digest(changed)
    with pytest.raises(ValueError, match="complete bound inputs"):
        admission.replay(changed, "controlled-solver", 1, tmp_path / "unused.json")
    if solver_entries:
        raise AssertionError("an incomplete or extra input binding reached the solver")
