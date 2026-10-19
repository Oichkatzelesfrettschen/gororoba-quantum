> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.greedy_mwis.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.greedy_mwis.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 601062e29d882ca7739fc7a0d2cf7468d8a229286c750574ff1770177fbcadbb.

# greedy_mwis

iqm.applications.mis.greedy_mwis(*mwis_problem*, *seed=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L450-L476)  
Compute an approximation to the maximum-weight independent set using a greedy heuristic.

This function approximates a Maximum Weight Independent Set (MWIS) by computing a greedy minimum-weight vertex cover on a copy of the input graph and returning its complement. Node weights are interpreted according to the same attribute-priority convention used by [`MaximumWeightISInstance`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MaximumWeightISInstance.html#iqm.applications.mis.MaximumWeightISInstance "iqm.applications.mis.MaximumWeightISInstance") (see [`NODE_ATTR_PRIORITY`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.graph_utils.NODE_ATTR_PRIORITY.html#iqm.applications.graph_utils.NODE_ATTR_PRIORITY "iqm.applications.graph_utils.NODE_ATTR_PRIORITY")).

Parameters:  
- **mwis_problem** ([*MaximumWeightISInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MaximumWeightISInstance.html#iqm.applications.mis.MaximumWeightISInstance "iqm.applications.mis.MaximumWeightISInstance")) – MWIS Instance which we’re trying to solve.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Optional random seed used to break ties reproducibly during the greedy selection process.

Returns:  
A bitstring encoding the selected independent set.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")
