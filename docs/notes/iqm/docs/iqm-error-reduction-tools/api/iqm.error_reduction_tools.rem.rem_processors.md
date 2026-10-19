> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0f6b69c4e09f564ba91abec915681c15ecc2c73a794ba2c6d530fa4bd4d4068f.

# iqm.error_reduction_tools.rem.rem_processors

IQM’s Readout Error Mitigation (REM) module.

Functions

|  |  |
|----|----|
| [`estimate_counts_entropy`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.estimate_counts_entropy.html#iqm.error_reduction_tools.rem.rem_processors.estimate_counts_entropy "iqm.error_reduction_tools.rem.rem_processors.estimate_counts_entropy")(counts) | Estimate the Shannon entropy of the measurement probability distribution. |
| [`should_apply_mitigation`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.should_apply_mitigation.html#iqm.error_reduction_tools.rem.rem_processors.should_apply_mitigation "iqm.error_reduction_tools.rem.rem_processors.should_apply_mitigation")(counts\[, ...\]) | Determine whether to apply mitigation based on distribution entropy. |

Classes

|  |  |
|----|----|
| [`MitigationResult`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.MitigationResult.html#iqm.error_reduction_tools.rem.rem_processors.MitigationResult "iqm.error_reduction_tools.rem.rem_processors.MitigationResult") | Return type of [`ReadoutErrorMitigation.mitigate_counts()`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.html#iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.mitigate_counts "iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.mitigate_counts"). |
| [`ReadoutErrorMitigation`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation.html#iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation "iqm.error_reduction_tools.rem.rem_processors.ReadoutErrorMitigation")(readout_errors\[, ...\]) | Apply readout error mitigation to measurement counts, with optional twirling support. |

Inheritance

![Inheritance diagram of iqm.error_reduction_tools.rem.rem_processors](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/_images/inheritance-8479297e05f26d075baf92eeaf0863ff05b1ff1f.png)
