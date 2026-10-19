> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_pdf.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_pdf.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7b3e4002b248d154acab14aedd1d88996ec640866b0913c741493858edcbbc89.

# iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_pdf

iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_pdf(*filename: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *E: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *E2: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *rho2: [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")*, *title: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *spam2_content: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") = 'ideal'*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Generate pdf plots of two sets of POVM + state side by side in vector shape - Pauli basis.

The input sets can be either POVM/state directly or a difference different SPAM parametrizations to visualize errors.

Parameters:  
- **filename** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name under which the figures are saved in format “folder/name”

- **E** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – POVM

- **rho** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Initial state

- **E2** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – POVM \#2

- **rho2** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – Initial state \#2

- **title** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – The Figure title

- **spam2_content** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Label of the right SPAM plot to indicate whether it is the ideal SPAM parametrization or for instance the error between the reconstructed and target SPAM

Return type:  
None
