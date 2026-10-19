> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMResults.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMResults.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fb6fa9d6a787b3a7eb3bbd119b62981f050c065a5ccbfe69f290f7b457ef4445.

# iqm.error_reduction_tools.rem.rem_api.REMResults

*class* iqm.error_reduction_tools.rem.rem_api.REMResults(*mitigated_distributions*, *expectation_values*, *raw_counts*, *characterization*, *metadata*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Output of a completed REM workflow.

Example:

```
results = workflow.get_results()
print(results.mitigated_distributions[0])
results.characterization.save("charact.json")
```

Attributes

|  |  |
|----|----|
| [`mitigated_distributions`](#iqm.error_reduction_tools.rem.rem_api.REMResults.mitigated_distributions "iqm.error_reduction_tools.rem.rem_api.REMResults.mitigated_distributions") | One mitigated distribution per input circuit. |
| [`expectation_values`](#iqm.error_reduction_tools.rem.rem_api.REMResults.expectation_values "iqm.error_reduction_tools.rem.rem_api.REMResults.expectation_values") | Observable expectation values per circuit (`None` if no observables). |
| [`raw_counts`](#iqm.error_reduction_tools.rem.rem_api.REMResults.raw_counts "iqm.error_reduction_tools.rem.rem_api.REMResults.raw_counts") | One untwirled (but unmitigated) count distribution per input circuit. |
| [`characterization`](#iqm.error_reduction_tools.rem.rem_api.REMResults.characterization "iqm.error_reduction_tools.rem.rem_api.REMResults.characterization") | The `ReadoutErrorCharacterization` object (saveable for reuse). |
| [`metadata`](#iqm.error_reduction_tools.rem.rem_api.REMResults.metadata "iqm.error_reduction_tools.rem.rem_api.REMResults.metadata") | Workflow metadata. |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |

Parameters:  
- **mitigated_distributions** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*)

- **expectation_values** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]* *\|* *None*)

- **raw_counts** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]\]*)

- **characterization** ([*ReadoutErrorCharacterization*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization"))

- **metadata** ([*REMMetadata*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMMetadata.html#iqm.error_reduction_tools.rem.rem_api.REMMetadata "iqm.error_reduction_tools.rem.rem_api.REMMetadata"))

mitigated_distributions*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*  
One mitigated distribution per input circuit.

Each distribution sums to 1. With `nearest_probability` enabled (the default) the values form a valid probability distribution; otherwise they are quasi-probabilities that may be negative.

expectation_values*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")*  
Observable expectation values per circuit (`None` if no observables).

raw_counts*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*  
One untwirled (but unmitigated) count distribution per input circuit.

characterization*: [ReadoutErrorCharacterization](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization.html#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.ReadoutErrorCharacterization")*  
The `ReadoutErrorCharacterization` object (saveable for reuse).

metadata*: [REMMetadata](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMMetadata.html#iqm.error_reduction_tools.rem.rem_api.REMMetadata "iqm.error_reduction_tools.rem.rem_api.REMMetadata")*  
Workflow metadata.
