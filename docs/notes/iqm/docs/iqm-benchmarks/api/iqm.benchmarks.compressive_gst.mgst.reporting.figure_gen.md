> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 86be322ad58be9d1a5b0029cafabdc21b3d6aee8db758d5cd3d0391ed1bac955.

# iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen

Generation of figures.

Functions

|  |  |
|----|----|
| [`dataframe_to_figure`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.dataframe_to_figure.html#iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.dataframe_to_figure "iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.dataframe_to_figure")(df\[, row_labels, ...\]) | Turns a pandas DataFrame into a figure. |
| [`generate_gate_err_pdf`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_gate_err_pdf.html#iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_gate_err_pdf "iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_gate_err_pdf")(filename, gates1, gates2) | Main routine to generate plots of reconstructed gates, ideal gates and the noise channels. |
| [`generate_hamiltonian_visualizations`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_hamiltonian_visualizations.html#iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_hamiltonian_visualizations "iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_hamiltonian_visualizations")(dataset) | Plots the coherent errors as the difference of the entries of two Hamiltonian in the Pauli basis. |
| [`generate_spam_err_pdf`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_pdf.html#iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_pdf "iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_pdf")(filename, E, rho, E2, rho2) | Generate pdf plots of two sets of POVM + state side by side in vector shape - Pauli basis. |
| [`generate_spam_err_std_pdf`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_std_pdf.html#iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_std_pdf "iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.generate_spam_err_std_pdf")(filename, E, rho, ...) | Generate pdf plots of two sets of POVM + state side by side in matrix shape - standard basis. |
| [`plot_largest_errors`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_largest_errors.html#iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_largest_errors "iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_largest_errors")(param_delta, ...\[, ...\]) | Generate a bar plot showing the largest coherent errors. |
| [`plot_objf`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_objf.html#iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_objf "iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.plot_objf")(res_list, title\[, delta\]) | Plots the objective function over iterations in the algorithm. |
| [`set_size`](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.set_size.html#iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.set_size "iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.set_size")(w, h\[, ax\]) | Forcing a figure to a specified size. |
