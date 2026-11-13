"""Composed-limit sections: the containment equations, a section on a small fiber and the pass rule of a chain."""

from __future__ import annotations

import ast
import copy
import json
import operator
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACHMENTS))

import composed_limit_sections as cl  # noqa: E402

RECORD = ATTACHMENTS / "composed-limit-sections-result.json"


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_the_containment_equations_vanish_on_a_contained_plane_and_on_no_other() -> None:
    control = cl.convention_control()
    _same(control["contained_plane_nonzero_coefficients"], 0)
    _same(control["plane_sharing_one_covector_nonzero_coefficients"] > 0, True)
    _same(control["transverse_plane_nonzero_coefficients"] > 0, True)
    _same(control["detected"], True)


@pytest.mark.parametrize(("base", "modulus"), [(3, 11), (2, 13), (5, 17), (1, 7), (4, 19)])
def test_the_containment_equations_separate_the_planes_for_other_covector_families(base: int, modulus: int) -> None:
    control = cl.convention_control(base, modulus)
    _same(control["contained_plane_nonzero_coefficients"], 0)
    _same(control["plane_sharing_one_covector_nonzero_coefficients"] > 0, True)
    _same(control["transverse_plane_nonzero_coefficients"] > 0, True)


def test_gaussian_reduction_sends_i_to_the_root() -> None:
    _same(cl.reduce_gaussian(["0", "1"], 32009, 10754), 10754)
    _same(cl.reduce_gaussian(["-1", "0"], 32009, 10754), 32008)
    _same(cl.reduce_gaussian(["1/2", "-1"], 32009, 10754), (16005 - 10754) % 32009)
    _same(cl.reduce_gaussian(["0", "1"], 32009, 10754) ** 2 % 32009, 32008)


def test_gaussian_reduction_is_a_ring_homomorphism_at_each_prime_and_root() -> None:
    values = [("1/3", "-2"), ("5", "7/4"), ("-9/2", "1/5"), ("0", "-3/7")]
    for prime, root in cl.CELLS:
        _same(root * root % prime, prime - 1)
        for first in values:
            for second in values:
                a, b = (tuple(Fraction(part) for part in pair) for pair in (first, second))
                product = [str(a[0] * b[0] - a[1] * b[1]), str(a[0] * b[1] + a[1] * b[0])]
                total = [str(a[0] + b[0]), str(a[1] + b[1])]
                left, right = (cl.reduce_gaussian(list(pair), prime, root) for pair in (first, second))
                _same(cl.reduce_gaussian(product, prime, root), left * right % prime)
                _same(cl.reduce_gaussian(total, prime, root), (left + right) % prime)


def _evaluate(expression: str, values: dict[str, int]) -> int:
    """Exact value of an integer polynomial expression with +, - and * over named variables."""
    operations = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul}

    def walk(node: ast.AST) -> int:
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return node.value
        if isinstance(node, ast.Name):
            return values[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -walk(node.operand)
        if isinstance(node, ast.BinOp) and type(node.op) in operations:
            return int(operations[type(node.op)](walk(node.left), walk(node.right)))
        raise AssertionError(ast.dump(node))

    return walk(ast.parse(expression, mode="eval"))


@pytest.mark.parametrize("point", [(2, -3, 5), (1, 4, -2), (-7, 1, 3)])
def test_flag_equations_have_the_nonzero_coefficients_of_the_wedge_residual(point: tuple[int, int, int]) -> None:
    # Multi-term cancellation: every Pfaffian is a combination of three coordinates and every equation sums up to
    # five terms of the form, so a sign or index defect changes the number of nonvanishing equations at a point.
    names = ("y1", "y2", "y3")
    embedding = [[(7 * index + 3 * column) % 5 - 2 for column in range(3)] for index in range(len(cl.QUADS))]
    entries = [(5 * index) % 7 - 3 for index in range(len(cl.PAIRS))]
    form = [[0] * cl.KERNEL_DIMENSION for _ in range(cl.KERNEL_DIMENSION)]
    for value, (a, b) in zip(entries, cl.PAIRS, strict=True):
        form[a][b], form[b][a] = value, -value
    values = dict(zip(names, point, strict=True))
    pfaffians = [sum(c * v for c, v in zip(row, point, strict=True)) for row in embedding]
    equations = cl.flag_equations(entries, embedding, names)
    nonzero = sum(_evaluate(equation, values) != 0 for equation in equations)
    _same(nonzero, cl.wedge_residual(form, pfaffians))
    _same(nonzero > 0, True)


def test_flag_equations_of_a_coordinate_form_select_the_pfaffians_through_its_two_indices() -> None:
    # S_0 = f^0 ^ f^1 and pi = y1 f^0^f^1^f^2^f^3 + y2 f^2^f^3^f^4^f^5: only the second lies outside {f^0, f^1}.
    form = [0] * len(cl.PAIRS)
    form[cl.PAIRS.index((0, 1))] = 1
    embedding = [[0, 0] for _ in cl.QUADS]
    embedding[cl.QUAD_INDEX[(0, 1, 2, 3)]] = [1, 0]
    embedding[cl.QUAD_INDEX[(2, 3, 4, 5)]] = [0, 1]
    equations = cl.flag_equations(form, embedding, ("y1", "y2"))
    _same(equations != [], True)
    _same(any("y1" in equation for equation in equations), False)
    _same(all("y2" in equation for equation in equations), True)


def test_the_pass_rule_compares_reduced_components_and_the_section_degree() -> None:
    section = {
        "linear_conditions": 9,
        "section_projective_dimension": 2,
        "section_degree": 2,
        "reduced_degree": 1,
        "components_projective_dimension_degree": [[2, 1]],
    }
    expected = {"reduced_components": [[2, 1]], "section_degree": 2, "linear_conditions": None}
    chain = {"expected_through_one_point_stratum": expected, "points": [{"section": section}]}
    _same(cl.chain_passes(chain), True)
    _same(cl.chain_passes({**chain, "points": [{"section": {**section, "section_degree": 1}}]}), False)
    two = {**section, "components_projective_dimension_degree": [[2, 1], [2, 1]]}
    _same(cl.chain_passes({**chain, "points": [{"section": two}]}), False)
    empty = {**section, "section_projective_dimension": -1}
    _same(cl.chain_passes({"expected_through_one_point_stratum": None, "points": [{"section": empty}]}), False)
    _same(cl.chain_passes({**chain, "points": [{"section": {**section, "reduced_degree": 2}}]}), False)
    counted = {**expected, "linear_conditions": 9}
    _same(cl.chain_passes({**chain, "expected_through_one_point_stratum": counted}), True)
    _same(cl.chain_passes({**chain, "expected_through_one_point_stratum": {**counted, "linear_conditions": 10}}), False)
    _same(cl.chain_passes({**chain, "expected_through_one_point_stratum": {**counted, "linear_conditions": 8}}), False)
    two_degrees = {
        **section,
        "components_projective_dimension_degree": [[3, 3], [3, 4]],
        "reduced_degree": 7,
    }
    split = {"reduced_components": [[3, 3], [3, 4]], "section_degree": None, "linear_conditions": None}
    _same(cl.chain_passes({"expected_through_one_point_stratum": split, "points": [{"section": two_degrees}]}), True)
    _same(
        cl.chain_passes(
            {"expected_through_one_point_stratum": split, "points": [{"section": {**two_degrees, "reduced_degree": 6}}]}
        ),
        False,
    )


def test_the_retained_record_reproduces_each_fiber_over_vb_and_one_double_plane_over_va() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    _same((record["pass"], record["summary"]["sections_agree_between_the_primes"]), (True, True))
    _same((record["summary"]["chain_count"], record["summary"]["section_count"]), (41, 136))
    _same(record["summary"]["pairs_compared_at_both_primes"], 19)
    _same(
        record["summary"]["pairs_at_one_prime_only"],
        [["X+->N+", "B9->N+", 32029], ["X+->N+", "VB->N+", 32029], ["X+->N+", "Va+->N+", 32029]],
    )
    single = {chain["source"] for chain in record["chains"] if chain["prime_coverage"] != "both_primes"}
    _same(single, {"X+->N+"})
    _same({chain["prime"] for chain in record["chains"] if chain["source"] == "X+->N+"}, {32029})
    through_vb = {
        (chain["prime"], chain["source"]): chain["points"][0]["section"]["components_projective_dimension_degree"]
        for chain in record["chains"]
        if chain["through"].startswith("VB->")
    }
    _same(through_vb[(32009, "Iso->N+")], [[3, 1]])
    _same(through_vb[(32009, "W8->N-")], [[4, 1]])
    _same(through_vb[(32029, "X+->N+")], [[2, 1]])
    _same(through_vb[(32009, "E8bar->N+")], [[3, 3], [3, 4]])
    _same(through_vb[(32029, "E8bar->N-")], [[3, 3], [3, 4]])
    for chain in record["chains"]:
        _same(cl.chain_passes(chain), True)
        if chain["through"].startswith("Va"):
            section = chain["points"][0]["section"]
            _same((section["section_degree"], section["reduced_degree"]), (2, 1))


def _chain(source: str, through: str, prime: int, value: int = 1) -> dict[str, Any]:
    section = {"section_degree": value, "components_projective_dimension_degree": [[2, 1]]}
    return {"source": source, "through": through, "prime": prime, "points": [{"section": section}]}


def test_cross_prime_agreement_needs_both_primes_and_excludes_the_declared_single_prime_chains() -> None:
    both = [_chain("Iso->N+", "VB->N+", prime) for prime in cl.PRIMES]
    single = [_chain("X+->N+", "VB->N+", 32029)]
    found = cl.compare_primes([*both, *single])
    _same(found["agree"], True)
    _same(found["pairs_at_both_primes"], [["Iso->N+", "VB->N+"]])
    _same(found["pairs_at_one_prime_only"], [["X+->N+", "VB->N+", 32029]])
    # A pair that differs between the primes fails.
    _same(
        cl.compare_primes([_chain("Iso->N+", "VB->N+", 32009), _chain("Iso->N+", "VB->N+", 32029, 2)])["agree"], False
    )
    # Every chain at one prime is a vacuous comparison and fails.
    _same(cl.compare_primes(single)["agree"], False)
    _same(cl.compare_primes([_chain("Iso->N+", "VB->N+", 32009)])["agree"], False)
    # A chain at one prime outside the declared sources, or at the other prime, fails.
    _same(cl.compare_primes([*both, _chain("W8->N-", "VB->N-", 32029)])["agree"], False)
    _same(cl.compare_primes([*both, _chain("X+->N+", "VB->N+", 32009)])["agree"], False)


def _receipt_arguments() -> tuple[dict[str, Any], dict[str, Any]]:
    receipt = {
        "schema": "a5-fiber-cone-degree-receipt-v1",
        "status": "degree-certified",
        "degree": 2,
        "prime": 32029,
        "root_of_minus_one": "9115",
        "input": "p32029-r9115/iso-np.sing",
        "input_sha256": "a" * 64,
        "generator_count": 3,
        "generator_order_sha256": "b" * 64,
        "relation_sha256": "c" * 64,
        "relation_count": 68,
        "membership_check": {"checked": 68, "failures": 0},
    }
    keywords = {
        "header": {"name": "iso-np.sing", "sha256": "a" * 64, "generators": ["g1", "g2", "g3"]},
        "gens": {"sha256": "b" * 64, "generators": ["g1", "g2", "g3"]},
        "relations_sha256": "c" * 64,
        "prime": 32029,
        "root": 9115,
        "quadrics": 68,
    }
    return receipt, keywords


def test_a_receipt_binds_the_header_digest_the_generator_order_and_the_relation_file() -> None:
    receipt, keywords = _receipt_arguments()
    _same(cl.receipt_violation(receipt, **keywords), None)
    for field, value, failed in (
        ("input_sha256", "d" * 64, "input digest"),
        ("generator_order_sha256", "e" * 64, "generator order digest"),
        ("relation_sha256", "f" * 64, "relation digest"),
        ("generator_count", 4, "generator count"),
        ("relation_count", 69, "relation count"),
        ("prime", 32009, "prime"),
        ("root_of_minus_one", "21255", "prime"),
        ("status", "partial", "status"),
        ("degree", 3, "status"),
        ("input", "p32029-r9115/iso-nm.sing", "input"),
        ("membership_check", {"checked": 68, "failures": 1}, "membership"),
    ):
        _same(cl.receipt_violation({**receipt, field: value}, **keywords), failed)
    reordered = {**keywords["gens"], "generators": ["g2", "g1", "g3"]}
    _same(cl.receipt_violation(receipt, **{**keywords, "gens": reordered}), "generator order")


def _bound() -> dict[str, Any]:
    cells = cl.import_cells()
    hilbert = [json.loads(line) for line in cl.HILBERT.read_text(encoding="utf-8").splitlines() if line.strip()]
    witnesses = [json.loads(line) for line in cl.WITNESSES.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {"cells": cells, "hilbert": hilbert, "witnesses": witnesses}


@pytest.mark.audit
def test_the_k2_file_of_every_source_and_prime_binds_to_its_canonical_header() -> None:
    data = _bound()
    routes = {}
    for prime, root in cl.CELLS:
        for source, label in cl.SOURCES.items():
            _, _, row = cl._relations(label, prime, data["hilbert"])
            if label is None or row is None:
                continue
            binding = cl.bind_relations(
                label, prime, root, row, cells=data["cells"], witnesses=data["witnesses"], touched=set()
            )
            routes[(source, prime)] = binding["route"]
            _same(binding["header"]["sha256"], data["cells"][(source, prime, root)]["header_sha256"])
    _same(len(routes), 11)
    _same(routes[("E8bar->N+", 32009)], "sign_isomorphism_witness")
    _same({route for key, route in routes.items() if key != ("E8bar->N+", 32009)}, {"k2_span_witness"})
    _same(("X+->N+", 32009) in routes, False)


def test_a_k2_file_without_a_certified_generator_order_in_its_header_is_rejected() -> None:
    data = _bound()
    root = dict(cl.CELLS)[32029]
    _, _, row = cl._relations("Iso", 32029, data["hilbert"])
    _, _, other = cl._relations("W8 -> N-", 32029, data["hilbert"])
    if row is None or other is None:
        raise AssertionError("the Iso and W8 rows of k2-hilbert.jsonl at 32029 are missing")
    good = {"cells": data["cells"], "witnesses": data["witnesses"], "touched": set()}
    cl.bind_relations("Iso", 32029, root, row, **good)
    # A relation file whose digest no witness certifies.
    with pytest.raises(RuntimeError, match="no certified generator order"):
        cl.bind_relations("Iso", 32029, root, {**row, "relations_sha256": "0" * 64}, **good)
    # The relation file of another incidence under this header: its receipt names another input digest.
    swapped = {**row, "relations": other["relations"], "relations_sha256": other["relations_sha256"]}
    with pytest.raises(RuntimeError, match="no certified generator order"):
        cl.bind_relations("Iso", 32029, root, swapped, **good)
    # A header changed since the import record fails before any witness is read.
    mutated = copy.deepcopy(data["cells"])
    mutated[("Iso->N+", 32029, root)]["header_sha256"] = "0" * 64
    with pytest.raises(RuntimeError, match="changed since the import"):
        cl.bind_relations("Iso", 32029, root, row, cells=mutated, witnesses=data["witnesses"], touched=set())
    # A witness list without the span of this file and without a sign isomorphism.
    bare = [witness for witness in data["witnesses"] if witness["kind"] == "header-pair"]
    with pytest.raises(RuntimeError, match="no certified generator order"):
        cl.bind_relations("Iso", 32029, root, row, cells=data["cells"], witnesses=bare, touched=set())


def test_self_test_rejects_a_failed_record_and_a_surviving_mutation() -> None:
    with pytest.raises(RuntimeError, match="failed"):
        cl._self_test({"pass": False, "mutation_control": {"detected": True}})
    with pytest.raises(RuntimeError, match="outside"):
        cl._self_test({"pass": True, "mutation_control": {"detected": False}})


def test_self_test_rejects_a_field_outside_the_pass_and_mutation_flags() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    cl._self_test(record)
    broken = copy.deepcopy(record)
    broken["chains"][0]["points"][0]["section"]["section_degree"] += 1
    broken["chains"][0]["points"][0]["section"]["reduced_degree"] += 1
    with pytest.raises(RuntimeError, match="disagrees"):
        cl._self_test(broken)
    single = copy.deepcopy(record)
    single["chains"] = [chain for chain in single["chains"] if chain["prime"] == 32029]
    with pytest.raises(RuntimeError, match="disagrees"):
        cl._self_test(single)


@pytest.mark.audit
def test_the_retained_record_binds_the_current_producer_and_input_digests() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    _same(
        {
            "docs/evidence/a5-kernel-attachments/composed_limit_sections.py",
            "docs/evidence/a5-kernel-attachments/nullity8-fiber-import-result.json",
            "docs/evidence/a5-exceptional-fibers/witnesses.jsonl",
        }
        <= set(record["inputs"]),
        True,
    )
    _same([path for path, digest in record["inputs"].items() if cl._sha256(ROOT / path) != digest], [])
    bound = {binding["header"]["path"] for binding in record["k2_bindings"]}
    _same(bound <= set(record["inputs"]), True)


@pytest.mark.audit
def test_the_retained_record_regenerates_byte_for_byte() -> None:
    _same(cl._record_bytes(cl.build_record()), RECORD.read_bytes())
