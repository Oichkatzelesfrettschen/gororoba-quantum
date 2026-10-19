> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.greedy_router.greedy_router.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.greedy_router.greedy_router.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f0a03eba15c77afe02d5014ad21bee95f2d808f34c66fcbbf2087675c9366dc6.

# greedy_router

iqm.qaoa.transpiler.sparse.greedy_router.greedy_router(*problem_bqm*, *qpu*, *max_iter_color_pairs=1*, *key_best_route=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/sparse/greedy_router.py#L548-L593)  
The function which takes a problem BQM `problem_bqm` and a QPU `qpu` and returns a routing.

This serves as a ‘wrapper’ for the entire greedy routing algorithm. For details of the algorithm, see \[[7](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id4 "Ayse Kotil, Fedor Simkovic, and Martin Leib. Improved qubit routing for QAOA circuits. https://arxiv.org/abs/2312.15982, Dec 2023.")\].

Parameters:  
- **problem_bqm** ([*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – The `BinaryQuadraticModel` of the problem we’re trying to solve.

- **qpu** ([*QPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")) – The [`QPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU") that we’re going to solve the problem on.

- **max_iter_color_pairs** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – How many different starting color pairs (sorted by size) should be iterated over.

- **key_best_route** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*\[\[*[*Routing*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing")*\],* [*SupportsLessThan*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.greedy_router.SupportsLessThan.html#iqm.qaoa.transpiler.sparse.greedy_router.SupportsLessThan "iqm.qaoa.transpiler.sparse.greedy_router.SupportsLessThan")*\]* *\|* *None*) – The key to determine which routing is the best if `max_iter_color_pairs` is greater than 1. This should be a function that takes [`iqm.qaoa.transpiler.routing.Routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") on input and returns something comparable (typically a `float` or an `int`). It is assumed that this `key` is **minimized**. The default is `lambda o: len(o.layers)`, i.e., the routing with the minimal number of layers. Another recommended option is `lambda o: o.count_swap_gates()`.

Returns:  
A routing object containing all the swap and interaction layers needed to execute one QAOA layer.

Return type:  
[*Routing*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing")
