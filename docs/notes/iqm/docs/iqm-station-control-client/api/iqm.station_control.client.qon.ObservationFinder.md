> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.ObservationFinder.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.ObservationFinder.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a21216082fa7c167c84d7966adf57ee119248dad297d06e1111ccc387d9f3f91.

# ObservationFinder

Module: [`iqm.station_control.client.qon`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.client.qon.html#module-iqm.station_control.client.qon "iqm.station_control.client.qon")

*class* ObservationFinder(*observations*, *skip_unparseable=False*)  
Bases: [`dict`](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")

Query structure for a set of observations.

This class enables reasonably efficient filtering of an observation set based on the observation name elements (e.g. find all T1 times / parameters of a particular gate/impl/locus etc. in the set).

The class has utility methods for querying specific types observations. The idea is to keep all the logic related to the structure of the observation names encapsulated in this class/module.

Currently implemented using a nested dictionary that follows the dotted structure of the observation names. The nested dictionary is not ideal for all searches/filterings, but it’s just an implementation detail that can be improved later on without affecting the public API of this class.

Parameters:  
- **observations** (*Iterable\[*[*ObservationBase*](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.observation.ObservationBase.html#iqm.station_control.interface.models.observation.ObservationBase "iqm.station_control.interface.models.observation.ObservationBase")*\]*) – Observations to include in the query structure.

- **skip_unparseable** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, ignore any observation whose name cannot be parsed, otherwise raise an exception.

Methods

|  |  |
|----|----|
| [`get_coherence_times`](#iqm.station_control.client.qon.ObservationFinder.get_coherence_times "iqm.station_control.client.qon.ObservationFinder.get_coherence_times") | T1 and T2 coherence times for the given QPU components. |
| [`get_gate_duration`](#iqm.station_control.client.qon.ObservationFinder.get_gate_duration "iqm.station_control.client.qon.ObservationFinder.get_gate_duration") | Duration for the given gate/implementation/locus (in s), or None if not found. |
| [`get_gate_fidelity`](#iqm.station_control.client.qon.ObservationFinder.get_gate_fidelity "iqm.station_control.client.qon.ObservationFinder.get_gate_fidelity") | Fidelity of the given gate/implementation/locus, or None if not found. |
| [`get_measure_errors`](#iqm.station_control.client.qon.ObservationFinder.get_measure_errors "iqm.station_control.client.qon.ObservationFinder.get_measure_errors") | Measurement errors of the given gate/implementation/locus, or None if not found. |
| [`get_measure_repeatability`](#iqm.station_control.client.qon.ObservationFinder.get_measure_repeatability "iqm.station_control.client.qon.ObservationFinder.get_measure_repeatability") | Repeatability of the measurement and given implementation/locus, or None if not found. |
| [`get_qubit_frequency`](#iqm.station_control.client.qon.ObservationFinder.get_qubit_frequency "iqm.station_control.client.qon.ObservationFinder.get_qubit_frequency") | Qubit drive frequency, or None if not found. |

get_coherence_times(*components*)  
T1 and T2 coherence times for the given QPU components.

If not found, the component will not appear in the corresponding dict.

Parameters:  
**components** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\], [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]

get_gate_duration(*gate_name*, *impl_name*, *locus*)  
Duration for the given gate/implementation/locus (in s), or None if not found.

Parameters:  
- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| *None*

get_gate_fidelity(*gate_name*, *impl_name*, *locus*)  
Fidelity of the given gate/implementation/locus, or None if not found.

Parameters:  
- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| *None*

get_measure_errors(*gate_name*, *impl_name*, *locus*)  
Measurement errors of the given gate/implementation/locus, or None if not found.

Parameters:  
- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

Return type:  
[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"), [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\] \| *None*

get_measure_repeatability(*gate_name*, *impl_name*, *locus*)  
Repeatability of the measurement and given implementation/locus, or None if not found.

Parameters:  
- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*)

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| *None*

get_qubit_frequency(*qubit*)  
Qubit drive frequency, or None if not found.

Parameters:  
**qubit** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

Return type:  
[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| *None*

Inheritance

![Inheritance diagram of iqm.station_control.client.qon.ObservationFinder](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-f52126305c380a78cc1373bfd7467fa8ab2d3b6c.png)
