> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.cz_layers.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.entanglement.ghz_optimal.cz_layers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7c09a4b12f624b97186a39feaf85c9e7bb3a7be22457839aeabb710ad3a4e223.

# iqm.benchmarks.entanglement.ghz_optimal.cz_layers

iqm.benchmarks.entanglement.ghz_optimal.cz_layers(*pairs: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]  
Assign each CX of the tree to the earliest layer it can run in.

The GHZ tree is built breadth first, but a breadth-first level is not a layer of the executed circuit: two CXs of the same level that share their control qubit have to be serialized, while CXs of different levels can overlap. Scheduling each gate as early as its two qubits allow (ASAP) reproduces what the barriers and the transpiler actually do, so gates sharing a layer index are the ones played in parallel.

Parameters:  
**pairs** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*) – `(control, target)` qubit indices in circuit order.

Returns:  
The 0-based layer index of every pair.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]
