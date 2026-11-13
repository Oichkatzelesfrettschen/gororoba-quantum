"""Weight-slice fiber relations: torus weights, script generation, relation parsing and the pass rules of the record."""

from __future__ import annotations

import copy
import json
import math
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
ATTACHMENTS = ROOT / "docs" / "evidence" / "a5-kernel-attachments"
sys.path.insert(0, str(ATTACHMENTS))

import weight_slice_fiber_relations as wf  # noqa: E402

RECORD = ATTACHMENTS / "weight-slice-fiber-relations-result.json"
SINGULAR_REQUIRED = os.environ.get("GOROROBA_SINGULAR_REQUIRED") == "1"
SWAPPED_GRADING = (3, 0, 1, 2, 2, 1, 4, 4, 3)


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _record() -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(RECORD.read_text(encoding="utf-8"))
    return loaded


def _cell(record: dict[str, Any], incidence: str, field: str = "Q(i)") -> dict[str, Any]:
    return next(cell for cell in record["cells"] if cell["incidence"] == incidence and cell["field"] == field)


def _weight_spread(equation: str, grading: tuple[int, ...]) -> set[int]:
    """The set of torus weights of the monomials of a Singular polynomial in s1..s9 and i."""
    symbols = sp.symbols("s1:10")
    names = {f"s{index + 1}": symbol for index, symbol in enumerate(symbols)}
    polynomial = sp.Poly(sp.expand(sp.sympify(equation.replace("^", "**").replace("i", "I"), locals=names)), *symbols)
    return {
        sum(weight * power for weight, power in zip(grading, monomial, strict=True)) for monomial in polynomial.monoms()
    }


@pytest.fixture(scope="module")
def pieces() -> dict[str, wf.SlicePiece]:
    return {orbit: wf.orbit_task(orbit) for orbit in wf.ORBITS}


def test_the_torus_grading_of_both_basepoints_is_the_expected_nonnegative_weight_vector(
    pieces: dict[str, wf.SlicePiece],
) -> None:
    for orbit, piece in pieces.items():
        _same(piece.grading, wf.EXPECTED_GRADING_WEIGHTS)
        _same(tuple(wf.grading_weights(piece.normal_weights)), piece.grading)
        _same(sorted(piece.grading).count(0), 1)
        _same(len(piece.normal_weights), 9)
        _same(len(piece.tangent_weights), 6)
        _same((len(piece.kernel_weights), len(piece.complement_weights)), (9, 6))
        # The nine normal characters differ from every tangent character: a repeated weight would hide a direction.
        _same(set(piece.normal_weights) & set(piece.tangent_weights), set())
        point = json.loads(wf.BASEPOINTS_RESULT.read_text(encoding="utf-8"))["incidences"]
        _same({tuple(row["boundary_point"]) for row in point if row["boundary_orbit"] == orbit}, {piece.boundary_point})


def test_the_grading_is_two_w1_minus_w2_of_the_joint_weights_and_a_wrong_vector_differs() -> None:
    _same(wf.grading_weights([(0, -1, -2), (1, 0, 0), (2, 1, 2)]), [1, 2, 3])
    _same(wf.grading_weights(((3, 1, 0),)), [5])
    _same(SWAPPED_GRADING == wf.EXPECTED_GRADING_WEIGHTS, False)


def test_the_w8_and_iso_generators_are_weight_homogeneous_and_a_swapped_grading_breaks_w8(
    pieces: dict[str, wf.SlicePiece],
) -> None:
    for piece in pieces.values():
        for source in ("w8", "iso"):
            spreads = [_weight_spread(equation, piece.grading) for equation in piece.equations[source]]
            _same([len(spread) for spread in spreads], [1] * len(spreads))
        swapped = [_weight_spread(equation, SWAPPED_GRADING) for equation in piece.equations["w8"]]
        _same(any(len(spread) > 1 for spread in swapped), True)


def test_the_source_equation_table_has_the_expected_shape(pieces: dict[str, wf.SlicePiece]) -> None:
    for piece in pieces.values():
        _same(set(piece.equations), set(wf.SOURCES))
        _same(
            {source: len(equations) for source, equations in piece.equations.items()},
            {
                "w8": 3,
                "iso": 4,
                "e8": 27,
                "xp": 29,
                "xm": 29,
            },
        )
        _same(piece.matrix_lines.count("matrix "), 8)
        _same(piece.matrix_lines.rstrip().endswith("matrix W=dB*Dm+transpose(X)*aB*X;"), True)


def test_a_polynomial_outside_the_safe_alphabet_is_refused_before_it_reaches_singular() -> None:
    _same(wf._singular_polynomial(sp.Rational(1, 2) + sp.I), "(1/2 + i)")
    with pytest.raises(RuntimeError, match="unexpected character"):
        wf._singular_polynomial(sp.Symbol("x") + 1)
    with pytest.raises(RuntimeError, match="unexpected character"):
        wf._singular_polynomial(sp.Symbol("quit"))


def test_the_script_declares_the_ring_the_grading_and_the_stages_of_its_degree(
    pieces: dict[str, wf.SlicePiece],
) -> None:
    piece = pieces["N-"]
    rational = wf.fiber_script(piece, "w8", 0, 0)
    _same("ring r=(0,i),(s1,s2,s3,s4,s5,s6,s7,s8,s9),(wp(1,1,3,2,2,1,4,4,3)); minpoly=i^2+1;" in rational, True)
    _same("intvec tw=1,0,3,2,2,1,4,4,3;" in rational, True)
    _same("minAssGTZ(J)" in rational, True)
    _same("IX[n]=intvec(x1,x2)" in rational and "intvec(x1,x2,x3)" not in rational, True)
    _same(rational.rstrip().endswith('print("RESULT done 1");\nquit;'), True)
    modular = wf.fiber_script(piece, "e8", 32009, 10754)
    _same("ring r=32009,(s1,s2,s3,s4,s5,s6,s7,s8,s9),(wp(1,1,3,2,2,1,4,4,3)); number i=10754;" in modular, True)
    cubic = wf.fiber_script(piece, "w8", 0, 0, degree=3)
    _same("IX[n]=intvec(x1,x2,x3)" in cubic and "for(x3=x2;x3<=g;x3++)" in cubic, True)
    _same(cubic.count("}") - cubic.count("{"), 0)
    _same(wf._product_stage(3).count("{") - wf._product_stage(3).count("}"), 0)


def test_the_controls_change_the_script_where_they_say(pieces: dict[str, wf.SlicePiece]) -> None:
    piece = pieces["N-"]
    dropped = wf.fiber_script(piece, "xp", 0, 0, component_step=False)
    _same("minAssGTZ" in dropped, False)
    weights = wf.fiber_script(piece, "w8", 0, 0, weights=SWAPPED_GRADING, through_pfaffians_only=True)
    _same("intvec tw=3,0,1,2,2,1,4,4,3;" in weights, True)
    _same("RESULT generators" in weights or "RESULT relations" in weights, False)


@pytest.mark.parametrize(
    ("keywords", "message"),
    [
        ({"degree": 1}, "degree at least 2"),
        ({"weights": (1, 0, 3, 2, 2, 1, 4, 4)}, "nine nonnegative weights"),
        ({"weights": (1, -1, 3, 2, 2, 1, 4, 4, 3)}, "nine nonnegative weights"),
    ],
)
def test_the_script_builder_rejects_a_degree_below_two_and_a_malformed_grading(
    pieces: dict[str, wf.SlicePiece], keywords: dict[str, Any], message: str
) -> None:
    with pytest.raises(RuntimeError, match=message):
        wf.fiber_script(pieces["N-"], "w8", 0, 0, **keywords)


def test_a_modular_cell_needs_a_square_root_of_minus_one(pieces: dict[str, wf.SlicePiece]) -> None:
    _same((10754 * 10754) % 32009, 32008)
    wf.fiber_script(pieces["N-"], "w8", 32009, 21255)
    with pytest.raises(RuntimeError, match="not a square root of -1"):
        wf.fiber_script(pieces["N-"], "w8", 32009, 10755)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1", (1, 0)),
        ("-1", (-1, 0)),
        ("(i)", (0, 1)),
        ("(-i)", (0, -1)),
        ("(2*i)", (0, 2)),
        ("(-8*i)", (0, -8)),
        ("1/2", (sp.Rational(1, 2), 0)),
        ("(1/2*i+1)", (1, sp.Rational(1, 2))),
        ("(-1/3+i)", (sp.Rational(-1, 3), 1)),
        ("(3*i-2)", (-2, 3)),
    ],
)
def test_the_gaussian_parser_reads_every_printed_form(text: str, expected: tuple[Any, Any]) -> None:
    real, imaginary = wf.parse_gaussian(text)
    _same((real, imaginary), (sp.Rational(expected[0]), sp.Rational(expected[1])))


@pytest.mark.parametrize("text", ["", "()", "-", "(i+)", "x", "(1+i)*s1", "2**i", "1.5", "((i))"])
def test_the_gaussian_parser_raises_on_a_form_it_cannot_read(text: str) -> None:
    with pytest.raises(RuntimeError, match="cannot parse"):
        wf.parse_gaussian(text)


def test_a_relation_line_reads_into_product_indices_and_coefficients() -> None:
    _same(wf.parse_relation("RELATION 1,5:1 2,3:(2*i) 4,4:-1"), [((1, 5), "1"), ((2, 3), "(2*i)"), ((4, 4), "-1")])
    for bad in ("RELATIONS 144 of 300", "RELATION 1,5", "REL 1,5:1"):
        with pytest.raises(RuntimeError):
            wf.parse_relation(bad)
    _same(wf.relation_vector("RELATION 1,5:(2*i) 2,3:1/2", 32009, 10754, True), {(1, 5): 21508, (2, 3): 16005})
    _same(wf.relation_vector("RELATION 1,5:-1 2,3:7", 32009, 10754, False), {(1, 5): 32008, (2, 3): 7})


def test_the_reduction_comparison_accepts_equal_spaces_and_rejects_a_changed_modular_relation() -> None:
    prime, root = 32009, 10754
    gaussian = ["RELATION 1,1:1 1,2:(i)", "RELATION 1,2:1 2,2:-1"]
    modular = [f"RELATION 1,1:1 1,2:{root}", "RELATION 1,2:1 2,2:-1"]
    comparison = wf.compare_reduction(gaussian, modular, prime, root)
    _same((comparison["modular_rank"], comparison["reduced_rank"], comparison["joint_rank"]), (2, 2, 2))
    _same(comparison["spaces_equal"], True)
    # A modular relation that is a multiple of a reduced one spans the same space; a different one does not.
    scaled = [f"RELATION 1,1:2 1,2:{2 * root}", "RELATION 1,2:3 2,2:-3"]
    _same(wf.compare_reduction(gaussian, scaled, prime, root)["spaces_equal"], True)
    changed = [f"RELATION 1,1:1 1,2:{prime - root}", "RELATION 1,2:1 2,2:-1"]
    broken = wf.compare_reduction(gaussian, changed, prime, root)
    _same((broken["joint_rank"], broken["spaces_equal"]), (3, False))
    fewer = wf.compare_reduction(gaussian, modular[:1], prime, root)
    _same((fewer["modular_rank"], fewer["joint_rank"], fewer["spaces_equal"]), (1, 2, False))


def _fake_process(returncode: int = 0, stdout: str = "RESULT done 1\n", stderr: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)


def test_singular_starts_from_a_script_file_with_stdin_from_devnull(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def fake_run(command: list[str], **keywords: Any) -> SimpleNamespace:
        calls.append((command, keywords))
        _same(Path(command[-1]).read_text(encoding="utf-8"), "ring r=0,x,dp;")
        return _fake_process(stdout="RESULT germ_before 1 2 3\nRELATION 1,2:1\nRESULT done 1\n")

    monkeypatch.setattr(wf.subprocess, "run", fake_run)
    run = wf.run_singular("ring r=0,x,dp;")
    _same(run["values"], {"germ_before": ["1 2 3"], "done": ["1"]})
    _same(run["relations"], ["RELATION 1,2:1"])
    command, keywords = calls[0]
    _same(command[:2], ["prlimit", f"--as={wf.SINGULAR_ADDRESS_SPACE_BYTES}"])
    _same(command[2:5], ["Singular", "-q", "--no-warn"])
    _same(keywords["stdin"], subprocess.DEVNULL)
    _same("input" in keywords, False)
    _same(keywords["timeout"], wf.SINGULAR_TIMEOUT_SECONDS)


@pytest.mark.parametrize(
    "process",
    [
        _fake_process(returncode=1),
        _fake_process(stderr="warning"),
        _fake_process(stdout="   ? error occurred in line 3\nRESULT done 1\n"),
        _fake_process(stdout="RESULT germ_before 1 2 3\n"),
        _fake_process(stdout="RESULT done 0\n"),
    ],
)
def test_a_failed_or_unfinished_singular_run_raises(monkeypatch: pytest.MonkeyPatch, process: SimpleNamespace) -> None:
    monkeypatch.setattr(wf.subprocess, "run", lambda command, **keywords: process)
    with pytest.raises(RuntimeError, match="Singular failed|did not reach"):
        wf.run_singular("quit;")


def test_a_timeout_names_the_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command: list[str], **keywords: Any) -> SimpleNamespace:
        raise subprocess.TimeoutExpired(command, keywords["timeout"])

    monkeypatch.setattr(wf.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="exceeded"):
        wf.run_singular("quit;")


def test_the_version_banner_yields_the_version_number(monkeypatch: pytest.MonkeyPatch) -> None:
    banner = "Singular for x86_64-Linux version 4.4.1 (44105, 64 bit) Jun 30 2026 11:57:00\nwith\n\tGMP(6.3.0)\n"
    monkeypatch.setattr(wf.subprocess, "run", lambda command, **keywords: _fake_process(stdout=banner))
    _same(wf.singular_version(), (banner.splitlines()[0], "4.4.1"))
    monkeypatch.setattr(wf.subprocess, "run", lambda command, **keywords: _fake_process(stdout="Singular\n"))
    with pytest.raises(RuntimeError, match="no version"):
        wf.singular_version()


def _fiber_output(inhomogeneous: str = "") -> dict[str, Any]:
    values = {
        "germ_before": ["4 1 9"],
        "component": ["4 1 1", "3 2 0"],
        "germ_after": ["4 1 5"],
        "germ_inhomogeneous": ["0"],
        "pfaffian_nonzero": ["120"],
        "pfaffian_max_weight": ["8"],
        "pfaffian_inhomogeneous": [inhomogeneous],
        "generators": ["3"],
        "selected": ["3,5,9"],
        "generator_weights": ["4,4,5"],
        "products": ["6 8"],
        "relations": ["1"],
    }
    return {"values": values, "relations": ["RELATION 2,1:1 1,1:-1"]}


def test_a_fiber_run_summary_sorts_its_components_and_digests_the_sorted_relation_lines() -> None:
    summary = wf.summarize_fiber_run(_fiber_output())
    _same(
        summary["components"],
        [
            {"dimension": 3, "multiplicity": 2, "through_origin": False},
            {"dimension": 4, "multiplicity": 1, "through_origin": True},
        ],
    )
    _same(
        (summary["germ_before"], summary["germ_after"]),
        (
            {"dimension": 4, "multiplicity": 1, "generators": 9},
            {"dimension": 4, "multiplicity": 1, "generators": 5},
        ),
    )
    _same((summary["generator_count"], summary["product_count"], summary["product_max_weight"]), (3, 6, 8))
    _same(summary["selected_pfaffians_one_based"], [3, 5, 9])
    _same(summary["pfaffians_inhomogeneous"], [])
    first = _fiber_output()
    first["relations"] = ["RELATION 3,3:1", "RELATION 1,2:1"]
    second = _fiber_output()
    second["relations"] = ["RELATION 1,2:1", "RELATION 3,3:1"]
    _same(wf.summarize_fiber_run(first)["relations_sha256"], wf.summarize_fiber_run(second)["relations_sha256"])
    third = _fiber_output()
    third["relations"] = ["RELATION 3,3:1", "RELATION 1,2:-1"]
    _same(wf.summarize_fiber_run(third)["relations_sha256"] != wf.summarize_fiber_run(first)["relations_sha256"], True)
    _same(wf.summarize_fiber_run(_fiber_output(" 4 17"))["pfaffians_inhomogeneous"], [4, 17])


def test_a_run_that_stops_after_the_pfaffians_has_no_generator_fields() -> None:
    early = _fiber_output()
    for key in ("generators", "selected", "generator_weights", "products", "relations"):
        del early["values"][key]
    summary = wf.summarize_fiber_run(early)
    _same("generator_count" in summary, False)
    with pytest.raises(RuntimeError, match="lacks one"):
        wf.summarize_fiber_run({"values": {}, "relations": []})


def test_the_cells_are_ten_gaussian_cells_then_two_modular_cells() -> None:
    specs = wf.cell_specs()
    _same(len(specs), 12)
    _same([spec[2] for spec in specs], [0] * 10 + [32009] * 2)
    _same(specs[10:], [("N-", "w8", 32009, 10754), ("N-", "e8", 32009, 10754)])
    _same(wf.incidence_name("N-", "xp"), "X+->N-")
    _same(wf.incidence_name("N+", "e8"), "E8bar->N+")
    _same(wf.field_name(0, 0), "Q(i)")
    _same(wf.field_name(32009, 10754), "GF(32009), i = 10754")


def test_the_expected_counts_match_the_retained_fibers_of_the_import_record() -> None:
    fibers = wf.retained_fibers()
    for (orbit, source), counts in wf.EXPECTED_COUNTS.items():
        retained = fibers[wf.incidence_name(orbit, source)]
        _same(counts, (retained["generators"], retained["quadrics"]))
    for source, (dimension, multiplicity) in wf.EXPECTED_HILBERT.items():
        retained = fibers[wf.incidence_name("N-", source)]
        _same((dimension, multiplicity), (retained["projective_dimension"] + 1, retained["degree"]))
    _same({wf.EXPECTED_COUNTS[("N+", "xp")], wf.EXPECTED_COUNTS[("N-", "xm")]}, {(15, 69)})
    _same({wf.EXPECTED_COUNTS[("N+", "xm")], wf.EXPECTED_COUNTS[("N-", "xp")]}, {(3, 0)})


def test_the_retained_record_passes_its_own_rules_and_holds_the_validated_counts() -> None:
    record = _record()
    _same(wf.verdict(record), [])
    _same(record["pass"], True)
    _same(record["schema"], wf.SCHEMA)
    _same(record["execution_contract"]["degree"], wf.DEGREE)
    _same(
        {
            (cell["orbit"], cell["source"]): (cell["generator_count"], cell["relation_count"])
            for cell in record["cells"]
        },
        wf.EXPECTED_COUNTS,
    )
    _same([cell["field"] for cell in record["cells"]], ["Q(i)"] * 10 + ["GF(32009), i = 10754"] * 2)
    wide = _cell(record, "W8->N-")
    _same(
        (wide["hilbert"]["affine_dimension"], wide["hilbert"]["multiplicity"], wide["hilbert"]["saturated"]),
        (6, 50, True),
    )
    _same(
        (wide["germ_before"], wide["germ_after"]),
        ({"dimension": 6, "multiplicity": 2, "generators": 3}, {"dimension": 6, "multiplicity": 2, "generators": 3}),
    )
    # The component step changes X+ at N-: the germ ideal sheds its embedded part.
    narrow = _cell(record, "X+->N-")
    _same((narrow["germ_before"]["generators"], narrow["germ_after"]["generators"]), (9, 5))
    _same(wf.control_detected(record["mutation_controls"][0]), True)
    _same([entry["spaces_equal"] for entry in record["reduction_comparison"]], [True, True])


def test_the_retained_record_holds_only_integers_strings_and_digests() -> None:
    text = RECORD.read_text(encoding="utf-8")
    record = json.loads(text)
    stack: list[Any] = [record]
    while stack:
        value = stack.pop()
        if isinstance(value, float):
            raise AssertionError("the record holds a float")
        if isinstance(value, dict):
            stack.extend(value.values())
        elif isinstance(value, list):
            stack.extend(value)
    for cell in record["cells"]:
        _same(len(cell["relations_sha256"]), 64)
        int(cell["relations_sha256"], 16)
    for marker in ("/home/", "/tmp/", "worktrees", "\\Users"):
        _same(marker in text, False)
    _same(sorted(record["inputs"]), sorted(str(path.relative_to(ROOT)) for path in wf.SOURCE_PATHS))
    _same(record["tools"]["singular_version"], "4.4.1")


def _mutations() -> dict[str, Callable[[dict[str, Any]], None]]:
    return {
        "wrong grading weight vector": lambda rec: rec["basepoints"][0].update(grading_weights=list(SWAPPED_GRADING)),
        "grading weights changed in one basepoint only": lambda rec: rec["basepoints"][1]["grading_weights"].reverse(),
        "joint weights changed without the grading": lambda rec: rec["basepoints"][0]["normal_joint_weights"][
            0
        ].__setitem__(0, 3),
        "component step dropped": lambda rec: rec["cells"][4].update(component_step=False),
        "cell grading differs from its basepoint": lambda rec: rec["cells"][3]["grading_weights"].reverse(),
        "cell names another Singular version": lambda rec: rec["cells"][11].update(singular_version="4.3.2"),
        "record names another Singular version": lambda rec: rec["tools"].update(singular_version="4.3.2"),
        "components through the origin removed": lambda rec: rec["cells"][0].update(components=[]),
        "germ after the step differs from its components": lambda rec: rec["cells"][4]["germ_after"].update(
            multiplicity=9
        ),
        "generator count changed": lambda rec: rec["cells"][0].update(generator_count=23),
        "relation count changed": lambda rec: rec["cells"][1].update(relation_count=147),
        "relation lines differ from the count": lambda rec: rec["cells"][2].update(relation_lines=67),
        "product count changed": lambda rec: rec["cells"][3].update(product_count=119),
        "selected Pfaffians not increasing": lambda rec: rec["cells"][0]["selected_pfaffians_one_based"].reverse(),
        "selected Pfaffian beyond 126": lambda rec: rec["cells"][0]["selected_pfaffians_one_based"].__setitem__(
            -1, 127
        ),
        "an inhomogeneous Pfaffian": lambda rec: rec["cells"][5].update(pfaffians_inhomogeneous=[3]),
        "retained fiber missing": lambda rec: rec["cells"][6].update(retained_fiber=None),
        "retained fiber quadrics differ": lambda rec: rec["cells"][7]["retained_fiber"].update(quadrics=67),
        "hilbert multiplicity changed": lambda rec: rec["cells"][0]["hilbert"].update(multiplicity=49),
        "hilbert saturation lost": lambda rec: rec["cells"][1]["hilbert"].update(saturated=False),
        "a minimal prime changes degree": lambda rec: rec["cells"][0]["hilbert"]["minimal_primes"][0].__setitem__(
            1, 21
        ),
        "a minimal prime is missing": lambda rec: rec["cells"][1]["hilbert"]["minimal_primes"].pop(),
        "hilbert entry removed": lambda rec: rec["cells"][5].update(hilbert=None),
        "hilbert numerator differs between fields": lambda rec: rec["cells"][10]["hilbert"][
            "first_numerator"
        ].__setitem__(2, -143),
        "an unexpected hilbert entry": lambda rec: rec["cells"][2].update(
            hilbert=copy.deepcopy(rec["cells"][0]["hilbert"])
        ),
        "reduction rank differs": lambda rec: rec["reduction_comparison"][0].update(spaces_equal=False),
        "a reduction rank changes under a stored equality": lambda rec: rec["reduction_comparison"][0].update(
            joint_rank=145
        ),
        "hilbert numerator differs between basepoints": lambda rec: rec["cells"][0]["hilbert"][
            "first_numerator"
        ].__setitem__(2, -143),
        "reduction compares different selections": lambda rec: rec["reduction_comparison"][1].update(
            same_selected_pfaffians=False
        ),
        "modular cell dropped": lambda rec: rec["cells"].pop(),
        "cells reordered": lambda rec: rec["cells"].reverse(),
        "control missing": lambda rec: rec["mutation_controls"].pop(),
        "control undetected": lambda rec: rec["mutation_controls"][0].update(detected=False),
        "control flag without the numbers": lambda rec: rec["mutation_controls"][0].update(generator_count=3),
        "weight control flag without inhomogeneity": lambda rec: rec["mutation_controls"][1].update(
            inhomogeneous_pfaffians=0, inhomogeneous_germ_generators=0
        ),
    }


@pytest.mark.parametrize("name", list(_mutations()))
def test_the_checker_rejects_each_mutation_of_the_retained_record(name: str) -> None:
    broken = copy.deepcopy(_record())
    _mutations()[name](broken)
    _same(wf.verdict(broken) != [], True)


def test_the_controls_and_cell_rules_hold_at_a_higher_degree() -> None:
    record = _record()
    _same(all(wf.control_detected(control) for control in record["mutation_controls"]), True)
    cell = copy.deepcopy(_cell(record, "E8bar->N+"))
    # Degree 3: the generator count is the degree-2 value, the products and relations are those of the cubic table.
    cell.update(degree=3, product_count=math.comb(21 + 2, 3), relation_count=0, relation_lines=0)
    _same(wf._cell_problems(cell, 3), [])
    cell["generator_count"] = 20
    cell["selected_pfaffians_one_based"] = cell["selected_pfaffians_one_based"][:20]
    cell["generator_weights"] = cell["generator_weights"][:20]
    cell["product_count"] = math.comb(22, 3)
    _same(wf._cell_problems(cell, 3) != [], True)


def test_the_self_test_raises_on_a_failed_record_and_accepts_the_retained_one() -> None:
    wf._self_test(_record())
    broken = copy.deepcopy(_record())
    broken["cells"][0]["component_step"] = False
    with pytest.raises(RuntimeError, match="component step is off"):
        wf._self_test(broken)
    flagged = copy.deepcopy(_record())
    flagged["pass"] = False
    with pytest.raises(RuntimeError, match="fails"):
        wf._self_test(flagged)


def test_the_comparison_ignores_the_singular_build_banner_and_nothing_else() -> None:
    record = _record()
    rebuilt = copy.deepcopy(record)
    rebuilt["tools"]["singular"] = "Singular for x86_64-Linux version 4.4.1 (other build)"
    _same(wf.comparable(rebuilt), wf.comparable(record))
    for key in ("singular_version", "sympy", "python_flint"):
        changed = copy.deepcopy(record)
        changed["tools"][key] = "0"
        _same(wf.comparable(changed) != wf.comparable(record), True)
    other = copy.deepcopy(record)
    other["cells"][0]["relations_sha256"] = "0" * 64
    _same(wf.comparable(other) != wf.comparable(record), True)


@pytest.mark.audit
def test_the_retained_record_binds_the_current_producer_and_input_digests() -> None:
    record = _record()
    own = Path(wf.__file__).resolve().relative_to(ROOT).as_posix()
    _same(own in record["inputs"], True)
    _same([path for path, digest in record["inputs"].items() if wf._sha256(ROOT / path) != digest], [])


@pytest.mark.audit
@pytest.mark.skipif(shutil.which("Singular") is None and not SINGULAR_REQUIRED, reason="Singular is not installed")
def test_the_retained_record_regenerates_with_the_same_relation_digests() -> None:
    fresh = wf.build_record()
    _same(wf.comparable(fresh), wf.comparable(_record()))
    _same(fresh["pass"], True)


@pytest.mark.audit
@pytest.mark.skipif(shutil.which("Singular") is None and not SINGULAR_REQUIRED, reason="Singular is not installed")
def test_a_wrong_grading_and_a_dropped_component_step_run_through_singular_and_are_detected(
    pieces: dict[str, wf.SlicePiece],
) -> None:
    wrong = wf.run_item(
        wf.RunItem(
            "wrong_weight_vector",
            "N-",
            "w8",
            0,
            wf.fiber_script(pieces["N-"], "w8", 0, 0, weights=SWAPPED_GRADING, through_pfaffians_only=True),
        )
    )
    _same(len(wrong["summary"]["pfaffians_inhomogeneous"]) > 0, True)
    exact = wf.run_item(
        wf.RunItem(
            "right_weight_vector",
            "N-",
            "w8",
            0,
            wf.fiber_script(pieces["N-"], "w8", 0, 0, through_pfaffians_only=True),
        )
    )
    _same(exact["summary"]["pfaffians_inhomogeneous"], [])
