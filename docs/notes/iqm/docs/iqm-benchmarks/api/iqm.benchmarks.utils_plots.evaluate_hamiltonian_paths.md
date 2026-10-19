> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.evaluate_hamiltonian_paths.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.evaluate_hamiltonian_paths.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 271ef6c2b2b527e2cab5ff7553409544237805f733cf943210562be7d942aabf.

# iqm.benchmarks.utils_plots.evaluate_hamiltonian_paths

iqm.benchmarks.utils_plots.evaluate_hamiltonian_paths(*n_vertices: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *path_samples: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *backend: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [IQMBackendBase](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")*, *max_tries: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 10*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]  
Evaluates Hamiltonian paths according to the product of 2Q gate fidelities on the edges of the backend graph.

Parameters:  
- **n_vertices** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the number of vertices in the Hamiltonian paths to evaluate.

- **path_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the number of Hamiltonian paths to evaluate.

- **backend** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*IQMBackendBase*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase "(in IQM client v36.0.0)")) – the backend to evaluate the Hamiltonian paths on with respect to fidelity.

- **max_tries** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – the maximum number of tries to generate a Hamiltonian path.

Returns:  
A dictionary with keys being fidelity products and values being the respective Hamiltonian paths.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]\]
