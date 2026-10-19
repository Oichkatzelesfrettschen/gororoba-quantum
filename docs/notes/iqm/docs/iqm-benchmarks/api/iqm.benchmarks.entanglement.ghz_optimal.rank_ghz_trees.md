> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3cacd748b7c6d2b5a06aec15dc1de0e589f275260d709ea86324679e9f1d0c6a.

# iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees

iqm.benchmarks.entanglement.ghz_optimal.rank_ghz_trees(*qubit_layout: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *backend: [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *metrics: [Mapping](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Mapping "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Mapping](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Mapping "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*, *num_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *options: [TreeSearchOptions](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[TreeCandidate](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate.html#iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate "iqm.benchmarks.entanglement.ghz_optimal.TreeCandidate")\]  
Score one spanning tree per possible root qubit and return them best first.

Subset and tree are chosen together: which `num_qubits` qubits are cheapest depends on the shape of the tree that will connect them, so scoring the two separately picks an elongated set and then pays for it in depth.

Only the best candidate of each root is kept. The search generates many trees per root that differ by a single edge, and keeping them would fill the ranking with near-duplicates – one per root is what makes rank `n` a genuinely different starting node rather than a rounding difference.

Candidates whose costs agree to `_COST_TIE_DECIMALS` are ordered by CZ layer count, so that where the objective cannot tell two trees apart the shallower one ranks first.

Parameters:  
- **qubit_layout** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – The subset of system-qubits used in the protocol, indexed from 0.

- **backend** ([*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – The backend whose coupling map defines the connectivity.

- **metrics** ([*Mapping*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Mapping "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Mapping*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Mapping "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\],* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – The metrics dictionary from [`extract_fidelities_unified()`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.extract_fidelities_unified.html#iqm.benchmarks.utils.extract_fidelities_unified "iqm.benchmarks.utils.extract_fidelities_unified"), whose keys are physical qubit indices.

- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Size of the GHZ state; `None` uses every qubit of the layout.

- **options** ([*TreeSearchOptions*](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions") *\|* *None*) – What the search minimizes; defaults to [`TreeSearchOptions`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions.html#iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions "iqm.benchmarks.entanglement.ghz_optimal.TreeSearchOptions").

Returns:  
when no connected set of the requested size exists it holds a single linear-chain fallback.

Return type:  
The candidates sorted by non-decreasing cost, one per root, never empty

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `options.objective` is not one of [`TREE_OBJECTIVES`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES.html#iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES "iqm.benchmarks.entanglement.ghz_optimal.TREE_OBJECTIVES").
