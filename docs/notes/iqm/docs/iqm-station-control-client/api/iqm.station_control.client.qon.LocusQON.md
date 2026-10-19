> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.LocusQON.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.LocusQON.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 eded67ea1a413d62b4a0f8df0ed7f24135b06d6ac5b7c7eac34fbc577acef1c1.

# LocusQON

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* LocusQON(*\**, *locus_str*)  
Bases: [`QON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QON.html#iqm.station_control.client.qon.QON "iqm.station_control.client.qon.QON")

ABC for QONs associated with a locus.

Attributes

|  |  |
|----|----|
| [`locus`](#iqm.station_control.client.qon.LocusQON.locus "iqm.station_control.client.qon.LocusQON.locus") | Locus of the observation. |
| [`locus_str`](#iqm.station_control.client.qon.LocusQON.locus_str "iqm.station_control.client.qon.LocusQON.locus_str") | Sequence of names of QPU components to which the observation applies, encoded into a string. |

Methods

Parameters:  
**locus_str** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

locus_str*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Sequence of names of QPU components to which the observation applies, encoded into a string.

*property* locus*: [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), ...\]*  
Locus of the observation.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.LocusQON](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-a0eb3f8e084ec84ad6099dcad2ee2570f7090f48.png)
