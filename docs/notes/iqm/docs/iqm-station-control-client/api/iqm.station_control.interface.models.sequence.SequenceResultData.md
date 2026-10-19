> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9a72b3b390ad959f08bac7eda5ee15630d7e5c59bce7b2112fbf68c8f316f2df.

# SequenceResultData

Module: [`iqm.station_control.interface.models.sequence`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.html#module-iqm.station_control.interface.models.sequence "iqm.station_control.interface.models.sequence")

*class* SequenceResultData(*\**, *sequence_id*, *data*, *final*, *created_timestamp*, *modified_timestamp*)  
Bases: [`SequenceResultBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceResultBase.html#iqm.station_control.interface.models.sequence.SequenceResultBase "iqm.station_control.interface.models.sequence.SequenceResultBase")

The content of the sequence result stored in the database.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.sequence.SequenceResultData.model_config "iqm.station_control.interface.models.sequence.SequenceResultData.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`created_timestamp`](#iqm.station_control.interface.models.sequence.SequenceResultData.created_timestamp "iqm.station_control.interface.models.sequence.SequenceResultData.created_timestamp") | Time when the object was created in the database. |
| [`modified_timestamp`](#iqm.station_control.interface.models.sequence.SequenceResultData.modified_timestamp "iqm.station_control.interface.models.sequence.SequenceResultData.modified_timestamp") | Time when the object was last modified in the database. |
| `sequence_id` | Unique identifier of the sequence result. |
| `data` | JSON serializable dict. |
| `final` | Indicates whether this result was marked as final. |

Methods

Parameters:  
- **sequence_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **final** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **created_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **modified_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)") *\|* *None*)

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

created_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)")*  
Time when the object was created in the database.

modified_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Time when the object was last modified in the database.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sequence.SequenceResultData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-df588d60ff0ae870e9649ccd371735b42402c6a3.png)
