> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_rotation_param_results.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_rotation_param_results.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 adc2ee3ccfca202a401c555c3c214e51a1171a2238c5f6744e61d42fabf569c9.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_rotation_param_results

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_rotation_param_results(*dataset: Dataset*, *qubit_layout: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *X_opt: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *K_target: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *X_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *E_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *rho_array: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[DataFrame, [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\]  
Produces result tables and data for Kraus rank 1 estimates.

This includes parameters of the Hamiltonian generators in the Pauli basis for all gates. If bootstrapping data is available, error bars will also be generated.

Parameters:  
- **dataset** (*Dataset*) – xarray.Dataset A dataset containing counts from the experiment and configurations

- **qubit_layout** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – List\[int\] The list of qubits for the current GST experiment

- **X_opt** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 3D numpy array The gate set after gauge optimization

- **K_target** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – 4D numpy array The Kraus operators of all target gates, used to compute distance measures.

- **X_array** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* *None*) – ndarray, optional Array of bootstrap gate estimates, used for error bars

- **E_array** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* *None*) – ndarray, optional Array of bootstrap POVM estimates, used for error bars

- **rho_array** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* *None*) – ndarray, optional Array of bootstrap state estimates, used for error bars

Returns:  
- Pandas DataFrame containing Hamiltonian (rotation) parameters with formatted values

- Dictionary with raw values and uncertainty bounds if bootstrapping was used

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[*DataFrame*, [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\]
