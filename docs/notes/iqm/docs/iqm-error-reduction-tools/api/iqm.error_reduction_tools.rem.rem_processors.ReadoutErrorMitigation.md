> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c0db7b41fddadd06353d66909274674afd714137169330383d2fc6bd507c2b04.

# iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation

*class* iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation(*readout_errors*, *max_entropy=28.0*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Apply readout error mitigation to measurement counts, with optional twirling support.

This class performs tensor-product inversion of readout confusion matrices to correct measurement errors. Supports both standard and symmetrized (twirled) characterization data.

Methods

|  |  |
|----|----|
| `_mitigate`(counts, cl_index_to_qubit_name\[, ...\]) | Apply readout error mitigation to the given counts. |
| `_normalize_observables`(observables, ...) | Normalize observables to the canonical qubit-name list format. |
| `_symmetrize_copy`(charact_data) | Return a symmetrized copy of characterization data without modifying the original. |
| `_validate_charact_data`() | Validate the characterization data format. |
| `_validate_counts_and_mapping`(counts, ...) | Validate the counts format and qubit mapping. |
| `_warn_high_error_rates`(charact_data) | Emit warnings for qubits whose readout error rate is \>= 20%. |
| [`from_client`](#iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.from_client "iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.from_client")(client\[, qubits, ...\]) | Create ReadoutErrorMitigation by running characterization on a quantum computer. |
| [`get_calibration_data`](#iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.get_calibration_data "iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.get_calibration_data")() | Get the calibration data for all qubits. |
| [`mitigate_counts`](#iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.mitigate_counts "iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.mitigate_counts")(experiment_counts, ...\[, ...\]) | Mitigate a list of measurement count dictionaries for one or more observables. |
| [`symmetrize_charact_data`](#iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.symmetrize_charact_data "iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.symmetrize_charact_data")() | Symmetrize the characterization data by averaging error rates. |

Parameters:  
- **readout_errors** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *AssignmentMatrix\]* *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*)

- **max_entropy** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

*classmethod* from_client(*client*, *qubits=None*, *number_of_circuits=100*, *shots=10000*, *symmetrize=True*, *seed=None*, *equatorial_randomization=True*, *max_entropy=28.0*)  
Create ReadoutErrorMitigation by running characterization on a quantum computer.

Runs the full characterization workflow on the quantum computer and then returns an initialized ReadoutErrorMitigation instance.

Parameters:  
- **client** (*IQMClient*) – Client for connecting to an IQM quantum computer.

- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – List of qubit names to characterize (e.g., \[“QB1”, “QB2”\]). If None, characterizes all qubits available on the client.

- **number_of_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of calibration circuits to generate.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Total shots for characterization, distributed across all circuits.

- **symmetrize** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, generates complementary I/X preparation pairs.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Random seed for reproducible characterization.

- **equatorial_randomization** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, randomizes X gate phases.

- **max_entropy** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Maximum allowed Shannon entropy (in bits) threshold.

Returns:  
ReadoutErrorMitigation instance with characterization data.

Return type:  
[ReadoutErrorMitigation](#iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation "iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation")

Example

```
>>> from iqm.iqm_client import IQMClient
>>> client = IQMClient.from_url("https://example.iqm.fi")
>>> mitigator = ReadoutErrorMitigation.from_client(
...     client=client,
...     qubits=["QB1", "QB2"],
...     number_of_circuits=30,
...     shots=10000,
... )
>>> mitigated = mitigator.mitigate(counts, cl_index_to_qubit_name=["QB1", "QB2"])
```

get_calibration_data()  
Get the calibration data for all qubits.

Returns:  
Dictionary mapping qubit names to their calibration matrices (2x2 numpy arrays).

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\]

symmetrize_charact_data()  
Symmetrize the characterization data by averaging error rates.

Converts matrices to symmetrized scalar error rates by averaging P(0\|1) and P(1\|0). If data is already scalar, this method has no effect.

Return type:  
None

mitigate_counts(*experiment_counts*, *qubit_to_bit_mapping*, *observables=None*, *twirled=False*, *force_mitigation=False*, *nearest_probability=True*, *client=None*, *auto_characterize_shots=10000*, *auto_characterize_circuits=20*)  
Mitigate a list of measurement count dictionaries for one or more observables.

Bitstrings and bit indices follow **little-endian** (Qiskit) convention: bit index 0 is the **rightmost** character of the bitstring.

Parameters:  
- **experiment_counts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[SampledDistribution\]*) – Measurement count dictionaries. Each dict maps bitstrings (e.g., `"0101"`) to shot counts. Bitstrings follow **little-endian** convention (rightmost character = bit index 0).

- **qubit_to_bit_mapping** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* [*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*TwirledCircuit*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit.html#iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit "iqm.error_reduction_tools.utils.circuit_utils.TwirledCircuit")*\]*) –

  A property of the transpiled circuit: it maps every measured qubit name to its classical bit index and is fixed once the circuit has been run.

  Accepts multiple formats (auto-detected):

  - **dict** (canonical): `{"QB5": 0, "QB12": 1, "QB3": 2, "QB7": 3}`

  - **TwirledCircuit**: extracts mapping from `measured_qubits`

  - **list\[TwirledCircuit\]**: extracts from the first circuit

- **observables** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* *None*) –

  Observables to mitigate and compute ZZ…Z expectation values for. `observables` is a list of qubit-name subsets; for each subset the raw counts are first marginalized to the corresponding bit indices (looked up from `qubit_to_bit_mapping`), then readout-error-mitigated, and finally a ZZ…Z expectation value is computed.

  Supports three formats per element (auto-detected):

  - **Qubit names** (current): `[["QB3", "QB5"], ["QB1"]]`

  - **Pauli strings** (Z/I only): `["IIIZZIZI", "ZIIIIIIII"]`

  - **Bit indices**: `[[2, 4], [0]]`

  If `None`, a single observable covering all qubits in `qubit_to_bit_mapping` is used. Formats can be mixed within a single call.

- **twirled** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, symmetrize the characterization data before mitigation by averaging P(0\|1) and P(1\|0) into a single error rate per qubit. This is appropriate when the counts were obtained using readout twirling. The original `charact_data` on the instance is **not** modified; a temporary symmetrized copy is used. Default is `False`.

- **force_mitigation** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, apply mitigation even if complexity exceeds threshold.

- **nearest_probability** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, project each quasi-probability distribution onto the nearest valid probability distribution using `mthree`’s `nearest_probability_distribution` method. Eliminates negative values at the cost of a small bias. Default is True.

- **client** (*IQMClient* *\|* *None*) – Optional client for automatic characterization of missing qubits on the quantum computer.

- **auto_characterize_shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Shots to use when auto-characterizing (default: 10000).

- **auto_characterize_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of circuits for auto-characterization (default: 20).

Returns:  
- `"mitigated_counts"`: `list[list[dict[str, float]]]` — `result["mitigated_counts"][i][j]` is the mitigated quasi-probability distribution for circuit `i` under observable `j`.

- `"expectation_values"`: `list[list[float]]` — `result["expectation_values"][i][j]` is the ZZ…Z expectation value for circuit `i` under observable `j`.

- `"characterization_performed"`: `bool` — True if auto-characterization ran.

Return type:  
Dictionary containing

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `experiment_counts` or `qubit_to_bit_mapping` are empty, if any observable qubit is not in `qubit_to_bit_mapping`, or characterization data is missing and no `client` is provided.

Example — full-distribution mitigation:

```
>>> mitigator = ReadoutErrorMitigation(charact_data)
>>> result = mitigator.mitigate_counts(
...     experiment_counts=[{"00": 450, "11": 450}],
...     qubit_to_bit_mapping={"QB1": 0, "QB2": 1},
... )
>>> result["mitigated_counts"][0][0]   # circuit 0, observable 0
>>> result["expectation_values"][0][0]  # <ZZ> for circuit 0
```

Example — multiple observables in one call:

```
>>> result = mitigator.mitigate_counts(
...     experiment_counts=[{"0000": 450, "1111": 450}],
...     qubit_to_bit_mapping={"QB1": 0, "QB2": 1, "QB3": 2, "QB4": 3},
...     observables=[
...         ["QB1", "QB2", "QB3", "QB4"],  # full ZZZZ
...         ["QB1", "QB2"],                 # ZZ on first two qubits
...         ["QB3", "QB4"],                 # ZZ on last two qubits
...     ],
... )
>>> result["expectation_values"][0]  # [<ZZZZ>, <Z0Z1>, <Z2Z3>]
```

Example — auto-characterization:

```
>>> mitigator = ReadoutErrorMitigation(charact_data={})
>>> result = mitigator.mitigate_counts(
...     experiment_counts=counts_list,
...     qubit_to_bit_mapping={"QB1": 0, "QB2": 1},
...     client=client,
... )
```

Example — twirled mitigation (same instance reusable for both):

```
>>> rem = ReadoutErrorMitigation(charact_data=probs["charact_data"])
>>> result_twirled = rem.mitigate_counts(
...     [twirled_counts], mapping, twirled=True,
... )
>>> result_standard = rem.mitigate_counts(
...     [standard_counts], mapping, twirled=False,
... )
```

Example — Pauli-string observables (natural for Qiskit users):

```
>>> result = rem.mitigate_counts(
...     experiment_counts=[counts],
...     qubit_to_bit_mapping={"QB1": 0, "QB2": 1, "QB3": 2, "QB4": 3},
...     observables=["IZIZ", "ZZII"],
...     twirled=True,
... )
```

Example — bit-index observables (framework-agnostic):

```
>>> result = rem.mitigate_counts(
...     experiment_counts=[counts],
...     qubit_to_bit_mapping={"QB1": 0, "QB2": 1, "QB3": 2, "QB4": 3},
...     observables=[[0, 2], [2, 3]],
... )
```

Example — TwirledCircuit as mapping:

```
>>> result = rem.mitigate_counts(
...     experiment_counts=[counts],
...     qubit_to_bit_mapping=twirled_circuit,
...     twirled=True,
... )
```
