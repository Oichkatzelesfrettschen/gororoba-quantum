> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 47f976f5cc0065470465c57bb4a5b5808a1c232a9c640c5bad8406149872f6ca.

# utils

Full path: iqm.pulse.utils

Utility functions.

Module Attributes

|  |  |
|----|----|
| [`TOLERANCE`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.TOLERANCE.html#iqm.pulse.utils.TOLERANCE "iqm.pulse.utils.TOLERANCE") | Tolerance for floating point artefacts in waveform computations. |

Functions

|  |  |
|----|----|
| [`circuit_to_gate_implementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.circuit_to_gate_implementation.html#iqm.pulse.utils.circuit_to_gate_implementation "iqm.pulse.utils.circuit_to_gate_implementation")(circuit, ...) | Wrap a circuit to a single GateImplementation that can then be registered as a gate. |
| [`fuse_iq_pulses`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.fuse_iq_pulses.html#iqm.pulse.utils.fuse_iq_pulses "iqm.pulse.utils.fuse_iq_pulses")(iq_pulses) | Fuse multiple IQPulses into one by concatenating the sampled waveforms. |
| [`get_other_colour`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.get_other_colour.html#iqm.pulse.utils.get_other_colour "iqm.pulse.utils.get_other_colour")(station_properties, qubit) | Get the set of qubits that are in the other colour than the given qubit. |
| [`modulate_iq`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.modulate_iq.html#iqm.pulse.utils.modulate_iq "iqm.pulse.utils.modulate_iq")(pulse\[, assert_ranges\]) | Sampled baseband waveform of an IQ pulse. |
| [`phase_transformation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.phase_transformation.html#iqm.pulse.utils.phase_transformation "iqm.pulse.utils.phase_transformation")(\[psi_1, psi_2\]) | Implement an (RZ, PRX, RZ) gate sequence by modifying the parameters of the IQ pulse implementing the PRX. |
