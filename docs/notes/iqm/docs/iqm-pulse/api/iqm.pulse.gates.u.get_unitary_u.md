> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.get_unitary_u.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.get_unitary_u.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3eeb6e2e04f0c14cdf85e30f7946c17d1ce544bb03f5377b280c85048224e16c.

# iqm.pulse.gates.u.get_unitary_u

iqm.pulse.gates.u.get_unitary_u(*theta*, *phi*, *lam*)  
Unitary for an SU(2) gate.

See [`iqm.pulse.gates.u`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.u.html#module-iqm.pulse.gates.u "iqm.pulse.gates.u") for the definition of the gate parameters.

Parameters:  
- **theta** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – y rotation angle

- **phi** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – z rotation angle

- **lam** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – another z rotation angle

Returns:  
2x2 unitary representing `u(theta, phi, lam)`.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
