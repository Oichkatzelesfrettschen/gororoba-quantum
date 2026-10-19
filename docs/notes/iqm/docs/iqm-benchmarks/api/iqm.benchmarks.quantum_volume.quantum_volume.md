> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5eb047e761c7f758eb8e392824acbf0209cf59196c2a8faf8751ab2593fd64bb.

# iqm.benchmarks.quantum_volume.quantum_volume

Quantum Volume benchmark.

Functions

|  |  |
|----|----|
| [`compute_heavy_output_probabilities`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.compute_heavy_output_probabilities.html#iqm.benchmarks.quantum_volume.quantum_volume.compute_heavy_output_probabilities "iqm.benchmarks.quantum_volume.quantum_volume.compute_heavy_output_probabilities")(...) | Compute the HOP of all quantum circuits. |
| [`cumulative_hop`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.cumulative_hop.html#iqm.benchmarks.quantum_volume.quantum_volume.cumulative_hop "iqm.benchmarks.quantum_volume.quantum_volume.cumulative_hop")(hops) | Computes the cumulative average heavy output probabilities of a QV experiment. |
| [`cumulative_std`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.cumulative_std.html#iqm.benchmarks.quantum_volume.quantum_volume.cumulative_std "iqm.benchmarks.quantum_volume.quantum_volume.cumulative_std")(hops) | Computes the cumulative standard deviation heavy output probabilities of a QV experiment. |
| [`get_ideal_heavy_outputs`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.get_ideal_heavy_outputs.html#iqm.benchmarks.quantum_volume.quantum_volume.get_ideal_heavy_outputs "iqm.benchmarks.quantum_volume.quantum_volume.get_ideal_heavy_outputs")(qc_list, ...) | Calculate the heavy output bitrstrings of a list of quantum circuits. |
| [`get_rem_hops`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.get_rem_hops.html#iqm.benchmarks.quantum_volume.quantum_volume.get_rem_hops "iqm.benchmarks.quantum_volume.quantum_volume.get_rem_hops")(all_rem_quasidistro, ...) | Computes readout-error-mitigated heavy output probabilities. |
| [`heavy_projector`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.heavy_projector.html#iqm.benchmarks.quantum_volume.quantum_volume.heavy_projector "iqm.benchmarks.quantum_volume.quantum_volume.heavy_projector")(probabilities) | Project (select) the samples from a given probability distribution onto heavy outputs. |
| [`is_successful`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.is_successful.html#iqm.benchmarks.quantum_volume.quantum_volume.is_successful "iqm.benchmarks.quantum_volume.quantum_volume.is_successful")(heavy_output_probabilities\[, ...\]) | Check whether a QV benchmark returned heavy output results over the threshold, therefore being successful. |
| [`plot_hop_threshold`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.plot_hop_threshold.html#iqm.benchmarks.quantum_volume.quantum_volume.plot_hop_threshold "iqm.benchmarks.quantum_volume.quantum_volume.plot_hop_threshold")(qubits, depth, qv_result, ...) | Generate the figure representing each HOP, the average and the threshold. |
| [`qv_analysis`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.qv_analysis.html#iqm.benchmarks.quantum_volume.quantum_volume.qv_analysis "iqm.benchmarks.quantum_volume.quantum_volume.qv_analysis")(run) | Analysis function for a Quantum Volume experiment. |

Classes

|  |  |
|----|----|
| [`ExecutionInfo`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo.html#iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo "iqm.benchmarks.quantum_volume.quantum_volume.ExecutionInfo")(backend_name, timestamp) | Container for execution information of a QV job. |
| [`QuantumVolumeBenchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark.html#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeBenchmark")(backend_arg, ...) | Quantum Volume reflects the deepest circuit a given number of qubits can execute with meaningful results. |
| [`QuantumVolumeConfiguration`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration.html#iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration "iqm.benchmarks.quantum_volume.quantum_volume.QuantumVolumeConfiguration")(\*, benchmark, ...) | Quantum Volume configuration. |

Inheritance

![Inheritance diagram of iqm.benchmarks.quantum_volume.quantum_volume](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-778c92684b0446b62f3b0bfa27aac0c4f8c64224.png)
