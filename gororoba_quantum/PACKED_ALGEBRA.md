# Packed algebra experiments and independent admission

The campaign defines separate admission contracts for the static ripple and
box-kite acquisition, four-qubit rank-path sectors, and folded-QPE diagnostic.
The retained ripple and rank-sector cases have state
`historical_renewal_required`, with current admission and execution
authorization false. Renewed source-bound preparation and new written cases
must precede owner approval. Each family retains its scientific controls,
precision contract, calibration and compiled-circuit evidence.
The uniform ripple acquisition uses one static job on one backend. The
optional per-PUB allocation groups complete PUBs into homogeneous shot-tier jobs,
keeping the complete family on its selected backend. The folded
diagnostic retains twelve dynamic and four coherent PUBs in two jobs. The
coordinated 8,192-shot diagnostic has completed at 40 charged seconds; the
4,096-shot preparation is a comparison case excluded from duplicate execution.
The [independent audit](../results/ripple/folded-job-review.md) and
[hardware evidence PR #37](https://github.com/Oichkatzelesfrettschen/gororoba-quantum/pull/37)
supply the measured diagnostic results.

## Ripple acquisition

`ripple_experiments.py` constructs twelve lanes using 55 logical qubits before
routing: seven five-qubit box-kite lanes, two four-qubit walk lanes, and the
three original Design C ladder lanes of three, four, and five qubits.

The 146 explicit execution rows contain:

- 96 atlas rows, each containing one edge from each of seven box kites.
  Twelve edge blocks carry eight phases each. Edge blocks rotate across lanes;
  every edge's phase sweep binds one routed circuit object on one patch.
- Five companion duplicates that support matched A/B walk exchanges at
  depths zero through four. Each exchange preserves identical atlas neighbors.
- Eighteen isolated representative walk/edge endpoint rows.
- Twenty-four readout rows, one zero/one pair for every edge template in each
  atlas lane. The planner prepares and measures each template's actual final
  physical writer. Initial layout alone cannot determine that writer.
- Three isolated Design C primary rows. The nine original true/flip/omit
  ladder circuits share three existing atlas rows.

The fixed schedule seed shuffles matched bundles reproducibly. Sparse rows
omit inactive experiments entirely. An idle measured placeholder would alter
the neighboring workload and invalidate an isolated reference.

All walk conditions use one parameterized four-layer union template. Disabled
layers bind to zero after compilation, preserving routing and readout sites.
The shallow prefixes therefore retain the compiled template's native overhead;
their cost comes from the actual bound ISA, rather than an assumed depth ratio.
Design C retains its original builders and independent ideal laws. Distinct
ladder templates can route differently, so control comparisons retain routing
and final-readout confounds.

The contract covers the depth-four A/B crossover, individual phase
probabilities, directional bright-minus-dark effects, walk returns, labeled
ladder spectra, representative packing differences, and readout correctness.
Fringe fits and collision statistics remain descriptive. The acquisition
retains the whole shot-ordered distribution for later visualization.

Representative isolated controls measure packing residuals for their named
conditions. Their intervals cannot certify every edge or every possible
hardware crosstalk mechanism. The shared shot index permits joint-error
analysis; separate physical patches do not establish statistical independence.

## Fixed shot allocation

`--optimize --shot-allocation per-pub --shot-tiers 1024,4096` assigns complete
physical PUB rows to declared shot tiers before acquiring hardware data.
For each endpoint, the allocator first finds the smallest declared uniform
tier that passes its existing precision and conditional-power requirements.
Every contributing PUB receives at least that minimum, and matched rows share
the largest minimum among their companions.

Endpoint minima alone can lose to a uniform allocation because each active
tier adds job overhead. The allocator therefore groups PUBs by their resulting
minimum tier and enumerates every whole-group promotion to a declared tier at
or above that minimum. The search includes uniform assignments at or above
all required minima. Every alternative retains the original simulated
marginals and search-wide confidence allowance; deterministic repricing adds
zero model samples. Complete nominal and sensitivity ledgers, statistical
contracts, and per-job and aggregate ceilings qualify each alternative.

For each route, `minimum_charge` selects the feasible allocation with the
smallest worst-case nominal/scenario charge. `precision_at_budget` selects
the smallest worst normalized precision radius, then charge. The outer
optimizer revalidates one retained allocation per route. The allocation audit
retains every alternative, its PUB counts, costs and rejection reasons.
An explicit limit rejects searches exceeding 4096 assignments per route;
the search stays complete inside the declared whole-tier domain. Global PUB
allocation, packing and placement optimality remain unproved. A failed
endpoint withholds family admission.

The allocation preserves every science member, readout control, isolated row,
lane and within-PUB shot vector. Matched walk companion rows receive a common
tier and remain adjacent. Runtime 0.50 requires a separate job for each shot
value; row order is retained within a tier and changes across tiers. The
collector requires actual returned counts to match the approved allocation,
and family comparisons require compatible execution calibration. The sampling
model still assumes independent stationary repetitions within each PUB.

`record.json` retains the complete `pub_shots` mapping and allocation audit.
Its top-level `shots` is the largest allocated tier; the mapping supplies each
PUB's count. Approval checks bind that mapping and its complete job/cost
ledger. The raw archive retains every register in physical shot order. The
collection header joins measured marginals and execution evidence across tier
jobs; incomplete per-job group summaries remain labeled incomplete.

Repricing the retained planning summaries at their endpoint-minimum tiers
gives the following historical arithmetic, including two job overheads for
each static family. Fresh consolidation and admission must determine the
selected allocation and actual job count:

| Historical planning record | Model shots | Complete PUB allocation | Stress estimate (s) |
|---|---:|---|---:|
| [Ripple](../results/live/2026-10-12T062505.208379Z/record.json) | 32768 | 120 x 1024; 26 x 4096 | 68.913732608 |
| [Rank-sector](../results/live/2026-10-12T062505.552988Z/record.json) | 131072 | 15 x 1024; 21 x 4096 | 35.049098240 |

The static estimates total 103.962830848 seconds. Adding the
[corrected-source pilot](../results/ripple/CORRECTION_PREPARATION.md) stress
estimate of 14.474571264 seconds gives 118.437402112 seconds for five jobs.
The separate 4096-shot evaluation distributions remain distinct model evidence:
their replay fails one ripple endpoint and four rank endpoints. Those
distributions cannot substitute for the higher-shot planning summaries.
The historical arithmetic supplies a candidate allocation, while current
admission requires fresh calibration, complete endpoint checks, reviewed
code and digest-bound written cases.

Proposed service ceilings total 170 seconds: two 40-second ripple jobs, two
30-second rank jobs and one 30-second correction job. The user permits up to
180 seconds across the remaining acquisitions. Each family's alpha is 0.05;
a campaign-wide 95-percent simultaneous claim remains unestablished.

The grouping follows IBM's [client-side Sampler migration
guide](https://quantum.cloud.ibm.com/docs/guides/migrate-to-client-side-primitives).
Local CPU tests establish SDK handling and lossless decoding; future physical
results establish service schedules and charged time.

## Four-qubit rank sectors

The specified dimension-32 multiplication path is

```
a(t) = e1 + (t-1)^2 e10 + t(3-t)/2 e18 - t(t-1)/2 e25.
H = (0, 11, 19, 24).
input(r,j) = r XOR H[j].
output(r,j) = 1 XOR r XOR H[j].
```

Two data qubits identify a basis state inside one four-dimensional sector.
Two selector qubits implement the four signed-permutation terms. PREPARE,
SELECT and inverse PREPARE produce selector-success probability
`||L_a(t) v||^2 / (alpha(t)^2 ||v||^2)`, with
`alpha(t) = sum_s abs(a_s(t))`. The reduction preserves sector-resolved norm
observables. Cross-sector coherent observables require the larger register.

Eight four-qubit lanes evaluate four fixed probes at
`t = 0, 1/2, 1, 3/2, 2`, yielding 160 science members in twenty packed rows.
Sixteen individually isolated dark/bright reference rows bring the total to
36. Every condition in a sector binds one common seven-parameter template.
The 196 contracts cover 160 success means, sixteen packing differences, and
twenty directional effects.

The first four sectors have noncommuting Gram matrices at different parameter
values, which rules out a fixed common orthonormal singular frame. The last
four admit a constant orthonormal frame with squared-norm numerators
`0`, `4*t^2*(t-2)^2`, `(t-2)^2*(t-1)^2`, and `(t^2-t+2)^2`.
Every success prediction divides its numerator by `alpha(t)^2`.

`rank_sector_contracts.py` checks all 1,024 dimension-32 basis products against
an independent recursion, the full symbolic block identity, forty selected
four-by-four operators, all 160 bound science circuits, row occupancy, and
negative controls. Exact algebra establishes the rank statements. Finite noisy
frequencies test specified norm predictions within uncertainty; they cannot
certify an exact zero, exact rank, or the topology of the zero-divisor space.

## Time, precision, and provenance

The planner first checks compiled labeled ideal laws and predicts each
component under fresh calibration. The optimizer admits all required
endpoints together, accounting conservatively for arbitrary dependence
inside one shot and a search-wide finite-simulation allowance. Independent
stationary repetitions remain an assumption. A rejected endpoint rejects the
family; adding qubits cannot repair an unresolved statistical contrast.

The old 116-row, 1,024-shot, approximately 35-second illustration is superseded.
At the historical 250-microsecond repetition delay, 146 rows at 4,096 shots
already require 149.504 seconds of repetition delay alone. Gates,
initialization, readout, and job overhead add time. Fresh backend configuration,
compiled duration, native scheduling, and admission determine the proposed
seconds. Queue time and local preparation remain separate from QPU usage.

`--native-dry-run` reads the archived QPY circuits and calls the client-side
Runtime Sampler with `dry_run=True` for every batch. The adapter preserves the
job split, shot counts, mitigation policy, repetition delay, and execution
ceiling. Separate mock tags prevent confusion with real submission recovery.
The adapter binds record/QPY/source hashes, rechecks fresh calibration, stores
job identities before waiting, and retains native estimates and schedule CSVs.
An unavailable mock backend leaves an explicit unqualified sidecar. Randomized
mock outcomes never become physical measurements or visual data.

Native schedule duration, server usage estimate, local cost model, and final
charged usage are distinct evidence. The native report preserves total timing;
initialization and fixed-overhead components remain unseparated. Native dry
runs leave `record.json`, `isa.qpy`, and the approval marker unchanged.

All three families share the account allowance. Independently admitted cases
must also fit together with the retained campaign reserve. Every actual
submission still requires approval of its exact written case under
[AGENTS.md](../AGENTS.md), including per-job and aggregate ceilings.

## Visual interpretation

The [offline explorer](../results/ripple/cayley-dickson-ripples.html) depicts
exact local predictions. A future measured rendering can show probability
flow, phase-dependent edge darkness, exceptional-point norm suppression,
and hardware-minus-model residuals from the same retained records.
Computational-basis counts do not determine complex amplitudes. Interpolated
frames are artistic playback of separately prepared prefixes. The physical
ripple is controlled interference in the processor; mathematical geometry
and philosophical interpretation remain explicitly labeled layers.
