> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.extract_iqm_pulse_decorator.extract_iqm_pulse.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.extract_iqm_pulse_decorator.extract_iqm_pulse.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7e89f24f54d90939f5f6039288957df0026107d4e12a2e3c42ca155ca7b23525.

# iqm.qrisp_iqm.extract_iqm_pulse_decorator.extract_iqm_pulse

iqm.qrisp_iqm.extract_iqm_pulse_decorator.extract_iqm_pulse(*dqa: DynamicQuantumArchitecture*, *pass_manager: PassManager \| [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = 'default'*) → Callable\[\[Callable\], Callable\[..., Circuit \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[Any, ...\]\]\]  
Jasp-trace a Qrisp function and compile it to `Circuit`.

This is the primary entry point for taking a Qrisp quantum function and turning it into an IQM-native circuit without manual transpilation. The decorator:

1.  Traces the function with `make_jaspr()` to capture all quantum operations (including [`IQMPulseOperation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation") instances).

2.  Converts the Jasp representation into a Qrisp `QuantumCircuit`.

3.  Optionally applies transpilation passes via a `PassManager` (by default, a `convert_to_cz` pass is applied).

4.  Converts the transpiled circuit to an `Circuit` using [`qrisp_to_iqm_converter()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter.html#iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter "iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter").

Parameters:  
- **dqa** (*DynamicQuantumArchitecture*) – Determines the physical qubit names and available gate loci.

- **pass_manager** (*PassManager* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) –

  Transpilation strategy for the circuit before IQM conversion:

  - `"default"` — a `PassManager` containing only `convert_to_cz()`.

  - `None` — no transpilation; the circuit is converted as-is (useful when it contains only `IQMPulseOperation` gates).

  - A custom `PassManager` — full user control over layout, routing, and gate decomposition.

Returns:  
A decorator that, when applied to a function, returns a wrapper whose return type is `Circuit`, or `tuple[..., Circuit]` when the original function returns values.

If the decorated function has **no return value** (only builds a circuit as a side effect), the wrapper returns the corresponding IQM Circuit directly.

If the function **returns measurement results** (e.g., a `QuantumVariable` or a list of `Clbit`), the wrapper returns a tuple `(*processed_returns, iqm_circuit)` where classical bits are replaced by their IQM readout key strings (`"cb_0"`, `"cb_1"`, …).

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If *pass_manager* is a string other than `"default"`.

Return type:  
Callable\[\[Callable\], Callable\[…, Circuit \| [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[Any, …\]\]\]

Examples

First, obtain the device DQA via the IQM Backend:

``` python
from iqm.qrisp_iqm import IQMBackend

backend = IQMBackend(
    device_instance="garnet",
    token="YOUR_API_TOKEN",
)
dqa = backend.iqm_client.get_dynamic_quantum_architecture()
```

**Circuit without return values** (implicit circuit capture):

``` python
from qrisp import QuantumVariable, h, cx, measure
from iqm.qrisp_iqm import extract_iqm_pulse

@extract_iqm_pulse(dqa=dqa)
def bell_circuit():
    qv = QuantumVariable(2)
    h(qv[0])
    cx(qv[0], qv[1])
    measure(qv)

iqm_circuit = bell_circuit()          # → iqm.pulse.Circuit
print(iqm_circuit)
```

**Circuit returning a measurement result**:

``` python
from qrisp import QuantumFloat, h, measure

@extract_iqm_pulse(dqa=dqa)
def random_float():
    qf = QuantumFloat(3)
    h(qf)
    res = measure(qf)
    return res

random_bits, iqm_circuit = random_float()
print(random_bits)                    # → ("cb_0", "cb_1", "cb_2")
print(iqm_circuit)
```

**Pulse-only circuit (no transpilation needed)**:

``` python
from iqm.qrisp_iqm import delay

@extract_iqm_pulse(dqa=dqa, pass_manager=None)
def pulse_delay():
    qv = QuantumVariable(1)
    delay(qv, duration=100e-9)

iqm_circuit = pulse_delay()
# iqm_circuit.instructions contains a single delay operation
print(iqm_circuit.instructions[0].name)  # → "delay"
```
