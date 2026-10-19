> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.greedy_max_cut.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.greedy_max_cut.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a24412060c545580b74e862799607b7af2fdabbaa64e8dc3cb3e06d8d8c299d6.

# greedy_max_cut

iqm.applications.maxcut.greedy_max_cut(*max_cut_problem*, *seed=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L379-L419)  
Standard greedy algorithm for maxcut problem class.

Steps:

1.  Start with a random assignment of nodes in two groups.

2.  Iterate over all nodes

3.  For each node, switch it to the other group if it improves the cost function.

4.  Repeat steps 2-3 until no node can be switched.

5.  Return the final assignment.

Parameters:  
- **max_cut_problem** ([*MaxCutInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance")) – A problem instance of maxcut to be solved (approximately).

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Seed for randomizing the initial assignment of nodes.

Returns:  
A bitstring solution.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")
