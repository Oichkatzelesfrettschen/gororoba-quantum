> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.MitigationResult.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.MitigationResult.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7278d350f7b57b7fca2c7f772ff79db9c1fa6b4fc12c3d43372a8e005120a5ec.

# iqm.error_reduction_tools.rem.rem_processors.MitigationResult

*class* iqm.error_reduction_tools.rem.rem_processors.MitigationResult  
Bases: [`TypedDict`](https://docs.python.org/3.11/library/typing.html#typing.TypedDict "(in Python v3.11)")

Return type of [`ReadoutErrorMitigation.mitigate_counts()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.html#iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.mitigate_counts "iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.mitigate_counts").

Attributes

|  |  |
|----|----|
| [`mitigated_counts`](#iqm.error_reduction_tools.rem.rem_processors.MitigationResult.mitigated_counts "iqm.error_reduction_tools.rem.rem_processors.MitigationResult.mitigated_counts") | `result["mitigated_counts"][i][j]` is the mitigated quasi-probability distribution for circuit *i* under observable *j*. |
| [`expectation_values`](#iqm.error_reduction_tools.rem.rem_processors.MitigationResult.expectation_values "iqm.error_reduction_tools.rem.rem_processors.MitigationResult.expectation_values") | `result["expectation_values"][i][j]` is the ZZ…Z expectation value for circuit *i* under observable *j*. |
| [`characterization_performed`](#iqm.error_reduction_tools.rem.rem_processors.MitigationResult.characterization_performed "iqm.error_reduction_tools.rem.rem_processors.MitigationResult.characterization_performed") | True if auto-characterization ran during the call. |

Methods

mitigated_counts*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]\]*  
`result["mitigated_counts"][i][j]` is the mitigated quasi-probability distribution for circuit *i* under observable *j*.

expectation_values*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*  
`result["expectation_values"][i][j]` is the ZZ…Z expectation value for circuit *i* under observable *j*.

characterization_performed*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
True if auto-characterization ran during the call.
