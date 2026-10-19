> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataData.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5a963fc9bded4db8cc6f00fc41fd95c909180b132c7ca664fc94fad8dfb40eb4.

# SequenceMetadataData

Module: [`iqm.station_control.interface.models.sequence`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.html#module-iqm.station_control.interface.models.sequence "iqm.station_control.interface.models.sequence")

*class* SequenceMetadataData(*\**, *sequence_id*, *origin_id*, *origin_uri*, *created_timestamp*)  
Bases: [`SequenceMetadataBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.sequence.SequenceMetadataBase.html#iqm.station_control.interface.models.sequence.SequenceMetadataBase "iqm.station_control.interface.models.sequence.SequenceMetadataBase")

The content of the sequence metadata stored in the database.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.sequence.SequenceMetadataData.model_config "iqm.station_control.interface.models.sequence.SequenceMetadataData.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`created_timestamp`](#iqm.station_control.interface.models.sequence.SequenceMetadataData.created_timestamp "iqm.station_control.interface.models.sequence.SequenceMetadataData.created_timestamp") | Time when the object was created in the database. |
| `sequence_id` | Unique identifier of the sequence. |
| `origin_id` | Unique identifier of the creator. |
| `origin_uri` | Uniform resource identifier (weak reference) for the creator. |

Methods

Parameters:  
- **sequence_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)"))

- **origin_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **origin_uri** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **created_timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

created_timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)")*  
Time when the object was created in the database.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.sequence.SequenceMetadataData](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-ad590a43f5a8aeabf001ae9834572ed896783e2f.png)
