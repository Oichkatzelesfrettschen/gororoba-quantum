"""Quartic discriminant: identities, root patterns, sampled points, Singular parsing and the record rules."""

from __future__ import annotations

import copy
import json
import os
import re
import shutil
import sys
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_orbit_normal_forms as forms  # noqa: E402
import nullity4_quartic_discriminant as disc  # noqa: E402
import sympy as sp  # noqa: E402

Mutation = tuple[str, Callable[[dict[str, Any]], Any]]


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _need_singular() -> None:
    if os.environ.get("SINGULAR") is None and shutil.which("Singular") is None:
        if os.environ.get("GOROROBA_SINGULAR_REQUIRED") == "1":
            raise AssertionError("GOROROBA_SINGULAR_REQUIRED=1 and Singular 4.4 is absent")
        pytest.skip("Singular 4.4 is missing (package singular)")


def _point(parameters: str) -> tuple[Any, Any]:
    """(v_1, rho^2) of a parameter ideal of two linear equations in v and p^2, as fiber_jobs writes them."""
    v, p = sp.symbols("v p")
    first, second = (sp.sympify(part.replace("^", "**")) for part in parameters.split(", "))
    solved_v = sp.solve(first, v)
    solved_w = sp.solve(second, p**2)
    _same((len(solved_v), len(solved_w)), (1, 1))
    return solved_v[0], solved_w[0]


def _discriminant_at(v: Any, w: Any) -> Any:
    return sp.simplify(sp.sympify(forms.NODE_DISCRIMINANT).subs({forms.V1: v, forms.RHO**2: w}, simultaneous=True))


@pytest.mark.parametrize("name", disc.IDENTITIES)
def test_exact_identity_holds(name: str) -> None:
    _same(disc.identity(name), True)


def test_cross_square_identity_needs_its_sign() -> None:
    # G = -4 |x cross y|^2: the opposite sign leaves a nonzero remainder.
    _same(disc.quartic_cross_square(1), True)
    _same(disc.quartic_cross_square(-1), False)


def test_root_patterns_give_three_plus_the_gcd_degree() -> None:
    _same(disc.pattern_row([1, 1, 1]), [3, 3, 3, 5])
    _same(disc.pattern_row([2, 1]), [2, 4, 4, 6])
    _same(disc.pattern_row([3]), [1, 5, 5, 7])
    # gcd(chi, chi') has degree 1 for chi = (lambda - a)^2 (lambda - b) and degree 2 for chi = (lambda - a)^3.
    lam, a, b = sp.symbols("lambda a b")
    _same(sp.degree(sp.gcd((lam - a) ** 2 * (lam - b), sp.diff((lam - a) ** 2 * (lam - b), lam)), lam), 1)
    _same(sp.degree(sp.gcd((lam - a) ** 3, sp.diff((lam - a) ** 3, lam)), lam), 2)
    for pattern in disc.ROOT_PATTERNS.values():
        row = disc.pattern_row(pattern)
        _same(row[1] != row[3], True)


def test_double_root_point_is_a_double_root_of_chi() -> None:
    lam = sp.Symbol("lambda")
    for a in (Fraction(2), Fraction(3, 5), Fraction(7, 3)):
        point = disc.double_root_point(a)
        _same(point is None, False)
        v, w = (sp.Rational(x.numerator, x.denominator) for x in point or (a, a))
        b = -v - 2 * sp.Rational(a.numerator, a.denominator)
        chi = lam**3 + v * lam**2 - (1 + 2 * v * v + 2 * w) * lam + v
        _same(sp.expand(chi - (lam - sp.Rational(a.numerator, a.denominator)) ** 2 * (lam - b)), 0)
    for leaving in (Fraction(0), Fraction(1), Fraction(-1)):
        _same(disc.double_root_point(leaving), None)


def test_sampled_points_lie_on_their_strata() -> None:
    jobs = disc.fiber_jobs()
    for label, parameters in jobs:
        if label == "off the discriminant":
            v, p = (sp.Integer(part.split("-")[1]) for part in parameters.split(", "))
            _same(sp.sympify(forms.NODE_DISCRIMINANT).subs({forms.V1: v, forms.RHO: p}) != 0 and p != 0, True)
        elif label == "double root":
            v, w = _point(parameters)
            _same(_discriminant_at(v, w), 0)
            _same(w != 0, True)
            # A double root, not a triple root: v_1 differs from -3 a for the root a of the curve.
            _same(sp.expand(v**3 - 27 * v) != 0, True)
    _same(_discriminant_at(0, sp.Rational(-1, 2)), 0)
    _same(_discriminant_at(3 * sp.sqrt(3), -32), 0)
    _same(_discriminant_at(-3 * sp.sqrt(3), -32), 0)
    # Off the stratum: the sample at rho = 0, v_1 = 1 has a nonzero discriminant too, so the length 7 there is no
    # discriminant effect.
    _same(_discriminant_at(1, 0) != 0, True)


def test_sampled_points_are_the_points_of_the_labels() -> None:
    _same(disc.fiber_jobs(), disc.fiber_jobs())
    counts = {label: sum(1 for job_label, _ in disc.fiber_jobs() if job_label == label) for label in disc.FIBER_LABELS}
    _same(counts, {**disc.SAMPLES, **{label: len(p) for label, p in disc.FIXED_PARAMETERS.items()}})


def _singular_definitions(path: Path) -> dict[str, str]:
    found = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^(?:poly|vector) (\w+)\s*=\s*(.*);$", line.strip())
        if match:
            found[match.group(1)] = match.group(2)
    return found


def _expression(text: str) -> Any:
    # Singular writes m2 for m^2; the scripts name the variables c0, s, t, v, p, m.
    shorthand = re.sub(r"\b([vpm])(\d+)\b", r"\1**\2", text.replace("^", "**"))
    names = {"c0": forms.C0, "s": forms.S, "t": forms.T, "v": forms.V1, "p": forms.RHO, "m": forms.MU}
    return sp.sympify(shorthand, locals=names)


@pytest.mark.parametrize("script", [disc.CERTIFICATE_SCRIPT, disc.FIBER_SCRIPT], ids=lambda path: path.name)
def test_singular_polynomials_match_the_formulas_of_the_normal_form(script: Path) -> None:
    definitions = _singular_definitions(script)
    k = forms.kernel_vector(forms.C0, forms.S, forms.T)
    x = [_expression(part) for part in definitions["X"].strip("[]").split(",")]
    y = [_expression(part) for part in definitions["Y"].strip("[]").split(",")]
    for found, expected in ((x, k[0:3]), (y, k[8:11])):
        _same([sp.expand(a - b) for a, b in zip(found, expected, strict=True)], [0, 0, 0])
    n, r, q = forms._quartic_parts(forms.C0, forms.S, forms.T)
    for name, expected in (("n", n), ("r", r), ("q", q), ("rel", forms.QUADRIC_RELATION)):
        _same(sp.expand(_expression(definitions[name]) - expected), 0)
    _same(definitions["F"], "n*(n + r^2) + q^2")
    if "D" in definitions:
        _same(sp.expand(4 * _expression(definitions["D"]) - sp.sympify(forms.NODE_DISCRIMINANT)), 0)


def test_singular_polynomial_comparison_rejects_a_changed_sign() -> None:
    changed = _expression("c0*v - p*t").subs(forms.V1, -forms.V1)
    k = forms.kernel_vector(forms.C0, forms.S, forms.T)
    _same(sp.expand(changed - k[8]) == 0, False)


def _lines(*extra: str) -> list[str]:
    return [*extra, "MARKER DONE certificates"]


def test_singular_output_without_a_marker_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    class Done:
        returncode = 0
        stderr = ""
        stdout = "CERT a 1\n"

    monkeypatch.setattr(disc, "_singular", lambda: "Singular")
    monkeypatch.setattr(disc.subprocess, "run", lambda *args, **kwargs: Done())
    with pytest.raises(RuntimeError):
        disc._run_singular(disc.CERTIFICATE_SCRIPT, {})


def test_singular_error_line_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    class Done:
        returncode = 0
        stderr = ""
        stdout = "   ? wrong type declaration\nMARKER DONE certificates\n"

    monkeypatch.setattr(disc, "_singular", lambda: "Singular")
    monkeypatch.setattr(disc.subprocess, "run", lambda *args, **kwargs: Done())
    with pytest.raises(RuntimeError):
        disc._run_singular(disc.CERTIFICATE_SCRIPT, {})


def planted_singular(directory: Path, version: str, status: int, stderr: str, stdout: str) -> str:
    """An executable that answers --version with the banner of `version` and any script with the given streams."""
    path = directory / "Singular"
    path.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "--version" ]; then\n'
        f'  echo "Singular for x86_64-Linux version {version} (44105, 64 bit)"\n'
        "  exit 0\n"
        "fi\n"
        f"printf '%s\\n' '{stdout}'\n" + (f"echo '{stderr}' >&2\n" if stderr else "") + f"exit {status}\n"
    )
    path.chmod(0o755)
    return str(path)


@pytest.mark.parametrize(("status", "stderr"), [(7, "fatal: planted failure"), (7, ""), (0, "fatal: planted failure")])
def test_a_failed_singular_process_is_refused(tmp_path: Path, status: int, stderr: str) -> None:
    fake = planted_singular(tmp_path, disc.SINGULAR_VERSION, status, stderr, "MARKER DONE planted")
    with pytest.raises(RuntimeError):
        disc.run_checked(fake, disc.CERTIFICATE_SCRIPT, None, 60)


def test_a_clean_singular_process_is_accepted(tmp_path: Path) -> None:
    fake = planted_singular(tmp_path, disc.SINGULAR_VERSION, 0, "", "MARKER DONE planted")
    _same(disc.run_checked(fake, disc.CERTIFICATE_SCRIPT, None, 60), ["MARKER DONE planted"])


def test_another_singular_release_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SINGULAR", planted_singular(tmp_path, "4.3.2", 0, "", "MARKER DONE planted"))
    with pytest.raises(RuntimeError):
        disc._singular()
    monkeypatch.setenv("SINGULAR", planted_singular(tmp_path, disc.SINGULAR_VERSION, 0, "", "MARKER DONE planted"))
    _same(disc._singular(), str(tmp_path / "Singular"))


def test_certificate_parser_reads_flags_and_refuses_duplicates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(disc, "_run_singular", lambda script, extra: _lines("CERT x 1", "CAL y 0"))
    _same(disc.certificate_facts(), {"certificates": {"x": True}, "calibrations": {"y": False}})
    monkeypatch.setattr(disc, "_run_singular", lambda script, extra: _lines("CERT x 1", "CERT x 0"))
    with pytest.raises(RuntimeError):
        disc.certificate_facts()


def test_fiber_parser_reads_components_and_refuses_a_remainder(monkeypatch: pytest.MonkeyPatch) -> None:
    good = "FIBER point components 2 | points 4 length 5 remainder 0 | points 2 length 5 remainder 0"
    monkeypatch.setattr(disc, "_run_singular", lambda script, extra: _lines(good))
    _same(disc.fiber_facts(("triple root, v_1 = 0", "v")), [[2, 5], [4, 5]])
    bad = "FIBER point components 1 | points 4 length 5 remainder 1"
    monkeypatch.setattr(disc, "_run_singular", lambda script, extra: _lines(bad))
    with pytest.raises(RuntimeError):
        disc.fiber_facts(("triple root, v_1 = 0", "v"))


@pytest.mark.audit
def test_certificates_replay_on_singular() -> None:
    _need_singular()
    _same(
        disc.certificate_facts(),
        {"certificates": disc.CERTIFICATES, "calibrations": disc.CALIBRATIONS},
    )


@pytest.mark.audit
@pytest.mark.parametrize("label", disc.FIBER_LABELS)
def test_fiber_lengths_replay_on_singular(label: str) -> None:
    _need_singular()
    job = next(job for job in disc.fiber_jobs() if job[0] == label)
    _same(disc.fiber_facts(job), disc.FIBER_TALLY[label][0])


def test_expected_record_shares_no_list_with_the_constants() -> None:
    record = disc.expected_record()
    record["fibers"]["double root"][0][0][1] = 3
    _same(disc.FIBER_TALLY["double root"][0], [[4, 4]])
    record = disc.expected_record()
    record["double_root_basis"].append("x")
    _same(len(disc.DOUBLE_ROOT_BASIS), 3)


MUTATIONS: list[Mutation] = [
    ("identity", lambda record: record["identities"].__setitem__("double_root_locus", False)),
    ("double-root basis", lambda record: record["double_root_basis"].__setitem__(2, "2*a**3 + a**2*v + v")),
    ("triple-root basis", lambda record: record["triple_root_basis"].__setitem__(2, "v**3 - 9*v")),
    ("root pattern", lambda record: record["root_patterns"]["double root"].__setitem__(2, 5)),
    ("pattern multiplicities", lambda record: record["root_patterns"]["triple root"].__setitem__(0, [1, 1, 1])),
    ("certificate", lambda record: record["certificates"].__setitem__("hessian_nonzero_at_the_base_points", False)),
    ("calibration", lambda record: record["calibrations"].__setitem__("hessian_nonzero_off_the_base_unit", True)),
    ("fiber length", lambda record: record["fibers"]["double root"][0][0].__setitem__(1, 3)),
    ("fiber components", lambda record: record["fibers"]["triple root, v_1 = 0"][0].pop()),
    ("fiber point", lambda record: record["fiber_parameters"]["double root"].__setitem__(0, "v-1, p-1")),
    ("digest", lambda record: record["inputs"].__setitem__(next(iter(record["inputs"])), "0" * 64)),
    ("pass", lambda record: record.__setitem__("pass", False)),
    ("true as one", lambda record: record["identities"].__setitem__("double_root_locus", 1)),
]


def test_record_rules_accept_the_pinned_record(monkeypatch: pytest.MonkeyPatch) -> None:
    _same(disc.verdict(disc.expected_record()), [])
    # The rules run against the digests the record retains; the on-demand gate compares them with the live sources.
    retained = json.loads(disc.RECORD.read_text(encoding="utf-8"))
    retained_inputs = dict(retained["inputs"])
    monkeypatch.setattr(disc, "_inputs", lambda: dict(retained_inputs))
    _same(disc.verdict(retained), [])
    _same(disc.RECORD.read_text(encoding="utf-8"), disc._serialized(disc.expected_record()))
    retained["certificates"]["base_points_avoid_the_conic_n"] = False
    _same(disc.verdict(retained), ["a Singular certificate fails"])


@pytest.mark.parametrize("mutation", MUTATIONS, ids=[name for name, _ in MUTATIONS])
def test_record_rules_reject_a_mutated_record(mutation: Mutation) -> None:
    record = copy.deepcopy(disc.expected_record())
    mutation[1](record)
    _same(disc.verdict(record) != [], True)


def test_length_rules_hold_without_the_pinned_tally(monkeypatch: pytest.MonkeyPatch) -> None:
    # A planted length 3 on the double-root stratum fails the 3 + deg gcd rule even when the pinned tally agrees.
    tally = copy.deepcopy(disc.FIBER_TALLY)
    tally["double root"][0][0][1] = 3
    monkeypatch.setattr(disc, "FIBER_TALLY", tally)
    problems = disc.verdict(disc.expected_record())
    _same(any("a fiber of double root has another length" in problem for problem in problems), True)
