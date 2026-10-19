> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.run_mGST.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.algorithm.run_mGST.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ac5aea1b548af5d15553e412d89efa0afb99a1c29153d352778a0a4adcab24da.

# iqm.benchmarks.compressive_gst.mgst.algorithm.run_mGST

iqm.benchmarks.compressive_gst.mgst.algorithm.run_mGST(*args: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*, *method: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'SFN'*, *max_inits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 10*, *max_iter: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 200*, *final_iter: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 120*, *target_rel_prec: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 1e-05*, *threshold_multiplier: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 5*, *fixed_elements: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *init: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *verbose_level: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*) → [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\]  
Main mGST routine.

Parameters:  
- **args** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*,* [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*,* *None,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Tuple containing (y, J, \_, d, r, rK, n_povm, bsize, meas_samples) where: - y: 2D array of measurement outcomes for sequences in J - J: 2D array where each row contains gate indices of a gate sequence - \_: unused parameter - d: Number of different gates in the gate set - r: Superoperator dimension (square of physical dimension) - rK: Target Kraus rank - n_povm: Number of POVM elements - bsize: Size of the batch (number of sequences) - meas_samples: Number of samples per gate sequence for measurement array y

- **method** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Optimization method: “SFN” or “GD”

- **max_inits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Maximum number of random initializations to try

- **max_iter** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Maximum number of iterations on batches

- **final_iter** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Maximum number of iterations on full data set

- **target_rel_prec** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Target relative precision at which the optimization loop breaks

- **threshold_multiplier** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Multiplier for the stopping criterion threshold

- **fixed_elements** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") *\|* *None*) – List of element names to keep fixed during optimization (e.g., \[“E”, “rho”, “G0”\])

- **init** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]\]* *\|* *None*) – List of 3 numpy arrays \[K, E, rho\] for initialization; If not provided, random initialization is used

- **verbose_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Verbosity level: 0 (silent), 1 (info), 2 (info + plots)

Returns:  
Updated estimates of Kraus operators X: Updated estimates of superoperators corresponding to K E: Updated POVM estimate rho: Updated initial state estimate res_list: Collected objective function values after each iteration

Return type:  
K
