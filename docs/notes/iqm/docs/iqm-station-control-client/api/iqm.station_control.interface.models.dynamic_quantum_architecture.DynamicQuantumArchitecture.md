> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 647aa71d63849055cbee8f46b04a05fe1968d33c2c4452b255864eb51e195757.

# DynamicQuantumArchitecture

Module: [`iqm.station_control.interface.models.dynamic_quantum_architecture`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.html#module-iqm.station_control.interface.models.dynamic_quantum_architecture "iqm.station_control.interface.models.dynamic_quantum_architecture")

*class* DynamicQuantumArchitecture(*\**, *calibration_set_id*, *qubits*, *computational_resonators*, *gates*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

The dynamic quantum architecture (DQA).

Describes gates/operations for which calibration data exists in the calibration set.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`components`](#iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.components "iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.components") | All locus components (qubits and computational resonators) sorted. |
| [`model_config`](#iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.model_config "iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`calibration_set_id`](#iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.calibration_set_id "iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.calibration_set_id") | ID of the calibration set from which this DQA was generated. |
| [`qubits`](#iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.qubits "iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.qubits") | Qubits that appear in at least one gate locus in the calibration set. |
| [`computational_resonators`](#iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.computational_resonators "iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.computational_resonators") | Computational resonators that appear in at least one gate locus in the calibration set. |
| [`gates`](#iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.gates "iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture.gates") | Mapping of gate names to information about the gates. |

Methods

Parameters:  
- **calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **computational_resonators** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **gates** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*GateInfo*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.html#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo")*\]*)

calibration_set_id*: UUID*  
ID of the calibration set from which this DQA was generated.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

qubits*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Qubits that appear in at least one gate locus in the calibration set.

computational_resonators*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Computational resonators that appear in at least one gate locus in the calibration set.

gates*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [GateInfo](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo.html#iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo "iqm.station_control.interface.models.dynamic_quantum_architecture.GateInfo")\]*  
Mapping of gate names to information about the gates.

*property* components*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]*  
All locus components (qubits and computational resonators) sorted.

The components are first sorted alphabetically based on their non-numeric part, and then components with the same non-numeric part are sorted numerically. An example of components sorted this way would be: (‘COMPR1’, ‘COMPR2’, ‘QB1’, ‘QB2’, ‘QB3’, ‘QB10’, ‘QB11’, ‘QB20’).

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.dynamic_quantum_architecture.DynamicQuantumArchitecture](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-56704df1ecd0990b457bd35e94ab92e052b1983c.png)
