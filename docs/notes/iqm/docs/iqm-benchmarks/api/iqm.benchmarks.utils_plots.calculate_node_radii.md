> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.calculate_node_radii.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils_plots.calculate_node_radii.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d79951d2a529bafa526a3f02848df7fdafaf6899d2dce5f88fafc549977286e0.

# iqm.benchmarks.utils_plots.calculate_node_radii

iqm.benchmarks.utils_plots.calculate_node_radii(*metric_dict: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\], [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*, *qubit_nodes: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *sq_metric: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Calculate node radii based on the specified single qubit metric.

For the coherence metric, the fidelity is calculated as the idling fidelity of a single qubit gate duration.

Parameters:  
- **metric_dict** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\],* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – Dictionary containing various qubit metrics.

- **qubit_nodes** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – List of qubits to calculate the radius for.

- **sq_metric** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Metric to use for radius calculation.

- **Options** – “fidelity”, “coherence”, or “readout”.

Returns:  
Array of radii values for each qubit node.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If an unsupported metric type is provided.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
