# Ascella transition mesh and output-port diagnostic case

The seven-job [context study](../ascella-transition-context-diagnostics/findings.md) found large
changes in several transition distributions while returned mesh and input serializations matched.
Separate job times leave packing, device drift and physical response confounded. This user-requested
successor varies compilation identifiers and output-port mappings across the same five source settings,
with repeated matched-mesh anchors to monitor coarse differences between jobs.

The [campaign](campaign.json) contains six `qpu:ascella` jobs with 22 iterator entries each:
120 fresh compilations plus twelve anchors. Each of five settings has eight independently drawn,
distinct compilation identifiers under each of three output maps. Each job carries a matched-mesh
anchor for identity input 2 and another for identity input 0, using the registered original parameter
values and compilation identifiers. Returned `computed_circuit` and `computed_input` records decide
whether an anchor or new mesh actually matches a recorded implementation.

| Output map | Physical mapping and question |
|---|---|
| Original | Preserve all twelve output ports; measure variation across compilation identifiers. |
| Logical swap | Swap physical ports 2 and 5, and ports 0 and 3; test whether identity residuals follow logical settings or physical outputs. |
| Outer swap | Swap physical ports 2 and 8, and ports 5 and 9; test the same settings on ports outside the original six-mode output subspace. |

The mappings permute rows of the complete twelve-mode operator. The case transforms the physical
output labels, active-port set and leakage set by the same bijection. The provider SDK validates
every complete requested operator before submission. All twelve physical outputs and invalid
photon-number categories remain in the retained data. A changed output map also changes the compiled
operator, so a map association alone cannot uniquely identify a detector or control mechanism.

The [seed allocation](seed-allocation.json) names one ANU quantum-random draw and one unique draw
index per new compilation. New identifiers are distinct within the cohort and exclude the previously
registered base identifiers. Repeated anchors deliberately reuse the registered base identifiers;
their purpose is reproduction. The case retains every returned mesh, reports collisions with previous
meshes and excludes duplicate returned meshes from each primary group mean. If a group returns fewer
than eight unique new meshes, its finite-cohort result is marked incomplete or colliding.

Each entry requests 65,536 accepted events and at most 131,072 detected shots. Every job has a
300-second execution stop and a ceiling of 1.131072 credits; the six-job ceiling is **6.786432 credits**.
The seven-job diagnostic's packed jobs each took 16 seconds for five settings. Scaling that observed
rate gives roughly 70 seconds per 22-entry job, or roughly 422 seconds for six jobs, excluding queue
and collection time. That extrapolation has unknown error because the port maps and compilation seeds
differ. The live runner treats `expected_seconds=300` as the conservative stop-limit compatibility
input. It checks the current offer, processor, price, occupancy and frozen request on every submission.
Before the first job, the guard requires `22 * max(singleton duration) + 60 <= 300`; every completed
intervention job must also finish within 240 seconds before a successor is admitted.

The confidence family reserves **1,876 endpoints**: 132 new observations plus two retained singleton
anchors, each with twelve physical ports, one combined invalid category and one leakage aggregate.
The 95% simultaneous Clopper-Pearson intervals assume IID accepted events within each observation.
For each setting and output map, the analysis reports the finite set of unique returned meshes,
per-mesh counts, and means with limits formed by averaging simultaneous per-mesh bounds. The analysis
reports mean total variation against each returned mesh, and, for identity settings, correct-output
and leakage fractions. No bootstrap or assumed distribution over all possible meshes enters the case.

The five source settings were selected from an earlier screening result, so this is a mechanism
diagnostic and not an independent qualification of all dimension-six transitions. Packed result
position establishes metadata attribution but does not establish physical execution chronology.
Interleaved request order, matched anchors, independent seeds and output maps improve the controls;
time, calibration, mesh and detector response can still be confounded. The result measures accepted
events, while incident source pulses and undetected-photon loss remain unknown.

The [producer and runner](../../../scripts/ascella_transition_interventions.py) bind the retained
source operators, fresh draw, prior analysis, frozen payloads and written case. The runner retains
the raw result from each job before submitting its successor. Every job requires all predecessors to
be complete and attributable; a failed result, unknown submission outcome, changed payload, price or
status stops the sequence for diagnosis. The user requested independent compiled meshes and output-port
permutations after the seven-job diagnostic; this case supplies their exact scope and credit bounds.

The later matched-mesh repeat must start on the following Pacific calendar day. A separate case will
bind its time boundary, returned-mesh identity, sampling and cost before any delayed acquisition.
The earlier 54-setting pilot failed its frozen rule and keeps that outcome; a new confirmation cohort
is required to revisit broad acquisition.
