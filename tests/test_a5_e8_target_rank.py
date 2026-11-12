"""Bounded algebraic falsifiers for E8 target restriction; no retained-run replay."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from flint import nmod_mpoly_ctx

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "docs/evidence/a5-exceptional-fibers/monomial-ladder"))

import e8_target_rank as target  # noqa: E402


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _fixture() -> dict[str, Any]:
    # S=k[x,y], K=0, radical comparison ideal (y-x), in degree 2.
    # The two kernel vectors are combinations of three nonzero normal forms.
    context = nmod_mpoly_ctx.get(("y1", "y2"), modulus=101)
    x, _ = context.gens()
    normal = [x * x] * 3
    record = {
        "schema": target.BASIS_SCHEMA,
        "target": "fixture",
        "prime": 101,
        "root": 10,
        "degree": 2,
        "nvars": 2,
        "monomials": [[2, 0], [1, 1], [0, 2]],
        "radical_normal_forms": [target.encode_polynomial(poly) for poly in normal],
        "target_rows": target.kernel_rows(normal, 101),
        "base_dimension": 1,
        "upper_dimension": 3,
        "target_dimension": 2,
        "sources": {"synthetic": "digest"},
    }
    record["payload_sha256"] = target.payload_digest(record)
    return record


def test_kernel_uses_linear_combinations_and_validates_joint_independence() -> None:
    record = _fixture()
    target.validate_basis(record)
    _check(len(record["target_rows"]) == 2)
    _check(all(len(row) == 2 for row in record["target_rows"]))
    record["target_rows"][1] = record["target_rows"][0]
    record["payload_sha256"] = target.payload_digest(record)
    with pytest.raises(ValueError, match="kernel"):
        target.validate_basis(record)


def test_nonzero_normal_form_mutation_fails_even_after_digest_refresh() -> None:
    record = _fixture()
    record["radical_normal_forms"][0][0][1] = 2
    record["payload_sha256"] = target.payload_digest(record)
    with pytest.raises(ValueError, match="kernel"):
        target.validate_basis(record)


def test_consistent_forged_kernel_fails_fresh_algebraic_export(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    record = _fixture()
    context = nmod_mpoly_ctx.get(("y1", "y2"), modulus=101)
    x, _ = context.gens()
    real_normal = [x * x] * 3
    forged_normal = [context.from_dict({}), x * x, context.from_dict({})]
    record["radical_normal_forms"] = [target.encode_polynomial(poly) for poly in forged_normal]
    record["target_rows"] = target.kernel_rows(forged_normal, 101)
    record["payload_sha256"] = target.payload_digest(record)
    # Internal rank and digest checks cannot identify this false algebraic map.
    target.validate_basis(record)
    monkeypatch.setattr(target.targets, "TARGETS", {"fixture": None})
    monkeypatch.setattr(target, "export_basis", lambda *_: (record["monomials"], real_normal, {}))
    with pytest.raises(ValueError, match="fresh exact"):
        target.verify_export(record, "unused", 1, tmp_path / "unused.json")


def test_payload_digest_and_field_validation() -> None:
    record = _fixture()
    record["degree"] = 3
    with pytest.raises(ValueError, match="digest"):
        target.validate_basis(record)
    record = _fixture()
    record["prime"] = 99
    record["payload_sha256"] = target.payload_digest(record)
    with pytest.raises(ValueError, match="field"):
        target.validate_basis(record)
    record = _fixture()
    record["base_dimension"] = 1.0
    record["payload_sha256"] = target.payload_digest(record)
    with pytest.raises(ValueError, match="dimensions"):
        target.validate_basis(record)


def test_duplicate_or_wrong_degree_monomial_fails() -> None:
    record = _fixture()
    for monomial in ([2, 0], [0, 1]):
        changed = copy.deepcopy(record)
        changed["monomials"][1] = monomial
        changed["payload_sha256"] = target.payload_digest(changed)
        with pytest.raises(ValueError, match="monomial"):
            target.validate_basis(changed)


@pytest.mark.parametrize(("base", "upper", "dimension"), [(861, 952, 91), (1526, 1666, 140)])
def test_lower_bound_adds_only_target_rank_and_zero_proves_no_membership(base: int, upper: int, dimension: int) -> None:
    zero = target.bounds(base, upper, dimension, 0)
    _check(zero == {"lower": base, "upper": upper, "status": "lower_bound_only", "exact_membership_certified": False})
    partial = target.bounds(base, upper, dimension, 7)
    _check(partial["lower"] == base + 7 and partial["status"] == "lower_bound_only")
    complete = target.bounds(base, upper, dimension, dimension)
    _check(complete["lower"] == upper and complete["status"] == "certified_degree")
    # The total truncated rank can be less than base. It is not an argument of
    # this bound and must not replace the rank of the restricted target map.
    with pytest.raises(ValueError, match="rank"):
        target.bounds(base, upper, dimension, 742)


def test_export_rejects_error_truncation_and_failed_inclusion() -> None:
    valid = (
        "TARGET_INCLUSION 0\nTARGET_SIZE 2\nTARGET_B 1 y(1)^2\nTARGET_N 1 y(1)^2\n"
        "TARGET_B 2 y(1)*y(2)\nTARGET_N 2 y(1)^2\nTARGET_DONE\n"
    )
    monomials, normal = target.read_export(valid, 101, 2)
    _check(monomials == [[2, 0], [1, 1]] and len(target.kernel_rows(normal, 101)) == 1)
    for malformed in (
        valid.replace("TARGET_DONE", ""),
        valid.replace("INCLUSION 0", "INCLUSION 1"),
        "? error\n" + valid,
    ):
        with pytest.raises(ValueError):
            target.read_export(malformed, 101, 2)


def test_run_rejects_foreign_field_and_changed_input_bytes_before_algebra(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    record = _fixture()
    registry = SimpleNamespace(prime=101, root=10)
    monkeypatch.setattr(target.targets, "TARGETS", {"fixture": registry})
    monkeypatch.setattr(target.targets, "NGEN", 2)
    changed = copy.deepcopy(record)
    changed["root"] = 91
    changed["payload_sha256"] = target.payload_digest(changed)
    with pytest.raises(ValueError, match="field"):
        target.run(changed, 8, 1024**2, verification_output=tmp_path / "unused.json")
    monkeypatch.setattr(target, "bound_inputs", lambda _: {"synthetic": "changed"})
    with pytest.raises(ValueError, match="source digests"):
        target.run(record, 8, 1024**2, verification_output=tmp_path / "unused.json")


@pytest.mark.parametrize("mutation", ["conjugated_root", "permuted_generators"])
def test_run_rejects_ladder_loader_drift_before_ring_construction(
    mutation: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    record = _fixture()
    case = target.targets.Target("fixture", "synthetic", 101, 10, 1, "header", "k2", "gens")
    monkeypatch.setattr(target.targets, "TARGETS", {"fixture": case})
    monkeypatch.setattr(target.targets, "NGEN", 2)
    monkeypatch.setattr(target, "bound_inputs", lambda _: record["sources"])
    monkeypatch.setattr(target, "verify_export", lambda *_: {})
    monkeypatch.setattr(target.targets, "header_ideals", lambda _: (["j"], ["g1", "g2"]))
    ladder = SimpleNamespace(
        SIGN={"e8-nm": 1},
        limits=SimpleNamespace(
            PRIMES={101: 91 if mutation == "conjugated_root" else 10},
            header=lambda *_: (("x",), ["j"], ["g2", "g1"]),
        ),
    )
    monkeypatch.setattr(target, "ring_module", lambda: ladder)
    with pytest.raises(ValueError, match="embedding|ordered G"):
        target.run(record, 8, 1024**2, verification_output=tmp_path / "unused.json")


def test_full_denominator_kills_target_via_another_generator() -> None:
    # In k[[x]], G=(x^2,x), target x^2 lies in mI because x*x=x^2.
    # Restricting the denominator to the target generator would leave x^2
    # nonzero modulo x^3. The required propagation includes the second G.
    context = nmod_mpoly_ctx.get(("x",), modulus=101)
    x = context.gen(0)
    zero = context.from_dict({})
    ring = SimpleNamespace(prime=101)
    observed = []

    def basis(_ring: Any, order: int, maximal: bool) -> list[Any]:
        _check(maximal and order == 2)
        return [(x, zero)]

    def span(_ring: Any, generators: list[Any], values: list[Any], order: int) -> list[Any]:
        observed.append(len(generators))
        return [
            (context.from_dict({e: c for e, c in (g[0] * v[0]).to_dict().items() if sum(e) < order}), zero)
            for g in generators
            for v in values
        ]

    def rank_and_basis(_ring: Any, elements: list[Any], _order: int) -> tuple[int, list[Any]]:
        nonzero = [element for element in elements if element[0]]
        return target.coefficient_matrix([p for p, _ in elements], 101).rank(), nonzero

    ladder = SimpleNamespace(ring_basis=basis, span=span, rank_and_basis=rank_and_basis)
    full, stages = target.denominator(ladder, ring, [(x * x, zero), (x, zero)], 1, 3, 1024**2)
    _check(observed == [2] and stages[0]["denominator_rank"] == 1)
    _check(full == [(x * x, zero)])
    quotient_rank = rank_and_basis(ring, full + [(x * x, zero)], 3)[0] - len(full)
    _check(quotient_rank == 0)


def test_dense_array_guard_fails_before_allocating() -> None:
    _check(target.matrix_guard(1, 2, 1024) == 112)
    with pytest.raises(MemoryError, match="budget"):
        target.matrix_guard(1000, 20, 1024)


@pytest.mark.parametrize("order", [2, 4, 6, 8])
@pytest.mark.parametrize("low", [1, 2])
def test_factored_target_evaluation_equals_full_precision_expansion(order: int, low: int) -> None:
    # Quadratic algebra k[x] + k[x]b with b^2=x^2+x^3, weight(x)=weight(b)=1.
    # This checks both components and cutoffs that annihilate all degree-three terms.
    context = nmod_mpoly_ctx.get(("x",), modulus=101)
    x = context.gen(0)
    zero, one = context.from_dict({}), context.from_dict({(0,): 1})

    def cut(poly: Any, precision: int) -> Any:
        return context.from_dict({e: c for e, c in poly.to_dict().items() if sum(e) < precision})

    def multiply(left: Any, right: Any, precision: int) -> Any:
        p, q = left
        r, s = right
        return cut(p * r + q * s * (x**2 + x**3), precision), cut(p * s + q * r, precision - 1)

    ring = SimpleNamespace(zero=zero, one=one, mul=multiply, add=lambda a, b: (a[0] + b[0], a[1] + b[1]))
    generators = [(x + x**2, x), (2 * x + x**3, one + x), (x**2 + x**4, x)]
    if low == 2:
        generators = [(x * p, x * q) for p, q in generators]
    cases: tuple[dict[tuple[int, ...], int], ...] = (
        {(3, 0, 0): 2, (2, 1, 0): 100, (1, 0, 2): 4},
        {(3, 0, 0): 1, (0, 3, 0): 99, (0, 0, 3): 2, (1, 1, 1): 44},
    )
    for terms in cases:
        expected = (zero, zero)
        for exponent, coefficient in terms.items():
            value = (coefficient * one, zero)
            for j, power in enumerate(exponent):
                for _ in range(power):
                    value = multiply(value, generators[j], order)
            expected = ring.add(expected, value)
        _check(target.evaluate_polynomial(ring, generators, terms, order, low) == expected)


def test_membership_receipt_binds_field_order_and_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(target, "ROOT", tmp_path)
    monkeypatch.setattr(target, "EVIDENCE", tmp_path)
    case = target.targets.Target("fixture", "synthetic", 101, 10, 1, "header", "k2", "gens")
    for name in ("header", "gens", "k2"):
        (tmp_path / name).write_text(name)
    relation_hash = target.digest(tmp_path / "k2")
    witness = {
        "kind": "k2-span",
        "fiber": "synthetic",
        "prime": 101,
        "k2_source": "k2",
        "receipt": "receipt.json",
        "receipt_relations": "k2",
        "ok": True,
        "mutual_remainders": [0, 0],
        "k2_source_sha256": relation_hash,
        "receipt_relations_sha256": relation_hash,
    }
    receipt = {
        "status": "degree-certified",
        "degree": 2,
        "prime": 101,
        "root_of_minus_one": "10",
        "generator_count": 21,
        "generator_order_sha256": target.digest(tmp_path / "gens"),
        "input_sha256": target.digest(tmp_path / "header"),
        "relation_sha256": relation_hash,
        "relation_count": 148,
        "membership_check": {"checked": 148, "failures": 0},
    }
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(receipt))
    _check(target.membership_inputs(case, [witness]) == [path, tmp_path / "k2"])
    receipt["membership_check"] = {"checked": 148, "failures": 1}
    path.write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="membership receipt"):
        target.membership_inputs(case, [witness])


def test_replay_ignores_only_timing_and_rejects_changed_rank(monkeypatch: pytest.MonkeyPatch) -> None:
    basis = _fixture()
    retained: dict[str, Any] = {
        "schema": target.RANK_SCHEMA,
        "producer_sha256": target.digest(Path(target.__file__)),
        "order": 8,
        "selected_array_limit_bytes": 1024**2,
        "target_rank": 1,
        "elapsed_ms": 123,
        "denominator_stages": [{"denominator_rank": 7, "elapsed_ms": 44}],
    }
    retained["payload_sha256"] = target.payload_digest(retained)
    fresh = copy.deepcopy(retained)
    fresh["elapsed_ms"] = 456
    fresh["denominator_stages"][0]["elapsed_ms"] = 91
    monkeypatch.setattr(target, "run", lambda *_args, **_kwargs: fresh)
    _check(target.replay(basis, retained, "unused", 1)["status"] == "replayed")
    fresh["target_rank"] = 2
    with pytest.raises(ValueError, match="rank, bounds or provenance"):
        target.replay(basis, retained, "unused", 1)
