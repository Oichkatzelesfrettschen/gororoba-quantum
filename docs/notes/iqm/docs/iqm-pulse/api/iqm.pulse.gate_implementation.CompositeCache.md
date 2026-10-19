> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeCache.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.CompositeCache.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c7fb31c43f9b282a2e50f475658c294493d84223a2c7a30d2bea57f8c241fb3f.

# CompositeCache

Module: [`iqm.pulse.gate_implementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.html#module-iqm.pulse.gate_implementation "iqm.pulse.gate_implementation")

*class* iqm.pulse.gate_implementation.CompositeCache  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Cache for CompositeGate TimeBoxes.

Result from `` CompositeGate.__call__`() `` (or other methods returning a TimeBox) cannot be stored in the normal cache `GateImplementation._timebox_cache` as composites can include any gates in their calls, and we cannot trust that the cache is flushed correctly just based on if the composite itself has its own calibration data changed (we would have to flush also when any of the composite’s members get new calibration, and this cannot consistently be deduced). For this reason, the CompositeCache is located in the ScheduleBuilder class, and will be flushed whenever *any* gate implementation gets new calibration data.

Methods

|  |  |
|----|----|
| [`flush`](#iqm.pulse.gate_implementation.CompositeCache.flush "iqm.pulse.gate_implementation.CompositeCache.flush") | Flush the CompositeCache. |
| [`get`](#iqm.pulse.gate_implementation.CompositeCache.get "iqm.pulse.gate_implementation.CompositeCache.get") | Get a TimeBox from the cache. |
| [`set`](#iqm.pulse.gate_implementation.CompositeCache.set "iqm.pulse.gate_implementation.CompositeCache.set") | Store a TimeBox in the cache. |

&nbsp;

set(*gate_implementation*, *cache_key*, *timebox*, *extra_id=''*)  
Store a TimeBox in the cache.

Parameters:  
- **gate_implementation** ([*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")) – gate implementation that created the TimeBox.

- **cache_key** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\]*) – hashable key identifying the TimeBox (usually the `CompositeGate.__call__()` arguments cast into a tuple).

- **timebox** ([*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox")) – TimeBox that will be added to the cache.

- **extra_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – extra string id for further identifying the result if needed (for example if the TimeBox did not come from the call method, but some other method, this could be the method’s name).

Return type:  
*None*

&nbsp;

get(*gate_implementation*, *cache_key*, *extra_id=''*)  
Get a TimeBox from the cache.

Parameters:  
- **gate_implementation** ([*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")) – gate implementation that created the TimeBox.

- **cache_key** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*,* *...\]*) – hashable key identifying the TimeBox (usually the `CompositeGate.__call__()` arguments cast into a tuple).

- **extra_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – extra string id for further identifying the result (for example if the TimeBox did not come from the call method, but some other method, this could be the method’s name).

Returns:  
The cached TimeBox or None if not fund for this `gate_implementation`, `cache_key`, and `extra_id`.

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "iqm.pulse.timebox.TimeBox") \| *None*

&nbsp;

flush()  
Flush the CompositeCache.

Return type:  
*None*

Inheritance

![Inheritance diagram of iqm.pulse.gate_implementation.CompositeCache](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-73ffb8f1aaf7c1069a13a6b8819b1c970d65bd47.png)
