> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.NODE_ATTR_PRIORITY.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.NODE_ATTR_PRIORITY.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4dcca7c93ab88aead9de0b8a0073a124d7717ac134cd24dae42ba2b21296493e.

# NODE_ATTR_PRIORITY

iqm.applications.graph_utils.NODE_ATTR_PRIORITY*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]* *= ('bias', 'weight', 'field', 'value', 'h')*  
Ordered names of node attributes that may store node weights.

When extracting node weights from a graph, attributes are checked in this order and the first match is used. This allows the library to accept graphs originating from different conventions (e.g. “weight”, “field”, etc.).
