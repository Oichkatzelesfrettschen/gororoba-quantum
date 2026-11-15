"""The polar line of a nullity-4 point: rank of M on it, the SL_2-module structure of C(l_z) and the record rules."""

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
import nullity4_polar_line_module as module  # noqa: E402
import sympy as sp  # noqa: E402

Mutation = tuple[str, Callable[[dict[str, Any]], Any]]


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


@pytest.mark.parametrize("name", module.IDENTITIES)
def test_exact_identity_holds(name: str) -> None:
    _same(module.identity(name), True)


def test_a_flipped_sign_in_the_polar_vector_leaves_the_kernel() -> None:
    block = module._normal_form_block()
    relation = module.forms._quartic_relation(1)
    vector = module._at_rho(module.VECTORS[1], 1)
    _same(module._zero(list(block * sp.Matrix(vector)), relation, module.MU), True)
    vector[2] = -vector[2]
    _same(module._zero(list(block * sp.Matrix(vector)), relation, module.MU), False)


def test_a_flipped_sign_in_a_derivation_breaks_equivariance(monkeypatch: pytest.MonkeyPatch) -> None:
    entries = [list(rows) for rows in module.DERIVATION_ENTRIES]
    entries[0][0] = (entries[0][0][0], entries[0][0][1], -entries[0][0][2])
    monkeypatch.setattr(module, "DERIVATION_ENTRIES", tuple(tuple(rows) for rows in entries))
    _same(module.derivations_are_equivariant(), False)


def test_the_polar_vector_vanishes_only_at_the_rank_ten_point() -> None:
    # x = (s, v_1, mu) = 0 is (v_1, mu, rho) = (0, 0, sigma); every entry of p_sigma is one of s, v_1, mu or 0.
    for sigma in module.SIGMAS:
        entries = {entry for entry in module.VECTORS[sigma] if entry != 0}
        unsigned = {-entry if entry.could_extract_minus_sign() else entry for entry in entries}
        _same(unsigned, {module.S_VAR, module.V1, module.MU})
    # The point of sigma = 1 has rank 10 modulo the prime, so the COMPLEMENT block has rank 4 there.
    point = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    _same(gauss._rank(gauss._block(point)), 10)


@pytest.mark.parametrize("sigma", module.SIGMAS)
def test_minors_vanish_above_the_rank_and_on_mu_zero(sigma: int) -> None:
    b = module._b(module.VECTORS[sigma])
    _same(module.minors(b, 5), [])
    four = module.minors(b, 4)
    _same(len(four) > 0, True)
    on_zero = [sp.rem(sp.expand(m.subs(module.MU, 0)), module.S_VAR**2 + module.V1**2, module.V1) for m in four]
    _same(on_zero, [0] * len(four))


@pytest.mark.parametrize("sigma", module.SIGMAS)
def test_rank_four_off_mu_zero_and_the_calibration_ideals(sigma: int) -> None:
    b = module._b(module.VECTORS[sigma])
    four = module.minors(b, 4)
    variables = (module.SLACK, module.MU, module.V1, module.S_VAR)
    _same(module._is_unit([*four, module.CONE, 1 - module.SLACK * module.MU], variables), True)
    # Without the saturation by mu the ideal is proper: the cone holds points of mu = 0 where the minors vanish.
    _same(module._is_unit([*four, module.CONE], variables), False)
    # The 5 x 5 minors vanish identically, so they give no unit ideal.
    _same(module._is_unit([module.CONE, 1 - module.SLACK * module.MU], variables), False)


@pytest.mark.parametrize("sigma", module.SIGMAS)
def test_rank_three_on_mu_zero_needs_the_excluded_locus(sigma: int) -> None:
    b = module._b(module.VECTORS[sigma])
    three = [sp.expand(m.subs(module.MU, 0)) for m in module.minors(b, 3)]
    line = module.S_VAR**2 + module.V1**2
    variables = (module.SLACK, module.V1, module.S_VAR)
    for variable in (module.S_VAR, module.V1):
        _same(module._is_unit([*three, line, 1 - module.SLACK * variable], variables), True)
    # x = 0, the rank-10 point, lies in the variety of the unsaturated ideal.
    _same(module._is_unit([*three, line], (module.V1, module.S_VAR)), False)


@pytest.mark.parametrize("sigma", module.SIGMAS)
@pytest.mark.parametrize("sign", [1, -1])
def test_constant_matrices_on_the_lines_of_mu_zero(sigma: int, sign: int) -> None:
    # rank B = 3, rank of the stack of B D_k = 6, dim C(l_z) = 6 with 4 in FIXED, stable, M of rank 6 on l_z.
    _same(module.mu_zero_line((sigma, sign)), [3, 6, 6, 4, True, [6, 6]])


@pytest.mark.audit
@pytest.mark.parametrize("sigma", module.SIGMAS)
def test_stack_of_b_and_b_d1_has_full_rank_off_mu_zero(sigma: int) -> None:
    b = module._b(module.VECTORS[sigma])
    stack = module.minors(b.col_join(b * module._restrict(module.derivations()[0])), 8)
    variables = (module.SLACK, module.MU, module.V1, module.S_VAR)
    _same(module._is_unit([*stack, module.CONE, 1 - module.SLACK * module.MU], variables), True)
    _same(module._is_unit([*stack, module.CONE], variables), False)


def test_retained_samples_and_fixtures_agree_with_the_derived_ranks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _same(module.retained_agreement(), module.RETAINED)
    retained = json.loads(module.forms.RECORD.read_text(encoding="utf-8"))
    retained["samples"]["mu zero"][0][1] = 7
    retained["fixtures"][0][2] = 4
    path = tmp_path / "record.json"
    path.write_text(json.dumps(retained), encoding="utf-8")
    monkeypatch.setattr(module.forms, "RECORD", path)
    found = module.retained_agreement()
    _same(found["samples"], module.RETAINED["samples"] - 60)
    _same(found["fixtures"], module.RETAINED["fixtures"] - retained["fixtures"][0][-1])


def test_claims_follow_the_certificates() -> None:
    certificates = {"sigma = 1": copy.deepcopy(module.CERTIFICATE), "sigma = -1": copy.deepcopy(module.CERTIFICATE)}
    _same(module.derived_claims(certificates), module.CLAIMS)
    certificates["sigma = 1"]["rank_4_unit_off_mu_zero"] = False
    claims = module.derived_claims(certificates)
    _same(claims["mu nonzero"]["rank_of_B"], None)
    _same(claims["mu zero"], module.CLAIMS["mu zero"])


def test_expected_record_shares_no_list_with_the_constants() -> None:
    record = module.expected_record()
    record["certificates"]["sigma = 1"]["rank_3_unit_on_mu_zero"][0] = False
    _same(module.CERTIFICATE["rank_3_unit_on_mu_zero"], [True, True])
    _same(record["certificates"]["sigma = -1"]["rank_3_unit_on_mu_zero"], [True, True])
    _same(
        module.verdict(record),
        ["a minor identity or unit ideal of the polar line fails, or a calibration ideal is a unit"],
    )


MUTATIONS: list[Mutation] = [
    ("identity", lambda record: record["identities"].__setitem__("complement_blocks_intertwine", False)),
    ("five minors", lambda record: record["certificates"]["sigma = 1"].__setitem__("rank_5_minors_nonzero", 1)),
    ("unit ideal", lambda record: record["certificates"]["sigma = -1"].__setitem__("rank_4_unit_off_mu_zero", False)),
    ("stack", lambda record: record["certificates"]["sigma = 1"].__setitem__("stack_unit_off_mu_zero", False)),
    ("calibration", lambda record: record["certificates"]["sigma = 1"]["calibration_units"].__setitem__(0, True)),
    ("line", lambda record: record["certificates"]["sigma = -1"]["mu_zero_lines"][1].__setitem__(2, 5)),
    ("rank claim", lambda record: record["claims"]["mu nonzero"].__setitem__("rank_of_M_on_polar_line", 6)),
    ("dimension claim", lambda record: record["claims"]["mu zero"].__setitem__("dim_C", 3)),
    ("retained", lambda record: record["retained_agreement"].__setitem__("samples", 119)),
    ("digest", lambda record: record["inputs"].__setitem__(next(iter(record["inputs"])), "0" * 64)),
    ("pass", lambda record: record.__setitem__("pass", False)),
    ("true as one", lambda record: record["identities"].__setitem__("polar_line_is_a_submodule", 1)),
]


def test_record_rules_accept_the_pinned_record(monkeypatch: pytest.MonkeyPatch) -> None:
    _same(module.verdict(module.expected_record()), [])
    # The rules run against the digests the record retains; the on-demand gate compares them with the live sources.
    retained = json.loads(module.RECORD.read_text(encoding="utf-8"))
    retained_inputs = dict(retained["inputs"])
    monkeypatch.setattr(module, "_inputs", lambda: dict(retained_inputs))
    _same(module.verdict(retained), [])
    _same(module.RECORD.read_text(encoding="utf-8"), module._serialized(module.expected_record()))
    retained["claims"]["mu zero"]["dim_C"] = 3
    _same(module.verdict(retained), ["the ranks and dimensions on the polar line differ from the claims"])


@pytest.mark.parametrize("mutation", MUTATIONS, ids=[name for name, _ in MUTATIONS])
def test_record_rules_reject_a_mutated_record(mutation: Mutation) -> None:
    record = copy.deepcopy(module.expected_record())
    mutation[1](record)
    _same(module.verdict(record) != [], True)
