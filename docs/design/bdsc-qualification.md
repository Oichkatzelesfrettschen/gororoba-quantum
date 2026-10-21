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
case when the live record lacks `specs.architecture`. The qpu:belenos reads
of 2026-10-20 04:09 UTC (`running`) and 08:51 UTC (`calibration`) both lack
the architecture and several processing and version fields
([calibration.md](../notes/quandela/calibration.md)); a missing field reads
as absent, not as the earlier value. A qualification case therefore starts
from a fresh read that passes `plan`. The BDSC target keeps its frozen
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
  different completions on the unused columns (Householder and Givens,
  each checked unitary and at a Frobenius distance above 0.1 on the unused
  columns), crossed with two processing policies: provider defaults
  (`mitigations = None`) and an explicit empty list. One pair gives
  6 x 2 x 2 = 24 settings, the case 48, plus a second epoch that repeats the
  f and g references of every cell: 64 settings.
- **Decision.** Each residual's interval comes from Clopper-Pearson bounds
  at alpha / (8 x 6) per probability, simultaneous over the eight cells at
  alpha = 0.01. It reads compatible inside [-0.05, 0.05], violated when it
  misses that band, and inconclusive otherwise; an interval that merely
  contains zero establishes nothing. Means are compared within a processing
  policy, never across, since mitigation changes estimates by design.
- **Trials and cost.** 22080 eligible trials per setting put E0's expected
  intervals inside the margin. At the strategy.md billing rule, one job per
  setting and max_shots = 2 x 22080, the case costs 66.83 credits; whether
  that many shots yield 22080 eligible trials on an unmitigated route, and
  how long they take, is unknown, so the written case restates the shot
  budget and job count from the provider's answer.
- **Scope of an outcome.** A difference between preparation descriptions
  implicates preparation, compilation or both; between epochs,
  stationarity; between policies, processing rather than hardware drift; a
  violated sum rule rejects the combined linear-effect, preparation and
  conditioning model without naming its cause. A mesh hash that varies is
  not a proven varying effect, and identical hashes are not a proven
  stationary one. Passing every rule remains necessary and not sufficient.

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
| An empty mitigation list exposes the needed observation level | payload, returned metadata, provider acquisition statement | unacknowledged or irrecoverably processed outputs leave M3 unsupported |
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
