> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetType.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.ObservationSetType.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9aa34ad765059c9ec42df5805120fd59acabaac990462895ea7035d510f0848b.

# ObservationSetType

Module: [`iqm.station_control.interface.models.observation_set`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation_set.html#module-iqm.station_control.interface.models.observation_set "iqm.station_control.interface.models.observation_set")

*class* ObservationSetType(*value*)  
Bases: [`StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum "(in Python v3.11)")

Different types of observation sets.

Attributes

|  |  |
|----|----|
| [`GENERIC_SET`](#iqm.station_control.interface.models.observation_set.ObservationSetType.GENERIC_SET "iqm.station_control.interface.models.observation_set.ObservationSetType.GENERIC_SET") | For human users. |
| [`CALIBRATION_SET`](#iqm.station_control.interface.models.observation_set.ObservationSetType.CALIBRATION_SET "iqm.station_control.interface.models.observation_set.ObservationSetType.CALIBRATION_SET") | Describes an operating point of a quantum computer. |
| [`QUALITY_METRIC_SET`](#iqm.station_control.interface.models.observation_set.ObservationSetType.QUALITY_METRIC_SET "iqm.station_control.interface.models.observation_set.ObservationSetType.QUALITY_METRIC_SET") | Describes the quality of a calibration set at a certain point in time. |
| [`CHARACTERIZATION_SET`](#iqm.station_control.interface.models.observation_set.ObservationSetType.CHARACTERIZATION_SET "iqm.station_control.interface.models.observation_set.ObservationSetType.CHARACTERIZATION_SET") | Starting point for a calibration procedure. |

Methods

GENERIC_SET *= 'generic-set'*  
For human users.

CALIBRATION_SET *= 'calibration-set'*  
Describes an operating point of a quantum computer.

QUALITY_METRIC_SET *= 'quality-metric-set'*  
Describes the quality of a calibration set at a certain point in time.

CHARACTERIZATION_SET *= 'characterization-set'*  
Starting point for a calibration procedure.

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.observation_set.ObservationSetType](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-669538690e134ab5ddf1d14729cc1311760faef5.png)
