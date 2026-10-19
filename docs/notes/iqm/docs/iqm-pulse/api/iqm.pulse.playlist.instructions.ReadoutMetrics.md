> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutMetrics.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutMetrics.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f012ab5acee53fab1214dab382afa5b33c7936616c2693ccd60875e791e32c53.

# ReadoutMetrics

Module: [`iqm.pulse.playlist.instructions`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.html#module-iqm.pulse.playlist.instructions "iqm.pulse.playlist.instructions")

*class* iqm.pulse.playlist.instructions.ReadoutMetrics(*num_segments*, *integration_occurrences=\<factory\>*, *timetrace_occurrences=\<factory\>*, *timetrace_lengths=\<factory\>*, *implementations=\<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Necessary readout metrics needed for return data processing for a single `Playlist`.

Individual readout operations (and their results) are labeled using a *readout label* of the format `f"{component}__{readout_key}"`, where `component` is the name of the measured QPU component (typically a qubit), and `readout_key` is a string which identifies the individual measurement operation.

Attributes

|  |  |
|----|----|
| [`num_segments`](#iqm.pulse.playlist.instructions.ReadoutMetrics.num_segments "iqm.pulse.playlist.instructions.ReadoutMetrics.num_segments") | Number of segments in the Playlist this ReadoutMetrics object represents. |
| [`integration_occurrences`](#iqm.pulse.playlist.instructions.ReadoutMetrics.integration_occurrences "iqm.pulse.playlist.instructions.ReadoutMetrics.integration_occurrences") | Map each integration readout label to its number of occurrences in each Playlist segment. |
| [`timetrace_occurrences`](#iqm.pulse.playlist.instructions.ReadoutMetrics.timetrace_occurrences "iqm.pulse.playlist.instructions.ReadoutMetrics.timetrace_occurrences") | Map each time trace readout label to its number of occurrences in each Playlist segment. |
| [`timetrace_lengths`](#iqm.pulse.playlist.instructions.ReadoutMetrics.timetrace_lengths "iqm.pulse.playlist.instructions.ReadoutMetrics.timetrace_lengths") | Map each time trace readout label to its number of time trace samples. |
| [`implementations`](#iqm.pulse.playlist.instructions.ReadoutMetrics.implementations "iqm.pulse.playlist.instructions.ReadoutMetrics.implementations") | Map each integration or time trace readout label to its implementations (of the format `f"{measure_gate_name}.{implementation_name}"`). |

Methods

|  |  |
|----|----|
| [`extend`](#iqm.pulse.playlist.instructions.ReadoutMetrics.extend "iqm.pulse.playlist.instructions.ReadoutMetrics.extend") | Extend the metrics with a ReadoutTrigger in a given Playlist Segment. |
| [`filter_out`](#iqm.pulse.playlist.instructions.ReadoutMetrics.filter_out "iqm.pulse.playlist.instructions.ReadoutMetrics.filter_out") | Filter out readout labels from the contents of `self`. |
| [`get_components`](#iqm.pulse.playlist.instructions.ReadoutMetrics.get_components "iqm.pulse.playlist.instructions.ReadoutMetrics.get_components") | Get all QPU components in the readout labels in `self`. |
| [`get_keys`](#iqm.pulse.playlist.instructions.ReadoutMetrics.get_keys "iqm.pulse.playlist.instructions.ReadoutMetrics.get_keys") | Get all readout keys in the readout labels in `self`. |
| [`get_labels`](#iqm.pulse.playlist.instructions.ReadoutMetrics.get_labels "iqm.pulse.playlist.instructions.ReadoutMetrics.get_labels") | Get all the readout labels in `self`. |

Parameters:  
- **num_segments** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **integration_occurrences** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*)

- **timetrace_occurrences** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]*)

- **timetrace_lengths** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*)

- **implementations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*)

num_segments*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Number of segments in the Playlist this ReadoutMetrics object represents.

integration_occurrences*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*  
Map each integration readout label to its number of occurrences in each Playlist segment.

timetrace_occurrences*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*  
Map each time trace readout label to its number of occurrences in each Playlist segment.

timetrace_lengths*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]*  
Map each time trace readout label to its number of time trace samples.

implementations*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
Map each integration or time trace readout label to its implementations (of the format `f"{measure_gate_name}.{implementation_name}"`).

extend(*trigger*, *seg_idx*)  
Extend the metrics with a ReadoutTrigger in a given Playlist Segment.

Parameters:  
- **trigger** ([*ReadoutTrigger*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.ReadoutTrigger.html#iqm.pulse.playlist.instructions.ReadoutTrigger "iqm.pulse.playlist.instructions.ReadoutTrigger")) – The readout trigger.

- **seg_idx** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The index of the Playlist segment `trigger` belongs to.

Return type:  
*None*

filter_out(*labels=None*, *components=None*, *keys=None*)  
Filter out readout labels from the contents of `self`.

Parameters:  
- **labels** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Readout labels to filter out.

- **components** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – QPU components to filter out (all readout labels with these components will be removed).

- **keys** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Readout keys to filter out (all readout labels with these keys will be removed).

Return type:  
*None*

get_labels(*integration=True*, *timetrace=True*)  
Get all the readout labels in `self`.

Parameters:  
- **integration** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to get integration labels.

- **timetrace** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to get time trace labels.

Returns:  
The applicable readout labels in `self`.

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_components(*integration=True*, *timetrace=True*)  
Get all QPU components in the readout labels in `self`.

Parameters:  
- **integration** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to get components from the integration labels.

- **timetrace** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to get components from the time trace labels.

Returns:  
The applicable QPU components in `self`.

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

get_keys(*integration=True*, *timetrace=True*)  
Get all readout keys in the readout labels in `self`.

Parameters:  
- **integration** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to get readout keys from the integration labels.

- **timetrace** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to get readout keys from the time trace labels.

Returns:  
The applicable readout keys in `self`.

Return type:  
[*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

Inheritance

![Inheritance diagram of iqm.pulse.playlist.instructions.ReadoutMetrics](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-856121515889676732954d1ec63ffe9c848fe31c.png)
