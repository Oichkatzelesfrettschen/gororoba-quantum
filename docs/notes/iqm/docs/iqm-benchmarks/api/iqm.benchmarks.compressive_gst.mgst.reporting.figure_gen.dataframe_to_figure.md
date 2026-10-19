> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.dataframe_to_figure.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.dataframe_to_figure.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 35b2fcae2fb0481093a59a88ded6e75bbd13a56a8f0286f4dec863c7c3292d1a.

# iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.dataframe_to_figure

iqm.benchmarks.compressive_gst.mgst.reporting.figure_gen.dataframe_to_figure(*df: DataFrame*, *row_labels: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *col_width: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") = 2*, *fontsize: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 12*) → [Figure](https://matplotlib.org/stable/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure "(in Matplotlib v3.11.2)")  
Turns a pandas DataFrame into a figure.

This is needed to conform with the standard file saving routine of QCVV.

Parameters:  
- **df** (*DataFrame*) – A dataframe table containing GST results

- **row_labels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – The row labels for the dataframe

- **col_width** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Used to control cell width in the table

- **fontsize** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Font size of text/numbers in table cells

Returns:  
A figure representing the dataframe.

Return type:  
figure
