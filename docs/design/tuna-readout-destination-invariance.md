# Tuna readout destination-invariance diagnostic

The [readout diagnosis](../evidence/tuna-projector-geometry/readout-cause-diagnosis.md)
separates an observed response failure from its unidentified physical cause. Before changing
pulse timing, the cheapest controlled acquisition can change only classical destinations.
A physical-operation-identical pair tests the acquisition/reconstruction boundary. It does
not assume that a 2 microsecond gap is a repair.

The [generated proposal](../../results/quantum_inspire/proposals/tuna-readout-destination-invariance/proposal.json)
is a concrete **unapproved, statistically unadmitted draft**. Local compilation is complete.
Provider submission, circuit upload and remote compilation have not occurred for these cases.
The [decision draft](../evidence/tuna-projector-geometry/readout-destination-decision-draft.json)
intentionally reports its power/dependence model as unqualified; the acquisition-decision
validator therefore refuses it. Syntax-valid circuits are not an admitted experiment.

## Exact intervention and scope

Two batches use the nominal all-zero and all-one controls from the failed qualification.
Each requests the same three-job sequence:

| Job | Quantum operations | Early destinations for q4,q11,q6 |
|---|---|---|
| Baseline before | Exact retained control | 17,18,19 |
| Rotated destinations | Same complete physical instruction stream | 19,17,18 |
| Baseline after | Byte-identical copy of the first control | 17,18,19 |

All circuits retain `qubit[17]`, `bit[20]`, the same first three measured qubits, the same
terminal all-17 measurement, the same preparations and zero explicit gap. Terminal
classical destinations remain 0 through 16. The decoder reads each physical qubit through
its declared destination and inverse-permutes the rotated case before comparison.
The local compiler receipt compares the complete instruction stream, including destinations,
against the source, and separately verifies physical equality after removing only classical
measurement destinations. A changed quantum gate, measured qubit, order or wait fails that
comparison. Provider schedule equality remains an observation requirement.

A destination-dependent change after inverse decoding would contradict the intended
classical-naming invariance. It would direct investigation toward compilation, reconstruction
or acquisition association; it would not identify which subsystem failed. Destination
invariance would weaken that particular hypothesis while leaving a common mapping defect,
readout-context error and physical mechanisms possible. This case does not test register
width; compact-20 versus canonical-34 is a separate intervention if evidence calls for it.

The requested baseline–rotated–baseline sequence is a design request. The API has executed
other batches in a different order, so requested order must never substitute for provider
execution timestamps. If the rotated acquisition is not bracketed, the bracketed comparison
is inadmissible. Separate single-job batches could establish order after collection and pause,
but would change chronology and total case scope; those require a revised admitted manifest.

## Counts, timing and operational constraints

Each circuit requests 4096 shots: six circuits, 24,576 shots, two batches of three.
The measured control durations provide an estimated total of
3*(4.948185 + 4.896220) = **29.533215 seconds**, excluding queue and mandatory pauses.
This transfers a workload estimate, not a timing guarantee. The provider's 300-second
per-job ceiling gives 900 seconds per batch and 1800 seconds across six jobs as the
mechanical upper bound. The draft claims no smaller enforced ceiling.

Expected credits are zero subject to a fresh free-use and account-ledger observation.
Only one account hardware batch may be queued. Collect the first batch, satisfy the
account-wide hardware pause, and re-admit before the second. Failed jobs, changed manifests,
structural drift, nonzero charges or an ambiguous submission stop further batches; collect
all already dispatched jobs and preserve their identities. Automatic retries
are prohibited. Reconcile an ambiguous submission by its recorded identity.

The two manifest hashes are:

- Prepared zero: `5ac1585e5b4218077cc6de6845f6a996593087fbea5df395146c844260c7b0fb`.
- Prepared one: `55d66b9af385931f7418611bae14f31a9f29eb4a9e7bf87abe5571d552e5b76e`.

These hashes identify the generated draft. Any admission-driven change requires new hashes
before approval. The generator and local compiler replay are
`scripts/qi_tuna_readout_mapping_cases.py --check`, run under the QI compiler interpreter.

## Comparison and statistical admission still required

The proposed primary summaries are the four unnormalized early/final joint probabilities
for each of three ancillas under each of two nominal preparations: 24 cells. Compare the
inverse-decoded rotated arm with the pooled bracketing baselines, retaining the before/after
baseline contrast separately. All terminal bit rates, full raw histograms and shot-order
blocks remain diagnostics. A small full-distribution distance is not demanded over the
million possible width-20 strings at this sample size.

For scale only, under independent, stationary Bernoulli trials within each arm, Hoeffding
and a union bound over 24 cells give a simultaneous 99% radius on each rotated-minus-pooled
baseline difference of

    r = sqrt(log(4*24/0.01)/(2*4096))
      + sqrt(log(4*24/0.01)/(2*8192)) = 0.057113526713.

The union bound does not require independence between cells. It does require the stated
within-arm trial model and a common baseline distribution across the bracket. The calculation
is a conditional precision illustration, not a measured effective sample size or a power
qualification. Three jobs per preparation provide one intervention block; 4096 shots do not
create 4096 independent treatment assignments. Shot-lag summaries cannot validate arbitrary
drift, memory or between-job exchangeability. Baseline bracketing exposes some drift but
cannot eliminate a transient coincident with the rotated job.

Before execution, specify the practically relevant difference, baseline drift veto,
familywise comparison, missingness and failed-order behavior, and qualify uncertainty using
independent treatment blocks or explicit, justified dependence bounds. For example, a
0.10 difference threshold combined with the illustrative radius would require an observed
absolute difference above 0.157114 to certify departure under that model; this is not yet
a frozen decision rule or a power guarantee. An interval fully inside +/-0.10 would support
only bounded equivalence of the selected cells, not exact full-law invariance.

A separate comparison analyzer must bind the exact manifests and decoder, preserve raw
shots first, verify actual execution order, and reproduce all planned statistics and terminal
decisions before acquisition. Its contract tests must include changed destinations, swapped
physical targets, partial shots, reordered jobs, drift vetoes and failure preservation.
The existing frozen qualification analyzer must remain unchanged. The old live-admission
helper also binds the old manifest; a successor admission wrapper must bind both new
manifest hashes, compiler receipts and the new analyzer, reuse the structural checks, and
pass the expected manifest digest into guarded submission. The old helper cannot admit
these new cases unchanged.

## What would resolve the physical cause afterward

Request read-only provider evidence for completed jobs 1616329–1616331 before spending on
an expanded matrix: executed compiler/configuration identity; scheduled pulse start/end
and acquisition-window start/end; integration kernel, discriminator rotation and threshold;
per-qubit acquisition index to classical-bit mapping; calibration timestamps and addressed
readout-channel context; reset/repetition history; and analog IQ or multilevel labels if
retained. The API source readback establishes stored cQASM but exposes none of those analog
fields. The public calibration datasource remains unavailable.

If classical destination behavior qualifies, isolate q11 with spectators fixed and use two
preparations crossed with first-only, short/long late-only, and short/long repeated-readout
schedules. Ten distinct circuits, at least four three-job-or-smaller batches per pass, are
needed before independent repetitions. Match omitted measurements using verified served
operation durations. Compare sparse and multiplexed readout in a separate factor, then
spectator state in another. A gap-dependent recovery alone remains compatible with resonator
signal changes, electronics recovery, relaxation and transitions. A physical attribution
requires the analog/timing evidence or independently calibrated state-sensitive controls.

Execution admission therefore needs: the frozen comparison analyzer and justified precision
model; actual ordering/timing support; current backend, compiler, queue, pause and credit
checks; an admitted acquisition-decision record; and explicit approval of the exact revised
case. The prior qualification approval does not cover this diagnostic.
