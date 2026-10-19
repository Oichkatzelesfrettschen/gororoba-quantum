> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.greedy_mis.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.greedy_mis.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1fd4d1e3610e2472338012e147423190adc0c18ad0e031dd3e4d18d65e23b0a3.

# greedy_mis

iqm.applications.mis.greedy_mis(*mis_problem*, *seed=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/mis.py#L413-L447)  
Standard greedy algorithm for maximum independent set problem class.

Steps:

1.  Pick the lowest-degree node in the graph (break ties randomly).

2.  Add it to the independent set.

3.  Remove it and all its neighbors from the graph.

4.  Repeat steps 1-3 until the graph is empty.

5.  Return the independent set.

Parameters:  
- **mis_problem** ([*MISInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.mis.MISInstance.html#iqm.applications.mis.MISInstance "iqm.applications.mis.MISInstance")) – A problem instance of maximum independent set to be solved (approximately).

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Optional seed for randomly breaking ties.

Returns:  
A bitstring solution.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")
