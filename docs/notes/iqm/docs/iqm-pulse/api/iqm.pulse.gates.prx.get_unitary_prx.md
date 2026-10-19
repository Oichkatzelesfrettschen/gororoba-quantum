> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.get_unitary_prx.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.prx.get_unitary_prx.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 40b673cfab85a40841ca00e6ac1f372b611e686114c883a6d401372f36306947.

# iqm.pulse.gates.prx.get_unitary_prx

iqm.pulse.gates.prx.get_unitary_prx(*angle*, *phase*)  
Unitary for a PRX gate.

Parameters:  
- **angle** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – rotation angle (in rad)

- **phase** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – phase angle (in rad)

Returns:  
2x2 unitary representing `prx(angle, phase)`.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")
