> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4e58401143fd67fb3d565b2e60ed505544bb440f33d6c00f4d2d342b3fbede9a.

# iqm.benchmarks.optimization.qscore

The module contains functions and classes for the Qscore benchmarking process.

Functions

|  |  |
|----|----|
| [`calculate_optimal_angles_for_qaoa_p1`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.calculate_optimal_angles_for_qaoa_p1.html#iqm.benchmarks.optimization.qscore.calculate_optimal_angles_for_qaoa_p1 "iqm.benchmarks.optimization.qscore.calculate_optimal_angles_for_qaoa_p1")(graph) | Calculates the optimal angles for single layer QAOA MaxCut ansatz. |
| [`compute_expectation_value`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.compute_expectation_value.html#iqm.benchmarks.optimization.qscore.compute_expectation_value "iqm.benchmarks.optimization.qscore.compute_expectation_value")(counts, graph, ...) | Computes expectation value based on measurement results. |
| [`create_objective_function`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.create_objective_function.html#iqm.benchmarks.optimization.qscore.create_objective_function "iqm.benchmarks.optimization.qscore.create_objective_function")(counts, graph, ...) | Creates a function that maps the parameters to the parametrized circuit and returns exp values. |
| [`cut_cost_function`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.cut_cost_function.html#iqm.benchmarks.optimization.qscore.cut_cost_function "iqm.benchmarks.optimization.qscore.cut_cost_function")(x, graph) | Returns the number of cut edges in a graph (with minus sign). |
| [`get_optimal_angles`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.get_optimal_angles.html#iqm.benchmarks.optimization.qscore.get_optimal_angles "iqm.benchmarks.optimization.qscore.get_optimal_angles")(num_layers) | Provides the optimal angles for QAOA MaxCut ansatz given the number of layers. |
| [`group_rzz_gates`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.group_rzz_gates.html#iqm.benchmarks.optimization.qscore.group_rzz_gates "iqm.benchmarks.optimization.qscore.group_rzz_gates")(circuit) | Extract and group commuting RZZ gates so that gates sharing a qubit are placed next to each other. |
| [`is_successful`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.is_successful.html#iqm.benchmarks.optimization.qscore.is_successful "iqm.benchmarks.optimization.qscore.is_successful")(approximation_ratio) | Check whether a Q-score benchmark returned approximation ratio above beta\*, therefore being successful. |
| [`plot_approximation_ratios`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.plot_approximation_ratios.html#iqm.benchmarks.optimization.qscore.plot_approximation_ratios "iqm.benchmarks.optimization.qscore.plot_approximation_ratios")(nodes, beta_ratio, ...) | Generate the figure of approximation ratios vs number of nodes with error bars. |
| [`qscore_analysis`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.qscore_analysis.html#iqm.benchmarks.optimization.qscore.qscore_analysis "iqm.benchmarks.optimization.qscore.qscore_analysis")(run) | Analysis function for a QScore experiment. |
| [`run_qaoa`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.run_qaoa.html#iqm.benchmarks.optimization.qscore.run_qaoa "iqm.benchmarks.optimization.qscore.run_qaoa")(counts, graph_physical, qubit_node, ...) | Solves the cut size of MaxCut for a graph using QAOA. |

Classes

|  |  |
|----|----|
| [`QScoreBenchmark`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.QScoreBenchmark.html#iqm.benchmarks.optimization.qscore.QScoreBenchmark "iqm.benchmarks.optimization.qscore.QScoreBenchmark")(backend_arg, configuration) | Q-score estimates the size of combinatorial optimization problem that can be solved. |
| [`QScoreConfiguration`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.optimization.qscore.QScoreConfiguration.html#iqm.benchmarks.optimization.qscore.QScoreConfiguration "iqm.benchmarks.optimization.qscore.QScoreConfiguration")(\*, benchmark, shots, ...) | Q-score configuration. |

Inheritance

![Inheritance diagram of iqm.benchmarks.optimization.qscore](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-e1b35e811d8c822ec1339fdc743373a3b8c351fd.png)
