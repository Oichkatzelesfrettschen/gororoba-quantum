> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0f22203a8f87f9c8b05f405efb088a0eadb5a9e1d4179fdb661aa4b98ffdb705.

# iqm.benchmarks.entanglement.ghz

GHZ state benchmark.

Functions

|  |  |
|----|----|
| [`fidelity_analysis`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.fidelity_analysis.html#iqm.benchmarks.entanglement.ghz.fidelity_analysis "iqm.benchmarks.entanglement.ghz.fidelity_analysis")(run) | Analyze counts and compute the state fidelity. |
| [`fidelity_ghz_coherences`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.fidelity_ghz_coherences.html#iqm.benchmarks.entanglement.ghz.fidelity_ghz_coherences "iqm.benchmarks.entanglement.ghz.fidelity_ghz_coherences")(dataset, ...) | Estimates the GHZ state fidelity based on the multiple quantum coherences method based on \[Mooney, 2021\]. |
| [`fidelity_ghz_randomized_measurements`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.fidelity_ghz_randomized_measurements.html#iqm.benchmarks.entanglement.ghz.fidelity_ghz_randomized_measurements "iqm.benchmarks.entanglement.ghz.fidelity_ghz_randomized_measurements")(...) | Estimates GHZ state fidelity through cross-correlations of RMs. |
| [`generate_ghz_linear`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_linear.html#iqm.benchmarks.entanglement.ghz.generate_ghz_linear "iqm.benchmarks.entanglement.ghz.generate_ghz_linear")(num_qubits) | Generates a GHZ state by applying a Hadamard and a series of CX gates in a linear fashion. |
| [`generate_ghz_log_cruz`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_log_cruz.html#iqm.benchmarks.entanglement.ghz.generate_ghz_log_cruz "iqm.benchmarks.entanglement.ghz.generate_ghz_log_cruz")(num_qubits) | Generates a GHZ state in log-depth according to [https://arxiv.org/abs/1807.05572](https://arxiv.org/abs/1807.05572). |
| [`generate_ghz_log_mooney`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_log_mooney.html#iqm.benchmarks.entanglement.ghz.generate_ghz_log_mooney "iqm.benchmarks.entanglement.ghz.generate_ghz_log_mooney")(num_qubits) | Generates a GHZ state in log-depth according to [https://arxiv.org/abs/2101.08946](https://arxiv.org/abs/2101.08946). |
| [`generate_ghz_star`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_star.html#iqm.benchmarks.entanglement.ghz.generate_ghz_star "iqm.benchmarks.entanglement.ghz.generate_ghz_star")(num_qubits) | Generates the circuit for creating a GHZ state by maximizing the number of CZ gates between a pair of MOVE gates. |
| [`generate_ghz_star_optimal`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.generate_ghz_star_optimal.html#iqm.benchmarks.entanglement.ghz.generate_ghz_star_optimal "iqm.benchmarks.entanglement.ghz.generate_ghz_star_optimal")(qubit_layout, backend) | Generates the circuit for creating a GHZ state by maximizing the number of CZ gates between a pair of MOVE gates. |
| [`plot_fidelities`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.plot_fidelities.html#iqm.benchmarks.entanglement.ghz.plot_fidelities "iqm.benchmarks.entanglement.ghz.plot_fidelities")(observations, dataset, ...) | Plots all the fidelities stored in the observations into a single plot of fidelity vs. |

Classes

|  |  |
|----|----|
| [`GHZBenchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.GHZBenchmark.html#iqm.benchmarks.entanglement.ghz.GHZBenchmark "iqm.benchmarks.entanglement.ghz.GHZBenchmark")(backend, configuration) | The GHZ Benchmark estimates the quality of generated Greenberger–Horne–Zeilinger states. |
| [`GHZConfiguration`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.GHZConfiguration.html#iqm.benchmarks.entanglement.ghz.GHZConfiguration "iqm.benchmarks.entanglement.ghz.GHZConfiguration")(\*, benchmark, shots, ...) | GHZ state configuration. |

Inheritance

![Inheritance diagram of iqm.benchmarks.entanglement.ghz](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-25f4ac1063f59ff0ba57625ce03cc2831a7b21b5.png)
