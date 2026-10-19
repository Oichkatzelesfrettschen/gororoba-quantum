> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_hamiltonian_visualizations.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_hamiltonian_visualizations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 902778521d65d1e25c9112e94648b16b1d90cee00af0a02e922da6bbcf50cbfe.

# iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_hamiltonian_visualizations

iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_hamiltonian_visualizations(*dataset: Dataset*, *n_errs: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 4*, *threshold: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 0.01*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")\]  
Plots the coherent errors as the difference of the entries of two Hamiltonian in the Pauli basis.

1.  Matrix plots showing all parameters with color coding

2.  Bar plots showing the largest coherent errors

Parameters:  
- **dataset** (*Dataset*) – A dataset containing counts from the experiment, results, and configurations.

- **n_errs** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of largest errors to plot in bar charts. Default is 4.

- **threshold** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Minimum threshold for errors to display in bar charts. The threshold can lead to more than n_errs errors being displayed.

Returns:  
- Matrix plots

- Bar plots

Return type:  
A tuple containing two nested lists of figures for each qubit layout and gate
