> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cc4d114904abf3f9f35d8163e58f0bbc72e243a06b8e316814db0632236bc2e9.

# iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization

*class* iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization(*client*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

High-level interface for readout error characterization.

Wraps the lower-level functions in [`iqm.error_reduction_tools.readout_characterization.data_collection`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.html#module-iqm.error_reduction_tools.readout_characterization.data_collection "iqm.error_reduction_tools.readout_characterization.data_collection") and [`iqm.error_reduction_tools.readout_characterization.data_processing`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.html#module-iqm.error_reduction_tools.readout_characterization.data_processing "iqm.error_reduction_tools.readout_characterization.data_processing") behind a clean, lifecycle-oriented API.

**Typical online usage**:

```
config = RECConfiguration(shots=20_000, qubits=["QB1", "QB2", "QB5"])
rec = ReadoutErrorCharacterization(client)
rec.submit_job(config)
rec.retrieve_results()
probs = rec.get_readout_error_probabilities()
```

**Chained usage**:

```
probs = (
    ReadoutErrorCharacterization(client)
    .submit_job(config)
    .retrieve_results()
    .get_readout_error_probabilities()
)
```

**Offline usage (reload saved results)**:

```
rec = ReadoutErrorCharacterization.load("charact_garnet_20260311.json")
probs = rec.get_readout_error_probabilities()
```

Methods

|  |  |
|----|----|
| `__repr__`() | Printable representation. |
| [`from_dict`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.from_dict "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.from_dict")(data) | Construct a [`ReadoutErrorCharacterization`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization") from a dictionary. |
| [`get_job_id`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.get_job_id "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.get_job_id")() | Return the id of the calibration job submitted by [`submit_job()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.submit_job "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.submit_job"). |
| [`get_readout_error_probabilities`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.get_readout_error_probabilities "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.get_readout_error_probabilities")() | Return per-qubit readout error probabilities. |
| [`load`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.load "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.load")(path) | Reconstruct a [`ReadoutErrorCharacterization`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization") from a JSON file. |
| [`plot_error_probabilities`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.plot_error_probabilities "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.plot_error_probabilities")(\*\*kwargs) | Plot per-qubit readout error probabilities. |
| [`retrieve_results`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results")(\[job, job_info\]) | Retrieve measurement results from the calibration job. |
| [`save`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.save "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.save")(path) | Serialize the characterization state to a JSON file. |
| [`submit_job`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.submit_job "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.submit_job")(\[config\]) | Submit calibration circuits to the quantum computer. |
| [`to_dict`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.to_dict "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.to_dict")() | Serialize the characterization state to a JSON-compatible dictionary. |

Parameters:  
**client** (*IQMClient* *\|* *None*)

submit_job(*config=None*)  
Submit calibration circuits to the quantum computer.

Stores the returned job tracker and job metadata internally.

Parameters:  
**config** ([*RECConfiguration*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration") *\|* *None*) – Characterization configuration. Defaults to [`RECConfiguration`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration") with all default values when `None`.

Returns:  
The current instance for method chaining.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If no client was provided at construction time.

Return type:  
[*Self*](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")

retrieve_results(*job=None*, *job_info=None*)  
Retrieve measurement results from the calibration job.

Wraps [`retrieve_calibration_results()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results.html#iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results "iqm.error_reduction_tools.readout_characterization.data_collection.retrieve_calibration_results") and stores the raw counts internally.

`job` and `job_info` are always treated as a matched pair from the same calibration run. Either supply both to use an externally obtained job, or omit both to use the job stored internally by [`submit_job()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.submit_job "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.submit_job"). Passing only one of the two is an error.

Parameters:  
- **job** (*RunJobTracker* *\|* *None*) – Job to fetch results from.

- **job_info** ([*CalibrationJobInfo*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.html#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo") *\|* *None*) – [`CalibrationJobInfo`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo.html#iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo "iqm.error_reduction_tools.readout_characterization.data_collection.CalibrationJobInfo") that accompanies `job` (preparation strings, qubit list, etc.).

Returns:  
The current instance for method chaining.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If exactly one of `job` / `job_info` is provided.

- [**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If neither explicit arguments nor internal state are available.

Return type:  
Self

get_job_id()  
Return the id of the calibration job submitted by [`submit_job()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.submit_job "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.submit_job").

Returns:  
The job id as a string, or `None` when no job has been submitted (for example when the characterization was reconstructed offline via [`from_dict()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.from_dict "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.from_dict") or [`load()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.load "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.load")).

Return type:  
[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| None

get_readout_error_probabilities()  
Return per-qubit readout error probabilities.

Computes the probabilities on the first call (lazy evaluation) and caches the result internally. Subsequent calls return the cached value without recomputation.

Returns:  
Per-qubit readout error probabilities. See [`ErrorProbabilities`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.html#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities") for the structure.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`retrieve_results()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results") has not been called.

Return type:  
[*ErrorProbabilities*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.html#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities")

to_dict()  
Serialize the characterization state to a JSON-compatible dictionary.

The serialized form contains everything required to reconstruct a post-retrieval object offline via [`from_dict()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.from_dict "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.from_dict"):

| Key | Contents |
|----|----|
| `counts_by_prep` | Raw calibration counts |
| `measured_qubits` | Qubit labels |
| `config` | [`RECConfiguration`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration") used |
| `charact_data` | Cached assignment matrices (*optional*, present only if already computed) |
| `charact_data_std` | Matching standard deviations (*optional*, present only if already computed) |
| `timestamp` | ISO-8601 creation timestamp, in UTC |

Returns:  
JSON-serializable dictionary.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`retrieve_results()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results") has not been called.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

*classmethod* from_dict(*data*)  
Construct a [`ReadoutErrorCharacterization`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization") from a dictionary.

The reconstructed object holds raw results and cached error probabilities (when available). It has no client or job handle, but all analysis and visualization methods work normally.

Parameters:  
**data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Dictionary produced by [`to_dict()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.to_dict "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.to_dict") or loaded via [`load()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.load "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.load").

Returns:  
New [`ReadoutErrorCharacterization`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization") instance ready for offline analysis.

Return type:  
[*Self*](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")

save(*path*)  
Serialize the characterization state to a JSON file.

Parameters:  
**path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Destination file path (file will be overwritten if it exists).

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`retrieve_results()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results") has not been called yet.

Return type:  
None

*classmethod* load(*path*)  
Reconstruct a [`ReadoutErrorCharacterization`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization") from a JSON file.

Parameters:  
**path** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Path to a file created by [`save()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.save "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.save").

Returns:  
New [`ReadoutErrorCharacterization`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization") instance ready for offline analysis.

Return type:  
[*Self*](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")

plot_error_probabilities(*\*\*kwargs*)  
Plot per-qubit readout error probabilities.

Thin convenience wrapper around [`plot_error_probabilities()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.visualization.plot_error_probabilities.html#iqm.error_reduction_tools.readout_characterization.visualization.plot_error_probabilities "iqm.error_reduction_tools.readout_characterization.visualization.plot_error_probabilities"). All keyword arguments are forwarded verbatim (e.g. `title`, `show_plot`).

The visualization module is imported lazily to avoid pulling in `matplotlib` at package import time.

Raises:  
[**RuntimeError**](https://docs.python.org/3.11/library/exceptions.html#RuntimeError "(in Python v3.11)") – If [`retrieve_results()`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.retrieve_results") has not been called yet.

Return type:  
None
