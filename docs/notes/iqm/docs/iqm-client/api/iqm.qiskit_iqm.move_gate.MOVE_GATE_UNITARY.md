> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.MOVE_GATE_UNITARY.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.MOVE_GATE_UNITARY.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 68fd3aaf3c5df67682300212712e9e5a0d8712ac10f4e9fd5b9ebcf1e0c69b33.

# iqm.qiskit_iqm.move_gate.MOVE_GATE_UNITARY

iqm.qiskit_iqm.move_gate.MOVE_GATE_UNITARY *= \[\[1.0, 0.0, 0.0, 0.0\], \[0.0, 0.0, np.complex128(0.7648421872844885+0.644217687237691j), 0.0\], \[0.0, np.complex128(0.7648421872844885-0.644217687237691j), 0.0, 0.0\], \[0.0, 0.0, 0.0, 1.0\]\]*  
Unitary matrix for simulating the ideal MOVE gate.

This matrix is not a realistic description of MOVE, since it applies a zero phase on the moved state, and acts as identity in the \\\|11 angle\\ subspace, thus being equal to the SWAP gate.
