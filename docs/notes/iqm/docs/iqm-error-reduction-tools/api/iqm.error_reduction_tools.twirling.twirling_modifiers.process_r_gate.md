> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.process_r_gate.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.process_r_gate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 75e5f27d79bdc25ec5f94a95c494712f887389de419060462c5aac9ae527b58e.

# iqm.error_reduction_tools.twirling.twirling_modifiers.process_r_gate

iqm.error_reduction_tools.twirling.twirling_modifiers.process_r_gate(*operation*, *twirled_circuit*, *rgen*, *registers*, *enforce_readout_twirling_basis=None*, *twirling_prob=0.5*, *fix_axes=False*)  
Process an R gate: absorb pending operations, then optionally insert a twirling π rotation.

First delegates to take_care_of_pending_operations to commute any accumulated Z and π rotations into the gate parameters. Then, with probability `twirling_prob` (possibly adjusted by parity or readout twirling constraints), inserts a new π rotation via insert_twirling_pi_rotation. Finally appends the resulting PRX gate to the twirled circuit.

Parameters:  
- **operation** ([*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")) – The PRX CircuitOperation to process.

- **twirled_circuit** ([*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit")) – The new circuit being built.

- **rgen** ([*Generator*](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator "(in NumPy v2.5)")) – Random number generator for twirling decisions.

- **registers** ([*TrackingRegisters*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.html#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters")) – Tracking registers for Z, π-rotation state, etc.

- **enforce_readout_twirling_basis** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – If set (‘X’ or ‘I’), overrides twirling_prob to enforce a specific readout twirling outcome on the last SQG.

- **twirling_prob** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Probability of inserting a twirling π rotation. Defaults to 0.5.

- **fix_axes** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, the twirling π rotation axis is fixed to match the gate’s phase rather than being uniformly random. Defaults to False.

Return type:  
None
