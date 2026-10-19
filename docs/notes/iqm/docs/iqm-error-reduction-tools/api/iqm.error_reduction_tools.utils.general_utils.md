> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a431bfa8184f47113df5236f8f04b1f9b0db4e0ace8a6a2bd5dc90ca74ac7f1a.

# iqm.error_reduction_tools.utils.general_utils

Utils for circuit analysis.

Functions

|  |  |
|----|----|
| [`expectation_from_counts`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.expectation_from_counts.html#iqm.error_reduction_tools.utils.general_utils.expectation_from_counts "iqm.error_reduction_tools.utils.general_utils.expectation_from_counts")(counts\[, pauli_string\]) | Calculate expectation value of a Pauli string from measurement counts. |
| [`marginalize_counts`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.marginalize_counts.html#iqm.error_reduction_tools.utils.general_utils.marginalize_counts "iqm.error_reduction_tools.utils.general_utils.marginalize_counts")(counts, qubit_indices) | Marginalize counts with respect to a subset of qubits. |
| [`remove_whitespace_from_bitstrings`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.remove_whitespace_from_bitstrings.html#iqm.error_reduction_tools.utils.general_utils.remove_whitespace_from_bitstrings "iqm.error_reduction_tools.utils.general_utils.remove_whitespace_from_bitstrings")(counts) | Remove whitespace from bitstring keys in a counts dictionary. |
| [`total_variational_distance`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.general_utils.total_variational_distance.html#iqm.error_reduction_tools.utils.general_utils.total_variational_distance "iqm.error_reduction_tools.utils.general_utils.total_variational_distance")(dist_a, dist_b) | Total Variation Distance between two probability distributions. |
