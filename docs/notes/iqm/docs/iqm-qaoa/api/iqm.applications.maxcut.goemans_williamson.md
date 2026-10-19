> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.goemans_williamson.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.goemans_williamson.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8faf2aa2bee2630a4a6d8780d1e3a8f5c50fc6e3383a6e8d158724034fbc9ce3.

# goemans_williamson

iqm.applications.maxcut.goemans_williamson(*max_cut_problem*, *seed=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/maxcut.py#L422-L476)  
Runs the Goemans-Williamson algorithm for maxcut, returning a solution bitstring.

The Goemans-Williamson is a randomized algorithm for maxcut, with a guaranteed approximation ratio of around `0.87856`. The algorithm was first described in \[[1](https://docs.iqm.tech/4.7/iqm-qaoa/references.html#id5 "Michel X. Goemans and David P. Williamson. Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming. J. ACM, 42(6):1115–1145, November 1995. URL: https://doi.org/10.1145/227683.227684, doi:10.1145/227683.227684.")\].

Steps:

1.  Relax the problem to a semidefinite program (SDP) with each variable represented by a multi-dimensional vector on a unit sphere.

2.  Solve the SDP.

3.  Generate a random hyperplane through the origin.

4.  Assign the variables to `0` or `1` based on which side of the plane their multi-dimensional vector lies.

Parameters:  
- **max_cut_problem** ([*MaxCutInstance*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.maxcut.MaxCutInstance.html#iqm.applications.maxcut.MaxCutInstance "iqm.applications.maxcut.MaxCutInstance")) – A problem instance of maxcut to be solved (approximately).

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – An optional seed to fix the rotation of the random hyperplane.

Returns:  
A bitstring solution.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")
