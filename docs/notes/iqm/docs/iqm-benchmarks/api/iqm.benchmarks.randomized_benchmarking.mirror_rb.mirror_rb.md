> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 49f4ffa57835e0db69d2799c05f33fd57f66976a9a3d31ec56ff3df241985639.

# iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb

Mirror Randomized Benchmarking.

Functions

|  |  |
|----|----|
| [`compute_polarizations`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.compute_polarizations.html#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.compute_polarizations "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.compute_polarizations")(num_qubits, ...) | Estimates the polarization for a list of noisy counts with respect to corresponding ideal counts. |
| [`generate_fixed_depth_mrb_circuits`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_fixed_depth_mrb_circuits.html#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_fixed_depth_mrb_circuits "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_fixed_depth_mrb_circuits")(qubits, ...) | Generates a dictionary of MRB circuits at fixed depth, indexed by sample number. |
| [`generate_pauli_dressed_mrb_circuits`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_pauli_dressed_mrb_circuits.html#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_pauli_dressed_mrb_circuits "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.generate_pauli_dressed_mrb_circuits")(qubits, ...) | Samples a mirror circuit and generates samples of "Pauli-dressed" circuits. |
| [`list_to_numcircuit_times_numpauli_matrix`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.list_to_numcircuit_times_numpauli_matrix.html#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.list_to_numcircuit_times_numpauli_matrix "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.list_to_numcircuit_times_numpauli_matrix")(...) | Convert a flat list to a matrix of shape (num_circ_samples, num_pauli_samples). |
| [`mrb_analysis`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.mrb_analysis.html#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.mrb_analysis "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.mrb_analysis")(run) | Analysis function for a MRB experiment. |

Classes

|  |  |
|----|----|
| [`MirrorRBConfiguration`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration.html#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRBConfiguration")(\*, benchmark, shots, ...) | Mirror RB configuration. |
| [`MirrorRandomizedBenchmarking`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking.html#iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking "iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb.MirrorRandomizedBenchmarking")(backend_arg, ...) | Mirror RB estimates the fidelity of ensembles of n-qubit layers. |

Inheritance

![Inheritance diagram of iqm.benchmarks.randomized_benchmarking.mirror_rb.mirror_rb](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-187c1ab5b0511f33bfe63d8b55805e2fa12efa92.png)
