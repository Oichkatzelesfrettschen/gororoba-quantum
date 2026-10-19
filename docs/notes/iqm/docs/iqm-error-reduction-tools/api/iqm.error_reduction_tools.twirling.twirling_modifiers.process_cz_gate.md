> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.process_cz_gate.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.process_cz_gate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 aa826b1c025826ce108a3c8322e1cb446a30646b87e62c9806cdaead1d0a6f2a.

# iqm.error_reduction_tools.twirling.twirling_modifiers.process_cz_gate

iqm.error_reduction_tools.twirling.twirling_modifiers.process_cz_gate(*operation*, *new_circuit*, *registers*)  
Process a CZ gate: propagate pending π-rotation parity as Z kicks.

A CZ gate commutes with Z rotations but cojugates a R(π, φ) rotations as:

```
--[R(π, φ) ⊗ I]--[CZ]-- = --[CZ]--[R(π, φ) ⊗ Z]--
```

So, if there is a pending π-rotation on one qubit, a Z rotation of π is added to the *other* qubit.

Parameters:  
- **operation** ([*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")) – The CZ CircuitOperation to process.

- **new_circuit** ([*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit")) – The new circuit being built.

- **registers** ([*TrackingRegisters*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.html#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters")) – Tracking registers for Z and π-rotation state.

Return type:  
None
