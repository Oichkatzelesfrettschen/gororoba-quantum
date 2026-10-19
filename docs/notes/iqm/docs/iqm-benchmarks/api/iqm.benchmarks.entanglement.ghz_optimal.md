> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c27c61808e1a498d0c2f613b168f53c53a0b0451250084eb854f5a29ac27b423.

# iqm.benchmarks.entanglement.ghz_optimal

Choosing the qubits, the tree and the gate order of a GHZ state.

The GHZ state is prepared by spreading entanglement from one root qubit along a spanning tree of the chip’s coupling graph, so the tree decides both the gate error paid (its edges are the CZ gates played) and the circuit depth (its shape decides how many of them can run in parallel). Optimizing only the first of those – taking the minimum spanning tree, which minimizes the total `-log(CZ fidelity)` and nothing else – degenerates on a chip of similar couplers into a long snake, where every qubit is entangled early and then idles through the remaining layers while the rest of the tree is built.

This module backs the `"tree"` state generation routine of [`iqm.benchmarks.entanglement.ghz`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz.html#module-iqm.benchmarks.entanglement.ghz "iqm.benchmarks.entanglement.ghz"), and picks all three together:

- `_ghz_graph()` builds the weighted connectivity graph over the layout;

- `_tree_candidates()` enumerates the trees worth considering;

- `_schedule_cost()` prices each one against the objective in [`TreeSearchOptions`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions");

- [`rank_ghz_trees()`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees.html#iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees "iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees") returns the best candidate of each root, ordered by that price, and [`generate_ghz_tree_optimal()`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.generate_ghz_tree_optimal.html#iqm.benchmarks.entanglement.ghz_optimal.generate_ghz_tree_optimal "iqm.benchmarks.entanglement.ghz_optimal.generate_ghz_tree_optimal") turns the requested rank of that ranking into a circuit.

The root qubit is the one the objective weighs most heavily: it carries the extra Hadamard, normally holds the highest degree of the tree, and is entangled before the first layer, so it is exposed to the whole idle window. Which root wins therefore depends on its single-qubit gate fidelity, T1 and T2 as well as on the CZ fidelities of the tree edges.

Calibration comes from [`extract_fidelities_unified()`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.extract_fidelities_unified.html#iqm.benchmarks.utils.extract_fidelities_unified "iqm.benchmarks.utils.extract_fidelities_unified"), which does not report gate durations, so a single [`CZ_GATE_DURATION`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.CZ_GATE_DURATION.html#iqm.benchmarks.entanglement.ghz_optimal.CZ_GATE_DURATION "iqm.benchmarks.entanglement.ghz_optimal.CZ_GATE_DURATION") is assumed for every CZ layer.

Module Attributes

|  |  |
|----|----|
| [`CZ_GATE_DURATION`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.CZ_GATE_DURATION.html#iqm.benchmarks.entanglement.ghz_optimal.CZ_GATE_DURATION "iqm.benchmarks.entanglement.ghz_optimal.CZ_GATE_DURATION") | Duration assumed for every CZ layer, in seconds. |
| [`TREE_OBJECTIVES`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES.html#iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES "iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES") | Accepted values of [`TreeSearchOptions.objective`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.objective "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.objective"). |

Functions

|  |  |
|----|----|
| [`cx_pairs`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.cx_pairs.html#iqm.benchmarks.entanglement.ghz_optimal.cx_pairs "iqm.benchmarks.entanglement.ghz_optimal.cx_pairs")(direct_ghz, order) | Recover the physical-index CX pairs of a generated GHZ circuit, in circuit order. |
| [`cz_layers`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.cz_layers.html#iqm.benchmarks.entanglement.ghz_optimal.cz_layers "iqm.benchmarks.entanglement.ghz_optimal.cz_layers")(pairs) | Assign each CX of the tree to the earliest layer it can run in. |
| [`generate_ghz_tree_optimal`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.generate_ghz_tree_optimal.html#iqm.benchmarks.entanglement.ghz_optimal.generate_ghz_tree_optimal "iqm.benchmarks.entanglement.ghz_optimal.generate_ghz_tree_optimal")(qubit_layout, ...) | Build a shallow GHZ circuit from one of the ranked trees over the layout. |
| [`rank_ghz_trees`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees.html#iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees "iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees")(qubit_layout, backend, metrics) | Score one spanning tree per possible root qubit and return them best first. |
| [`select_ghz_tree`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.select_ghz_tree.html#iqm.benchmarks.entanglement.ghz_optimal.select_ghz_tree "iqm.benchmarks.entanglement.ghz_optimal.select_ghz_tree")(qubit_layout, backend, metrics) | Choose the qubits, the tree and the gate order of the GHZ state. |

Classes

|  |  |
|----|----|
| [`TreeCandidate`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.html#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate")(root, pairs, order, cost, ...) | One scored spanning tree, as returned by [`rank_ghz_trees()`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees.html#iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees "iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees"). |
| [`TreeSearchOptions`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions")(\[objective, idle_penalty, ...\]) | How the tree search trades gate fidelity against circuit depth. |

Inheritance

![Inheritance diagram of iqm.benchmarks.entanglement.ghz_optimal](https://docs.iqm.tech/4.7/iqm-benchmarks/_images/inheritance-b544c1e347a00aa950dbdde0ddebf0e44b8280a5.png)
