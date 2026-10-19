> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultBase.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultBase.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 716c7296dc92511ab2b7bac8cf66b57459ac758edbf564e61893a7c2af74e6a5.

# SequenceResultBase

Module: [`iqm.station_control.interface.models.sequence`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.html#module-iqm.station_control.interface.models.sequence "iqm.station_control.interface.models.sequence")

*class* SequenceResultBase(*\**, *sequence_id*, *data*, *final*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Abstract base class of the sequence result definition and data.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.sequence.SequenceResultBase.model_config "iqm.station_control.interface.models.sequence.SequenceResultBase.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`sequence_id`](#iqm.station_control.interface.models.sequence.SequenceResultBase.sequence_id "iqm.station_control.interface.models.sequence.SequenceResultBase.sequence_id") | Unique identifier of the sequence result. |
| [`data`](#iqm.station_control.interface.models.sequence.SequenceResultBase.data "iqm.station_control.interface.models.sequence.SequenceResultBase.data") | JSON serializable dict. |
| [`final`](#iqm.station_control.interface.models.sequence.SequenceResultBase.final "iqm.station_control.interface.models.sequence.SequenceResultBase.final") | Indicates whether this result was marked as final. |

Methods

Parameters:  
- **sequence_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **final** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

sequence_id*: [UUID](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)")*  
Unique identifier of the sequence result.

data*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
JSON serializable dict.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

final*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Indicates whether this result was marked as final.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sequence.SequenceResultBase](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-5e59df5b159e3e9e51f0003a7b6523f39b66d5a8.png)
