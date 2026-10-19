> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4506bb1e98ec42d080f53d7c1e03e01a33006fabbd39028905dabe01792a4564.

# IQMPulseOperation

Module: [`iqm.qrisp_iqm.pulse_operation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.html#module-iqm.qrisp_iqm.pulse_operation "iqm.qrisp_iqm.pulse_operation")

*class* iqm.qrisp_iqm.pulse_operation.IQMPulseOperation(*quantum_op: [QuantumOp](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "(in iqm.pulse v15.0.0)")*, *param_dict: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *num_clbits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 0*)  
Bases: `Operation`

Qrisp Operation that represents an IQM Pulse quantum operation.

This class allows users to insert specific IQM Pulse quantum operations (like barriers, delays, or custom gate implementations) directly into a Qrisp QuantumCircuit. These operations are treated as opaque boxes by the Qrisp transpiler, ensuring they survive the compilation process and reach the backend unchanged.

Mechanism for transpilation survival: Because IQMPulseOperation inherits from the base `Operation` class but does not provide a `definition` (decomposition into standard gates) or built-in QASM conversion, Qrisp’s transpilation passes generally ignore it. It passes through optimizations untouched, preserving its position in the circuit relative to other gates.

Parameter handling: Parameters are passed as a dictionary. Qrisp stores the values in `params` (required for any parameter optimization or bind logic). This class additionally stores parameter names in `param_names`. The IQM Pulse converter uses these names to reconstruct the dictionary argument required by `QuantumOp.__init__()`.

Parameters:  
- **quantum_op** (*QuantumOp*) – IQM Pulse quantum operation definition. This object is expected to contain the concrete parameter values in its `params` attribute and the concrete qubit count in its `arity` attribute.

- **param_dict** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Any\]* *\|* *None*) – Dictionary of parameter name-value pairs. Must match the QuantumOp’s params.

- **num_clbits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of classical bits the operation uses.

Examples

Create a delay operation and embed it in a Qrisp circuit:

``` python
from iqm.pulse.quantum_ops import QuantumOp
from iqm.pulse.gates.delay import Delay
from iqm.qrisp_iqm import IQMPulseOperation
from qrisp import QuantumCircuit

# Build the delay QuantumOp from the IQM SDK primitives
delay_quantum_op = QuantumOp(
    name="delay",
    arity=1,
    params={"duration": (float,)},
    implementations={"wait": Delay},
    symmetric=True,
)

# Wrap it in a Qrisp-compatible operation with a 100 ns duration
pulse_op = IQMPulseOperation(
    delay_quantum_op,
    param_dict={"duration": 100e-9},
)

# Insert into a Qrisp circuit — the delay survives transpilation
qc = QuantumCircuit(2)
qc.cz(0, 1)
qc.append(pulse_op, [qc.qubits[0]])
```

Methods

|  |  |
|----|----|
| [`bind_parameters`](#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.bind_parameters "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.bind_parameters") | Bind abstract (symbolic) parameters to concrete values. |
| [`get_unitary`](#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.get_unitary "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.get_unitary") | Returns the unitary matrix representation of the operation. |

bind_parameters(*subs_dict: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*) → [Self](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")  
Bind abstract (symbolic) parameters to concrete values.

Extends the base Operation.bind_parameters to also update `param_dict` with the resolved values. Only dynamic (JAX-compatible) parameters are substituted; static parameters are preserved unchanged.

Parameters:  
**subs_dict** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
[*Self*](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")

get_unitary(*decimals: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = -1*) → [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")  
Returns the unitary matrix representation of the operation.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the operation has no defined unitary.

Parameters:  
**decimals** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

Inheritance

![Inheritance diagram of iqm.qrisp_iqm.pulse_operation.IQMPulseOperation](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-3f66d2ff74fdb1e3bc3eec02082511c961a9731b.png)
