> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_remove_moves.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_remove_moves.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 393e7b3afc681f9e16a41e755ba108f18f8ebb78c4c77de15d0aa91fdf9b39da.

# iqm.iqm_client.transpile.transpile_remove_moves

iqm.iqm_client.transpile.transpile_remove_moves(*circuit: [Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")*) → [Circuit](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")  
Convert a Star architecture circuit into an equivalent simplified architecture circuit.

Converts a circuit involving resonators and MOVE gates into an equivalent simplified architecture circuit without them. The method assumes that in `circuit` a MOVE gate is always used to move a qubit state into a resonator before any other gates act on the resonator. If this is not the case, this function will not work as intended.

Parameters:  
**circuit** ([*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")) – Star architecture circuit from which resonators and MOVE gates should be removed.

Returns:  
Equivalent simplified architecture circuit without resonators and MOVEs.

Return type:  
[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")
