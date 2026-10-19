> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_Choi_EV_table.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_Choi_EV_table.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 68adc613ed63b283fdf08d4675098e7b10fb58a27adc7a870ad543b6b4554d10.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_Choi_EV_table

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_Choi_EV_table(*X_opt: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *n_evals: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *gate_labels: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*, *filename: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → DataFrame  
Outputs a .tex document containing a table with the larges eigenvalues of the Choi matrix for each gate.

Parameters:  
- **X_opt** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Array where CPT superoperators in standard basis are stacked along the first axis.

- **n_evals** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of eigenvalues to be returned

- **gate_labels** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – The names of gates in the gate set

- **filename** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – The file name of the output .tex file

Return type:  
*DataFrame*
