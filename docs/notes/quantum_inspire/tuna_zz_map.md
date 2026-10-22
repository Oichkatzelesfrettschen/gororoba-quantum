# Tuna-17 conditional Ramsey: a proposed cross-check of effective idle ZZ

**State: complete design reference, proposed and not submitted; not
recommended for acquisition unchanged.** This case is designed to measure
all 24 edges of the retained Tuna-17 coupling graph. It contains 384 Ramsey circuits and 32
pair-state readout calibrations, packed into 139 batches of at most three
jobs. At the catalogue default of 8192 shots, the total is 3,407,872 job
shots. This case has no acquisition, hardware result, spending authorization,
or automatic submission. It is a proposed independent check of the
acquired bipartite map. The later coherence and calibration records below
change the acquisition recommendation without changing this frozen grid.

The builder is `scripts/qi_zz_map.py`; the generated proposal is
`results/quantum_inspire/cases/zz_map_tuna_17/plan.json`. Each of its 139 batch
directories contains a `cases.json` compatible with `qi_platform.py` and
the exact cQASM payloads with SHA-256 digests. The complete analysis is in
`scripts/qi_zz_map_analysis.py`.

The retained campaign-retention source-binding successor is
[`zz-map-tuna17-campaign-retention/plan.json`](../../../results/quantum_inspire/cases/zz-map-tuna17-campaign-retention/plan.json).
The successor binds the campaign-retention submission guards in `scripts/qi_platform.py`.
All 416 cQASM payloads and scientific settings match the frozen proposal above; the
submission-source digest and the case hashes that bind that digest change. Gate `core-594`
previously replayed that successor. The original proposal retains its recorded bytes, and the
acquisition recommendation below also applies to the successor.

The retained submission-deadline successor is
[`zz-map-tuna17-submission-deadline/plan.json`](../../../results/quantum_inspire/cases/zz-map-tuna17-submission-deadline/plan.json).
Its recorded bytes remain immutable.

The active unsubmitted source-binding successor is
[`zz-map-tuna17-deadline-recovery/plan.json`](../../../results/quantum_inspire/cases/zz-map-tuna17-deadline-recovery/plan.json).
The successor binds collection deadlines and durable proof of expiry before
initial resource dispatch. The deadline bounds logical request initiation;
network and server latency determine completion. All 416 cQASM payloads and
scientific settings match the retained proposals. Gate `core-594` replays the
active successor. Each earlier proposal retains its recorded bytes.

The active successor replays against the exact
[proposal catalogue](../../evidence/quantum_inspire/catalogue-submission-deadline-proposal.json)
whose SHA-256 appears in its source digests. The frozen catalogue separates
proposal reproducibility from the account inventory refreshed after acquisitions.
The frozen and refreshed Tuna-17 records have identical topology, gate set,
capacity, compiler configuration and execution limits; queue and status differ.
Submission checks the live backend, account queue and hardware pause afresh;
the archived catalogue establishes proposal provenance rather than availability.

## Acquisition decision after the later Tuna-17 results

The [retained readout experiment](experiments.md#post-readout-frequency-tail-on-tuna-17-preregistered)
records changes in Q9's idle population and Q0/Q6's prepared-state response
during the series. Its initial assignment calibration no longer describes
Q6 after a platform calibration: the corrected Ramsey visibility reaches
1.079. These observations make stability across separate batches a
concrete concern for this proposal, whose four joint calibration states
already require at least two batches per matching.

The current runner requires a 120 s account-wide pause after completed
hardware jobs. This 139-batch case therefore entails at least
`138 * 120 = 16,560 s`, or **4.6 hours of pauses alone**, before execution,
collection, queue and calibration overhead. The existing map measured
poor coherence on Q5/Q6/Q7 by 2 us, and no retained acquisition establishes
that every edge can support the mandatory 20 and 40 us points here.
Excited-neighbor relaxation also limits how long its final state can label
the complete sensing window.

A shorter pilot or a targeted reciprocal comparison should fix its delay
ladder and calibration policy before acquisition. The strong edges (11,14)
and (1,4), and the discrepant reciprocal estimates on (8,11), are supported
by the acquired map as concrete comparison targets. A Q1/Q2 nonedge control
remains a separate experiment. This document retains the complete original
case for review; it does not silently shorten its delays or relax its
all-delay inference criteria. Publication of the design does not authorize
its QX or hardware execution.

## Relation to the acquired bipartite map

The repository already retains an exploratory map of all 24 edges from
[`qi_coupler_zz_map.py`](../../../scripts/qi_coupler_zz_map.py), its
[Tuna analysis](../../../results/quantum_inspire/coupler_zz_tuna_17_analysis.json)
and the [experiment report](experiments.md#residual-zz-of-every-tuna-17-coupler).
That acquisition used ten circuits, including readout references, at
16384 shots each. Its bipartite preparation measures conditional sectors
of several neighbors at once. The present proposal tests the pair model
in a different preparation and parallel context:

| Choice | Acquired bipartite map | This proposed check |
|---|---|---|
| Neighbor state | Prepared in \|+>, then conditioned on measured Z outcomes | Prepared separately in \|0> and \|1> |
| Placement | Two bipartite role assignments | Eight induced matchings |
| Delays | 0.5 and 2 us | Six delays from zero through 40 us |
| Readout references | All-zero and all-one registers | Four joint pair states per matching |
| Inference | Multi-neighbor additive fit; end-quality rule fixed after acquisition | Pair-rate reconstruction with full assignment covariance, fixed signal and reciprocity checks, Holm correction over 24 edges |

The existing map retains 15 edges with two usable probe ends and one usable
end for each other edge. These are prior results, not measurements of this
proposal. Comparing the two would test sensitivity to preparation,
neighbor-sector readout and acquisition context; agreement would not
identify an individual coupler setting or a unique physical mechanism.

## Question and limits of the claim

The question is whether changing the state of a neighboring qubit changes
a probe's idle frequency, and whether both directions on an edge agree
with one static diagonal pair interaction. The four conditional rates also
give the local rotating-frame detunings and their difference, using
identical explicit idle times.

These measurements determine **effective edge interactions in the stated
parallel context**. They do not read or reconstruct a coupler's flux,
frequency, calibration setting, or individual physical contribution.
Residual ZZ is a coherent conditional interaction; it is not population
leakage out of the computational subspace. A map could locate an association
with the weak zero-divisor region, but it cannot by itself establish why
that region lost contrast.

The public [transmon hardware description](https://www.quantum-inspire.com/backends/transmons/)
identifies 17 qubits and 24 dedicated tunable couplers, with dedicated
coupler flux lines. Its [operational guide](https://www.quantum-inspire.com/kbase/tuna-operational-specifics/)
documents gate access, OpenSquirrel ALAP scheduling, 20 ns native
single-qubit gates, 60 ns CZ, 800 ns measurement, initialization of 200 or
500 us, and explicit waits in 20 ns cycles. These are the sources retained
in the repository and bound into `plan.json`.

The relevant Tuna-5 study is Vallés-Sanclemente et al.,
[Physical Review Letters 136, 200801 (2026)](https://doi.org/10.1103/wdfj-4nbt).
It demonstrates that residual ZZ and exchange interactions can be nulled,
but their zeros are not simultaneous. Operating-point choices therefore
trade off spectator effects on different operations. The public sources do
not establish that every Tuna-17 idle point is the ZZ-minimizing point.

## Model and signs

Use the repository convention in
[`conditional_ramsey_hamiltonian.md`](../conditional_ramsey_hamiltonian.md):

\[
H/\hbar=(\omega_A Z_A+\omega_B Z_B+J Z_A Z_B)/2,
\qquad Z|0\rangle=|0\rangle.
\]

For each canonical edge `a < b`, A is qubit a and B is qubit b. No Bell
preparation or CZ is needed. The four rows identify all three parameters:

| Probe and fixed neighbor | Rate | Row over (omega_A, omega_B, J) |
|---|---|---|
| A, B prepared 0 | nu_A0 = omega_A + J | (1, 0, 1) |
| A, B prepared 1 | nu_A1 = omega_A - J | (1, 0, -1) |
| B, A prepared 0 | nu_B0 = omega_B + J | (0, 1, 1) |
| B, A prepared 1 | nu_B1 = omega_B - J | (0, 1, -1) |

Thus `omega_A = (nu_A0 + nu_A1)/2`,
`omega_B = (nu_B0 + nu_B1)/2`, and the two directional estimates are
`J_A = (nu_A0 - nu_A1)/2` and `J_B = (nu_B0 - nu_B1)/2`. Their agreement
is a consistency check of the static pair model under the preparation, readout and
parallel-context assumptions. A resolved disagreement does not select a
specific physical mechanism.

Report `J/(2*pi)` in Hz and explicitly distinguish it from the full
conditional frequency change on flipping the neighbor:

\[
\Delta f_{1-0}=(\nu_1-\nu_0)/(2\pi)=-J/\pi.
\]

The matched-idle frequency difference is `(omega_A - omega_B)/(2*pi)`.
These are effective frequencies in the gate reference frames, not the
qubits' absolute GHz transition frequencies. A and B are probed in
different conditional settings, so this extraction assumes stability
across those settings. It is not a simultaneous two-equatorial-qubit
measurement in one shot, and that additional arm is not included in the
cost.

## Explicit circuit sequence

Every payload allocates 17 qubits and 17 classical bits, starts with
`init q`, and measures all qubits with the same `b = measure q` mapping.
Qubit 0 is the rightmost character of a Tuna result string.

1. Initialize every qubit; apply `barrier q`.
2. Prepare each active neighbor using `X90; mX90` for state 0 or
   `X90; X90` for state 1. Every stage has a full-register barrier, and
   every other qubit receives `wait(1)` in each of the two stages. Both
   conditions have two physical 20 ns pulses and 40 ns of preparation.
3. Prepare every probe with `Y90` (the +X state); other qubits wait one
   cycle. Apply `barrier q`.
4. Apply the same explicit idle to all 17 qubits. The zero-idle control
   omits the wait but retains the barriers and the finite preparation and
   analysis durations.
5. Read X with `mY90` or Y with `X90`; all other qubits wait one cycle.
   Apply `barrier q`, then measure all qubits.

With the stated Hamiltonian, these choices give
`X = cos(nu*t + phi0)` and `Y = sin(nu*t + phi0)` in the ideal equatorial
limit; the analyzer uses `X,Y = 1 - 2*P1` and `atan2(Y,X)`. The native gate
signs and the matched neighbor preparations are checked as two-by-two
matrix identities by the builder's contract.

No gates are applied during the sensing window. The neighbor is measured
in its physical final state; no final X silently converts a decay into
an apparent success. Raw and readout-corrected conditional estimates and
retention are all retained. Final-state conditioning does not prove the
absence of a decay followed by re-excitation, nor remove state-preparation
error.

The free phase intercept absorbs a static preparation phase. It does not
guarantee removal of time-dependent drive transients after preparation.
Likewise, full-register barriers and equal explicit waits constrain the
documented scheduler, but a generated source is not a retained compiled
hardware schedule. The proposal does not claim such a schedule was read.

All rotations are multiples of pi/2 and exactly on Tuna's pi/36 grid. The
rotation grid does not impose a pi/36 floor on estimating an accumulated
phase: X/Y outcome probabilities vary continuously with that phase.

## Delays and phase ambiguity

The proposal translates the repository's existing physical delay ladder
into Tuna cycles and checks that translation against its retained source:

| Explicit wait cycles | Time |
|---:|---:|
| 0 | 0 |
| 25 | 0.5 us |
| 100 | 2 us |
| 400 | 8 us |
| 1000 | 20 us |
| 2000 | 40 us |

The acquisition order is `0, 400, 25, 2000, 100, 1000` cycles, with probe
direction, quadrature and neighbor-state ordering reversed on alternate
delay blocks. This predetermined ordering prevents a monotonic delay sweep
from being identical to elapsed job order. It does not make the settings
simultaneous or remove arbitrary drift. Analysis sorts by physical delay.

The acquired bipartite map reports minimum Ramsey visibilities of 0.043,
0.270 and 0.084 for Q5, Q6 and Q7 over its 0.5 and 2 us settings. The
preparation and parallel context differ here, so those values are not a
prediction for this case. They do make the six-delay requirement material:
if coherence is insufficient at any delay, including 40 us, the primary
edge inference is inconclusive. It does not become evidence for zero ZZ.
A shorter-delay redesign would need a separately fixed case before
acquisition; the analyzer does not select a favorable prefix after seeing
the data. In light of the later drift and coherence records, that redesign
is the recommended next planning step, rather than acquiring this entire
ladder as written.

The first nonzero interval supplies an unambiguous conditional-rate range
of strictly less than 1 MHz in magnitude. The primary inference is
conditional on that bounded-frequency assumption. The integer delay grid
admits global aliases; an unwrap guard cannot discover all of them from
these measurements alone.

## Parallel placement

Ordinary disjoint edges can still have a direct connection between active
pairs. Exciting another pair can then contaminate the conditional shift.
The builder instead colors the squared line graph and validates an
**induced matching** in every packing: no shared endpoints and no coupling
edge connecting endpoints of different active pairs.

The retained topology produces these eight packings:

| Packing | Canonical edges |
|---|---|
| pack-00 | (4,8), (6,9), (10,13), (14,16) |
| pack-01 | (0,1), (5,8), (7,10), (15,16) |
| pack-02 | (0,2), (3,6), (8,11) |
| pack-03 | (8,12) |
| pack-04 | (2,5), (7,11), (12,15) |
| pack-05 | (3,5), (4,7), (12,14) |
| pack-06 | (2,4), (9,12), (11,13) |
| pack-07 | (1,4), (5,9), (11,14) |

Every listed edge appears exactly once. The other qubits start in 0 and
receive only the matched waits. Longer-range interactions, microwave
crosstalk, imperfect initialization, readout effects and indirect paths
remain possible. Results are therefore labeled by the complete packing,
not assumed independent because the edges are spatially separated.

Q1 and Q2 have no edge in the retained graph. This map measures their edges
to shared neighbors but does not directly measure an interaction between
Q1 and Q2 or reproduce their simultaneous-drive failure. A separate static
conditional-Ramsey on nonedge (1,2) would add 48 circuits and four readout
calibrations: 52 jobs, 18 batches if acquired alone, and 425,984 job shots
at 8192 shots. A driven-neighbor diagnostic needs its own matched arm and
budget. Neither option is generated or included here.

## Readout and preregistered analysis

Each packing receives all four pair-state calibrations, `00, 01, 10, 11`,
prepared on its canonical pairs. Unused qubits remain in 0. The same
two-pulse state preparations and fixed-duration padding are used. The
calibration preparations themselves can have error: the inferred channel
is a measured preparation-and-assignment model, not a perfect detector
tomography certificate.

The four calibrations for one packing span at least two three-circuit
batches, and its Ramsey settings span further batches. The correction
assumes the measured assignment channel remains stable across that
packing. Batch boundaries, pauses and recalibration can violate that
assumption; the analyzer does not infer or remove between-batch drift.

For each edge, the analyzer constructs a full four-by-four column-stochastic
matrix `A[observed, prepared]`, with canonical state index
`2*bit_a + bit_b`. It inverts the joint pair channel before conditioning on
the prepared neighbor state. Using only independent per-qubit flips would
discard exactly the conditional-readout possibility this control addresses.
No corrected probability is clipped into [0,1]. Raw values are reported
alongside corrected ones.

The numerical criteria are fixed in `plan.json`:

- The assignment-matrix condition number must be at most 100.
- The neighbor-retention lower three-standard-error bound must exceed 0.10.
- The equatorial radial amplitude must be at least 0.05, with radial
  signal-to-noise at least 5.
- At every ladder step, including the first, the three-standard-error
  innovation interval must lie strictly inside the selected +/-pi unwrap
  branch.
- Every out-of-range corrected probability is flagged; nonphysicality
  exceeding three standard errors blocks the corresponding inference.
- Primary rates require all six delays. A shorter-prefix fit is not
  silently substituted when a long-delay signal fails.
- Fits use ordinary least squares with a free intercept and uncertainty
  propagated through all four shared assignment columns, conditioning,
  phase extraction and rate reconstruction.
- Phase-linearity lack of fit is flagged at p < 0.01; disagreement of the
  two directional J estimates is flagged at two-sided p < 0.01. They are
  model checks, separate from the edge-discovery family.
- Corrected J discoveries use Holm familywise alpha = 0.05 over all 24
  edges, assigning invalid edges p = 1. This correction does not require
  independent edges.

Per-edge estimates retain the two-bit joint outcome distribution and the
shared calibration uncertainty. The implementation does not use cross-edge
covariance to make a device-wide independent-sample claim. A later analysis
of correlations among edges must use their complete same-shot strings.

## Exact acquisition counts and timing scope

| Item | Count |
|---|---:|
| Physical edges | 24 |
| Induced matchings | 8 |
| Probe directions per edge | 2 |
| Neighbor states | 2 |
| Quadratures | 2 |
| Delays | 6 |
| Ramsey circuits per matching | 48 |
| Total Ramsey jobs | 384 |
| Readout calibration jobs | 32 |
| Total jobs | 416 |
| Batches (global deterministic packing) | 139 |
| Batch sizes | 138 batches of 3, then 1 of 2 |
| Shots per job | 8192 |
| Total job shots | 3,407,872 |
| Ramsey edge observations | 9,437,184 |
| CZ gates | 0 |

The catalogue permits five circuits per batch, while the repository's
hardware submission policy limits each batch to three. The builder imports
`HARDWARE_BATCH_CIRCUITS` from `qi_platform.py` and binds that source's
digest into every manifest. It preserves all 416 payloads and their order
when dividing this proposal into **139 hardware batches**. Adjacent settings are
grouped in deterministic order; a batch boundary may cross from one
packing into the next.

The retained catalogue allows 300 s per Tuna job. Summing documented
primitive durations gives approximately 722 s with 200 us initialization
or 1744 s with 500 us initialization over the whole proposal; the longest
single-job primitive sum in the latter scenario is 4.431 s. These are
explicit planning scenarios, not execution-time bounds or an account
charge. They exclude any undocumented repetition, control, compilation,
job, queue and calibration overhead. Batch regrouping changes
those unpriced overheads while preserving the circuit-level primitive
sums. Actual QPU seconds and any monetary charge remain unset in the
machine-readable proposal. These primitive sums exclude the current
policy's minimum 16,560 s of pauses between the 139 hardware batches;
elapsed acquisition time cannot be inferred from the primitive sums alone.

## Offline generation, review and future collection

From the repository root:

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/qi_zz_map.py --check results/quantum_inspire/cases/zz-map-tuna17-deadline-recovery --catalogue docs/evidence/quantum_inspire/catalogue-submission-deadline-proposal.json
"$PYTHON" scripts/qi_zz_map.py --self-test --catalogue docs/evidence/quantum_inspire/catalogue-submission-deadline-proposal.json
```

The generator imports neither the Quantum Inspire SDK nor Qiskit, performs
no network access and has no submit command. Its checks cover the retained
topology, induced matching, complete condition grid, physical delay
translation, matrix gate identities, exact batch/shot budget and payload
hashes. CPU-bound independent payload rendering uses the repository's
ordered process pool.

The 416 retained payloads also passed local parsing and semantic analysis
with libqasm 1.2.1 and IR construction with OpenSquirrel 0.9.1 under Python
3.13.16. Every register has 17 qubits and 17 bits, initializes every qubit,
and measures each `q[i]` into `b[i]` exactly once. After register-wide
instructions are expanded, every wire carries four fixed 20 ns cycles
plus the chosen delay: 4, 29, 104, 404, 1004 or 2004 cycles, excluding
initialization and measurement. This check used no backend compilation,
hardware scheduling or remote execution; it does not upgrade the primitive
timing estimates into a measured schedule.

A future acquisition copies the reviewed `batch-NNN` directories into a
dedicated run root, keeping their relative names. `qi_platform.py` already
requires the exact batch case and an approval string, and records jobs,
timing, raw shots and ledger rows. Each completed batch keeps its own
`submission.json`, `results.json` and `raw/<file>.json`. The analyzer reads
the approved plan and that run root; it does not synthesize missing
measurements or rewrite a prior acquisition or analysis.

Before such an acquisition the current catalogue and service state must be
read, the case and budget reviewed, and the repository's required hardware
approval obtained. The current policy also requires a QX dry run first,
then one hardware batch at a time: collect the preceding batch, pass its
sanity checks and pause before the next submission. The retained QX
catalogue exposes 10 qubits, so these 17-qubit payloads cannot be submitted
unchanged to QX. The separate [compact QX preflight](tuna_zz_qx_preflight.md)
supplies proposed twins: 416 circuits in 139 batches at 1024 shots per
circuit, totaling 425,984 emulator job shots. Its jobs are additional to
the hardware-map count, and neither proposal has been executed. The
already retained QX controls for the bipartite map and zero-divisor
witnesses do not validate these new payloads. A revised hardware grid
would need corresponding revised twins; running the current preflight
does not resolve the acquisition-design concerns above.
