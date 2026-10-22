# Tuna-17 order pilot: adversarial admission

The frozen eight-setting pilot measures device-specific grouped output frequencies of ordinary complex circuits. The approved plan SHA-256 is `43e0b67a8aaaa1203eacd5f0be9e4c74ac5f4f55576dc16f96591245864dc8a2`. The pilot contains eight batches, each with two readout references and one science circuit, for 24 jobs at 16384 shots each. The circuit bytes and approved shot budgets remain fixed.

## Preregistration addendum

The pilot is **descriptive device reconnaissance**. Primary observations are raw paired-channel probabilities. The analysis reports requested and quantized native grouped predictions, signed observed-minus-predicted residuals, and total-variation residuals. These quantities supply descriptive comparisons. The experiment establishes neither representative equivalence, process fidelity, calibrated confidence coverage nor fundamental quaternionic scalar physics.

Each setting appears once, in fixed chronological order. A representative difference includes preparation, compiled-circuit effects and time-dependent device drift. Within-job shots supply repeated outcomes conditional on that acquisition; they supply no between-job replication. Contemporary all-zero/all-one references observe readout and do not isolate coherent circuit drift.

Output reference contrast at least 0.2 is an acquisition-quality guard. The guard establishes neither bias correction, precision nor agreement with a science prediction. The analysis preserves both reference one-probability vectors, their physical/logical mapping and their contrasts. A wrong deterministic science outcome can satisfy the readout guard; the report therefore sets `scientific_continuation_admitted=false` explicitly.

Lag-one and block diagnostics remain descriptive. At probability 0.25 and 16384 IID shots the nominal standard error is about 0.003383; a clustered sequence can have the same overall frequency with much larger block variability. Nominal IID intervals remain sensitivity displays. A future inferential equivalence claim needs justified margins, independent acquisition replication, a counterbalanced order and dependence-aware analysis under a separately reviewed and approved case.

Wave, Fourier and packed-drive acquisitions retain separate approvals and entry assessments. Completion of this pilot authorizes collection and descriptive analysis of its approved batches, rather than automatic scientific continuation to another family.

## Multidimensional review and resolution

| Dimension | Grounded finding | Resolution and verification |
|---|---|---|
| Scientific observables | An undefined "pilot passes" condition could turn readout quality into conformance | Descriptive scope, explicit residuals and separate continuation assessment; eight native operators are unitary to at most 5.94e-16 and have dark probabilities 0 for six controls and 0.25 for two joint-phase cases |
| Statistics and identifiability | One lexicographic acquisition per setting confounds representative and time | State the confounding, retain both readout vectors and withhold invariance/equivalence claims; repeated/counterbalanced acquisition requires a different case |
| Approval and concurrency | A manifest could change consistently during pacing between the approved-plan check and submission | Pass the frozen per-batch digest into `qi_platform.submit`; compare loaded manifest bytes under the account submit lock before creating remote resources; the pacing-mutation regression fails before the correction and passes afterward |
| Numerical and simulator conformance | Ideal algebra alone does not validate native approximation or bit interpretation | Full native operators and measurement mapping are retained; local QX and Perceval SLOS/Naive probes agree with stored laws within their respective sampling/rounding limits |
| Provider availability | Entitlement, type status, physical heartbeat and queue scope are distinct | Direct API and MCP observations agree on an offline Tuna-17 type/instance; `enabled=true` denotes entitlement. Global queue count 6 and account-only queue count 0 concern different populations |
| Shared account | Another operator can acquire between local observations | Give Claude priority, monitor the account, and enforce terminal hardware jobs plus 120 seconds from the latest finish and the account queue rule again under the submit lock |

The review read the numerical pilot and frozen settings, complete campaign analyzer and relevant submission/collection/pacing paths. Deterministic checks cover full operator unitarity, prediction grouping, changed receipt/manifests, swapped layouts, and approval changes during a simulated pacing wait. Local probes create no cloud resource.

## Execution hold and evidence

Execution waits for review closure, required validation, a fresh service availability check, and the shared-account deferral. The operator's local deferral record sets a minimum own-submission time of 2026-10-22T05:32:52.443652 UTC; the server pause and queue checks still apply afterward. A global queue estimate supplies neither a reservation nor an account-specific completion promise.

Read-only API observations at 05:16:26 UTC and MCP observations at 05:16:37 UTC on 2026-10-22 both reported Tuna-17 offline with last physical heartbeat 05:14:02.499865 UTC. Other physical-instance heartbeats advanced. The MCP source performs fresh status reads and caches only the authenticated client; the investigation reproduced a service state change rather than a status-cache defect. Every eventual submission refreshes the live state.

The API refresh at 05:30:53 UTC reported Tuna-17 executing, with account queue count zero. The preceding MCP refresh reported idle with heartbeat 05:30:12 UTC. The observations demonstrate live status transitions; execution admission still requires fresh checks after validation and the deferral.

The [operator runbook](../runbooks/hypercomplex-operator-cases.md) holds commands and approved identities. The [local simulator record](../evidence/hypercomplex-operators/local-qx-perceval.json) retains matched inputs, predictions and sampled results. The [installed-package QX crosscheck](../evidence/hypercomplex-operators/packaged-local-qx.json) records six settings at 16384 shots each through qxelarator-python313 0.10.0. The [research design](hypercomplex-operator-evidence.md) states the broader algebra and hardware boundaries. Temporary live snapshots and shared-account monitoring stay under ignored operator scratch; committed provider records omit account credentials and identifiers.
