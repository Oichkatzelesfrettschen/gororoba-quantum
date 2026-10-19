> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ac389c495f859c012ab6380d5fa5961d974db75999eadbfde4364c6ef47942b0.

# iqm.benchmarks.utils_shadows

Shadow Tomography utility functions.

Functions

|  |  |
|----|----|
| [`CUE`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.CUE.html#iqm.benchmarks.utils_shadows.CUE "iqm.benchmarks.utils_shadows.CUE")(random_gen, n) | Prepares single qubit Haar-random unitary (drawn from Circuilar Unitary Ensemble - CUE). |
| [`get_local_shadow`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.get_local_shadow.html#iqm.benchmarks.utils_shadows.get_local_shadow "iqm.benchmarks.utils_shadows.get_local_shadow")(counts, unitary_arg, ...\[, ...\]) | Constructs shadows for each individual initialisation. |
| [`get_negativity`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.get_negativity.html#iqm.benchmarks.utils_shadows.get_negativity "iqm.benchmarks.utils_shadows.get_negativity")(rho, n_qubits_a, n_qubits_b) | Computes the negativity of a given density matrix. |
| [`local_shadow_tomography`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.local_shadow_tomography.html#iqm.benchmarks.utils_shadows.local_shadow_tomography "iqm.benchmarks.utils_shadows.local_shadow_tomography")(qc, n_unitaries, ...) | Prepares the circuits to perform local Haar or Clifford shadow tomography. |
| [`validate_shadow_tomography_params`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_shadows.validate_shadow_tomography_params.html#iqm.benchmarks.utils_shadows.validate_shadow_tomography_params "iqm.benchmarks.utils_shadows.validate_shadow_tomography_params")(...) | Validates the parameters for shadow tomography functions. |
