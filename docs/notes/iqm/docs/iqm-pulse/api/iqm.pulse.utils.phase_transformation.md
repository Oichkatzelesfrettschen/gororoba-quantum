> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.phase_transformation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.phase_transformation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 995718b9a2a878ecc31cf386e31643bb83a31f835c9f4675b17381c67bc9867f.

# iqm.pulse.utils.phase_transformation

iqm.pulse.utils.phase_transformation(*psi_1=0.0*, *psi_2=0.0*)  
Implement an (RZ, PRX, RZ) gate sequence by modifying the parameters of the IQ pulse implementing the PRX.

By commutation rules we have

\\RZ(\psi_2) \\ PRX(\theta, \phi) \\ RZ(\psi_1) = PRX(\theta, \phi+\psi_2) \\ RZ(\psi_1 + \psi_2).\\

Hence an arbitrary (RZ, PRX, RZ) gate sequence is equivalent to (RZ, PRX) with adjusted angles.

Use case: with resonant driving, the PRX gate can be implemented using an `IQPulse` instance, and the preceding RZ can be handled by decrementing the local oscillator phase beforehand (something the IQPulse instruction can also do), which is equivalent to rotating the local computational frame around the z axis in the opposite direction of the required quantum state rotation.

Parameters:  
- **psi_1** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – RZ angle before the PRX (in rad)

- **psi_2** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – RZ angle after the PRX (in rad)

Returns:  
change to the PRX phase angle (in rad), phase increment for the IQ pulse that implements the remaining RZ (in rad)

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
