> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6810b6e68edb6cfd7a1a436ae8fff8e9910b360b4b9a591476fb2833ac614e8c.

# iqm.benchmarks.utils

General utility functions.

Functions

|  |  |
|----|----|
| [`bootstrap_counts`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.bootstrap_counts.html#iqm.benchmarks.utils.bootstrap_counts "iqm.benchmarks.utils.bootstrap_counts")(original_counts\[, ...\]) | Returns num_bootstrap_samples resampled copies of the original_counts. |
| [`count_2q_layers`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.count_2q_layers.html#iqm.benchmarks.utils.count_2q_layers "iqm.benchmarks.utils.count_2q_layers")(circuit_list) | Calculate the number of layers of parallel 2-qubit gates in a list of circuits. |
| [`count_native_gates`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.count_native_gates.html#iqm.benchmarks.utils.count_native_gates "iqm.benchmarks.utils.count_native_gates")(backend_arg, ...) | Count the number of IQM native gates of each quantum circuit in a list. |
| [`error_profile_to_fidelities`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.error_profile_to_fidelities.html#iqm.benchmarks.utils.error_profile_to_fidelities "iqm.benchmarks.utils.error_profile_to_fidelities")(backend) | Convert IQMFakeBackend error profile to fidelity metrics. |
| [`extract_fidelities_unified`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.extract_fidelities_unified.html#iqm.benchmarks.utils.extract_fidelities_unified "iqm.benchmarks.utils.extract_fidelities_unified")(backend) | Returns couplings and CZ-fidelities from calibration data URL for external station API. |
| [`generate_state_tomography_circuits`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.generate_state_tomography_circuits.html#iqm.benchmarks.utils.generate_state_tomography_circuits "iqm.benchmarks.utils.generate_state_tomography_circuits")(qc, ...) | Generate all quantum circuits required for a quantum state tomography experiment. |
| [`get_active_qubits`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_active_qubits.html#iqm.benchmarks.utils.get_active_qubits "iqm.benchmarks.utils.get_active_qubits")(qc) | Extract active qubits from a quantum circuit. |
| [`get_iqm_backend`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_iqm_backend.html#iqm.benchmarks.utils.get_iqm_backend "iqm.benchmarks.utils.get_iqm_backend")(backend_label) | Get the IQM backend object from a backend name (str). |
| [`get_measurement_mapping`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_measurement_mapping.html#iqm.benchmarks.utils.get_measurement_mapping "iqm.benchmarks.utils.get_measurement_mapping")(circuit) | Extracts the final measurement mapping (qubits to bits) of a quantum circuit. |
| [`get_neighbors_of_edges`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_neighbors_of_edges.html#iqm.benchmarks.utils.get_neighbors_of_edges "iqm.benchmarks.utils.get_neighbors_of_edges")(edges, graph) | Given a Sequence of edges and a graph, return all neighboring nodes of the edges. |
| [`get_pauli_expectation`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_pauli_expectation.html#iqm.benchmarks.utils.get_pauli_expectation "iqm.benchmarks.utils.get_pauli_expectation")(counts, pauli_label) | Gets an estimate of a Pauli expectation value for a given set of counts and a Pauli measurement label. |
| [`get_tomography_matrix`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.get_tomography_matrix.html#iqm.benchmarks.utils.get_tomography_matrix "iqm.benchmarks.utils.get_tomography_matrix")(pauli_expectations) | Reconstructs a density matrix from given Pauli expectations. |
| [`marginal_distribution`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.marginal_distribution.html#iqm.benchmarks.utils.marginal_distribution "iqm.benchmarks.utils.marginal_distribution")(prob_dist_or_counts, ...) | Compute the marginal distribution over specified bits (indices). |
| [`median_with_uncertainty`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.median_with_uncertainty.html#iqm.benchmarks.utils.median_with_uncertainty "iqm.benchmarks.utils.median_with_uncertainty")(observations) | Computes the median of a Sequence of float observations and returns value and propagated uncertainty. |
| [`perform_backend_transpilation`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.perform_backend_transpilation.html#iqm.benchmarks.utils.perform_backend_transpilation "iqm.benchmarks.utils.perform_backend_transpilation")(qc_list, ...) | Transpile a list of circuits to backend specifications. |
| [`process_backend`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.process_backend.html#iqm.benchmarks.utils.process_backend "iqm.benchmarks.utils.process_backend")(backend) | Process the backend input to ensure it is an IQMBackendBase instance and extract the station name. |
| [`random_hamiltonian_path`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.random_hamiltonian_path.html#iqm.benchmarks.utils.random_hamiltonian_path "iqm.benchmarks.utils.random_hamiltonian_path")(graph, n_vertices) | Generates a random Hamiltonian path with n_vertices from a given NetworkX graph. |
| [`reduce_to_active_qubits`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.reduce_to_active_qubits.html#iqm.benchmarks.utils.reduce_to_active_qubits "iqm.benchmarks.utils.reduce_to_active_qubits")(circuit\[, ...\]) | Reduces a quantum circuit to only its active qubits. |
| [`remove_directed_duplicates_to_list`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.remove_directed_duplicates_to_list.html#iqm.benchmarks.utils.remove_directed_duplicates_to_list "iqm.benchmarks.utils.remove_directed_duplicates_to_list")(cp_map) | Remove duplicate edges from a coupling map and returns as a list of edges (as a list of pairs of vertices). |
| [`retrieve_all_counts`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.retrieve_all_counts.html#iqm.benchmarks.utils.retrieve_all_counts "iqm.benchmarks.utils.retrieve_all_counts")(iqm_jobs\[, identifier\]) | Retrieve the counts from a list of IQMJob objects. |
| [`retrieve_all_job_metadata`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.retrieve_all_job_metadata.html#iqm.benchmarks.utils.retrieve_all_job_metadata "iqm.benchmarks.utils.retrieve_all_job_metadata")(iqm_jobs) | Retrieve the metadata from a list of Job objects. |
| [`set_coupling_map`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.set_coupling_map.html#iqm.benchmarks.utils.set_coupling_map "iqm.benchmarks.utils.set_coupling_map")(qubits, backend\[, ...\]) | Set a coupling map according to the specified physical layout. |
| [`sort_batches_by_final_layout`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.sort_batches_by_final_layout.html#iqm.benchmarks.utils.sort_batches_by_final_layout "iqm.benchmarks.utils.sort_batches_by_final_layout")(...) | Sort batches of circuits according to the final measurement mapping in their corresponding backend. |
| [`split_into_disjoint_pairs`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.split_into_disjoint_pairs.html#iqm.benchmarks.utils.split_into_disjoint_pairs "iqm.benchmarks.utils.split_into_disjoint_pairs")(pairs) | Split a Sequence of pairs of integers into a List of a minimal number of Lists of disjoint pairs. |
| [`split_sequence_in_chunks`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.split_sequence_in_chunks.html#iqm.benchmarks.utils.split_sequence_in_chunks "iqm.benchmarks.utils.split_sequence_in_chunks")(sequence_in, split_size) | Split a given Sequence into chunks of a given split size, return as a List of Sequences. |
| [`submit_execute`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.submit_execute.html#iqm.benchmarks.utils.submit_execute "iqm.benchmarks.utils.submit_execute")(sorted_transpiled_qc_list, ...) | Submit function to execute lists of quantum circuits on the specified backend. |
| [`timeit`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.timeit.html#iqm.benchmarks.utils.timeit "iqm.benchmarks.utils.timeit")(f) | Decorator for calculating the amount of time a function takes to execute. |
| [`xrvariable_to_counts`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.xrvariable_to_counts.html#iqm.benchmarks.utils.xrvariable_to_counts "iqm.benchmarks.utils.xrvariable_to_counts")(dataset, identifier, ...) | Retrieve counts from xarray dataset. |

Classes

|  |  |
|----|----|
| [`ObservationType`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.ObservationType.html#iqm.benchmarks.utils.ObservationType "iqm.benchmarks.utils.ObservationType")(value) | Enumeration representing relevant keys to fetch for each operation in the observations. |
| [`PhysicalLayout`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.PhysicalLayout.html#iqm.benchmarks.utils.PhysicalLayout "iqm.benchmarks.utils.PhysicalLayout")(value) | Physical layout type. |
| [`RoutingMethod`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.RoutingMethod.html#iqm.benchmarks.utils.RoutingMethod "iqm.benchmarks.utils.RoutingMethod")(value) | Qiskit routing method options to use in transpilation. |

Inheritance

![Inheritance diagram of iqm.benchmarks.utils](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-bd9f8ea6107654c251aa028febdf18c0c643c207.png)
