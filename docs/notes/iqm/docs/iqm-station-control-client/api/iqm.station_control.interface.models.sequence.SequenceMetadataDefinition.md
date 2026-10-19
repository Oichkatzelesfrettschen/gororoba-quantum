> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataDefinition.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataDefinition.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 27c1e6190315f91f79b7b23790e285804252cffe76e551a1b6472dbaf45819cc.

# SequenceMetadataDefinition

Module: [`iqm.station_control.interface.models.sequence`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.html#module-iqm.station_control.interface.models.sequence "iqm.station_control.interface.models.sequence")

*class* SequenceMetadataDefinition(*\**, *sequence_id*, *origin_id*, *origin_uri*)  
Bases: [`SequenceMetadataBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataBase.html#iqm.station_control.interface.models.sequence.SequenceMetadataBase "iqm.station_control.interface.models.sequence.SequenceMetadataBase")

The content of the sequence metadata object when creating it.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.sequence.SequenceMetadataDefinition.model_config "iqm.station_control.interface.models.sequence.SequenceMetadataDefinition.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `sequence_id` | Unique identifier of the sequence. |
| `origin_id` | Unique identifier of the creator. |
| `origin_uri` | Uniform resource identifier (weak reference) for the creator. |

Methods

Parameters:  
- **sequence_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **origin_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **origin_uri** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'forbid', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sequence.SequenceMetadataDefinition](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-e72c062b8b491ddb993a848f9ce5f41c8a6bd50e.png)
