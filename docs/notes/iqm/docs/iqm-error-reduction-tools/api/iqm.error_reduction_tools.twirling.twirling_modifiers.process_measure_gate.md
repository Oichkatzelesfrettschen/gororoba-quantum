> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.process_measure_gate.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.process_measure_gate.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f8d33616068ecee120c55d9f58f10b26ecb872a6ef07eb16ca232386eb26c158.

# iqm.error_reduction_tools.twirling.twirling_modifiers.process_measure_gate

iqm.error_reduction_tools.twirling.twirling_modifiers.process_measure_gate(*operation*, *new_circuit*, *registers*, *drop_final_rz=True*)  
Process a measurement gate: record readout twirling character and append.

Determines the net readout twirling character (‘I’ or ‘X’) from the parity of accumulated π rotations on the measured qubit, stores it in `registers.rot_chars`, and appends the measurement operation.

Parameters:  
- **operation** ([*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")) – The measurement CircuitOperation to process.

- **new_circuit** ([*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit")) – The new circuit being built.

- **registers** ([*TrackingRegisters*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters.html#iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters "iqm.error_reduction_tools.twirling.twirling_modifiers.TrackingRegisters")) – Tracking registers for π-rotation state and readout characters.

- **drop_final_rz** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True (default), any pending virtual-Z before measurement is silently dropped. If False, raises NotImplementedError.

Return type:  
None
