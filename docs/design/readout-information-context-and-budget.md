# Paired readout errors under controlled actor preparation

This unapproved IBM design asks whether changing preparation on disjoint actor
qubits changes fixed reporters' error response, and whether a pair's
computational-basis parity error beats its cleaner individual bit by a frozen
margin. Preparation, gate, readout, reconstruction and drift errors all enter
the observed channel; a result does not identify a unique physical cause.
The information-order calculation below is a separate classical research
control, not a primary endpoint of the proposed IBM acquisition.

The [OpenAI mathematics collection, family 119](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/119.md)
describes the Courtade–Kumar information-contraction result for uniform inputs
and independent symmetric bit-flip noise. The collection labels its outputs
research data with varying verification. The two-bit controls below stand on
their own finite calculation; a QPU measurement neither proves nor disproves
the general mathematical statement. The original question predates the
collection: [Courtade and Kumar (2013)](https://doi.org/10.1109/ISIT.2013.6620221).

## Exact model and mutation

Let X be two independent uniform input bits and Y the full two-bit output.
Let F be the XOR of the two inputs. The baseline model independently flips
each bit with probability p = 1/4. Its two coordinate information values are
`1-h2(1/4) = 0.1887218755` bits, and its parity information is
`1-h2(3/8) = 0.0455659971` bits. Here `h2` is binary entropy.

The positive mutation flips both bits together with probability 1/4 and leaves
both unchanged otherwise. Each one-bit flip marginal stays 1/4, while parity is
always preserved: the coordinate information stays `0.1887218755` bits and
the parity information becomes 1 bit. The
[finite-channel control](../../scripts/readout_information_controls.py)
enumerates the exact rational probabilities and independently checks the
entropy identities. The example is a mathematical sensitivity control, not a
prediction that a device has a 25% readout error.

An observed positive value of
`I(F;Y) - max(I(X0;Y), I(X1;Y))` contradicts the independent symmetric-channel
model when input distribution, association and uncertainty assumptions hold.
The contrast includes preparation and measurement. Equal one-bit marginals do
not establish independent errors, and a negative or unresolved contrast does
not establish that a channel is independent. Noise context, input imbalance,
time drift and output-label mistakes remain alternative explanations.

## Proposed acquisition and falsifiers

### Fixed reporters and changing actors

The first IBM candidate holds reporter preparation and the measured register
fixed while changing activity on disjoint actor qubits. A controlled assignment
must be randomized at the unit the provider actually executes, with assignment
probabilities and carryover assumptions retained. Counterbalancing alone does
not identify a causal effect. If assignment or exposure is not qualified, the
result is an activity-associated response contrast. Equal measurement
instructions do not establish identical physical readout pulses; served
schedule evidence and its limits belong in the admission record.

Before discovery, freeze shot validity, candidate eligibility, input patterns,
selection, assignment, the maximum number of pairs, decision rules and the
error budget. Freeze selected pairs and any trained predictor after discovery
and before confirmation data are opened. A later acquisition can test
persistence; concealed data from the same acquisition supports a holdout but
does not by itself establish persistence. IBM does not guarantee PUB order or
one batch, so a later list entry is not proof of later physical execution.

For output bits compared with their commanded preparation, let `p_ab` be the
probability of paired error bits `(a,b)`. The parity improvement over the
better individual bit is `G = min(p_11-p_01, p_11-p_10)`. A per-pair
intersection-union decision requires both one-sided tests to clear a frozen
practical margin; the family of pairs and other claims needs its own error
allocation. The two component tests do not themselves require an additional
division of the per-pair level. A failure to reject is inconclusive, not
equivalence. A separate upper-bound test and frozen equivalence region support
an equivalence decision.

Write `s = p_11`, `r = p_01 + p_10` and `d = p_01 - p_10`. Then
`G = s - r/2 - |d|/2`. A context comparison must report the change in `G`,
parity error `r` and each marginal error together. Additional simultaneous
errors can increase `G` while leaving parity error unchanged and worsening
both individual bits. These descriptive quantities need separate registered
uncertainty and multiplicity rules before supporting confirmatory claims.

For error signs `Z_i = (-1)**E_i`, `G` equals
`(E[Z_i Z_j] - max(E[Z_i], E[Z_j])) / 2`. Under the specific model
`E_i = B xor U_i` with mutually independent common and private flips, even
group parity signs cancel `B` and odd group parity signs retain it. The model
also implies `E[Z_1 Z_2 Z_3] = E[Z_1] E[Z_2 Z_3]`, and the two analogous
permutations. These equations are falsifiable model restrictions; agreement
does not identify a physical mechanism. A fourth cumulant is likewise not a
four-body mechanism identifier: four copies of a shared Bernoulli error have
fourth cumulant `p(1-p)(1-6p(1-p))`, including zero for nontrivial values of
`p`. A Cayley-Dickson claim additionally needs the separate sign mutation and
interference test.

For fixed marginal error probabilities, `G <= 2 p_min - p_max`, attained by
the maximally shared joint distribution. Consequently, `G > delta` requires
`p_max + delta < 2 p_min`. An empirical estimate is not a population bound;
candidate screening must account for estimation uncertainty. The
`parity_error_summary` calculation returns exact fractions from decoded shot
bits and is descriptive. It supplies neither confidence bounds nor an
admission decision. Input patterns remain separate unless a preregistered
pooled estimand is justified.

An illustrative one-sided Hoeffding intersection-union bound for a fixed-size
IID sample uses the fact that each component
has a per-shot difference in `[-1,1]`, and the common radius is
`sqrt(2 log(1/alpha)/n)`. The lower bound for `G` is the smaller of the two
component lower bounds. This construction controls one pair at its declared
level, not a family of pairs. For 100,000 shots with 3,000 joint errors and
500 of each isolated error, `G_hat = 0.025` and the 5% illustrative lower
bound is approximately 0.0173. The hypothetical frequencies are not hardware
predictions. The arithmetic appears only in a test, not an exported analyzer
or CLI result. Its IID and fixed-completion assumptions need evidence and
independent review. One exact finite-sample boundary-null enumeration is a
checked example, not a proof of least favorability over the composite null.

For one pair at one-sided alpha 0.05, the same radius is approximately
0.0173 at 20,000 shots. If the smaller marginal error is 0.01, the population
feasibility bound limits `G` to at most 0.01. The illustrative Hoeffding
construction therefore cannot certify a positive improvement at that sample
size when the sample marginals also obey the 0.01 cap. A valid sharper paired
method might have useful power; a realistic case must establish that with its
own assumptions, multiplicity, marginal ranges and shot budget. The existing
[empirical Bernstein contract](../../gororoba_quantum/QPU_OPTIMIZATION.md)
belongs to other registered families and does not automatically admit this
case. For a paired score with range 2, sample variance 0.02, 20,000 shots and a
one-sided tail 0.05, the full stated radius is approximately 0.00358, including
the range-dependent correction. At 8,192 shots it is approximately 0.00635.
These are hypothetical fixed-variance calculations before multiplicity or
power allowances, not a claim that a 0.005 effect is resolvable. A future
analyzer needs separate score variances, an independently reviewed coverage and
sampling contract, numerical outward rounding and fail-closed admission. A
choice between empirical Bernstein and another interval needs a prespecified
method and appropriate error allocation.

The case retains shot order, preparation, actor assignment, block identity,
mapping and available timing alongside joint counts. It specifies dependence
assumptions and uses inference justified under them. A purge window, alternating
shots, or a sequential method alone does not establish independence. Each
endpoint reports one of invalid acquisition, inconclusive, confirmed effect,
or bounded equivalence. A diagnostic burst search has its own exposure and
requires measured wall-clock timing for rate claims.

1. Freeze the reporter-pair candidate universe, calibration-based eligibility,
   physical mapping rule, actor set, input patterns, allocation and validity
   rules before discovery. Freeze selected reporter pairs before confirmation.
2. Build `actor_alternatives` for each chosen input and fixed measured register.
   Randomize actor assignment at an execution unit whose ordering and identity
   the provider exposes. Retain assignment probabilities and predeclare
   carryover assumptions. Compare compiled arm duration and reporter exposure;
   an unresolved mismatch remains a confound.
3. Retain complete joint outcomes, input and actor assignments, calibration,
   block identity and all available timing. Decode error bits against each
   commanded preparation and calculate `G` separately by input and context.
4. Freeze the actor response and paired parity decisions, including practical
   margins, multiplicity, selection, dependence and confirmation rules. A
   missing input stratum, ambiguous order, changed map or failed reference makes
   the affected claim inconclusive. Calibration and repeated shots do not alone
   prove stationarity or independent observations.

The classical information-order positive mutation remains an exploratory
model check. Any fixed bijection on the full output preserves all three mutual
information values and is an invariance check, not a negative control. An
independently assigned source/outcome association permutation or an explicitly
specified dependence-breaking channel, changed input weights, and a preparation
fault are separate alternatives; their allocation and any randomness require
the repository's recorded quantum-random source. A held-out confirmation and a
justified error bound are prerequisites for a device claim; this design does
not supply a completed uncertainty method.

The [logical circuit catalogue](../../scripts/readout_information_circuits.py)
constructs both contexts and all four inputs for a selected target pair and
measures every register bit. The catalogue is not an execution schedule or a
native case: it chooses neither physical layout nor assignment order, timing,
calibration, or provider. Ideal-state tests verify target preparation and
full-register mapping on a small statevector and check all 156 logical bits
structurally; they do not simulate a 156-qubit device. A source-bound provider
case must add the missing allocation, compilation, ordering, cost and
uncertainty controls.

The same catalogue's `actor_alternatives` constructs all four reporter inputs
with a specified, disjoint nonempty set of actor qubits either unexcited or
prepared with `x`, and measures the entire logical register in every arm.
The preparation intervention changes actor state as well as drive activity.
The constructor selects no physical layout, assignment order, repetitions or
timing; equal compiled duration and equal physical measurement pulses are
unverified. It is an unapproved source catalogue, not a randomized case.
The separate `padded_actor_alternatives` accepts per-qubit X durations in
ticks and pads each preparation to the maximum selected duration. It requires
caller-supplied durations and selects no physical layout. Native compilation
and provider scheduling remain independent checks.

The separate [IQM native-source catalogue](../../scripts/readout_information_iqm.py)
constructs the same unassigned preparations using `prx` angles in radians and a
single ordered measurement locus. Its tests compare every preparation with the
logical catalogue. The native-source catalogue has no job body, shot count,
randomized schedule or approval, and its tests do not establish provider
compilation or execution. A 28 October read-only Garnet dynamic-architecture
observation listed 20 qubits and single-qubit `prx` and `measure` loci for all
20. That observation does not establish that a 20-qubit measurement is admitted
as one joint operation or that a particular case fits the 2.50-credit limit.

The classical control module also computes descriptive plug-in information
from four nonempty integer-count rows, weighting each input stratum by one
quarter. The tests reconstruct both exact synthetic channels. Reweighting does
not randomize the actual acquisition order, correct drift, authenticate source
association or provide confidence bounds; no retained device result enters
this calculation without a separate acquisition and analysis contract.

An illustrative, conservative 99% simultaneous information-order bound for a
fixed number `n` of completed observations in each input stratum
and context. For one pair, a union bound covers 32 output-cell events. If each
cell indicator has a predictable conditional mean and the stratum membership
and fixed sample schedule satisfy the martingale assumptions, the two-sided
cell radius is `sqrt(log(6400)/(2n))`. For uniformly weighted inputs, the
corresponding joint total-variation radius is at most twice that cell radius,
capped at one. Entropy continuity for the four-output and eight joint outcomes
then bounds each information error; twice their sum bounds the error of the
parity-minus-maximum-coordinate contrast. The predictable target is the
realized average of conditional probabilities, which can vary with history; it
is not automatically a stationary channel or a causal context effect.

At 20,000 observations per stratum the computed contrast radius is about 1.03
bits, larger than the largest possible one-bit contrast. This particular bound
therefore cannot certify a positive contrast at that sample size. A sharper
justified method or multiple fixed-size blocks could change the result. The
test-only calculation illustrates feasibility; it does not provide an
outward-rounded admission decision, correct confounding, or justify stopping
based on observed outcomes. The fixed completion, ordering, multiplicity and
predictability assumptions need independent review before any device claim.
The continuity and concentration ingredients are described by
[Audenaert](https://doi.org/10.1088/1751-8113/40/28/S18) and
[Hoeffding](https://doi.org/10.1214/aop/1176996452).

A read-only IBM Target query on 28 October 2026 found 156 physical qubits on
`ibm_kingston`, with `x` and `measure` supported on each qubit. That observation
qualifies neither a logical-to-physical mapping nor a served schedule, duration,
or future calibration. The current logical catalogue has one selected target
pair per source; simultaneous multiple-pair coverage requires a separately
specified input assignment and covariance contract.

An offline preliminary layout uses reporters 0 and 1 and actor 2. The retained
Kingston snapshot's 14 October 2026 calibration lists coupling edges 0-1 and
1-2 and readout-error metrics 0.0126953125 and 0.0084228515625 for reporters
0 and 1. Those metrics do not establish the error-bit marginals under the
candidate intervention. A local Qiskit `optimization_level=0`, ALAP schedule
using a reconstructed 156-qubit Target containing only the snapshot's `x`
and `measure` instructions and an identity layout places all measurements at
tick 0 for the idle `00` arm and tick 8 for every other arm; the snapshot has
4 ns ticks. The 32 ns discrepancy is a concrete source-level schedule
confound, not evidence about served pulses. The offline
[schedule replay](../../scripts/readout_actor_schedule_replay.py) rebuilds the
restricted Target from the retained snapshot, prints the snapshot digest and
the replay and constructor source digests, checks compiled X preparations and
measurement mapping, and reports padded and unpadded schedules under ASAP and
ALAP. The stdout is a diagnostic, not a retained byte-checked receipt; the
restricted Target omits the full provider Target and scheduler. A complete
fresh Target, compilation and readout evidence remain required before physical
admission.

A read-only primary-account query at 2026-10-28 18:41 UTC reported 68 rolling
seconds, Kingston active with 42 queued jobs, and a configured 0--2 ms
repetition range. The separate Heron published 20 microsecond floor still
applies. A full live Target read at 18:42--18:43 UTC reported `dt = 4 ns`,
32 ns X, 2.180 microsecond measurement and 2.212 microsecond reset on every
one of its 156 qubits, with calibration timestamp 2026-10-28 17:56:30 UTC.
For reporters 0 and 1 and actor 2, local level-zero compilation with identity
layout placed the unpadded `idle 00` measurement at tick 0 and the other seven
at tick 8. With per-qubit padding derived from that Target, both ASAP and ALAP
placed every measurement at tick 8 and the last measurement end at tick 553.
These local observations have no retained replay producer or digest and do not
establish a provider-served schedule, physical pulses, initialization or
carryover. A new case must bind its own full Target and compilation evidence.

## Two-reporter qualification case

The first candidate qualifies the three-qubit reporter/actor source and its
sampling and cost contract for a later array. An activity contrast on reporters
0 and 1 is a device-specific secondary observation; this candidate neither
qualifies the remaining qubits nor establishes an array-wide effect. A successful
qualification permits writing a separately approved confirmation case; it does
not authorize that case, establish IID shots, or establish a physical mechanism.

The proposed 20-second ceiling covers the complete qualification program,
including a delay-selection pilot, discovery, reference circuits and any
confirmation jobs. A delay is frozen before confirmation. A hardware pilot that
chooses a delay needs its own written case and approval, and its charge consumes
the same total ceiling. If all stages cannot fit, the qualification stops
instead of removing controls after acquisition.

| Allocation per input and actor arm | Shots | Executions over eight conditions | Status |
|---|---:|---:|---|
| Delay-selection pilot | Unspecified | Unspecified | Required only when choosing the delay from hardware data; separately approved and charged |
| Discovery | 10,000 | 80,000 | Proposed, not frozen |
| Confirmation | 30,000 | 240,000 | Proposed, not frozen; per-condition precision uses 30,000 shots |
| Initialization and carryover references | Unspecified | Unspecified | Their design, sampling and charges remain open |
| Combined science allocation | 40,000 | 320,000 | Discovery plus confirmation only; excludes pilot and references |

The initialization model distinguishes three operations. `rep_delay` is the
runtime wait between executions. Runtime `init_qubits` requests implicit
initialization; IBM's local estimator models that request by adding one Target
reset duration per execution. An explicit reset instruction in a submitted
circuit is a separate operation and enters the scheduled circuit duration.
The present source catalogue contains no explicit reset. A Target reset's
duration is an estimation input, not evidence that the service implements
initialization as that exact physical reset or that initialization is adequate.
The exact submitted options, compilation and returned timing must establish
which operations can be observed; unsupported physical details remain unknown.

Qualification decisions bind a frozen constructor, analyzer, calibration,
assignment, validity and sampling contract:

- **Pass:** all mandatory compilation, mapping, timing, accounting and raw-data
  checks pass; every declared initialization and carryover equivalence interval
  lies within its own preregistered tolerance; and the full program remains
  within its approved ceiling. The separately justified inference assumptions
  still bound the conclusion.
- **Fail:** an observed mandatory timing or mapping mismatch, or a valid
  uncertainty interval entirely outside a declared equivalence region, rejects
  the corresponding qualification. A failed control does not identify the
  physical cause.
- **Inconclusive:** missing ordering, data, calibration identity or a valid
  uncertainty interval crossing a threshold withholds the decision. A
  nonsignificant difference alone never qualifies equivalence.

No numerical carryover tolerance, minimum detectable improvement, statistical
family, actual randomization unit or reference allocation is currently frozen.
A production analyzer must validate the versioned contract, exact candidate
and analysis digests, assignment and raw-acquisition evidence before issuing
any verdict. A Boolean assertion of independence is not evidence of independence;
unverifiable dependencies withhold the confirmatory verdict. The current code
returns descriptive error tables only. The candidate cannot yet be frozen or
submitted.

For eight conditions at 40,000 total shots each, a provisional cost model adds
the observed 2.212 microsecond compiled circuit and one 2.212 microsecond reset
per execution to the requested repetition delay. Using IBM's approximate two
seconds per sub-job gives the following scenarios:

| Repetition delay | Execution terms | One sub-job | Two sub-jobs |
|---|---:|---:|---:|
| 30 microseconds | 11.016 s | 13.016 s | 15.016 s |
| 50 microseconds | 17.416 s | 19.416 s | 21.416 s |

The scenarios assume the locally scheduled duration, simultaneous reset cost,
320,000 executions and no additional reference or pilot executions. They are
estimates rather than upper bounds. The provider controls sub-job splitting,
and initialization, mitigation, reference programs, pilot, scheduler and
other overhead may add cost. Neither scenario is admitted under a 20-second
ceiling without a complete fresh dry run and defensible margin. Under the
two-sub-job scenario, 30 microseconds leaves approximately 4.984 seconds for
all omitted qualification costs and uncertainty, while 50 microseconds
already exceeds 20 seconds by approximately 1.416 seconds. These differences
are arithmetic against the model, not available budget guarantees.
The [exact scenario calculator](../../scripts/readout_actor_cost_model.py)
requires explicit execution counts for pilot, discovery, references and
confirmation, and adds the declared sub-job overhead. Zero means a stage has
no executions in that scenario; it is not evidence that an unallocated stage
is unnecessary. The calculator uses exact nanosecond arithmetic and makes no
provider charge or admission decision. Its single per-execution duration is
valid only for a scenario where every declared execution uses that duration;
different reference circuits require separately accounted scenarios.
Its `estimate_mixed_cost` accepts separate execution counts and repetition,
circuit and initialization durations per batch within every stage, so a delay
pilot and longer reference circuits can enter one scenario. The caller still
declares sub-job count and overhead; the result is not a provider guarantee.
Distinct repetition delays require at least one sub-job each. Shot tiers,
stage boundaries and provider splitting can require additional sub-jobs; the
calculator does not infer a job manifest. A retained case must bind the exact
input allocations, durations and their provenance alongside the estimate.

### Runner and sampling integration gates

The source catalogue is not registered as an IBM execution family. The
approved-run wrapper binds `live_run.py`; it cannot submit this catalogue as a
case without a new registered construction and analysis path. The runner's
experiment digest covers its declared source manifest, not the new scripts
automatically, so a case must bind every constructor, analyzer and cost
dependency explicitly. The runner groups PUBs by shot count; different
discovery and confirmation tiers can produce separate jobs and overhead.

The runner currently forms dense distributions indexed by all classical bits.
A 156-bit member would require an array of size `2**156` and cannot use that
path. A practical implementation needs validated small-component packing with
the intended full measurement footprint or a separately reviewed sparse
full-shot path. The preferred path retains the complete aligned shot record
from one full-register PUB and projects only declared small outcomes. The
current `collect` path writes raw registers first but subsequently calls the
dense distribution conversion; the legacy adjudicator also narrows full
bitstrings to `int64`. Both paths need an explicit case-specific sparse
branch before they can process a 156-bit case. The current full-register
barrier also crosses the disjoint ownership required by the existing packing
and archive validators, so simply wrapping it in a packed group is insufficient.
An independently bound receipt must protect the raw index as well as its files.
The current [ownership regression](../../tests/scripts/test_readout_barrier_ownership.py)
shows that component-local barriers pass, while the validator rejects both a
cross-component synchronization barrier and a cross-component CZ. A future
versioned validator must distinguish those operations without discarding the
synchronization barrier or weakening the rule for computational gates.
The case must check its required synchronization against compiled and served
schedule evidence; source instruction order alone is insufficient.
Ordered raw bitstrings within one PUB do not establish the
immediately preceding physical circuit in a mixed-PUB job: the provider does
not guarantee PUB order or a single batch, and retained execution windows need
not be per-shot times. Missing predecessor evidence withholds any claim that
requires it.

| Stage | Observed execution path | Sparse-case obligation |
|---|---|---|
| Construction | The logical catalogue builds one full-register circuit; it does not register an execution family. | Bind the constructor, physical layout, preparation and global-barrier ownership to an approved family. |
| Planning and submission | Existing group and simulation machinery expects component distributions; the approved-run wrapper only submits registered `live_run.py` cases. | Avoid dense ideal and noise paths for the full register, or prove a compatible representation; bind the exact QPY and source closure. |
| Raw serialization | `write_raw_result` retains each PUB register's ordered bitstrings, metadata and file digests before analysis. | Bind the index itself to a trusted receipt, plus PUB identity, register names, widths, counts and measurement map. |
| Collection and adjudication | Standard collection calls `_distribution`, which allocates `2**clbits`; legacy `adjudicate.bit_values` converts complete strings to `int64`. | Project declared bits before either conversion and preserve the original full shots. |
| Inference | The current paired helpers return descriptive values. | Validate assignment, ordering, sampling and multiplicity evidence before a separately reviewed analyzer issues a decision. |

Projecting multiple components from the same full-register shot preserves the
supplied same-index relationship. Separate component acquisitions cannot
establish simultaneous cross-component failure. Equal list lengths are a
structural check, not independent proof that the provider aligned registers.
The receipt must connect the independently approved submission identity and QPY
digest to the actual job and PUB, register and measurement map, preparation,
raw index and file digests. A receipt recomputed from the same untrusted
manifest establishes internal consistency only. Provider-result alignment
requires a documented contract or supporting evidence beyond those hashes.
`snapshot_metrics` updates the raw index as metrics arrive, so a receipt that
binds an index must name the exact indexed snapshot and its lifecycle; an
earlier index digest cannot authenticate a later rewrite.
`write_raw_result` writes a separate `acquisition-index.json` containing the
job identity and raw PUB and result-metadata hashes. Atomic create-once
publication rejects a different existing snapshot. The raw result files use
the same create-once publication, and a per-job advisory lock serializes raw
collection and metrics updates. Concurrent identical collectors preserve the
same indexed bytes; a conflicting collector refuses the existing raw file.
Metrics revisions continue through the existing index and cannot alter those snapshot bytes. The snapshot
is also written by `preserve_raw`, whose weaker checks do not authenticate a
submission. An admitted analysis receipt still needs to bind that snapshot and
selected metadata revisions to the independently trusted submission and
collection anchors. Recomputing the expected digest from mutable files would
establish consistency only. That trusted receipt lifecycle remains unintegrated.

The local `project_reporter_shots` helper projects ordered single-register
Qiskit bitstrings onto two specified classical-bit indices without constructing
a `2**156` distribution. It rejects malformed or oversized input and preserves
the supplied list order, up to one million shots and 100 million input
characters per call. The helper does not authenticate the source register,
physical mapping, provider timing or predecessor identity, and is not wired
into the IBM collector or an admitted acquisition case.

The separate [sparse PUB projection](../../scripts/readout_sparse_projection.py)
accepts complete declared register, classical-bit, logical-bit, physical-bit and
preparation maps, validates equal register lengths and bitstrings, and computes
only declared pair error tables and group error-parity counts. It pairs list
positions from one PUB without mutating the full input. Its ordered register
hashes and manifest digest describe the supplied data; neither authenticates a
provider response or proves physical cross-register alignment. The projection
is not wired into collection, QPY validation or confirmatory inference.

The offline [receipt verifier](../../scripts/readout_sparse_receipt.py) checks a
caller-supplied receipt digest, the bound bytes and the QPY measurement wiring
before projecting. The receipt's `manifest_sha256` binds the original JSON
bytes; the projection's `manifest_canonical_sha256` binds a canonical JSON
serialization. The verifier returns the former as `manifest_bytes_sha256`.
The verifier checks neither the active actor's gates nor preparation semantics,
approval or provider provenance; its family label is supplied by the caller.
QPY byte limits and decoded-size checks do not bound the decoder's peak
resources, so QPY input needs an independent trust and resource boundary.
The verifier has no production collection or adjudication route and issues no
statistical decision.

A separate synthetic probe of input construction, serialization, JSON and QPY
parsing, receipt checking and projection used 180,345 shots across two
registers totaling 156 bits, one pair and one group. Python 3.14.7 and NumPy
2.5.4 reported cumulative peak RSS of 98,744 KiB initially, 149,096 KiB after
input construction and 206,824 KiB after serialization, verification and
projection. The raw JSON occupied 29,576,760 bytes and elapsed time was 0.34 s.
The synthetic receipt and its anchor share an origin; the probe measures
consistency and local resource use, not provenance or provider collection.

A deterministic local probe of 180,345 distinct 156-bit strings, one pair and
one three-bit group used 29,035,545 declared work units. On Python 3.14.7 and
NumPy 2.5.4, process high-water RSS was 70,160 KiB after constructing the
input and 73,264 KiB after projection, an observed increase of 3,104 KiB; the
projection took 0.064 s. The observation excludes raw JSON loading, provider
collection, input construction and larger projection families. High-water RSS
is not an exact allocation, and the work cap is not a universal memory or
runtime guarantee.

A separate local probe includes creation of 180,345 distinct strings, JSON
serialization and `json.loads` before projection. On Python 3.14.7 and NumPy
2.5.4, process high-water RSS was 31,716 KiB initially, 70,244 KiB after input
construction, 126,180 KiB after serialization, 126,180 KiB after parsing, and
127,252 KiB after projection. The JSON payload was 28,674,957 bytes; total
elapsed time was 0.254 s. High-water readings are cumulative, and Python's
allocator can retain freed input memory. This test includes synthetic parsing
but not provider collection, QPY parsing, receipt validation or real results.

```sh
"$PYTHON" - <<'PY'
import resource
import sys
import time
sys.path.insert(0, "scripts")
from readout_sparse_projection import project_pub
width, shots = 156, 180345
raw = {"pub_name": "wide", "pub_index": 0, "registers": {
    "c": {"num_bits": width, "num_shots": shots,
          "bitstrings": [format(index, "0156b") for index in range(shots)]}}}
manifest = {
    "schema": "readout-sparse-projection-v1", "condition": "wide-ground",
    "pub_name": "wide", "pub_index": 0, "registers": {"c": width},
    "bits": [{"register": "c", "index": index, "logical": index,
              "physical": index, "prepared": 0} for index in range(width)],
    "pairs": [[0, 155]], "groups": [[0, 1, 155]],
}
before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
start = time.perf_counter()
result = project_pub(raw, manifest)
elapsed = time.perf_counter() - start
after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print("shots", result["num_shots"], "work", result["work_units"])
print("peak RSS KiB before/after", before, after, "seconds", elapsed)
PY
```

For error-cell order `00, 01, 10, 11`, the two paired component scores are
`(0, -1, 0, 1)` and `(0, 0, -1, 1)`. Each uses the same joint shots but its
own variance and one-sided lower bound; their minimum tests the margin `G`.
`paired_component_moments` computes the two means and `n-1` sample
variances and covariance exactly from a four-cell table. Their usual
unbiasedness for population moments assumes IID sampling; dependence can
invalidate it. The function supplies descriptive
moments only: it authenticates neither the table nor the sampling assumptions
and returns no confidence interval or confirmatory decision.
Existing empirical-Bernstein machinery is registered for other families and
assumes stationary IID shots within each PUB. Its planning path also accounts
for uncertainty in a modeled variance. A numerical radius at a hypothetical
variance is not a power calculation. Any extension to independent but
non-identical observations needs its own reviewed estimand and contract; none
of these assumptions permits arbitrary dependence. Power for both component
inequalities must account for failures of both, while multiplicity across
selected pairs and other claims remains separate.
The two component scores share outcomes: their population covariance is
`p_11 - (p_11-p_01)(p_11-p_10)`. With the two score means `mu_1` and
`mu_2`, the covariance `c` determines `p_11 = c + mu_1 mu_2`,
`p_01 = p_11 - mu_1`, `p_10 = p_11 - mu_2`, and normalization determines
`p_00`. Covariance alone is insufficient, but the means and same-shot
covariance identify this four-cell law. For empirical data, the unbiased
sample covariance uses denominator `n-1`, so the reconstruction first
multiplies it by `(n-1)/n`. Exact cell counts avoid that normalization and
retain the joint outcome distribution directly. Joint power still requires
the case's shot model and the joint law; the algebraic identity establishes
neither independence nor physical shot alignment. A conservative
joint-power lower bound from component miss-probability bounds needs no
independence between the two scores, but still needs a justified shot model
for each component.

For 30,000 confirmation shots per condition, range 2 and one-sided alpha 0.05,
sample variances 0.005, 0.02 and 0.05 give illustrative empirical-Bernstein
radii 0.001683, 0.002792 and 0.004080, respectively, before multiplicity.
An observed lower bound above a practical margin also requires a sufficiently
large realized improvement: at sample variance 0.02 and a 0.0035 margin, the
observed `G` must exceed approximately 0.006292 for that illustrative radius.
The two component scores may have different sample variances; a future test
must compute both bounds before taking their minimum. The radius alone does
not establish power. The
10,000/30,000 split, candidate count, conditions requiring precision, margin,
randomization and simultaneous family remain unapproved design choices.

Delay qualification is a separate acquisition if hardware observations choose
between 30 and 50 microseconds. A proposed qualification reads, for each frozen
reporter and preparation pattern, the difference in next-shot error probability
conditional on the previous observed reporter error, and requires a simultaneous
interval entirely inside a prespecified practical equivalence region. The
criterion requires established predecessor identity and a justified dependence
model; unavailable ordering, an interval crossing the region, or missing strata
returns inconclusive. Marginal initialization references alone do not establish
temporal independence. The tolerance, method and required exposures are not yet
frozen, and neither delay is declared scientifically superior.

The proposed 20-second IBM ceiling is a design target, not an allocation or a
confirmed runtime. Eight conditions at 8,192 total shots each and an assumed
250 microsecond repetition delay consume 16.384 seconds in repetition delays
alone; discovery and confirmation must share those shots or add their cost.
Eight conditions at 20,000 shots and 100 microseconds consume 16 seconds in
repetition delays alone. Both arithmetic examples exclude circuit duration,
reference controls and other overhead. The shorter delay also changes the
initialization exposure and needs its own controls and fresh backend range.
The 28 October balance observation does not establish today's quota.

## Provider-specific envelopes

The IBM row contemplates the paired-error endpoint. The IQM information-order,
IQM driven-idle, Open Quantum and Ascella rows are separate questions or
provider candidates requiring their own cases and admission.
The balances below are ephemeral read-only observations on 28 October 2026;
the query identities were not retained. Refresh and retain a sanitized,
timestamped account and backend snapshot before admission.

| Candidate | Working objective | Live balance observation and remaining admission |
|---|---|---|
| IBM Heron | Large-register target-pair and spectator-context test with fresh Target-derived physical maps and ordered joint outcomes | Primary account reported 68 seconds remaining on 28 October. Compile, estimate the full batch including overhead, prove the map/order and fit the approved limit. |
| IQM Garnet | 20-qubit information-order candidate | Account reported 2.50 credits, expiring 31 October 2026 at 17:00 Pacific. Garnet charges 0.50 per billed second; server-side credit cap is unavailable. |
| IQM Garnet, separate follow-up | Matched driven-versus-idle successor to the retained schedule discrepancy | The follow-up shares the same 2.50-credit balance and needs its own intervention, estimand, controls and case. |
| Open Quantum Rigetti | Separate, unapproved larger-register candidate; retain unpublished work outside Public Compute | Account reported 25 Spark credits. Public Compute publishes uploads and results; fresh native admission and exact cost precede any upload. |
| Quandela Ascella, separate follow-up | Same target optical mesh after randomized high/low programmed predecessor, with anchors | Platform reported available; account-wide remaining credit is unverified. Served iteration order and fixed target compilation must be demonstrated. |

IQM bills each job at `ceil(runtime_seconds) * rate`, where runtime includes
server compilation and execution. The observed rates imply at most 5 whole
billed seconds on Garnet, 3 on Emerald, or 8 on Sirius for 2.50 credits, before
allowing any margin. A previously measured 24-circuit Garnet job cost 1 credit,
but its 1.92-second runtime does not bound a new circuit's runtime. The
[idle schedule study](iqm-garnet-idle-schedule-train-readout.md) found excess
spectator decay and measured parallel versus isolated trains; the successor must
hold spectator preparation, duration and measurement fixed while comparing the
train intervention and include controls for initialization and actual schedule.
The server lacks a hard per-job credit cap; cancellation can race billing. The
strict 2.50-credit ceiling requires an enforceable provider-side bound before
submission. A historical timing estimate or client watchdog does not supply it.

A read-only Sirius observation at 16:26 UTC on 28 October returned a 16-qubit
computer summary while its default dynamic architecture listed 24 qubit labels.
The default `measure` and `prx` implementations each listed the same 16 loci;
the separate `measure_fidelity` implementation listed all 24 labels. The 24
labels are therefore not evidence that 24 qubits support the proposed
preparation and readout. Any case must inspect the required instruction loci
under its own fresh calibration rather than infer usable width from either
the label count or a different measurement implementation.

IBM's observed 68 seconds are part of its rolling 28-day quota. A read-only
account query on 28 October returned 43 jobs created in the preceding 365 days,
all with finalized reported QPU charges totaling 532 seconds. If IBM counts
exactly those charges toward its published 20-minute, 12-month eligibility
threshold, another 668 seconds would be needed; the provider's eligibility
counter and full boundary conditions are authoritative. Spending the observed
68 seconds alone would not reach 20 minutes under that assumption. The
[IBM offer](https://www.ibm.com/quantum/blog/open-plan-updates) requires opt-in;
the rolling-quota balance is not the eligibility counter.

Ascella is Quandela's photonic QPU; QX is Quantum Inspire's simulator. A
predecessor intervention on Ascella would test end-to-end history dependence,
not a thermal mechanism. Programmed phase-load proxies do not measure heater
voltages. The existing Ascella seed-order analysis treated predecessor association
as exploratory, so a randomized successor needs a fresh outcome-independent
schedule, confirmed iteration order and source-bound anchors.

The separate [predecessor draft](../runbooks/evidence-closure.md#first-acquisition-candidate-predecessor-intervention)
defines the 0.1 minimum effect as a total-variation distance, with simultaneous
coverage of 18 distributions at family alpha 0.05 under an independent-trial
model. Its frozen target, counterbalanced orders, compilation identity and
observation-chain assumptions remain admission obligations. QX can check its own
documented program and output semantics; its outcome does not establish IBM,
IQM or Ascella execution order, compilation or physical noise.

The separate unsubmitted Ascella eight-iteration draft in the primary checkout
uses target positions 1, 3, 5 and 7 and compares the magnitudes of the two
reversed-order differences. That decision rule admits linear drift as a false
history effect. For 32,768 events at each target, counts 3,277, 8,192, 13,107
and 18,022 for one output follow an exactly linear sequence and give both
pairwise total-variation distances `4915/32768`, about 0.149994; subtracting
the draft's 0.028591 radius exceeds its 0.1 threshold. The rule is inadmissible
for a predecessor claim until revised and reviewed. The signed contrast
`(P_1 - P_3 - P_5 + P_7)/2` cancels linear drift only when the four actual
observation times have the required spacing. Quadratic drift remains perfectly
confounded with endpoint assignment in that schedule. A changed schedule,
timing evidence, carryover model, uncertainty contract, cost and fresh approval
are separate admission obligations.
For eight equally spaced target observations, the candidate assignment
`A,B,B,A,B,A,A,B` and weights `(1,-1,-1,1,-1,1,1,-1)/4` cancel
constant, linear and quadratic functions of observation index. The cancellation
is a property of the proposed contrast, not evidence of physical timing or
independence.

Retained [context results](../evidence/ascella-transition-context-diagnostics/findings.md)
show identity input 5 singleton-to-reverse total variation 0.0654, with
simultaneous interval [0.0568, 0.0747] under the stated IID model and matching
returned mesh and input serializations. The comparisons span jobs and cannot
identify order, packing, calibration or drift. The draft's 0.1 threshold can
bound movement below 0.1 without excluding smaller operationally relevant
movement. The [mesh and port results](../evidence/ascella-transition-mesh-port-diagnostics/findings.md)
also show moving identity-input-0 anchors and stable-within-uncertainty
identity-input-2 anchors, so one reference does not establish stationarity for
every target response.

The [coherence transform](../../scripts/ascella_coherence_analysis.py) uses
five angles `theta_k = k pi/5` and fits five basis functions. On that grid,
`cos(6 theta_k) = cos(4 theta_k)`, `sin(6 theta_k) = -sin(4 theta_k)` and
`cos(10 theta_k) = 1`. A fitted fourth-harmonic coefficient describes the
sampled response but does not identify its harmonic mechanism. A discrimination
case needs preregistered off-grid angles and competing response predictions;
more events at the same five angles cannot resolve exact aliases.

The IBM actor case and IQM case proceed independently. The IQM balance is a
strict ceiling: a server-enforced bound must guarantee the 2.50-credit limit
before submission. Historical runtime fits and client cancellation inform risk
but do not guarantee the charged amount. The IBM case needs its own explicit
approval for the actor intervention and endpoints; an existing approval for a
different family or constructor is not transferable by name.

## Prior-art challenge and remaining work

| Question | Existing evidence and boundary | Added candidate question |
|---|---|---|
| Actor-dependent response | [Packed Pauli response](packed-pauli-response-current-balance.md) already fixes the measured register while changing preparation load. | Measure a fixed reporter error contrast and retain the actual assignment and exposure; the earlier design's phase-sensitive Pauli score is a different endpoint. |
| Correlated bursts | [Heron burst plan](../state/plans/heron-correlated-error-burst-search.json) calls for a rate and resource calculation. | Describe a shot-weight tail only when the acquisition contract supports it; require measured exposure for a rate claim. |
| Parity | The finite common-flip control above demonstrates a possible classical improvement. | Test the paired error-table margin on frozen candidates and input patterns; the control is not evidence of device protection. |
| Prediction | Shared-shot outcomes are retained by the proposed fixed-register design. | Compare disjoint features against a frozen activity/time baseline on held-out data; same-shot diagnosis and lagged prediction are distinct. |
| Predecessor history | The [Ascella predecessor draft](../runbooks/evidence-closure.md#first-acquisition-candidate-predecessor-intervention) specifies an optical target and requires qualified order and trial assumptions. | Compare a fixed target after assigned interventions without interpreting phase settings as measured power. |

This table indexes the nearest repository comparisons; it is not a completed
primary-source novelty review. The OpenAI/math family 119 scope states an
information-contraction claim under independent symmetric noise. Its parity
information question differs from the error-probability contrast `G` above.
The repository's existing finite-channel controls do not prove the general
statement or establish a physical mechanism.

The retained [Starmon-5 study](../notes/papers/2310.01120.md) is a concrete
published comparison within its documented reading scope: it prepared all
32 five-qubit computational states and measured a full assignment matrix,
combining preparation and readout errors. The proposed IBM case adds a
prespecified actor assignment and held-out comparison of the error-table
margin `G`; the existing [packed Pauli case](packed-pauli-response-current-balance.md)
already changes preparation load with a fixed measured register but targets a
different response. The Starmon source is not established as the globally
nearest publication, and the proposed combination remains unverified as novel.

The retained [Rudinger et al. IBM experiment](../notes/papers/1810.05651.md)
is a closer intervention precedent: a fixed target is measured under idle and
neighboring CNOT activity, and the authors identify unequal exposure time as a
confound. The proposed `G` decision under randomized actor preparation differs
in endpoint; context-dependent error is established prior art. The Starmon-5
assignment matrix could in principle yield paired error tables by marginalizing
its input-associated outcomes. The retained source review does not establish
access to the full numeric matrix or its randomization, and does not establish
novelty of this particular analysis.

The underlying methods are established. The [Starmon-5 study](../notes/papers/2310.01120.md)
measured a multi-qubit assignment matrix and explicitly noted that preparation
and readout errors were combined. [Unfolding quantum computer readout noise](https://doi.org/10.1038/s41534-020-00309-7)
and [spatially correlated driven-qubit noise](https://doi.org/10.1038/s41534-024-00842-9)
are close precedents. [Simultaneous randomized benchmarking](https://doi.org/10.1103/PhysRevLett.109.240504),
[crosstalk detection](https://doi.org/10.22331/q-2020-09-11-321),
[driven-idle crosstalk suppression](https://doi.org/10.1088/2058-9565/ad5a37), and
[2026 spatial crosstalk characterization](https://doi.org/10.1103/2zb3-4vwq)
also preclude a broad claim that correlated error or driven-idle comparisons are new.
The [packed Pauli response design](packed-pauli-response-current-balance.md)
already proposes sparse/dense preparation on large registers. The IBM
candidate's distinct proposed endpoint is a held-out paired-error improvement,
not a claim that packed crosstalk characterization is new. Whether this precise
combination has appeared elsewhere remains unestablished.

Before requesting approval, finish the primary-source comparison, specify a
bounded uncertainty and holdout contract, generate exact source and decoder
artifacts, verify native placement and served ordering, estimate and bound each
provider's charge, refresh account and device admission, and independently
review the complete case. No simulator job, QPU job, upload, booking or
provider random draw is authorized by this document.
