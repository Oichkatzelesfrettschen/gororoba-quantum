> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.max_cut_exact.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.max_cut_exact.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4a08a2c5b2735773a7248c37ac59b29d164eb913831e390d0c0d43101b4e67f3.

# max_cut_exact

iqm.applications.maxcut.max_cut_exact(*problem*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L479-L589)  
Runs an exact solver for the (weighted) maxcut problem, using branch-and-bound.

Parameters:  
**problem** ([*MaxCutInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance") *\|* [*WeightedMaxCutInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.WeightedMaxCutInstance.html#iqm.applications.maxcut.WeightedMaxCutInstance "iqm.applications.maxcut.WeightedMaxCutInstance")) – The (weighted) problem instance to be solved.

Returns:  
A set containing all of the bitstrings strings that minimize the energy of the problem.

Return type:  
[set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
