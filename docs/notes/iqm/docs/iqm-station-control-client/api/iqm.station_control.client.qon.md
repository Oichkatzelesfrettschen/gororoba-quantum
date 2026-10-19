> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6134048d9955402bc2c05fa3d80b4cedd5c562e11f2f411755b7c438c6efd06f.

# qon

Full path: iqm.station_control.client.qon

Qualified observation name parsing and creation.

Module Attributes

|  |  |
|----|----|
| [`LOCUS_SEPARATOR`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.LOCUS_SEPARATOR.html#iqm.station_control.client.qon.LOCUS_SEPARATOR "iqm.station_control.client.qon.LOCUS_SEPARATOR") | Separates QPU components in a locus string. |
| [`Locus`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Locus.html#iqm.station_control.client.qon.Locus "iqm.station_control.client.qon.Locus") | Sequence of QPU component physical names a quantum operation acts on. |
| [`Suffixes`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Suffixes.html#iqm.station_control.client.qon.Suffixes "iqm.station_control.client.qon.Suffixes") | Suffixes in a dut_field, split into key/value pairs. |
| [`GATE_FIDELITY_METHODS`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.GATE_FIDELITY_METHODS.html#iqm.station_control.client.qon.GATE_FIDELITY_METHODS "iqm.station_control.client.qon.GATE_FIDELITY_METHODS") | Mapping from quantum operation name to the standard methods for obtaining its fidelity. |

Functions

|  |  |
|----|----|
| [`locus_str_to_locus`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.locus_str_to_locus.html#iqm.station_control.client.qon.locus_str_to_locus "iqm.station_control.client.qon.locus_str_to_locus")(locus_str) | Convert a locus string into a locus. |
| [`locus_to_locus_str`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.locus_to_locus_str.html#iqm.station_control.client.qon.locus_to_locus_str "iqm.station_control.client.qon.locus_to_locus_str")(locus) | Convert a locus into a locus string. |

Classes

|  |  |
|----|----|
| [`Domain`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html#iqm.station_control.client.qon.Domain "iqm.station_control.client.qon.Domain") | Known observation domains/categories. |
| [`LocusQON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.LocusQON.html#iqm.station_control.client.qon.LocusQON "iqm.station_control.client.qon.LocusQON") | ABC for QONs associated with a locus. |
| [`ObservationFinder`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.ObservationFinder.html#iqm.station_control.client.qon.ObservationFinder "iqm.station_control.client.qon.ObservationFinder") | Query structure for a set of observations. |
| [`QON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QON.html#iqm.station_control.client.qon.QON "iqm.station_control.client.qon.QON") | ABC for qualified observation names. |
| [`QONCharacterization`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONCharacterization.html#iqm.station_control.client.qon.QONCharacterization "iqm.station_control.client.qon.QONCharacterization") | QON representing a QPU property. |
| [`QONControllerSetting`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONControllerSetting.html#iqm.station_control.client.qon.QONControllerSetting "iqm.station_control.client.qon.QONControllerSetting") | QON representing a controller setting observation. |
| [`QONGateCharacterization`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateCharacterization.html#iqm.station_control.client.qon.QONGateCharacterization "iqm.station_control.client.qon.QONGateCharacterization") | QON representing an auxiliary gate property, used e.g. during calibration or preprocessing. |
| [`QONGateDefinition`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateDefinition.html#iqm.station_control.client.qon.QONGateDefinition "iqm.station_control.client.qon.QONGateDefinition") | QON representing a part of a quantum operation definition. |
| [`QONGateMetric`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateMetric.html#iqm.station_control.client.qon.QONGateMetric "iqm.station_control.client.qon.QONGateMetric") | QON representing a gate quality metric. |
| [`QONGateParam`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONGateParam.html#iqm.station_control.client.qon.QONGateParam "iqm.station_control.client.qon.QONGateParam") | QON representing a gate parameter observation. |
| [`QONMetric`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONMetric.html#iqm.station_control.client.qon.QONMetric "iqm.station_control.client.qon.QONMetric") | Base class for QON representing a gate or system quality metric. |
| [`QONMetricRegistry`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONMetricRegistry.html#iqm.station_control.client.qon.QONMetricRegistry "iqm.station_control.client.qon.QONMetricRegistry") | Registry for QONMetric subclasses, mapping method names to parser classes. |
| [`QONOther`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONOther.html#iqm.station_control.client.qon.QONOther "iqm.station_control.client.qon.QONOther") | QON representing arbitrary user-defined observations. |
| [`QONSystemMetric`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONSystemMetric.html#iqm.station_control.client.qon.QONSystemMetric "iqm.station_control.client.qon.QONSystemMetric") | QON representing a system quality metric. |

Inheritance

![Inheritance diagram of iqm.station_control.client.qon](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-a263a9980c1f619434f7d5311ddf66527813b16c.png)
