> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.CircuitMeasurementCountsList.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.CircuitMeasurementCountsList.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4473d8b0eea8a5fe6ba7651a4aaf15593112a9bf82209e4dcaf5b28e9cab6479.

# CircuitMeasurementCountsList

Module: [`iqm.station_control.client.list_models`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.html#module-iqm.station_control.client.list_models "iqm.station_control.client.list_models")

*class* CircuitMeasurementCountsList(*root=PydanticUndefined*)  
Bases: [`ListModel`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.list_models.ListModel.html#iqm.station_control.client.list_models.ListModel "iqm.station_control.client.list_models.ListModel")

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.client.list_models.CircuitMeasurementCountsList.model_config "iqm.station_control.client.list_models.CircuitMeasurementCountsList.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| `root` |  |

Methods

Parameters:  
**root** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CircuitMeasurementCounts*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.CircuitMeasurementCounts.html#iqm.station_control.interface.models.circuit.CircuitMeasurementCounts "iqm.station_control.interface.models.circuit.CircuitMeasurementCounts")*\]*)

model_config*: ClassVar\[ConfigDict\]* *= {'ser_json_inf_nan': 'constants'}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.client.list_models.CircuitMeasurementCountsList](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-638c1d42593b36894bc7592716be2cf639344a7c.png)
