> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 dc06f3b6d28c6ef264958a049dadac68328388351066d2919031d244eaa5a07a.

# iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler

*class* iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler(*client=None*, *config=None*, *compilation_options=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Manages the twirl → submit → retrieve lifecycle for readout-twirled circuits.

Parameters:  
- **client** (*IQMClient* *\|* *None*) – Client instance for connecting to an IQM quantum computer. Used for topology look-up (only required for the `"LOCAL"` readout-twirling strategy), compilation, and job submission. May be `None` when the twirler is used purely as a circuit transformer — i.e. when calling only [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") (with a non-`LOCAL` strategy) and [`get_twirled_circuits()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_twirled_circuits "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_twirled_circuits") to drive submission externally. Required by [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit") and by the `"LOCAL"` strategy.

- **config** ([*TwirlingConfiguration*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration.html#iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration "iqm.error_reduction_tools.twirling.twirling_api.TwirlingConfiguration") *\|* *None*) – Twirling configuration. Defaults are sensible for most cases.

- **compilation_options** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Any\]* *\|* *None*) –

  Extra key-value pairs passed to the IQM compiler context when [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit") compiles circuits. Use this to activate compiler features such as dynamical decoupling. For example:

  ```
  compilation_options={"DDStrategy": my_dd_strategy}
  ```

Example — full lifecycle (requires client):

```
twirler = CircuitTwirler(client, config=TwirlingConfiguration(readout_twirl_strategy="LOCAL", seed=42))
twirler.twirl(circuits).submit(shots=20_000)
mitigated_counts = twirler.retrieve_counts()
```

Example — circuit-twirling-only, no client needed:

```
config = TwirlingConfiguration(readout_twirl_strategy="NONE", circuit_twirling=True)
twirler = CircuitTwirler(config=config)
randomized = twirler.twirl(circuits).get_twirled_circuits()
```

Attributes

|  |  |
|----|----|
| [`readout_twirling_applied`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.readout_twirling_applied "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.readout_twirling_applied") | Whether readout twirling was actually applied to the counts. |

Methods

|  |  |
|----|----|
| `_convert_circuits`(circuits) | Convert heterogeneous input circuits to `TwirledCircuit`. |
| `_extract_qubit_to_bit_mapping`(circuit) | Derive the qubit → classical-bit mapping from measurement operations. |
| [`from_dict`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.from_dict "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.from_dict")(data, client) | Reconstruct a [`CircuitTwirler`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler") from a dictionary. |
| [`get_job`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_job "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_job")() | Return job from [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit"). |
| [`get_job_id`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_job_id "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_job_id")() | Return the id of the job submitted by [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit"). |
| [`get_qubit_to_bit_mapping`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_qubit_to_bit_mapping "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_qubit_to_bit_mapping")() | Return qubit-to-classical-bit mappings extracted during [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl"). |
| [`get_rot_strings`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_rot_strings "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_rot_strings")() | Return rotation strings produced by [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl"). |
| [`get_twirled_circuits`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_twirled_circuits "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_twirled_circuits")(\[return_qiskit\]) | Return the randomized circuits produced by [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl"). |
| [`get_twirled_circuits_flat`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_twirled_circuits_flat "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.get_twirled_circuits_flat")(\[return_qiskit\]) | Return all randomized circuits as a single flat list. |
| [`load_twirling_info`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.load_twirling_info "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.load_twirling_info")(path, client) | Load twirling state from a JSON file. |
| [`retrieve_counts`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.retrieve_counts "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.retrieve_counts")() | Wait for job completion, untwirl, and sum counts per input circuit. |
| [`save_twirling_info`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.save_twirling_info "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.save_twirling_info")(path) | Save twirling state to a JSON file. |
| [`submit`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit")(\[shots, client\]) | Compile and submit all randomized circuits to the quantum computer for execution. |
| [`to_dict`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.to_dict "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.to_dict")() | Serialize twirling state to a plain dictionary. |
| [`twirl`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl")(circuits) | Convert input circuits to pulse form, generate rotation strings, and randomize. |

twirl(*circuits*)  
Convert input circuits to pulse form, generate rotation strings, and randomize.

Parameters:  
**circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit") *\|* *QuantumCircuit* *\|* *QuantumCircuit* *\|* [*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")*\]*) – Input circuits to twirl.

Returns:  
`self`, to allow method chaining.

Raises:  
- [**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If a circuit type is not supported.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If *circuits* is empty.

Return type:  
[*CircuitTwirler*](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler")

submit(*shots=20000*, *client=None*)  
Compile and submit all randomized circuits to the quantum computer for execution.

`shots` refers to the number of shots *per input (target) circuit*. It is distributed evenly across that circuit’s twirled instances, so the untwirled, aggregated counts for each input circuit are based on (approximately) `shots` shots regardless of how many input circuits are submitted.

Parameters:  
- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of shots per input circuit, split across its twirled instances.

- **client** (*IQMClient* *\|* *None*) –

  Client for submitting the task to the quantum computer. If provided, it overrides the client supplied at construction time and is also stored on the instance for any subsequent calls (e.g. [`retrieve_counts()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.retrieve_counts "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.retrieve_counts")). This makes it possible to construct a client-less `CircuitTwirler` purely as a circuit transformer and only bind a client at submission time.

  When the strategy used at [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") time was `"LOCAL"`, the rotation strings are tied to the *exact* quantum computer that was used during [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl"). Using a different quantum computer here raises [`ValueError`](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)"); re-run [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") with the new QC first.

Returns:  
`self`, to allow method chaining.

Raises:  
- [**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") has not been called yet, or if no client is available (neither at construction nor here).

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If a different `client` instance is passed here while the `"LOCAL"` strategy was used at [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") time.

Return type:  
[CircuitTwirler](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler")

retrieve_counts()  
Wait for job completion, untwirl, and sum counts per input circuit.

Uses [`untwirl_and_sum_counts()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts.html#iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts "iqm.error_reduction_tools.twirling.twirling_processors.untwirl_and_sum_counts") (the same function used in the tutorial notebooks) to untwirl and aggregate the raw counts.

Returns:  
One count dictionary per original input circuit.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit") has not been called yet.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]

get_twirled_circuits(*return_qiskit=False*)  
Return the randomized circuits produced by [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl").

Parameters:  
**return_qiskit** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – When `True`, convert each circuit to a Qiskit `QuantumCircuit` before returning. Defaults to `False` (returns `Circuit`).

Returns:  
Nested list with one inner list of randomized variants per input circuit, in the same order as the circuits passed to [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl").

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") has not been called yet.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\]\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*QuantumCircuit*\]\]

get_twirled_circuits_flat(*return_qiskit=False*)  
Return all randomized circuits as a single flat list.

Parameters:  
**return_qiskit** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – When `True`, convert each circuit to a Qiskit `QuantumCircuit` before returning. Defaults to `False` (returns `Circuit`).

Returns:  
Flat list of all randomized circuits, matching the order used internally by [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit").

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") has not been called yet.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[*QuantumCircuit*\]

get_rot_strings()  
Return rotation strings produced by [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl").

Returns:  
Nested list — one inner list per input circuit, each containing one rot string (e.g. `"IXXI"`) per randomized variant.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") has not been called yet.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]\]

get_qubit_to_bit_mapping()  
Return qubit-to-classical-bit mappings extracted during [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl").

Returns:  
`{qubit_name: classical_bit_index}`.

Return type:  
One mapping per input circuit

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") has not been called yet.

*property* readout_twirling_applied*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Whether readout twirling was actually applied to the counts.

`True` only if a non-`NONE` strategy was requested *and* twirling was not skipped by a fallback (missing LOCAL topology, MOVE-gate QPU). This is the correct value to pass as `twirled` to `mitigate_counts()`: symmetrizing the confusion matrix is only appropriate when the counts were readout-twirled.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`twirl()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl") has not been called yet.

get_job()  
Return job from [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit").

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit") has not been called yet.

Return type:  
[object](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

get_job_id()  
Return the id of the job submitted by [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit").

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`submit()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.submit") has not been called yet.

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

to_dict()  
Serialize twirling state to a plain dictionary.

Includes rotation strings, qubit-to-bit mappings, and the configuration — enough to reconstruct the twirler for post-processing without re-running on hardware.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*classmethod* from_dict(*data*, *client*)  
Reconstruct a [`CircuitTwirler`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler") from a dictionary.

The restored instance has rotation strings and mappings populated but no circuits or job — it can be used for post-processing only.

Parameters:  
- **data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Any\]*) – Dictionary as returned by [`to_dict()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.to_dict "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.to_dict").

- **client** (*IQMClient*) – Client for connecting to the quantum computer.

Returns:  
A [`CircuitTwirler`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler") with restored state.

Return type:  
[CircuitTwirler](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler")

save_twirling_info(*path*)  
Save twirling state to a JSON file.

Parameters:  
**path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Destination file path.

Return type:  
None

*classmethod* load_twirling_info(*path*, *client*)  
Load twirling state from a JSON file.

Parameters:  
- **path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Path to a JSON file previously written by [`save_twirling_info()`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.save_twirling_info "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.save_twirling_info").

- **client** (*IQMClient*) – Client for connecting to the quantum computer.

Returns:  
A [`CircuitTwirler`](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler") with restored state.

Return type:  
[CircuitTwirler](#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler")
