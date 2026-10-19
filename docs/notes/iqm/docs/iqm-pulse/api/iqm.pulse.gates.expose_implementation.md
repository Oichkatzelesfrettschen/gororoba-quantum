> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.expose_implementation.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.expose_implementation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 971b2b28c5f995bde6da29c41dbf8e92f8f4aee753948115ba723af34b77758d.

# iqm.pulse.gates.expose_implementation

iqm.pulse.gates.expose_implementation(*implementation*, *overwrite=False*)  
Add the given gate implementation to the list of known implementations.

Parameters:  
- **implementation** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")*\]*) – GateImplementation to add so that it can be found with [`get_implementation_class()`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.get_implementation_class.html#iqm.pulse.gates.get_implementation_class "iqm.pulse.gates.get_implementation_class").

- **overwrite** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, does not raise an error if implementation already exists.

Return type:  
*None*
