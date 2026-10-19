> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONOther.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONOther.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 aa2f6dbf73df891c36573c452aa4233f9e13287bdbf967e154e54559b57e139f.

# QONOther

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONOther(*rest*)  
Bases: [`QON`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QON.html#iqm.station_control.client.qon.QON "iqm.station_control.client.qon.QON")

QON representing arbitrary user-defined observations.

Has the form `characterization.other.*`.

Attributes

|  |  |
|----|----|
| [`domain`](#iqm.station_control.client.qon.QONOther.domain "iqm.station_control.client.qon.QONOther.domain") | Type/purpose of the observation. |
| [`rest`](#iqm.station_control.client.qon.QONOther.rest "iqm.station_control.client.qon.QONOther.rest") | User-defined observation name part, can contain further dots. |

Methods

Parameters:  
**rest** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

rest*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
User-defined observation name part, can contain further dots.

*property* domain*: [Domain](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.Domain.html#iqm.station_control.client.qon.Domain "iqm.station_control.client.qon.Domain")*  
Type/purpose of the observation.

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONOther](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-8ac7e7d4726942d84d34e12e7c4b8a713f7e3823.png)
