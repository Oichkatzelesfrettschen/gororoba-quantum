> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultDefinition.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultDefinition.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e00594df8f00ecf8c5c49c1c38037b9802541c2a7abad6c48a2c18c04f1bb21f.

# SequenceResultDefinition

Module: [`iqm.station_control.interface.models.sequence`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.html#module-iqm.station_control.interface.models.sequence "iqm.station_control.interface.models.sequence")

*class* SequenceResultDefinition(*\**, *sequence_id*, *data*, *final*)  
Bases: [`SequenceResultBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultBase.html#iqm.station_control.interface.models.sequence.SequenceResultBase "iqm.station_control.interface.models.sequence.SequenceResultBase")

The content of the sequence result object when creating it.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.sequence.SequenceResultDefinition.model_config "iqm.station_control.interface.models.sequence.SequenceResultDefinition.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `sequence_id` | Unique identifier of the sequence result. |
| `data` | JSON serializable dict. |
| `final` | Indicates whether this result was marked as final. |

Methods

Parameters:  
- **sequence_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **final** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'forbid', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sequence.SequenceResultDefinition](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-cebf58aca70913c66dbd1a055d57d6e77feb0bee.png)
