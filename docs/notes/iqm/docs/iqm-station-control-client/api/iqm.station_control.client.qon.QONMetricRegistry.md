> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONMetricRegistry.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONMetricRegistry.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 46127fff637f96af5f1460110969c098939156d712823180a19b94656ecd24ee.

# QONMetricRegistry

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* QONMetricRegistry  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Registry for QONMetric subclasses, mapping method names to parser classes.

Allows extensible registration of new metric parsing strategies for new methods.

Methods

|  |  |
|----|----|
| [`get_parser`](#iqm.station_control.client.qon.QONMetricRegistry.get_parser "iqm.station_control.client.qon.QONMetricRegistry.get_parser") | Retrieve the parser class for a given method name. |
| [`register`](#iqm.station_control.client.qon.QONMetricRegistry.register "iqm.station_control.client.qon.QONMetricRegistry.register") | Decorator for registering a QONMetric subclass as the parser for one or more method names. |
| [`registered_methods`](#iqm.station_control.client.qon.QONMetricRegistry.registered_methods "iqm.station_control.client.qon.QONMetricRegistry.registered_methods") | Get a list of all registered method names. |

*classmethod* register(*method_names*)  
Decorator for registering a QONMetric subclass as the parser for one or more method names.

Parameters:  
**method_names** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – One or more method names to associate with the subclass.

Returns:  
The decorator function.

*classmethod* get_parser(*method_name*)  
Retrieve the parser class for a given method name.

Parameters:  
**method_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The method name to look up.

Returns:  
The QONMetric subclass registered for the method.

Raises:  
**UnknownObservationError** – `method_name` is not registered.

Return type:  
[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[*QONMetric*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.QONMetric.html#iqm.station_control.client.qon.QONMetric "iqm.station_control.client.qon.QONMetric")\]

*classmethod* registered_methods()  
Get a list of all registered method names.

Returns:  
List of registered method names.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.QONMetricRegistry](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-303e4a9e648cfed657364d3f7c1447a9b0abad12.png)
