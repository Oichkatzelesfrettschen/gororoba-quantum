> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.DutList.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.DutList.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 814207d088a748e02e25f17806f01713c079a4d5423dbebdea637a4eb209777f.

# DutList

Module: [`iqm.station_control.client.list_models`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.html#module-iqm.station_control.client.list_models "iqm.station_control.client.list_models")

*class* DutList(*root=PydanticUndefined*)  
Bases: [`ListModel`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.ListModel.html#iqm.station_control.client.list_models.ListModel "iqm.station_control.client.list_models.ListModel")

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.client.list_models.DutList.model_config "iqm.station_control.client.list_models.DutList.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `root` |  |

Methods

Parameters:  
**root** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*DutData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dut.DutData.html#iqm.station_control.interface.models.dut.DutData "iqm.station_control.interface.models.dut.DutData")*\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'ser_json_inf_nan': 'constants'}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.client.list_models.DutList](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-f1294c2bb05867b6fe7604d6808d2edc5eb41a2b.png)
