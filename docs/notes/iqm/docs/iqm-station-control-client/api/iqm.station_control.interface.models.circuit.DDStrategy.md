> Full piece: [https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.DDStrategy.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 2eb37a0f2594ac184fdc9084dad841b6c5da3a9b1e4723de83d9498a0092b80c.

# DDStrategy

Module: [`iqm.station_control.interface.models.circuit`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.models.circuit.html#module-iqm.station_control.interface.models.circuit "iqm.station_control.interface.models.circuit")

*class* DDStrategy(*\**, *merge_contiguous_waits=True*, *target_qubits=None*, *skip_leading_wait=True*, *skip_trailing_wait=True*, *gate_sequences=\<factory\>*)  
Bases: [`PydanticBase`](https://docs.iqm.tech/4.7/iqm-station-control-client/api/iqm.station_control.interface.pydantic_base.PydanticBase.html#iqm.station_control.interface.pydantic_base.PydanticBase "iqm.station_control.interface.pydantic_base.PydanticBase")

Describes a particular dynamical decoupling strategy.

The current standard DD stategy can be found in `STANDARD_DD_STRATEGY`, but users can use this class to provide their own dynamical decoupling strategies.

See Ezzell et al., Phys. Rev. Appl. 20, 064027 (2022) for information on DD sequences.

Create a new model by parsing and validating input data from keyword arguments.

Raises \[ValidationError\]\[pydantic_core.ValidationError\] if the input data cannot be validated to form a valid model.

self is explicitly positional-only to allow self as a field name.

Attributes

|  |  |
|----|----|
| [`model_config`](#iqm.station_control.interface.models.circuit.DDStrategy.model_config "iqm.station_control.interface.models.circuit.DDStrategy.model_config") | Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\]. |
| [`merge_contiguous_waits`](#iqm.station_control.interface.models.circuit.DDStrategy.merge_contiguous_waits "iqm.station_control.interface.models.circuit.DDStrategy.merge_contiguous_waits") | Merge contiguous `Wait` instructions into one if they are separated only by `Block` instructions. |
| [`target_qubits`](#iqm.station_control.interface.models.circuit.DDStrategy.target_qubits "iqm.station_control.interface.models.circuit.DDStrategy.target_qubits") | Qubits on which dynamical decoupling should be applied. |
| [`skip_leading_wait`](#iqm.station_control.interface.models.circuit.DDStrategy.skip_leading_wait "iqm.station_control.interface.models.circuit.DDStrategy.skip_leading_wait") | Skip processing leading `Wait` instructions. |
| [`skip_trailing_wait`](#iqm.station_control.interface.models.circuit.DDStrategy.skip_trailing_wait "iqm.station_control.interface.models.circuit.DDStrategy.skip_trailing_wait") | Skip processing trailing `Wait` instructions. |
| [`gate_sequences`](#iqm.station_control.interface.models.circuit.DDStrategy.gate_sequences "iqm.station_control.interface.models.circuit.DDStrategy.gate_sequences") | Available decoupling gate sequences to choose from in this strategy. |

Methods

Parameters:  
- **merge_contiguous_waits** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **target_qubits** ([*frozenset*](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*)

- **skip_leading_wait** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **skip_trailing_wait** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **gate_sequences** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\],* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]*)

merge_contiguous_waits*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Merge contiguous `Wait` instructions into one if they are separated only by `Block` instructions.

target_qubits*: [frozenset](https://docs.python.org/3.11/library/stdtypes.html#frozenset "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Qubits on which dynamical decoupling should be applied. If `None`, all qubits are targeted.

skip_leading_wait*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Skip processing leading `Wait` instructions.

skip_trailing_wait*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Skip processing trailing `Wait` instructions.

gate_sequences*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| PRXSequence, [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]*  
Available decoupling gate sequences to choose from in this strategy.

Each sequence is defined by a tuple of `(ratio, gate pattern, align)`:

> - ratio: Minimal duration for the sequence (in PRX gate durations).
>
> - gate pattern: Gate pattern can be defined in two ways. It can be a string containing “X” and “Y” characters, encoding a PRX gate sequence. For example, “YXYX” corresponds to the XY4 sequence, “XYXYYXYX” to the EDD sequence, etc. If more flexibility is needed, a gate pattern can be defined as a sequence of PRX gate argument tuples (that contain a rotation angle and a phase angle). For example, sequence “YX” could be written as `[(math.pi, math.pi / 2), (math.pi, 0)]`.
>
> - align: Controls the alignment of the sequence within the time window it is inserted in. Supported values:
>
>   - “asap”: Corresponds to a ASAP-aligned sequence with no waiting time before the first pulse.
>
>   - “center”: Corresponds to a symmetric sequence.
>
>   - “alap”: Corresponds to a ALAP-aligned sequence.

The Dynamical Decoupling algorithm uses the best fitting gate sequence by first sorting them by `ratio` in descending order. Then the longest fitting pattern is determined by comparing `ratio` with the duration of the time window divided by the PRX gate duration.

model_config*: ClassVar\[ConfigDict\]* *= {'extra': 'ignore', 'ser_json_inf_nan': 'constants', 'validate_assignment': True, 'validate_default': True}*  
Configuration for the model, should be a dictionary conforming to \[ConfigDict\]\[pydantic.config.ConfigDict\].

Inheritance

![Inheritance diagram of iqm.station_control.interface.models.circuit.DDStrategy](https://docs.iqm.tech/4.7/iqm-station-control-client/_images/inheritance-d50f583f3b3a8a41e3684696bf881a8fa4716372.png)
