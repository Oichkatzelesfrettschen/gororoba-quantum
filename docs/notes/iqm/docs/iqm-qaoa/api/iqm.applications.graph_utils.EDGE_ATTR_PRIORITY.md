> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.EDGE_ATTR_PRIORITY.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.EDGE_ATTR_PRIORITY.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b45f1ce07814cb80fa3b400760f87247a1c99008fcc278715ba7447606fa145a.

# EDGE_ATTR_PRIORITY

iqm.applications.graph_utils.EDGE_ATTR_PRIORITY*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ('bias', 'weight', 'coupling', 'interaction', 'J')*  
Ordered names of edge attributes that may store edge weights.

When extracting edge weights from a graph, attributes are checked in this order and the first match is used. This allows the library to accept graphs originating from different conventions (e.g. “weight”, “coupling”, etc.).
