> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataBase.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fc71a4c518dbf66da00ee27ee907eef4ac345c58a58b5eee36a709dac4d40648.

# SequenceMetadataBase

Module: [`iqm.station_control.interface.models.sequence`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.html#module-iqm.station_control.interface.models.sequence "iqm.station_control.interface.models.sequence")

*class* SequenceMetadataBase(*\**, *sequence_id*, *origin_id*, *origin_uri*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Abstract base class of the sequence metadata definition and data.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.sequence.SequenceMetadataBase.model_config "iqm.station_control.interface.models.sequence.SequenceMetadataBase.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`sequence_id`](#iqm.station_control.interface.models.sequence.SequenceMetadataBase.sequence_id "iqm.station_control.interface.models.sequence.SequenceMetadataBase.sequence_id") | Unique identifier of the sequence. |
| [`origin_id`](#iqm.station_control.interface.models.sequence.SequenceMetadataBase.origin_id "iqm.station_control.interface.models.sequence.SequenceMetadataBase.origin_id") | Unique identifier of the creator. |
| [`origin_uri`](#iqm.station_control.interface.models.sequence.SequenceMetadataBase.origin_uri "iqm.station_control.interface.models.sequence.SequenceMetadataBase.origin_uri") | Uniform resource identifier (weak reference) for the creator. |

Methods

Parameters:  
- **sequence_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **origin_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **origin_uri** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

sequence_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*  
Unique identifier of the sequence.

origin_id*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Unique identifier of the creator. E.g. notebook researcher username, or calibration service ID.

origin_uri*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Uniform resource identifier (weak reference) for the creator. E.g. calibration service ID.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sequence.SequenceMetadataBase](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-d487f62f7817a563173b52d38dd937e7e74b15a8.png)
