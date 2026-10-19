> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepDefinitionLite.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.SweepDefinitionLite.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 53365fef5b798c52a2acba4f84fda136777140c5ce0bfc16ae3f66397223274c.

# SweepDefinitionLite

Module: [`iqm.station_control.interface.models.sweep`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sweep.html#module-iqm.station_control.interface.models.sweep "iqm.station_control.interface.models.sweep")

*class* SweepDefinitionLite(*\**, *sweep_id*, *dut_label*, *settings*, *sweeps*, *return_parameters*, *playlist*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Lightweight version of SweepDefinition.

Can be used when the full tree representation of the settings is not needed.

Attributes

|  |  |
|----|----|
| `qpu_runtime` |  |
| [`sweep_id`](#iqm.station_control.interface.models.sweep.SweepDefinitionLite.sweep_id "iqm.station_control.interface.models.sweep.SweepDefinitionLite.sweep_id") | Unique identifier of the sweep. |
| [`dut_label`](#iqm.station_control.interface.models.sweep.SweepDefinitionLite.dut_label "iqm.station_control.interface.models.sweep.SweepDefinitionLite.dut_label") | DUT label of the device being used. |
| [`settings`](#iqm.station_control.interface.models.sweep.SweepDefinitionLite.settings "iqm.station_control.interface.models.sweep.SweepDefinitionLite.settings") | Mapping of setting names to their values for initial settings to set before the sweep. |
| [`sweeps`](#iqm.station_control.interface.models.sweep.SweepDefinitionLite.sweeps "iqm.station_control.interface.models.sweep.SweepDefinitionLite.sweeps") | Sweeps that define the swept parameters, i.e. a list of parallel sweeps, where the data values of all sweeps in the tuple are interleaved, and updated simultaneously during the sweep. |
| [`return_parameters`](#iqm.station_control.interface.models.sweep.SweepDefinitionLite.return_parameters "iqm.station_control.interface.models.sweep.SweepDefinitionLite.return_parameters") | Parameters that will be queried from devices and saved for each spot (variable-tuple) of the N-dimensional sweep. |
| [`playlist`](#iqm.station_control.interface.models.sweep.SweepDefinitionLite.playlist "iqm.station_control.interface.models.sweep.SweepDefinitionLite.playlist") | A `Playlist` that should be uploaded to the controllers. |

Methods

Parameters:  
- **sweep_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **settings** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Annotated\[*[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* *ndarray,* *PlainValidator(func=~exa.common.data.value.validate_value,* *json_schema_input_type=~typing.Any),* *PlainSerializer(func=~exa.common.data.value.serialize_value,* *return_type=PydanticUndefined,* *when_used=always),* *WithJsonSchema(json_schema={},* *mode=None)\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)") *\|* *None\]*)

- **sweeps** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)")*,* *...\]\]*)

- **return_parameters** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **playlist** ([*Playlist*](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)") *\|* *None*)

sweep_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*  
Unique identifier of the sweep.

dut_label*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
DUT label of the device being used.

settings*: dict\[str, ~types.Annotated\[bool \| str \| int \| float \| complex \| ~numpy.ndarray, ~pydantic.functional_validators.PlainValidator(func=~exa.common.data.value.validate_value, json_schema_input_type=~typing.Any), ~pydantic.functional_serializers.PlainSerializer(func=~exa.common.data.value.serialize_value, return_type=PydanticUndefined, when_used=always), ~pydantic.json_schema.WithJsonSchema(json_schema={}, mode=None)\] \| list \| None\]*  
Mapping of setting names to their values for initial settings to set before the sweep. Must only contain non-None, non-readonly controller settings.

sweeps*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[Sweep](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)"), ...\]\]*  
Sweeps that define the swept parameters, i.e. a list of parallel sweeps, where the data values of all sweeps in the tuple are interleaved, and updated simultaneously during the sweep.

return_parameters*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Parameters that will be queried from devices and saved for each spot (variable-tuple) of the N-dimensional sweep. Each item must correspond to a setting name in settings.

playlist*: [Playlist](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.playlist.Playlist.html#iqm.models.playlist.playlist.Playlist "(in IQM data definitions v3.1.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
A `Playlist` that should be uploaded to the controllers.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sweep.SweepDefinitionLite](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-2a472f97c8cf01f56f6d2d4df4dcd56dac369460.png)
