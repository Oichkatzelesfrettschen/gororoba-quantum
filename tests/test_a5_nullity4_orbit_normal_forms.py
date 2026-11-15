"""Orbit normal forms of the nullity-4 strata: identities, the kernel quartic, the certificate and the record rules."""

from __future__ import annotations

import copy
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_gauss_image as gauss  # noqa: E402
import nullity4_orbit_normal_forms as forms  # noqa: E402
import sympy as sp  # noqa: E402

PRIME = gauss.PRIME
Mutation = tuple[str, Callable[[dict[str, Any]], Any]]


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def _root(value: int) -> int:
    return next(root for root in range(PRIME) if root * root % PRIME == value % PRIME)


def _modular(expression: Any, values: dict[Any, int]) -> int:
    return int(sp.Poly(sp.expand(expression), *values).eval(values)) % PRIME


@pytest.mark.parametrize("name", forms.IDENTITIES)
def test_exact_identity_holds(name: str) -> None:
    _same(forms.identity(name), True)


def test_kernel_parametrization_needs_its_signs() -> None:
    # The vector with the sign of its third coordinate reversed leaves the kernel of M(z).
    z = forms.quadric_point()
    k = forms.kernel_vector(forms.C0, forms.S, forms.T)
    _same(forms._zero(forms.block(z, forms.ALL, forms.ALL) * sp.Matrix(k)), True)
    k[2] = -k[2]
    _same(forms._zero(forms.block(z, forms.ALL, forms.ALL) * sp.Matrix(k)), False)


def test_kernel_quartic_agrees_with_the_block_of_the_retained_producer() -> None:
    # (v_1, rho) = (1, 1): mu^2 = -3, a square modulo the prime. The three vectors k span ker M(z) modulo the
    # prime, and G on that kernel is
    # 4 (n (n + r^2) + q^2) at three vectors.
    v1, rho = 1, 1
    mu = _root(-(1 + v1 * v1 + rho * rho))
    values = {forms.V1: v1, forms.RHO: rho, forms.MU: mu}
    z = [_modular(entry, values) for entry in forms.quadric_point()]
    _same(gauss._rank(gauss._block(z)), 12)
    for c0, s, t in ((1, 0, 0), (2, 5, -3), (7, 1, 4)):
        k = [_modular(entry, values) for entry in forms.kernel_vector(c0, s, t)]
        _same(any(sum(a * b for a, b in zip(row, k, strict=True)) % PRIME for row in gauss._block(z)), False)
        n, r, q = (_modular(part, values) for part in forms._quartic_parts(c0, s, t))
        _same(int(forms._forms(k)[2]) % PRIME, 4 * (n * (n + r * r) + q * q) % PRIME)
    basis = [
        [_modular(entry, values) for entry in forms.kernel_vector(*point)]
        for point in ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    ]
    _same(gauss._rank(basis), 3)


def test_exclusion_of_the_line_r_zero_rests_on_rho_nonzero() -> None:
    # The exclusion of the line r = 0 needs rho != 0: the mixed coefficient of q is -2 rho^2, and at rho = v_1 = 0,
    # mu^2 = -1, the quartic is (s - i t)(s + i t)(c0^2 + s^2 + t^2), which holds two lines.
    tau, theta = sp.symbols("tau theta")
    _, _, q = forms._quartic_parts(forms.RHO * tau, -forms.MU * tau, theta)
    mixed = sp.Poly(sp.expand(q), tau, theta).coeff_monomial(tau * theta)
    _same(sp.expand(mixed.subs(forms.RHO, 0)), 0)
    _same(sp.expand(mixed.subs(forms.RHO, 1)), -2)
    n, r, q = forms._quartic_parts(forms.C0, forms.S, forms.T)
    quartic = sp.expand((n * (n + r**2) + q**2).subs({forms.RHO: 0, forms.V1: 0}))
    degenerate = sp.expand(sp.rem(quartic, forms.MU**2 + 1, forms.MU))
    _same(sp.expand(degenerate - (forms.S**2 + forms.T**2) * n), 0)


def test_node_cubic_at_orthogonal_u_and_v() -> None:
    lam = sp.Symbol("lambda")
    cubic = forms.node_cubic().subs(forms.V1, 0)
    _same(sp.expand(cubic - lam * (lam**2 - 1 - 2 * forms.RHO**2)), 0)


@pytest.mark.parametrize("sigma", [1, -1])
def test_common_kernel_certificate_accepts_h_and_rejects_z(sigma: int) -> None:
    _same(forms.common_kernel_certificate(sigma), forms.CERTIFICATE)
    # With h replaced by z the matrix W vanishes modulo the relation, so no unit ideal exists.
    _same(forms.common_kernel_matrix(sigma, mutation=True), [])
    # W vanishes at the rank-10 point (v_1, mu, rho) = (0, 0, sigma), which the three factors exclude.
    at = {forms.V1: 0, forms.MU: 0, forms.RHO: sigma}
    _same(
        [sp.expand(entry.subs(at)) for entry in forms.common_kernel_matrix(sigma)],
        [0] * int(forms.CERTIFICATE["entries"]),
    )


def test_point_facts_on_and_off_rank_twelve() -> None:
    _same(forms.sample_facts(("mu nonzero", 0)), [False, 8, 3, 3, 1, True])
    _same(forms.sample_facts(("mu zero", 0)), [True, 6, 6, 4, 1, True])
    # (v_1, mu, rho) = (0, 0, 1) is the singular point of V(G) with N1 = N3, u.v = 0 and mu = 0, of rank 10.
    _same(forms.point_facts([1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]), None)


def test_fixture_with_mu_zero_has_rank_six_on_its_polar_line() -> None:
    jobs = [job for job in gauss._fixture_splits() if job[1] == forms.QUARTIC_STRATUM]
    with_mu = next(job for job in jobs if job[2][7] != 0)
    without = next(job for job in jobs if job[2][7] == 0)
    _same(forms.fixture_facts(with_mu)[:5], [False, 8, 3, 1, True])
    _same(forms.fixture_facts(without)[:5], [True, 6, 6, 1, True])


def test_quaternion_position_of_integer_split_points() -> None:
    def split(units: dict[int, int]) -> list[int]:
        return [units.get(unit, 0) for unit in range(1, 16)]

    # e_1 + 2 (e_8 + e_9) + e_13: u = i e_1, v = -2 e_1 - i e_5, two real directions.
    _same(forms.in_one_quaternion_subalgebra(split({1: 1, 8: 2, 9: 2, 13: 1})), True)
    # Units 1, 3 and 10: the real directions e_1, e_3 of u and e_2 of v span the associative 3-plane of e_1, e_2.
    _same(forms.in_one_quaternion_subalgebra(split({1: 1, 3: 1, 10: 1})), True)
    # Units 1, 3 and 12: the directions e_1, e_3, e_4, whose span lacks e_1 e_3 = -e_2.
    _same(forms.in_one_quaternion_subalgebra(split({1: 1, 3: 1, 12: 1})), False)
    # Units 1, 3, 10 and 13: four independent real directions.
    _same(forms.in_one_quaternion_subalgebra(split({1: 1, 3: 1, 10: 1, 13: 1})), False)


def test_singular_scheme_off_and_on_the_discriminant() -> None:
    jobs = forms.scheme_jobs()
    _same(forms.scheme_facts(jobs["off the discriminant"][0]), [3, 0])
    _same(forms.scheme_facts(jobs["on the discriminant"][0]), [4, 0])
    _same(forms.long_grid_points(), [forms.LONG_POINTS, forms.LONG_POINTS])


MUTATIONS: list[Mutation] = [
    ("identity", lambda record: record["identities"].__setitem__("kernel_quartic_formula", False)),
    ("pfaffian sign", lambda record: record.__setitem__("complement_pfaffian_sign", 0)),
    ("product", lambda record: record.__setitem__("kernel_product", "")),
    ("cubic", lambda record: record.__setitem__("node_cubic", "lambda**3")),
    (
        "unit ideal",
        lambda record: record["common_kernel_certificate"]["sigma = 1"]["unit_ideals"].__setitem__(1, False),
    ),
    (
        "mutation accepted",
        lambda record: record["common_kernel_certificate"]["sigma = -1"].__setitem__("mutation_entries", 14),
    ),
    ("sample", lambda record: record["samples"]["mu nonzero"][0].__setitem__(4, 2)),
    ("fixture", lambda record: record["fixtures"][1].__setitem__(7, 6)),
    ("position", lambda record: record["quaternion_position"][0].__setitem__(2, False)),
    ("digest", lambda record: record["inputs"].__setitem__(next(iter(record["inputs"])), "0" * 64)),
    ("scheme", lambda record: record["singular_schemes"]["on the discriminant"][0].__setitem__(0, 3)),
    ("long point", lambda record: record["long_grid_points"].__setitem__(1, 31)),
    ("pass", lambda record: record.__setitem__("pass", False)),
    ("true as one", lambda record: record["identities"].__setitem__("pfaffian_adjoint", 1)),
]


def test_record_rules_accept_the_pinned_record(monkeypatch: pytest.MonkeyPatch) -> None:
    _same(forms.verdict(forms.expected_record()), [])
    # The retained text is the record the constants determine; a changed value fails the rules. The rules run
    # against the digests the record retains; the on-demand gate compares them with the live sources.
    retained = json.loads(forms.RECORD.read_text(encoding="utf-8"))
    retained_inputs = dict(retained["inputs"])
    monkeypatch.setattr(forms, "_inputs", lambda: dict(retained_inputs))
    _same(forms.verdict(retained), [])
    _same(forms.RECORD.read_text(encoding="utf-8"), forms._serialized(forms.expected_record()))
    retained["complement_pfaffian_sign"] = 0
    _same(forms.verdict(retained), ["the Pfaffian of the complement block is not G"])


@pytest.mark.parametrize("mutation", MUTATIONS, ids=[name for name, _ in MUTATIONS])
def test_record_rules_reject_a_mutated_record(mutation: Mutation) -> None:
    record = copy.deepcopy(forms.expected_record())
    mutation[1](record)
    _same(forms.verdict(record) != [], True)
