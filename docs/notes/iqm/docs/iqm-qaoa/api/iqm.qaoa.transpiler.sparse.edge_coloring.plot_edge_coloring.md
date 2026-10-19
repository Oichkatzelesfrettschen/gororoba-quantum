> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.plot_edge_coloring.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.sparse.edge_coloring.plot_edge_coloring.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d12afe8869b771ed52030fa607644e910f118f31c0ff4f6436f06cddb5f3f154.

# plot_edge_coloring

iqm.qaoa.transpiler.sparse.edge_coloring.plot_edge_coloring(*graph*, *pos=None*, *color_palette=None*, *default_color='#00000000'*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/sparse/edge_coloring.py#L84-L118)  
A method that plots the edge coloring of a graph.

Careful! Here the variable `color_palette` is a list of strings, to convey the colors for plotting the graph. It maps the colors as integers (i.e., indices of the list) into strings which actually describe the color to plot, e.g., ‘r’ for red. This is different from other function in this module where `color_palette` is a set of integers.

Parameters:  
- **graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")) – A [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") whose edge coloring we want to plot.

- **pos** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]* *\|* *None*) – A dictionary of positions for drawing `graph` (i.e., the layout). If not provided, it defaults to the circular layout.

- **color_palette** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – A list of strings describing the colors to use in the plot.

- **default_color** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The color to use for edges that don’t have a color assigned to them yet.

Return type:  
None
