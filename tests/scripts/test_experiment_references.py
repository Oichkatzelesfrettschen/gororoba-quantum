"""Independent contracts for finite experiment targets and their controls."""

from __future__ import annotations

import numpy as np
import pytest

import experiment_references as references


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_exact_report_distinguishes_three_bases_and_tao() -> None:
    report = references.self_check()
    records = {(row["preparation"], row["measurement"]): row for row in report["overlaps"]}
    require(records[("tao", "computational")]["maximum_unbiasedness_residual"] == "0", "Tao lost flat entries")
    require(records[("tao", "product_fourier")]["maximum_unbiasedness_residual"] != "0", "Tao became unbiased")
    require(report["active_indices"] == [0, 1, 2, 4, 5, 6], "six-level encoding changed")


@pytest.mark.parametrize("name", references.BASIS_NAMES)
def test_embedded_basis_preserves_leakage_and_order(name: str) -> None:
    embedded = references.embedded_basis(name)
    np.testing.assert_allclose(embedded.conj().T @ embedded, np.eye(8), atol=2e-15, rtol=0)
    np.testing.assert_array_equal(embedded[:, references.LEAKAGE_INDICES], np.eye(8)[:, references.LEAKAGE_INDICES])
    np.testing.assert_allclose(
        embedded[np.ix_(references.ACTIVE_INDICES, references.ACTIVE_INDICES)],
        references.mub_bases(include_tao=True)[name],
        atol=0,
        rtol=0,
    )


def test_transition_direction_and_noncommuting_basis_order() -> None:
    bases = references.mub_bases(include_tao=True)
    expected = bases["tao"].conj().T @ bases["product_chirped"]
    actual = references.transition_matrix("product_chirped", "tao")
    np.testing.assert_allclose(actual, expected, atol=3e-16, rtol=0)
    require(not np.allclose(actual, expected.conj().T), "transition direction test lacks sensitivity")


def test_returned_copies_cannot_corrupt_reference_cache() -> None:
    bases = references.mub_bases()
    bases["computational"][0, 0] = 0
    require(references.mub_bases()["computational"][0, 0] == 1, "mutable basis cache escaped")
    report = references.reference_report()
    report["active_indices"][0] = 99
    require(references.reference_report()["active_indices"][0] == 0, "mutable report cache escaped")


def test_unknown_basis_rejected() -> None:
    with pytest.raises(ValueError, match="unknown basis"):
        references.embedded_basis("missing")
    with pytest.raises(ValueError, match="unknown preparation"):
        references.transition_matrix("computational", "missing")


def test_fano_checks_and_sign_counterexample() -> None:
    record = references.fano_reference()
    require(record["incidence_rank_gf2"] == 4, "incorrect Fano rank")
    require(record["common_plus_eigenspace_dimension"] == 8, "incorrect Fano eigenspace")
    require(record["x_z_intersection_parities"] == [[1] * 7 for _ in range(7)], "line X/Z checks commute")
    witness = record["sign_lift_counterexample"]
    require(witness["matching_xor"], "counterexample lacks matching parity skeleton")
    require(any(value != "0" for value in witness["real_product"]), "real counterexample vanished")


def test_sedenion_full_operator_and_sign_mutation() -> None:
    operators = references.sedenion_operators()
    witness = operators["witness"]
    np.testing.assert_allclose(witness.conj().T @ witness, np.eye(32), atol=0, rtol=0)
    kernel_output = witness @ operators["kernel_input"]
    bright_output = witness @ operators["bright_input"]
    np.testing.assert_allclose(kernel_output[:16], np.zeros(16), atol=0, rtol=0)
    np.testing.assert_allclose(np.vdot(bright_output[:16], bright_output[:16]), 1, atol=3e-16, rtol=0)
    mutated = operators["left_second"].copy()
    mutated[10 ^ 4, 4] *= -1
    mutated_branch = (operators["left_first"] + mutated) @ operators["kernel_input"][:16] / 2
    require(float(np.vdot(mutated_branch, mutated_branch).real) > 0, "sign mutation leaves kernel signal unchanged")


def test_spectral_estimands_keep_normalization() -> None:
    record = references.spectral_reference()
    require(record["exact_expectation"] == "1/4", "wrong exact expectation")
    require(record["exact_return_probability"] == "1/16", "return conflated with expectation")
    require(record["exact_lcu_success_probability"] == "1/16", "LCU normalization missing")
    require(record["approximate_expectation"] == "3/16", "wrong approximate expectation")
    require(record["approximate_success_probability"] == "9/64", "approximate filter treated as projector")
    require(record["approximate_lcu_success_probability"] == "9/256", "approximate LCU normalization missing")


def test_amplification_full_operators_and_omission_controls() -> None:
    operators = references.quarter_mass_operators()
    for operator in operators.values():
        np.testing.assert_allclose(operator.conj().T @ operator, np.eye(4), atol=0, rtol=0)
    np.testing.assert_array_equal(operators["amplified"][:, 0], [0, 0, 0, 1])
    for name in ("preparation", "omit_oracle", "omit_reflection"):
        require(abs(operators[name][3, 0]) ** 2 == 0.25, f"omission control {name} changed")
    wrong_order = operators["oracle"] @ operators["reflection"] @ operators["preparation"]
    require(abs(wrong_order[3, 0]) ** 2 == 0.25, "reflection-order mutation lacks sensitivity")
