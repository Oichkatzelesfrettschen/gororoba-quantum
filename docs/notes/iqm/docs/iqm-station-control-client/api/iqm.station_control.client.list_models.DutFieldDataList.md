> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.DutFieldDataList.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.DutFieldDataList.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 20117758cc4a28421a95ed8cfa2db288a51662d639416dd6a243782539079f39.

# DutFieldDataList

Module: [`iqm.station_control.client.list_models`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.html#module-iqm.station_control.client.list_models "iqm.station_control.client.list_models")

*class* DutFieldDataList(*root=PydanticUndefined*)  
Bases: [`ListModel`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.ListModel.html#iqm.station_control.client.list_models.ListModel "iqm.station_control.client.list_models.ListModel")

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.client.list_models.DutFieldDataList.model_config "iqm.station_control.client.list_models.DutFieldDataList.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `root` |  |

Methods

Parameters:  
**root** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*DutFieldData*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.dut.DutFieldData.html#iqm.station_control.interface.models.dut.DutFieldData "iqm.station_control.interface.models.dut.DutFieldData")*\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'ser_json_inf_nan': 'constants'}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.client.list_models.DutFieldDataList](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-836912df2595d1aaac25df4a09b26f4df4036269.png)
