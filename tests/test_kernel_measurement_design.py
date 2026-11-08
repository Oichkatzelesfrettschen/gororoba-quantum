"""Tests for kernel_sensitive_measurement_design."""

import numpy as np

import kernel_measurement_design as kmd


def test_basis_degeneracy_pair():
    """Verify that e_1 + e_9 (nullity 0) and e_1 + e_10 (nullity 8) have identical basis heralding."""
    if not kmd.verify_basis_degeneracy():
        raise AssertionError("Basis degeneracy check failed")


def test_coherent_probes_distinguish_degenerate_pair():
    """Verify that coherent 2-Flat superposition probes break the basis-heralding degeneracy."""
    op0, op8 = kmd.DEGENERATE_PAIR
    probes = kmd.find_distinguishing_coherent_probes(op0, op8)
    if not probes:
        raise AssertionError("No distinguishing coherent probes found")
    # Probe (j=1, k=9) or (j=1, k=10)
    for _probe, norm0, norm8 in probes[:5]:
        if abs(norm0 - norm8) <= 1e-4:
            raise AssertionError(f"Probe failed to separate responses: {norm0} vs {norm8}")


def test_sedenion_pauli_words_and_clique_cover():
    """Verify that the 84-blade bank generates the 28-word Pauli space and chi_QWC = 13."""
    words = kmd.sedenion_blade_pauli_words()
    if len(words) != 28:
        raise AssertionError(f"Expected 28 Pauli words, got {len(words)}")
    groups = kmd.greedy_qwc_clique_cover(words)
    if len(groups) != 13:
        raise AssertionError(f"Expected 13 QWC groups, got {len(groups)}")
    # Check that each group is mutually QWC
    for g in groups:
        for w1 in g:
            for w2 in g:
                if not kmd.is_qwc(w1, w2):
                    raise AssertionError(f"Words {w1} and {w2} do not commute qubit-wise")


def test_exact_bias_identity():
    """Verify that block_bias_decomposition satisfies identity error <= 1e-14."""
    rng = np.random.default_rng(42)
    # Simulate an 8-bin block with N_true = 1 (5 bright bins, 3 dark bins)
    tau = np.array([1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0])
    c_obs = tau * 0.25 + rng.normal(0, 0.05, size=8)
    summary = kmd.block_bias_decomposition(c_obs, tau)
    if summary.nullity_true != 1:
        raise AssertionError(f"Expected nullity 1, got {summary.nullity_true}")
    if summary.identity_error >= 1e-14:
        raise AssertionError(f"Identity error {summary.identity_error} exceeds 1e-14")


def test_tautological_all_bright_block():
    """Verify that an all-bright block (N_b = 4, |B_-| = 0) has theoretical bias identically 0 and N_hat == 4."""
    tau = np.ones(8)
    c_obs = np.array([0.12, 0.15, 0.09, 0.18, 0.14, 0.11, 0.13, 0.16])
    summary = kmd.block_bias_decomposition(c_obs, tau)
    if summary.nullity_true != 4:
        raise AssertionError(f"Expected nullity 4, got {summary.nullity_true}")
    if summary.bias_theoretical != 0.0:
        raise AssertionError(f"Expected bias 0.0, got {summary.bias_theoretical}")
    if abs(summary.n_hat - 4.0) >= 1e-14:
        raise AssertionError(f"Expected N_hat 4.0, got {summary.n_hat}")
    if summary.identity_error >= 1e-14:
        raise AssertionError(f"Identity error {summary.identity_error} exceeds 1e-14")


def test_neyman_shot_allocation():
    """Verify that Neyman allocation assigns more shots to higher-variance blocks."""
    variances = [0.01, 0.04, 0.09, 0.16]
    shots = kmd.neyman_optimal_shot_allocation(10000, variances)
    if sum(shots) != 10000:
        raise AssertionError(f"Total shots {sum(shots)} != 10000")
    if not (shots[0] < shots[1] < shots[2] < shots[3]):
        raise AssertionError(f"Non-monotonic shot allocation: {shots}")
