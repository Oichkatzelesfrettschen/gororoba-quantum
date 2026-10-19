> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMMetadata.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMMetadata.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 44251194a88d39381ab94f8b36f24c09eacd1fdd240d52cc0d18173e229fe6db.

# iqm.error_reduction_tools.rem.rem_api.REMMetadata

*class* iqm.error_reduction_tools.rem.rem_api.REMMetadata(*timestamp*, *shots*, *twirling_strategy*, *characterization_reused*, *characterization_job_id*, *twirling_job_id*, *rec_config*, *twirling_config*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Metadata about a completed REM workflow run.

Attributes

|  |  |
|----|----|
| [`timestamp`](#iqm.error_reduction_tools.rem.rem_api.REMMetadata.timestamp "iqm.error_reduction_tools.rem.rem_api.REMMetadata.timestamp") | ISO-8601 timestamp when results were retrieved, in UTC. |
| [`shots`](#iqm.error_reduction_tools.rem.rem_api.REMMetadata.shots "iqm.error_reduction_tools.rem.rem_api.REMMetadata.shots") | Total shots used for circuit execution. |
| [`twirling_strategy`](#iqm.error_reduction_tools.rem.rem_api.REMMetadata.twirling_strategy "iqm.error_reduction_tools.rem.rem_api.REMMetadata.twirling_strategy") | Twirling strategy name used. |
| [`characterization_reused`](#iqm.error_reduction_tools.rem.rem_api.REMMetadata.characterization_reused "iqm.error_reduction_tools.rem.rem_api.REMMetadata.characterization_reused") | `True` if the user provided pre-existing characterization. |
| [`characterization_job_id`](#iqm.error_reduction_tools.rem.rem_api.REMMetadata.characterization_job_id "iqm.error_reduction_tools.rem.rem_api.REMMetadata.characterization_job_id") | Id of the readout error characterization job, or `None` when a pre-existing characterization was reused (no job was submitted). |
| [`twirling_job_id`](#iqm.error_reduction_tools.rem.rem_api.REMMetadata.twirling_job_id "iqm.error_reduction_tools.rem.rem_api.REMMetadata.twirling_job_id") | Id of the twirled-circuit job submitted to the quantum computer. |
| [`rec_config`](#iqm.error_reduction_tools.rem.rem_api.REMMetadata.rec_config "iqm.error_reduction_tools.rem.rem_api.REMMetadata.rec_config") | Configuration used for readout error characterization. |
| [`twirling_config`](#iqm.error_reduction_tools.rem.rem_api.REMMetadata.twirling_config "iqm.error_reduction_tools.rem.rem_api.REMMetadata.twirling_config") | Configuration used for circuit twirling. |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |

Parameters:  
- **timestamp** ([*datetime*](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)"))

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **twirling_strategy** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **characterization_reused** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **characterization_job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **twirling_job_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

- **rec_config** ([*RECConfiguration*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration"))

- **twirling_config** ([*TwirlingConfiguration*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.html#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration"))

timestamp*: [datetime](https://docs.python.org/3.11/library/datetime.html#datetime.datetime "(in Python v3.11)")*  
ISO-8601 timestamp when results were retrieved, in UTC.

shots*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Total shots used for circuit execution.

twirling_strategy*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Twirling strategy name used.

characterization_reused*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
`True` if the user provided pre-existing characterization.

characterization_job_id*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Id of the readout error characterization job, or `None` when a pre-existing characterization was reused (no job was submitted).

twirling_job_id*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Id of the twirled-circuit job submitted to the quantum computer.

rec_config*: [RECConfiguration](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration")*  
Configuration used for readout error characterization.

twirling_config*: [TwirlingConfiguration](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.html#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration")*  
Configuration used for circuit twirling.
