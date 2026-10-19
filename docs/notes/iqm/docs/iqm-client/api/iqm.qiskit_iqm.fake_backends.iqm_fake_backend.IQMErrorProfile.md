> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1f1775ec286707737ca2328a120195b39fe424b0c4a18bff4a303bc1649450ea.

# IQMErrorProfile

Module: [`iqm.qiskit_iqm.fake_backends.iqm_fake_backend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.html#module-iqm.qiskit_iqm.fake_backends.iqm_fake_backend "iqm.qiskit_iqm.fake_backends.iqm_fake_backend")

*class* iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile(*t1s: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *t2s: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *single_qubit_gate_depolarizing_error_parameters: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*, *two_qubit_gate_depolarizing_error_parameters: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\], [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*, *single_qubit_gate_durations: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *two_qubit_gate_durations: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*, *readout_errors: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*, *name: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Characteristics of an IQM QPU specimen, used for constructing an error model.

All the attributes of this class refer to the components of the QPU using their physical names. There are two types of QPU components, qubits and computational resonators.

Parameters:  
- **t1s** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – maps components to their \\T_1\\ times (in ns)

- **t2s** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – maps components to their \\T_2\\ times (in ns)

- **single_qubit_gate_depolarizing_error_parameters** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – Depolarizing error parameters for single-qubit gates. Maps single-qubit gate names to a mapping of qubits (on which the gate acts) to a depolarizing error. The error, used in a one-qubit depolarizing channel, concatenated with a thermal relaxation channel, leads to average gate fidelities that would be determined by benchmarking.

- **two_qubit_gate_depolarizing_error_parameters** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\],* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – Depolarizing error parameters for two-qubit gates. Maps two-qubit gate names to a mapping of pairs of qubits (on which the gate acts) to a depolarizing error. The error, used in a two-qubit depolarizing channel, concatenated with thermal relaxation channels for the qubits, leads to average gate fidelities that would be determined by benchmarking.

- **single_qubit_gate_durations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – Gate duration (in ns) for each single-qubit gate

- **two_qubit_gate_durations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – Gate duration (in ns) for each two-qubit gate.

- **readout_errors** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*) – Maps physical qubit names to dicts that describe their single-qubit readout errors. For each qubit, the inner dict maps the state labels “0” and “1” to the probability \\P(\neg x\|x)\\ of observing the state \\\ket{\neg x}\\ given the true state is \\\ket{x}\\.

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Identifier of the QPU specimen.

Example

```
IQMErrorProfile(
    t1s={"QB1": 10000.0, "QB2": 12000.0, "QB3": 14000.0},
    t2s={"QB1": 10000.0, "QB2": 12000.0, "QB3": 13000.0},
    single_qubit_gate_depolarizing_error_parameters={"prx": {"QB1": 0.0005, "QB2": 0.0004, "QB3": 0.0010}},
    two_qubit_gate_depolarizing_error_parameters={"cz": {("QB1", "QB2"): 0.08, ("QB2", "QB3"): 0.03}},
    single_qubit_gate_durations={"prx": 50.},
    two_qubit_gate_durations={"cz": 100.},
    readout_errors={"QB1": {"0": 0.02, "1": 0.03},
                    "QB2": {"0": 0.02, "1": 0.03},
                    "QB3": {"0": 0.02, "1": 0.03}},
    name="threequbit-example_sample"
)
```

Attributes

|                                                   |     |
|---------------------------------------------------|-----|
| `name`                                            |     |
| `t1s`                                             |     |
| `t2s`                                             |     |
| `single_qubit_gate_depolarizing_error_parameters` |     |
| `two_qubit_gate_depolarizing_error_parameters`    |     |
| `single_qubit_gate_durations`                     |     |
| `two_qubit_gate_durations`                        |     |
| `readout_errors`                                  |     |

Methods

|  |  |
|----|----|
| [`thermal_relaxation`](#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile.thermal_relaxation "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile.thermal_relaxation") | One-qubit relaxation error channel. |

thermal_relaxation(*component: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*, *duration: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*) → QuantumError  
One-qubit relaxation error channel.

Parameters:  
- **component** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **duration** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

Return type:  
*QuantumError*

Inheritance

![Inheritance diagram of iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMErrorProfile](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-06bc0573c1cd21219688e666da3be47193abb157.png)
