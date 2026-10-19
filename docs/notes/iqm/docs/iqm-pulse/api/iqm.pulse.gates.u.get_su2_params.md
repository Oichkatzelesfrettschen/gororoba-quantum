> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.get_su2_params.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.get_su2_params.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fb24fe5ed098948fe5abe547428d9fff90c7eef31694b950b124ebf6fd8df4bb.

# iqm.pulse.gates.u.get_su2_params

iqm.pulse.gates.u.get_su2_params(*unitary*, *threshold=1e-13*)  
Calculate parameters for an SU(2) gate given its unitary.

The parameters are calculated up to global phase, and such that `0 <= theta <= pi` and `-pi <= phi, lam < pi`. See [`iqm.pulse.gates.u`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.html#module-iqm.pulse.gates.u "iqm.pulse.gates.u") for the definition of the gate parameters.

Parameters:  
- **unitary** ([*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")) – U(2) matrix to calculate parameters for, ignoring the global phase.

- **threshold** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Precision threshold to decide if the unitary describes a pure Z rotation, a pi rotation, or neither.

Returns:  
Parameters theta, phi, lambda for the `u` gate.

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
