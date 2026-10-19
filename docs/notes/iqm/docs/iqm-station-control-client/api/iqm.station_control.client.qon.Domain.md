> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b71341fe00dd9a588ad584802c9c03b2346574dbf9f0970f8723fd0371228525.

# Domain

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* Domain(*value*)  
Bases: [`StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum "(in Python v3.11)")

Known observation domains/categories.

Attributes

|  |  |
|----|----|
| [`CONTROLLER_SETTING`](#iqm.station_control.client.qon.Domain.CONTROLLER_SETTING "iqm.station_control.client.qon.Domain.CONTROLLER_SETTING") | Settings for the control instruments. |
| [`GATE_PARAMETER`](#iqm.station_control.client.qon.Domain.GATE_PARAMETER "iqm.station_control.client.qon.Domain.GATE_PARAMETER") | Parameters for quantum operations. |
| [`CHARACTERIZATION`](#iqm.station_control.client.qon.Domain.CHARACTERIZATION "iqm.station_control.client.qon.Domain.CHARACTERIZATION") | Characterization data for the QPU. |
| [`METRIC`](#iqm.station_control.client.qon.Domain.METRIC "iqm.station_control.client.qon.Domain.METRIC") | Quality metrics for quantum operations. |
| [`GATE_DEFINITION`](#iqm.station_control.client.qon.Domain.GATE_DEFINITION "iqm.station_control.client.qon.Domain.GATE_DEFINITION") | Definitions of the quantum operations. |

Methods

CONTROLLER_SETTING *= 'controllers'*  
Settings for the control instruments. Calibration data.

GATE_PARAMETER *= 'gates'*  
Parameters for quantum operations. Calibration data.

CHARACTERIZATION *= 'characterization'*  
Characterization data for the QPU.

METRIC *= 'metrics'*  
Quality metrics for quantum operations.

GATE_DEFINITION *= 'gate_definitions'*  
Definitions of the quantum operations.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.Domain](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-6a4f7b0f15fcd3847e1cf481307816912d541ff3.png)
