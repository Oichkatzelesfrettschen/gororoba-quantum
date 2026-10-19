> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMWorkflow.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMWorkflow.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 34a07ee4e28a00b0e7bef475b25633e1e8204fe3eec7d559f812dc8f58124fb6.

# iqm.error_reduction_tools.rem.rem_api.REMWorkflow

*class* iqm.error_reduction_tools.rem.rem_api.REMWorkflow(*client*, *\**, *config=None*, *characterization=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

End-to-end readout error mitigation workflow.

Combines readout error characterization, circuit twirling, and postprocessing behind a clean, lifecycle-oriented API.

**Two-step (async) usage** — submit jobs, do other things, then retrieve:

```
workflow = REMWorkflow(client, config=config)
workflow.submit(circuits, observables=["ZZII", "IIZZ"])
# ... user can do other things while QPU jobs run ...
results = workflow.get_results()
```

**One-liner (blocking) usage** — for notebooks and demos:

```
results = REMWorkflow(client).run(circuits)
```

**Reusing previous characterization**:

```
workflow = REMWorkflow(client, characterization="charact.json")
results = workflow.run(circuits)
```

Parameters:  
- **client** (*IQMClient*) – Client for connecting to the quantum computer.

- **config** ([*WorkflowConfiguration*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.html#iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration "iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration") *\|* *None*) – Workflow configuration. Defaults are sensible for most cases.

- **characterization** ([*ReadoutErrorCharacterization*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization") *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Pre-existing readout error characterization. Accepts a [`ReadoutErrorCharacterization`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization") object, a `dict` (from `rec.to_dict()`), or a file path `str`. When `None`, characterization is run automatically during [`submit()`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit").

Methods

|  |  |
|----|----|
| [`get_characterization`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_characterization "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_characterization")() | Return the `ReadoutErrorCharacterization` (saveable for reuse). |
| [`get_expectation_values`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_expectation_values "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_expectation_values")() | Return observable expectation values per circuit, or `None`. |
| [`get_job_ids`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_job_ids "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_job_ids")() | Return the ids of the QPU jobs submitted by this workflow. |
| [`get_mitigated_distributions`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_mitigated_distributions "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_mitigated_distributions")() | Return mitigated distributions per input circuit. |
| [`get_raw_counts`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_raw_counts "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_raw_counts")() | Return unmitigated (but untwirled) counts per input circuit. |
| [`get_results`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_results "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.get_results")() | Wait for jobs, retrieve results, and apply readout error mitigation. |
| [`load_characterization`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.load_characterization "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.load_characterization")(source) | Load pre-existing readout error characterization. |
| [`run`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.run "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.run")(circuits\[, observables\]) | Submit jobs and retrieve results in one blocking call. |
| [`submit`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit")(circuits\[, observables\]) | Submit characterization and twirled circuit jobs to the QPU. |

load_characterization(*source*)  
Load pre-existing readout error characterization.

Parameters:  
**source** ([*ReadoutErrorCharacterization*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization") *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)") *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A `ReadoutErrorCharacterization` object, a dict (as returned by `rec.to_dict()`), or a JSON file path.

Returns:  
`self` for method chaining.

Raises:  
[**TypeError**](https://docs.python.org/3.11/library/exceptions.html#TypeError "(in Python v3.11)") – If the source type is not supported.

Return type:  
[*REMWorkflow*](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow "iqm.error_reduction_tools.rem.rem_api.REMWorkflow")

submit(*circuits*, *observables=None*)  
Submit characterization and twirled circuit jobs to the QPU.

If no characterization was loaded, a REC job is submitted automatically. All input circuits are twirled and submitted as a separate job.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")) – Quantum circuits to mitigate. Accepts any type supported by [`twirl()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.html#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl"): Qiskit `QuantumCircuit`, `Circuit`, [`TwirledCircuit`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit"), or any object with a `to_qiskit()` method (e.g. `qrisp.QuantumCircuit`).

- **observables** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*) – Observable specifications for expectation value computation. Supports qubit names (`[["QB3", "QB5"]]`), Pauli strings (`["ZZII"]`), or bit indices (`[[0, 1]]`). Pass `None` to mitigate the full distribution only.

Returns:  
`self` for method chaining.

Return type:  
[*REMWorkflow*](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow "iqm.error_reduction_tools.rem.rem_api.REMWorkflow")

get_results()  
Wait for jobs, retrieve results, and apply readout error mitigation.

Blocks until both the characterization and circuit jobs complete, then performs REM postprocessing and packages all outputs.

Returns:  
[`REMResults`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMResults.html#iqm.error_reduction_tools.rem.rem_api.REMResults "iqm.error_reduction_tools.rem.rem_api.REMResults") with mitigated counts, expectation values, raw counts, characterization data, and metadata.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`submit()`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit") has not been called.

Return type:  
[*REMResults*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMResults.html#iqm.error_reduction_tools.rem.rem_api.REMResults "iqm.error_reduction_tools.rem.rem_api.REMResults")

run(*circuits*, *observables=None*)  
Submit jobs and retrieve results in one blocking call.

Convenience wrapper equivalent to:

```
self.submit(circuits, observables=observables)
return self.get_results()
```

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")) – Quantum circuits to mitigate. Accepts any type supported by [`twirl()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.html#iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl "iqm.error_reduction_tools.twirling.twirling_api.CircuitTwirler.twirl").

- **observables** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*) – Observable specifications (same format as [`submit()`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit")).

Returns:  
[`REMResults`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMResults.html#iqm.error_reduction_tools.rem.rem_api.REMResults "iqm.error_reduction_tools.rem.rem_api.REMResults") with all outputs.

Return type:  
[*REMResults*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMResults.html#iqm.error_reduction_tools.rem.rem_api.REMResults "iqm.error_reduction_tools.rem.rem_api.REMResults")

get_characterization()  
Return the `ReadoutErrorCharacterization` (saveable for reuse).

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If characterization is not yet available.

Return type:  
[*ReadoutErrorCharacterization*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization")

get_job_ids()  
Return the ids of the QPU jobs submitted by this workflow.

Returns:  
Mapping with keys `"characterization"` and `"twirling"`. `"characterization"` is `None` when a pre-existing characterization was reused (no characterization job was submitted).

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`submit()`](#iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit "iqm.error_reduction_tools.rem.rem_api.REMWorkflow.submit") has not been called yet.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| None\]

get_raw_counts()  
Return unmitigated (but untwirled) counts per input circuit.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If results are not yet available.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]

get_mitigated_distributions()  
Return mitigated distributions per input circuit.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If results are not yet available.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]

get_expectation_values()  
Return observable expectation values per circuit, or `None`.

Returns `None` if no observables were specified.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If results are not yet available.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\] \| None
