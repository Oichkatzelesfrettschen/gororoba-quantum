> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.circuit_to_gate_implementation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.utils.circuit_to_gate_implementation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f1f93be78bf714a0afb605a7b98d2b020abdec1f38b783d42a04e5cd3fc1369b.

# iqm.pulse.utils.circuit_to_gate_implementation

iqm.pulse.utils.circuit_to_gate_implementation(*circuit*, *circuit_locus*)  
Wrap a circuit to a single GateImplementation that can then be registered as a gate.

Returns a composite GateImplementation which, when called, produces a TimeBox with the circuit contents scheduled ASAP. `circuit` must contain only gates that are registered in IQM Pulse. The gate implementation does not need calibration data of its own: it uses the calibration of the member gates.

Parameters:  
- **circuit** ([*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "iqm.pulse.circuit_operations.Circuit")) – Circuit to wrap, typically a small subset of a larger circuit.

- **circuit_locus** (*Locus*) – All the locus component names used in `circuit`, in the order they appear in the gate locus.

Returns:  
Composite gate implementation class which can be registered to iqm-pulse as an implementation of a new gate.

Return type:  
[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[*CompositeGate*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeGate.html#iqm.pulse.gate_implementation.CompositeGate "iqm.pulse.gate_implementation.CompositeGate")\]
