> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.quantum_op_to_qrisp_func.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.quantum_op_to_qrisp_func.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 65d4c56a01db61d0709863fa5fc69bcf21e38b4857e3385c1462f6cceda22af9.

# iqm.qrisp_iqm.pulse_operation.quantum_op_to_qrisp_func

iqm.qrisp_iqm.pulse_operation.quantum_op_to_qrisp_func(*quantum_op: [QuantumOp](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "(in iqm.pulse v15.0.0)")*) → [QrispFunction](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.QrispFunction.html#iqm.qrisp_iqm.pulse_operation.QrispFunction "iqm.qrisp_iqm.pulse_operation.QrispFunction")  
Create a function for appending IQM Pulse quantum operations to a Qrisp quantum circuit.

Returns a callable that can be used to append an IQMPulseOperation for the specified QuantumOp to a Qrisp circuit. The returned function accepts locus qubits as positional arguments and operation parameters as keyword arguments.

In Jasp tracing mode, dynamic (JAX-traced) parameter values are supported: SymPy placeholder symbols are used in the operation definition, while the actual traced values are forwarded via `param_tracers`.

Parameters:  
**quantum_op** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "(in iqm.pulse v15.0.0)")) – IQM Pulse quantum operation definition.

Returns:  
Function for adding the corresponding operation to a Qrisp circuit.

Return type:  
[*QrispFunction*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.QrispFunction.html#iqm.qrisp_iqm.pulse_operation.QrispFunction "iqm.qrisp_iqm.pulse_operation.QrispFunction")

Example

Define a custom `delay` pulse operation, convert it into a Qrisp gate function, and use it inside a Jasp-traced circuit that is then compiled to an IQM pulse circuit:

``` python
from qrisp import QuantumVariable, h, cx, measure
from iqm.pulse.quantum_ops import QuantumOp
from iqm.qrisp_iqm import extract_iqm_pulse, quantum_op_to_qrisp_func

delay_quantum_op = QuantumOp(name="delay", params={"duration": (float,)})
delay = quantum_op_to_qrisp_func(delay_quantum_op)

@extract_iqm_pulse(dqa=...)
def my_circuit():
    qv = QuantumVariable(2)
    h(qv[0])
    delay(qv[0], duration=100e-9)
    cx(qv[0], qv[1])
    return measure(qv)

meas_keys, iqm_circuit = my_circuit()
```
