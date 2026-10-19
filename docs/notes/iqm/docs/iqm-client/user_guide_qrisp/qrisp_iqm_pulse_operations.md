> Full piece: [https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/qrisp_iqm_pulse_operations.html](https://docs.iqm.tech/4.7/iqm-client/user_guide_qrisp/qrisp_iqm_pulse_operations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e74b46aa646bfde6601dd8d2795711c7ef618508b6f7d20e741a67bbb66f4e04.

# Pulse operations & conversion

Provides a Qrisp frontend for IQM’s IQMClient pulse-level compiler. This module does **not** perform pulse-level compilation itself — it lets you construct pulse-aware Qrisp circuits, extract them as IQM `Circuit` objects, and then hand them to IQMClient for compilation into a pulse-level playlist. For more info on how to modify and build pulse level compilation schedules, please see the [`IQMClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient") documentation.

A typical workflow:

``` python
import os
from qrisp import QuantumVariable, h, cx, measure
from iqm.qrisp_iqm import IQMBackend, extract_iqm_pulse, quantum_op_to_qrisp_func
from iqm.pulse.quantum_ops import QuantumOp

os.environ["IQM_SERVER_URL"] = "https://resonance.iqm.tech/"
os.environ["IQM_QUANTUM_COMPUTER"] = "garnet"
os.environ["IQM_TOKEN"] = "<YOUR_TOKEN>"

backend = IQMBackend()
dqa = backend.iqm_client.get_dynamic_quantum_architecture()

# Define a custom pulse operation (e.g. a delay)
delay = quantum_op_to_qrisp_func(QuantumOp(name="delay", params={"duration": (float,)}))

@extract_iqm_pulse(dqa=dqa)
def my_circuit():
    qv = QuantumVariable(2)
    h(qv[0])
    delay(qv[0], duration=300e-9)   # survives transpilation as a native pulse op
    cx(qv[0], qv[1])
    return measure(qv)

# Extract as IQM pulse Circuit
meas_keys, iqm_pulse_qc = my_circuit()

from iqm.iqm_client import IQMClient
iqm_client = IQMClient()

# Compile to a pulse playlist via IQMClient
compiler = iqm_client.get_standard_compiler()
playlist, context = compiler.compile([iqm_pulse_qc])
```

`extract_iqm_pulse()` traces a Qrisp function via Jasp and converts it to an IQM Pulse `Circuit`. `IQMPulseOperation` lets you embed native pulse instructions (delays, barriers, custom gates) that survive transpilation unchanged.

## Circuit conversion

|  |  |
|----|----|
| [`qrisp_to_iqm_converter`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter.html#iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter "iqm.qrisp_iqm.iqm_converter.qrisp_to_iqm_converter") | Converts a Qrisp QuantumCircuit to an IQM `Circuit`. |

## Pulse operations

|  |  |
|----|----|
| [`IQMPulseOperation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation") | A Qrisp `Operation` subclass that wraps a native IQM pulse [`QuantumOp`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "(in iqm.pulse v15.0.0)"). Survives transpilation unchanged, enabling pulse-level instructions (delays, barriers, custom gates) to be embedded directly in Qrisp circuits. |
| `quantum_op_to_qrisp_func()` | Convenience function that converts an IQM [`QuantumOp`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "(in iqm.pulse v15.0.0)") into a Qrisp-callable gate function (usable like `h`, `cx`, etc.). |
| `extract_iqm_pulse()` | Decorator that traces a Qrisp quantum function via Jasp, transpiles the resulting circuit, and converts it to an IQM `Circuit`. Supports custom `PassManager` pipelines (or `None` to skip transpilation). Returns measurement keys alongside the compiled circuit. |

## Custom pulse operations

|  |  |
|----|----|
| [`delay()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.custom_pulse_operations.delay.html#module-iqm.qrisp_iqm.custom_pulse_operations.delay "iqm.qrisp_iqm.custom_pulse_operations.delay") | A pre-built delay operation that inserts idle time into the circuit. This is a [`IQMPulseOperation`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.pulse_operation.IQMPulseOperation.html#iqm.qrisp_iqm.pulse_operation.IQMPulseOperation "iqm.qrisp_iqm.pulse_operation.IQMPulseOperation") wrapper around IQM’s native delay gate. |
