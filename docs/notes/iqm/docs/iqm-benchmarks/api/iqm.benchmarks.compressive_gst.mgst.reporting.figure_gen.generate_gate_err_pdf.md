> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_gate_err_pdf.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_gate_err_pdf.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4c553e7a9d8bd17705d41ce482ea695d8226641325ecb4f6a890cd7ad0450629.

# iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_gate_err_pdf

iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_gate_err_pdf(*filename: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *gates1: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *gates2: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *basis_labels: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *gate_labels: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *save_fig: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\]  
Main routine to generate plots of reconstructed gates, ideal gates and the noise channels.

of the reconstructed gates. The matrices are shown as Hinton diagrams, where the size of each square represents the magnitude of the matrix element and the color represents its sign as well as the magnitude. The basis is arbitrary but using gates in the Pauli basis is recommended.

Parameters:  
- **filename** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name under which the figures are saved in format “folder/name”

- **gates1** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A gate set in the same format as the “X”-tensor. These gates are assumed to be the GST estimates.

- **gates2** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – A gate set in the same format as the “X”-tensor. These are assumed to be the target gates.

- **basis_labels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – A list of labels for the basis elements. For the standard basis this could be \[“00”, “01”,…\] and for the Pauli basis \[“I”, “X”, “Y”, “Z”\] or the multi-qubit version.

- **gate_labels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – A list of names for the gates

- **save_fig** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to save the generated figures as pdf files

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Figure*](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\]
