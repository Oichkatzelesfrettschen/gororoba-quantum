# Ascella transition context diagnostic case

Five settings in the retained [dimension-six pilot](../ascella-cancellation-transition-acquisition/findings.md)
show contrasting behavior. Identity inputs 2 and 5 and Fourier-to-chirped input 4 failed their frozen
criteria; identity input 0 and Fourier-to-chirped input 0 passed. The pilot ran all settings in one
twelve-entry iterator, so the observed setting residual can include iterator context, mesh differences,
device drift and output-port response.

The user authorized seven `qpu:ascella` acquisitions in the order below. Every setting retains the
prior pilot's exact complete operator, parameter values, compilation seed and seed provenance. A seed
requests a compilation; matching returned `computed_circuit` and `computed_input` digests establishes
whether two acquisitions actually used the same recorded implementation. Every setting retains twelve
physical outputs and all invalid photon-number events.

| Job | Requested settings | Iterator entries |
|---|---|---:|
| Identity 2 | failed identity input 2 | 1 |
| Identity 5 | failed identity input 5 | 1 |
| Cross-basis 4 | failed Fourier-to-chirped input 4 | 1 |
| Identity 0 | passing identity input 0 | 1 |
| Cross-basis 0 | passing Fourier-to-chirped input 0 | 1 |
| Forward packing | identity 2, identity 5, cross-basis 4, identity 0, cross-basis 0 | 5 |
| Reverse packing | cross-basis 0, identity 0, cross-basis 4, identity 5, identity 2 | 5 |

Each iterator entry requests 65,536 accepted events and at most 131,072 detected shots. All jobs use
one photon at connected input 0, the twelve-mode 342-operation template, no mitigation, and the
one-detected-photon filter. The provider's stop limit is 300 seconds per job, or 2,100 seconds across
seven jobs. The per-job ceiling is 1.131072 credits, for a total ceiling of **7.917504 credits**.
The ceiling uses the recorded one-credit job price and the current `10^-6` price per billed shot.
The runner refreshes price, token occupancy and both processor and offer status before every submission.

The preceding same-template acquisition took 4 seconds for each singleton and 37 seconds for twelve
packed settings. A simple transfer of the per-setting packed time gives roughly 15.4 seconds per
five-setting job and roughly 51 seconds across these seven jobs, excluding queues and collection.
This is an extrapolation from a different setting mix, with unknown error. The CLI's
`expected_seconds=300` is the conservative stop-limit compatibility input, rather than that forecast.
Before each packed job the guard requires `5 * longest preceding completed job duration + 60 <= 300`.
Incomplete, failed, unattributable or over-limit predecessors stop the sequence. Scientific failure
is data and does not by itself stop the remaining controls.

The frozen confidence family includes the five previously observed pilot settings and the fifteen
new observations. For each of the twenty observations it reserves twelve physical-port categories,
one invalid category and one leakage aggregate: **280 endpoints**. Simultaneous 95% Clopper-Pearson
intervals condition on IID events within each setting. Report the total-variation point estimate and
conservative simultaneous lower and upper bounds for prior versus singleton, singleton versus forward,
singleton versus reverse, and forward versus reverse. Report leakage differences with simultaneous
intervals. A matched-mesh interpretation requires matching returned mesh and input records; otherwise
the comparison remains descriptive and its matched-mesh verdict is inconclusive.

Requested iterator position binds returned setting metadata, but the provider result does not record
physical timestamps for individual packed iterations. A forward-versus-reverse difference can motivate
investigation of request context; the comparison does not establish physical execution order or causality.
The singleton jobs and packed jobs occur at different times, so temporal variation and calibration may
confound context. Accepted samples condition on detected events; incident-pulse loss remains unmeasured.

The [campaign](campaign.json) binds the source manifest and exact seven successor payloads. The guarded
runner creates only the next case under the retained-run directory, compares its current provider body
against the preflight apart from Perceval's validated process UUID, and checks earlier retained receipts.
The raw provider result is collected before each successor job. A changed payload, price or live status
refuses submission. The [source script](../../../scripts/ascella_transition_context.py) and its focused
tests implement construction, result attribution and the confidence bounds.

Independent compilation, physical-port permutations and a matched-mesh repetition on the following
Pacific calendar day answer additional questions and require their own source-bound acquisition cases.
The earlier pilot's failed qualification remains unchanged; a new confirmation cohort is required
before considering the full 54-setting campaign.
