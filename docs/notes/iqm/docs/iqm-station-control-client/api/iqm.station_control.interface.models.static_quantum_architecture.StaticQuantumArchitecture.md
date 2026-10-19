> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fd117c59eca2705d70ba738af0de424a5589c32e626b83663521f1be151e4974.

# StaticQuantumArchitecture

Module: [`iqm.station_control.interface.models.static_quantum_architecture`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.static_quantum_architecture.html#module-iqm.station_control.interface.models.static_quantum_architecture "iqm.station_control.interface.models.static_quantum_architecture")

*class* StaticQuantumArchitecture(*\**, *dut_label=None*, *qubits*, *computational_resonators*, *connectivity*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

The static quantum architecture (SQA) provides information about the QPU.

For example, the names of its components and the connections between them.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.model_config "iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`dut_label`](#iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.dut_label "iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.dut_label") | Identifies the QPU. |
| [`qubits`](#iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.qubits "iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.qubits") | Names of the qubits on the QPU, sorted. |
| [`computational_resonators`](#iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.computational_resonators "iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.computational_resonators") | Names of the computational resonators on the QPU, sorted. |
| [`connectivity`](#iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.connectivity "iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture.connectivity") | Components (qubits and computational resonators) connected by a coupler on the QPU, sorted. |

Methods

Parameters:  
- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **computational_resonators** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **connectivity** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\]*)

dut_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Identifies the QPU.

qubits*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of the qubits on the QPU, sorted.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

computational_resonators*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Names of the computational resonators on the QPU, sorted.

connectivity*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]\]*  
Components (qubits and computational resonators) connected by a coupler on the QPU, sorted.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.static_quantum_architecture.StaticQuantumArchitecture](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-041b80820e1f7bd3ece42be66dc0a5a0709539e4.png)
