> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.PlotData.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.PlotData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 eb1c94c61abdcdd52b954875a29bce288c770ebac69d320803afd82ffc52fdea.

# PlotData

Module: [`iqm.applications.graph_utils`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.html#module-iqm.applications.graph_utils "iqm.applications.graph_utils")

*class* iqm.applications.graph_utils.PlotData(*graph*, *pos*, *node_colors*, *edge_colors*, *edge_widths*, *labels*, *edge_labels*, *node_size*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/graph_utils.py#L185-L204)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Precomputed visualization information used for drawing the graph.

Attributes

|  |  |
|----|----|
| [`graph`](#iqm.applications.graph_utils.PlotData.graph "iqm.applications.graph_utils.PlotData.graph") | The graph to be drawn. |
| [`pos`](#iqm.applications.graph_utils.PlotData.pos "iqm.applications.graph_utils.PlotData.pos") | Layout positions of the nodes. |
| [`node_colors`](#iqm.applications.graph_utils.PlotData.node_colors "iqm.applications.graph_utils.PlotData.node_colors") | Colors for each node. |
| [`edge_colors`](#iqm.applications.graph_utils.PlotData.edge_colors "iqm.applications.graph_utils.PlotData.edge_colors") | Colors for each edge. |
| [`edge_widths`](#iqm.applications.graph_utils.PlotData.edge_widths "iqm.applications.graph_utils.PlotData.edge_widths") | Widths for each edge. |
| [`labels`](#iqm.applications.graph_utils.PlotData.labels "iqm.applications.graph_utils.PlotData.labels") | Labels for nodes. |
| [`edge_labels`](#iqm.applications.graph_utils.PlotData.edge_labels "iqm.applications.graph_utils.PlotData.edge_labels") | Labels for edges (possibly empty). |
| [`node_size`](#iqm.applications.graph_utils.PlotData.node_size "iqm.applications.graph_utils.PlotData.node_size") | Scaled node size for plotting. |

Methods

Parameters:  
- **graph** ([*Graph*](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)"))

- **pos** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*)

- **node_colors** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **edge_colors** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **edge_widths** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*)

- **labels** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **edge_labels** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\],* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **node_size** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

graph*: [Graph](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)")*  
The graph to be drawn.

pos*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*  
Layout positions of the nodes.

node_colors*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Colors for each node.

edge_colors*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Colors for each edge.

edge_widths*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*  
Widths for each edge.

labels*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Labels for nodes.

edge_labels*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\], [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Labels for edges (possibly empty).

node_size*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Scaled node size for plotting.

Inheritance

![Inheritance diagram of iqm.applications.graph_utils.PlotData](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-05696338b567c1c75eec46768dd06e5f0e450e08.png)
