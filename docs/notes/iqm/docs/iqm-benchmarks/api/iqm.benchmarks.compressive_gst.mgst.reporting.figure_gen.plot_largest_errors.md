> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_largest_errors.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_largest_errors.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7551c87fbe0cda03ba9df0e21cd0c0dfdbc36c2511958c8e4b9cd741d0adca73.

# iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_largest_errors

iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_largest_errors(*param_delta: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *param_labels: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *n_errs: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *threshold: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*, *gate_label: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *has_uncertainties: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *yerr_low: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *yerr_high: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *param_delta_high: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *param_delta_low: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")  
Generate a bar plot showing the largest coherent errors.

Parameters:  
- **param_delta** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Difference between measured and ideal parameters

- **param_labels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Labels for the Pauli basis elements

- **n_errs** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of largest errors to display

- **threshold** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Minimum threshold for errors to display

- **gate_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Label of the gate being visualized

- **has_uncertainties** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether uncertainty data is available

- **yerr_low** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* *None*) – Lower error bounds

- **yerr_high** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* *None*) – Upper error bounds

- **param_delta_high** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* *None*) – Upper bound differences

- **param_delta_low** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)") *\|* *None*) – Lower bound differences

Returns:  
The generated bar plot figure

Return type:  
[*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")
