> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 62f4c0d00769769cb2a0c321c1f5ea437b3bd1a1e98c8ba958df2635fe8d64aa.

# iqm.error_reduction_tools.rem.rem_api

High level REM (Readout Error Mitigation) workflow API.

Combines readout error characterization, circuit twirling and post-processing into a single lifecycle-oriented interface.

Typical usage:

```
from iqm.error_reduction_tools.rem import REMWorkflow, WorkflowConfiguration
from iqm.error_reduction_tools.twirling.twirling_api import TwirlingConfiguration

config = WorkflowConfiguration(shots=20_000, twirling=TwirlingConfiguration(readout_twirl_strategy="LOCAL"))
results = REMWorkflow(client, config=config).run(circuits, observables=["ZZII", "IIZZ"])

print(results.mitigated_distributions)
print(results.expectation_values)
```

Classes

|  |  |
|----|----|
| [`REMMetadata`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMMetadata.html#iqm.error_reduction_tools.rem.rem_api.REMMetadata "iqm.error_reduction_tools.rem.rem_api.REMMetadata")(timestamp, shots, ...) | Metadata about a completed REM workflow run. |
| [`REMResults`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMResults.html#iqm.error_reduction_tools.rem.rem_api.REMResults "iqm.error_reduction_tools.rem.rem_api.REMResults")(mitigated_distributions, ...) | Output of a completed REM workflow. |
| [`REMWorkflow`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.REMWorkflow.html#iqm.error_reduction_tools.rem.rem_api.REMWorkflow "iqm.error_reduction_tools.rem.rem_api.REMWorkflow")(client, \*\[, config, ...\]) | End-to-end readout error mitigation workflow. |
| [`WorkflowConfiguration`](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration.html#iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration "iqm.error_reduction_tools.rem.rem_api.WorkflowConfiguration")(\[rec, twirling, ...\]) | Configuration for the full readout error mitigation (REM) workflow. |

Inheritance

![Inheritance diagram of iqm.error_reduction_tools.rem.rem_api](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/_images/inheritance-7fffea92bd58ff03b854cacfe8785f6f22092cf0.png)
