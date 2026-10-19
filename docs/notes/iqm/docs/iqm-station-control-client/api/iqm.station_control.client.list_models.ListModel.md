> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.ListModel.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.ListModel.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 45013d5d2d382783b2b2a0486a475a785d174a43f507faa593c397a875c1e938.

# ListModel

Module: [`iqm.station_control.client.list_models`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.html#module-iqm.station_control.client.list_models "iqm.station_control.client.list_models")

*class* ListModel(*root=PydanticUndefined*)  
Bases: `RootModel`

A Pydantic BaseModel for a container model of a list of objects.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.client.list_models.ListModel.model_config "iqm.station_control.client.list_models.ListModel.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `root` |  |

Methods

Parameters:  
**root** (*RootModelRootType*)

model_config*: ClassVar\[ConfigDict\]* *= {'ser_json_inf_nan': 'constants'}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.client.list_models.ListModel](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-8eb0e9622e1880561c9efeea14adaf547ea4ac98.png)
