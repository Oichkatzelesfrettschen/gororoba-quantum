# Belenos dark-subspace certificate: provider qualification

The 160-setting certificate of [bdsc.md](../notes/quandela/bdsc.md) needs
three provider contracts that no retained run establishes: one measurement
effect shared by every preparation, a declared level of the acquisition
chain that its confidence analysis attaches to, and an acceptance effect
proportional to the identity or bounded away from it. M2 to M4 of the
qualification table stay blocked until each contract is supported. This
document states each contract, the qualification measurement that tests
it, and the claim each outcome supports. `provider_contract.json` records
each capability's status and the question it puts to Quandela,
`qualification_case.json` the first executable case, and
[bdsc-qualification-case.md](../runbooks/bdsc-qualification-case.md) the
order in which that case runs. No acquisition is authorized by any of
them; each run waits for its own written case.

## Platform precondition

`scripts/qd_platform.py plan` refuses a platform whose Explorer row and
processor record do not both read `available`, and refuses a mesh-sensitive
case when the live record lacks `specs.architecture`. Every qpu:belenos
read from 2026-10-20 to 2026-10-21 lacks the architecture and the
`commands`, `default_mitigations`, `known_mitigations` and `type` fields
([calibration.md](../notes/quandela/calibration.md)); a missing field reads
as absent, not as the earlier value. The qualification case submits each
body as a numeric unitary, which the service compiles itself, so it needs
no architecture; the absent `default_mitigations` leaves the
provider-default policy's processing undeclared, which the empty-list
policy avoids. A qualification case therefore starts from a fresh read
that passes `plan`. The BDSC target keeps its frozen
2026-10-17 receipt (`docs/evidence/bdsc/inputs/receipt.json`); a
detector-aware case planned from a newer receipt carries a new target
digest beside it.

## Contract A: preparation and measurement

The certificate reconstructs one effect F = U^dagger Q_A U from
p_s = <psi_s| F |psi_s>, with psi_s = V_s r prepared from the source mode r.
The service receives T_s = U V_s and compiles each body to its occupied
column: S3 (job 1d7160c1) and S4 (job e5b74123) on sim:belenos returned all
574 phases changed with only the occupied column preserved, and on
qpu:belenos the served mesh follows the body and the compilation seed
(belenos_mesh job-02 and job-07, [strategy.md](../notes/quandela/strategy.md)
sections 2 and 9). Agreement with the requested column distributions is
request-to-distribution testing, not tomography of one effect.

Let J embed the 16 logical inputs in the 24 chip modes and let a known
preparation unitary V_s satisfy V_s |r> = J psi_s. The intended transformation
is T_s = U V_s. A complete returned transformation T~_s de-embeds to

    F~_s = J^dagger V_s T~_s^dagger Q_A T~_s V_s^dagger J,

which equals J^dagger U^dagger Q_A U J for every s when T~_s = U V_s. The
comparison needs full complex transformations and the calibrated detector
effects; occupied-column intensities are not enough. De-embedding a declared
matrix still says nothing about the physical preparation, which needs its
own bound: unknown preparation and unknown measurement are not identifiable
from the same observations by assigning either its ideal coordinates.

Equal phases are sufficient for a common effect and not necessary. A served
transformation W_s U V_s with W_s^dagger Q_A W_s = Q_A gives the same
p_s, so the object to preserve or bound is the induced effect
J^dagger T^dagger Q_A T J on the logical input space J, not the phase bytes.
With unequal detector efficiencies Q_A becomes a calibrated effect that the
same condition must preserve. A returned mesh that meets it numerically
still says nothing about its physical realization, which needs calibration.

Three routes satisfy the contract:

1. a physically fixed readout with independently controlled preparation;
2. per-preparation transformations proved to preserve the induced effect,
   with physical deviations bounded;
3. a declared label-independent randomized implementation whose average
   effect is the object under test.

A common implementation differs from a common distribution. For any
requested p_s a service can prepare sqrt(p_s) |A> + sqrt(1 - p_s) |D> from
the occupied source input and reproduce every scalar probability without a
fixed measurement on independently prepared states, so response agreement
alone resolves neither M2 nor M4. Qualification needs evidence of the
physical factorization, an effect-preserving implementation, or a justified
label-independent average.

Basis-state injection into a fixed unitary is insufficient on its own:
basis probabilities fix the diagonal of F, and the bank's real and
imaginary pairs carry the off-diagonals. The questions for Quandela are
whether a requested full transformation can be preserved, whether a native
architecture configuration can run without state-specific optimization, and
whether coherent inputs can be injected independently of the readout. No
`no_transpile` parameter is documented, and none is assumed; the
abstract `Experiment` representation and local SLOS execution establish
none of these capabilities.

## Contract B: acquisition and processing

The chain runs source attempts, emitted photons, detector events, accepted
records, corrected estimates, returned samples or counts; a confidence
statement attaches to one declared level. DetectorBalancing is the
qpu:belenos default. In Perceval 1.3.1 it returns probabilities corrected by
inverse detector loss, under its stated assumptions of loss without dark
counts and independent detectors, and `probs_to_sample_count` then perturbs
each probability by a normal draw, clips at zero, renormalizes and rounds.
At n p = 1 that gives P(0) close to Phi(-1/2) = 0.3085, which the retained
local conversion record reads as 0.305 against the binomial 0.3679
([bdsc.md](../notes/quandela/bdsc.md), M3). The record is a local Perceval
1.3.1 conversion study; the frozen receipt names server Perceval 1.3.0, so
the server path a run takes is bound per run, not inferred from it.

For a RemoteComputer the Perceval 1.3 reference documents `mitigations =
None` as the provider defaults and an empty list as disabling remote
mitigations ([error_mitigation](../notes/quandela/perceval/reference/runtime/error_mitigation/index.md)),
and Perceval 1.3.1 `PayloadGenerator.from_computation` writes the list into
the payload whenever it is not None, so the empty list reaches the server; `use_mitigations_remotely = False` moves correction to
the client rather than removing it. Whether the server honors the empty
list on this account, and whether every server-side transformation stops
with it, is unverified. A `samples` result is not chronological evidence by
type: the conversion code can expand and shuffle a histogram drawn from
probabilities, so time order is established by the acquisition path or not
at all. A binomial-looking count distribution also proves nothing, since a
draw from a probability vector is binomial too.

## Contract C: acceptance and conditioning

With selected effect G_A and total acceptance effect D,
p(A | accepted, rho) = Tr(G_A rho) / Tr(D rho). This is the original-frame
measurement only when D = tau I, or when a bound
(1 - delta) tau I <= D <= (1 + delta) tau I is propagated, under which
F = G_A / tau satisfies 0 <= F <= (1 + delta) I. The receipt-derived
delta of about 0.97 treats relative output figures as efficiencies and is an
unqualified model, not a measured acceptance bound. A minimum-detected-photon
filter of one is an at-least-one rule; `support_multi_photon = False` in the
Perceval 1.3.1 constraint checker limits input photons per mode, not per
circuit, and `accepted_state_kinds` of the remote platform, not the local
SLOS model, decides which input kinds the service accepts.

### Event thinning as an acceptance equalizer

Suppose a fixed interferometer has independent terminal detector
efficiencies eta_m > 0, negligible dark counts and no unmodeled internal
loss. A detected mode-m event has probability r_m = eta_m |(U psi)_m|^2.
Retaining each genuine mode-m event independently with probability
q_m = eta_* / eta_m, eta_* <= min_m eta_m, gives r_m q_m = eta_* |(U psi)_m|^2,
so the retained acceptance effect is eta_* I and the conditional distribution
is the ideal one under those assumptions. Thinning discards real events
rather than generating counts, at an efficiency cost set by the weakest
detector. It needs uncorrected event-level records and calibrated efficiency
ratios, and applied to balanced or resampled data it restores nothing. It
is a requirement to put to the provider, not a capability of the account.

A genuine raw histogram suffices: independently thinning each of N_m iid
detected events with probability q_m gives N'_m | N_m ~ Binomial(N_m, q_m)
(`bdsc.thin_histogram`), so timestamps serve drift and correlation analysis
rather than thinning. The input must be uncorrected counts with a supported
sampling law; thinning balanced or probability-resampled counts recovers no
provenance. Through a lossy transfer T into the detectors,
r_m = eta_m |(T psi)_m|^2 and the thinned acceptance is eta_* T^dagger T
(`bdsc.thinned_acceptance`), scalar only when T^dagger T = tau I on the
declared inputs or bounded near it. Thinning equalizes terminal
efficiencies and leaves internal mode-dependent loss; the self-test shows a
graded internal loss surviving it. With estimated efficiencies, q_m is
frozen before confirmatory analysis and the uncertainty of q_m eta_m
propagates. Dark counts, multi-photon threshold ambiguity and detector
correlations need terms the loss-only identity lacks.

## Qualification measurements

The pilot of `docs/evidence/bdsc/pilot.json` (three target and complement
pairs, real rotations, imaginary phases and held-out angles, 24 settings)
supplies the preparations. Each test below supports a narrower claim than
the certificate.

1. **Preparation-independent consistency.** For orthonormal f, g and
   |+-> = (f +- g)/sqrt2, |+-i> = (f +- i g)/sqrt2, every fixed linear
   effect gives p_+ + p_- = p_f + p_g = p_+i + p_-i, because the density
   operators sum equally. The preparations are generated independently and
   acquired in randomized order, on the selected and complement outcomes and
   on single modes where the processing level justifies it. A violation
   locates an inconsistency among preparation, common effect, conditioning,
   drift and processing; passing is necessary, not sufficient. Bodies that
   prepare the same nominal state through different completions on unused
   columns must also agree.
2. **Processing provenance.** Matched requests under provider defaults and
   under an explicit empty mitigation list. Their means need not agree,
   because correction changes estimates; the outcome is which observation
   level each result represents, whether uncorrected records are reachable,
   whether a result was converted from a probability estimate, which
   uncertainty belongs to it, and whether its time order is real. On
   hardware the true p of a dark output is unknown, so the local p = 1e-4
   conversion study stays a software falsifier.
3. **Restricted against full transformation.** Compare the submitted and
   returned full transformations and the induced effect
   J^dagger U^dagger Q_A U J, with relative phases kept for coherent inputs.
   This compares declared transformations; physical error needs empirical
   calibration. A provider that promises only the occupied-column
   distribution places the result in request-to-distribution testing.

## First qualification case

`qualification_case.json` holds the case; it tests operational consistency
and makes no dark-subspace claim.

- **Banks.** For trusted orthonormal f, g the six states f, g,
  (f +- g)/sqrt2 and (f +- i g)/sqrt2 satisfy, for every fixed linear
  effect, Delta_R = p_+ + p_- - p_f - p_g = 0 and
  Delta_I = p_+i + p_-i - p_f - p_g = 0. Two pairs: (k_1, f_9) from the
  pilot, and (f_2, f_3) = (e1, e2), whose individual responses separate the
  real and imaginary extra-null alternatives E_R and E_I.
- **Variants.** Two preparation descriptions with the same chip column and
  different actions on the unused columns, each a fixed 24-mode template
  whose 47 parameters an iteration binds: outward-ladder fans the photon
  from source mode 6 through adjacent splitters to its left and right
  neighbours, reverse-ladder swaps two unused inputs, carries the photon to
  mode 0 through fixed full splitters and ladders it rightward across every
  mode; both end in one phase per mode, use Perceval's BS.Rx convention,
  reach every bank column to 1e-12, and stay at least 2.0 apart in
  Frobenius norm on the unused columns. They cross two processing policies:
  provider defaults (`mitigations = None`) and an explicit empty list. Both
  epochs acquire all six states of every cell: 2 pairs x 2 descriptions x
  2 policies x 2 epochs x 6 states = 96 settings. Repeating only f and g
  would see diagonal changes alone: I/2 + X/4 and I/2 + Y/4 agree on f and
  g and differ on + and +i.
- **Jobs.** A job fixes one circuit and one mitigation list. Both
  templates are parameter settings of one union circuit (the reverse-ladder
  splitters with its fixed ones free, the outward-ladder splitters, one
  phase per mode; the other block's splitters at 0 reproduce each
  template's unitary to 1e-12), so the case runs one job per pair, policy
  and epoch: 8 jobs of 12 iterations, the six states under both templates,
  each iteration with its own compilation seed and a QRNG-drawn order.
  Every sum-rule and completion contrast compares iterations of one job,
  and drift between jobs reaches only the epoch family.
- **Decision.** Clopper-Pearson at alpha / 96 per observation, alpha = 0.01,
  gives one simultaneous event, and every prespecified contrast
  sum_j c_j p_j inherits it through
  Delta_L = sum_(c_j > 0) c_j L_j + sum_(c_j < 0) c_j U_j
  (`bdsc.contrast_readout`). Three families: 32 within-cell sum rules
  (Delta_R and Delta_I per cell and epoch), 48 cross-template differences
  at one policy and epoch, and 48 cross-epoch differences at one template
  and policy, each with a declared margin of 0.02. A contrast reads
  compatible inside its margin, violated when its interval misses the band,
  and inconclusive otherwise. Within-cell linearity alone proves nothing
  across cells: I/2 and I/2 + X/4 both obey every sum rule and differ on
  +. No contrast compares the two policies, since mitigation changes
  estimates by design; an observation enters the event only when its
  policy's observation contract supports Bernoulli trials, the alpha split
  counts every observation regardless, and a contrast that touches an
  unadmitted observation reads not admitted.
- **Epochs.** Epoch 2 follows at least one platform calibration cycle, so
  its family tests reproducibility across a calibration change, an
  intervention that may legitimately move the effect; within-epoch
  stability rests on the randomized order alone, and the epochs are never
  pooled into one stationary reconstruction.
- **Power.** False certification of any family is bounded by alpha; the
  probability of passing an acceptable implementation is a separate
  number. Under E0 itself, one effect across templates, policies and
  epochs, and independent Bernoulli trials, 2000 seeded replicates per
  trial count give the probability that all 128 contrasts read compatible
  at margin 0.02: 0 at 45000 and 175000, 0.683 at 250000, 0.912 at 275000,
  0.9845 at 300000. The case fixes 300000, the first grid point at or
  above the 0.95 target. Drift, preparation error or a corrected sampling
  law lower this power.
- **Resources.** 300000 eligible trials per setting are 28800000 in all;
  max_shots = 2 x 300000 per iteration. A job bills 1 credit plus 1e-6 per
  shot of its largest iteration's max_shots, so each job costs 1.6 credits
  and the case 12.8; one job per setting would cost 153.6 for the same
  trials ([quandela-credit-optimization.md](../runbooks/quandela-credit-optimization.md)).
  An iteration takes 6.3 s plus 26 us per sample, so a 12-iteration job
  takes about 169 s, 0.56 of the 300 s limit, and the case about 1354 s
  against a 2400 s ceiling. One ANU QRNG request of 192 uint16 values
  (about 2 s, no credits, one of the free tier's 100 monthly requests)
  fixes the 96 compilation seeds and each job's iteration order. The
  written case restates credits and seconds from the live
  `qd_platform.py plan` output before approval; whether 600000 shots yield
  300000 eligible trials on an unmitigated route is a provider question.
- **Scope of an outcome.** A violated cross-template contrast implicates
  preparation, compilation or both; a violated epoch contrast,
  reproducibility across the calibration change; a violated sum rule, the
  combined linear-effect, preparation and conditioning model without
  naming its cause. Policies are compared by what each output represents,
  never by means; a returned iteration names no applied mitigation (its
  fields are the perf, noise, shot-count and computed experiment, circuit
  and input fields), so that answer comes from the provider contract. A mesh hash that varies is not a proven
  varying effect, and identical hashes are not a proven stationary one.
  Passing every family remains necessary and not sufficient.

Before binomial inference the returned object needs its observation
contract: aggregated genuine events or a reconstruction from probabilities,
physical order of samples, the rejected and no-click categories, what shot,
sample and eligible trial mean, the correction calibration, and detector
saturation, dead time or batching that makes trials dependent. Each policy
is a separate immutable execution configuration bound to its serialized
request and the server's effective response. Repeated batches test
dispersion and drift but cannot prove provenance, since a synthetic
multinomial generator passes a binomial dispersion test. Block-correlated,
corrected or resampled data need a likelihood or concentration bound built
for that object, and resampling an estimated distribution never raises the
nominal n.

## Conjecture ledger

Each conjecture names the observable that tests it and what a result can and
cannot establish. A software conversion test, a numerical returned-mesh
comparison and a physical subspace certificate are different evidence
levels and never share one "verified" label.

| Conjecture | Observable test | Falsification or limit |
|---|---|---|
| One common effect describes the preparation bank | six-state sum rules and held-out responses | a validated violation rejects the combined model; passing does not prove physical factorization |
| Equivalent preparation descriptions are operationally equivalent | matched states, different completions, randomized order | a difference beyond the frozen margin rejects the equivalence |
| An empty mitigation list exposes the needed observation level | payload, retained job body, provider acquisition statement | unacknowledged or irrecoverably processed outputs leave M3 unsupported |
| Terminal detector imbalance explains acceptance variation | calibrated efficiencies and held-out thinning predictions | residual coherent or state-dependent acceptance rejects the terminal-only model |
| The intended four-space stays aligned | the a_U / gamma_L certificate | an inconclusive bound is not a falsification; misalignment needs its own evidence |
| A fifth globally low eigenvalue exists | U_5 <= 0.1 c_L, or a confirmed five-space witness | a low complement Rayleigh quotient alone is insufficient |
| Exactly five eigenvalues lie below the threshold | U_5 and L_6 | overlapping intervals leave the count unresolved |
| Complex controls are necessary for the error family | real bank against phase-sensitive controls | agreement on real inputs cannot exclude E_I |
| A label-independent randomized average is the right object | frozen randomization law and held-out epoch tests | label-dependent mixtures or unbounded drift void its interpretation |

Published subspace verification ([2410.12551](../notes/papers/2410.12551.md))
exploits target structure for efficiency once the trusted objects and the
error model are stated; it supplies no provider contract for this detector
measurement.

## Approval boundary

Each qualification case names its settings, processing variants, stopping
rule, maximum credits and the interpretation of every outcome before
submission, and waits for the written-case approval every provider job
needs ([AGENTS.md](../../AGENTS.md#hardware-services)). A passing diagnostic never
extends into the 160-setting acquisition, which needs all three contracts
supported and its own approved case. The historical cost of five jobs and
about six credits at 10^5 trials per setting rests on the processed-output
throughput model and is replanned once raw acquisition, disabled mitigation
or added calibration changes timing or billing.
