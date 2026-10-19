> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1333dc61965663a24df24572169951d07252a8a96b58e4e09f3d20011fdb7d22.

# CircuitMeasurementCounts

Module: [`iqm.station_control.interface.models.circuit`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.html#module-iqm.station_control.interface.models.circuit "iqm.station_control.interface.models.circuit")

*class* CircuitMeasurementCounts(*\**, *measurement_keys*, *counts*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Circuit measurement counts in histogram representation.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.model_config "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`measurement_keys`](#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.measurement_keys "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.measurement_keys") | Measurement keys in the order they are concatenated to form the state bitstrings in [`counts`](#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.counts "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.counts"). |
| [`counts`](#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.counts "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.counts") | Mapping from computational basis states, represented as bitstrings, to the number of times they were observed when executing the circuit. |

Methods

Parameters:  
- **measurement_keys** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

measurement_keys*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Measurement keys in the order they are concatenated to form the state bitstrings in [`counts`](#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.counts "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.counts").

For example, if [`measurement_keys`](#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.measurement_keys "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.measurement_keys") is `['mk_1', 'mk2']` and `'mk_1'` measures `QB1` and `'mk_2'` measures `QB3` and `QB5`, then [`counts`](#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.counts "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.counts") could contains keys such as `'010'` representing shots where ``` QB1`, ``QB3 ``` and `QB5` were observed to be in the state \\\|010 angle\\.

counts*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Mapping from computational basis states, represented as bitstrings, to the number of times they were observed when executing the circuit.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.circuit.CircuitMeasurementCounts](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-9dd68a09921b8c7a9ad0d44a031e4d50f25b0349.png)
