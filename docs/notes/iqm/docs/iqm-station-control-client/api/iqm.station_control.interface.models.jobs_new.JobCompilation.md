> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobCompilation.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.JobCompilation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c39967b3c76092601ee1b2d1d916dcf27d3a0ac9353e2eeec9e4b2ef212dd1c6.

# JobCompilation

Module: [`iqm.station_control.interface.models.jobs_new`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.jobs_new.html#module-iqm.station_control.interface.models.jobs_new "iqm.station_control.interface.models.jobs_new")

*class* JobCompilation(*\**, *calibration_set_id=None*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Progress information about job compilation.

Only circuit-level jobs are compiled on the server side, for pulse-level jobs this struct is empty.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.jobs_new.JobCompilation.model_config "iqm.station_control.interface.models.jobs_new.JobCompilation.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`calibration_set_id`](#iqm.station_control.interface.models.jobs_new.JobCompilation.calibration_set_id "iqm.station_control.interface.models.jobs_new.JobCompilation.calibration_set_id") | ID of the calibration set used by the compiler. |

Methods

Parameters:  
**calibration_set_id** ([*UUID*](https://docs.python.org/3.11/library/uuid.html#uuid.UUID "(in Python v3.11)") *\|* *None*)

calibration_set_id*: UUID \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
ID of the calibration set used by the compiler.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.jobs_new.JobCompilation](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-44eff4e8c23f6f812fa9f4724d3d447221be32ce.png)
