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
  pooled into one stationary reconstruction. Each observation, epoch
  included, draws its own compilation seed, so a cross-epoch contrast
  compares two compilations of one request rather than one compilation
  twice.
- **Power.** False certification of any family is bounded by alpha; the
  probability of passing an acceptable implementation is a separate
  number. Under E0 itself, one effect across templates, policies and
  epochs, and independent Bernoulli trials, 2000 seeded replicates per
  trial count give the probability that all 128 contrasts read compatible
  at margin 0.02: 0 at 45000 and 175000, 0.683 at 250000, 0.912 at 275000,
  0.9845 at 300000. The case fixes 300000, the first grid point at or
  above the 0.95 target. Drift, preparation error or a corrected sampling
  law lower this power, and the retained runs falsify its premise
  ([Confirmation design](#confirmation-design-and-its-falsified-premise)).
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

## Confirmation design and its falsified premise

The [forensic reconstruction](../notes/quandela/bdsc-acceptance-diagnostics.md#forensic-reconstruction-of-the-retained-belenos-runs)
of the five retained qpu:belenos runs suspends the confirmation design.
Development and diagnostic acquisitions continue under their own approved
cases, and no certification decision is available until the observation
model and the measurement identity support the theorem.

**The banks are phase-blind.** Both pairs send f and g to disjoint outputs,
so every superposition requests the same output intensities. The returned
compiled circuits reproduce those intensities to 2.5e-4 and leave the
relative phase free. The sum rules of these banks therefore test intensity
linearity, the even components m_X = m_Y = m_Z, and the odd components
d_X, d_Y measure setting-to-setting response differences rather than
coherent quadratures. A phase claim needs a measurement that recombines the
two outputs in at least two quadratures.

**Fixed decisions for the next confirmatory case.** These margins are
engineering tolerances, never inferred from the observed deficits, and they
govern a prospective case without reinterpreting a retained one.

| Quantity | Decision |
|---|---|
| Campaign confidence of the qualification contrasts | 99 %, alpha = 0.01 |
| Sum-rule, cross-template and matched-repeat equivalence margins | 0.02 each |
| Campaign power | at least 0.95 |
| Design-point residual of every declared contrast, for power | at most 0.005 |
| Dark-subspace certificate | theta_max <= 10 degrees at joint confidence 0.95 |

**Planning family.** The planning neighborhood of acceptable
implementations is 0 <= F_e <= I with ||F_e - E0||_op <= 0.01. A repeat pair
satisfies ||F_2 - F_1||_op <= 0.003, and each setting adds a fixed
probability perturbation of at most 0.001. The family bounds sum-rule
deviations by 0.004, cross-template deviations by 0.002 and repeat
deviations by 0.005. It plans power without assuming that the hardware
belongs to it, and it imposes no full-effect fidelity requirement on the
subspace certificate.

**Direct-contrast bound.** For a contrast sum_j c_j p_j on independent
bounded trials, the simultaneous Hoeffding radius is
r = sqrt((1/2) sum_j (c_j^2 / n_j) log(2M / alpha)) ([note](../notes/papers/hoeffding-1963.md)).
A union bound needs no independence between contrasts; it does need the
observation assumptions of each one. The two-acquisition design has
M = 128 contrasts, 32 sum rules, 48 template comparisons and 48 temporal
comparisons, and its worst contrast has four unit coefficients. At equal n,
when every true contrast stays within 0.005, the campaign power is at least
1 - 256 exp(-(n/2)(0.015 - r_max)^2), with r_max = sqrt(2 log(25600) / n).
`scripts/bdsc_forensics.py` records the arithmetic (`planning`):

| Eligible trials per setting | Radius r_max | Power lower bound |
|---:|---:|---:|
| 300000 | 0.00823 | 0.7375 |
| 331672 | 0.00782 | 0.9500 |
| 350000 | 0.00762 | 0.9816 |
| 400000 | 0.00712 | 0.9990 |

The bound is conservative: at 300000 trials it gives 0.7375 where the
seeded simulation of the frozen Clopper-Pearson rule under exact E0 gives
0.9845, because the bound allows every contrast a residual of 0.005 and
replaces the exact interval by a concentration inequality.

The calculated power is conditional on the declared observation law,
nuisance model and dependence assumptions, and it is no universal bound on
hardware power. Positive correlations can reduce the effective information,
while other dependence structures or variance-reducing estimators can behave
differently. Detection conditioning does not by itself destroy binomial
sampling, and integer counts do not by themselves establish it.

**The retained observations falsify the planning premise.** The 350000-trial
point describes an independent-binomial design with prescribed small
contrast residuals, and the retained runs do not support it as a prediction
of the present implementation. Within one template the four superpositions
request one output intensity, yet their selected fractions spread by an SD of
0.006 to 0.031, against a reference counting error of 0.0009. Default-policy
residuals reach 0.08, and fixed requests moved by up to 0.071 when the seed,
the characterization and possibly the default processing changed. More trials within one compilation
reduce counting uncertainty and leave a persistent setting-dependent
response untouched: moving from 300000 to 350000 trials changes the reference
error at p = 1/2 from 0.000913 to 0.000845. The 0.02 margins stay. Three
findings stay distinct:

| Finding | Conclusion it supports |
|---|---|
| Responses differ from the ideal probabilities | ideal-response agreement fails at the observed scale |
| Sum-rule residuals exceed the margin under an admitted likelihood | the declared common linear-observation model fails for that case |
| Repeated identical states vary across controlled compilations | compilation-associated variability is measured |

Four-state scatter alone settles none of them, because a fixed effect with
off-diagonal elements spreads the superpositions while satisfying both sum
rules; the acceptance note gives one with an SD of 0.023.

**Randomized compilation is a new estimand.** Suppose there are R
independent seed realizations, B repeat blocks per realization and n trials
per block. Under a hierarchical model,
Var(mu_s) = Var_r(p_sr) / R + E_r[p_sr (1 - p_sr)] / (R B n), and temporal
or correlated components add terms. The first term falls only with
independent compilations, and a persistent mean bias falls with neither. A
contrast c plans against c^T Sigma_seed c, so R B n returned observations are
never independent evidence of the seed-averaged response. An ensemble
certificate needs p_sr = Tr(F_r rho_s) with a state-independent seed law
pi_r. The effect it certifies is then F_bar = sum_r pi_r F_r, and for
positive effects with every pi_r > 0, ker F_bar = intersection_r ker F_r: an exact null survives averaging only
when every component shares it. State-specific compilation, F_sr, admits no
such common operator, and acceptance can reweight seeds among the retained
events. Compiler-seed averaging differs from randomized compiling, which
prescribes a logically equivalent randomization under stated assumptions.

**Next step.** The [crossed diagnostic case](../runbooks/bdsc-qualification-case.md#amendment-of-2026-10-22-a-crossed-diagnostic-replaces-the-confirmation-plan)
([case.json](../evidence/bdsc/diagnostic/case.json)) separates counting noise,
matched-request change between blocks, seed dependence, template and
state-by-seed interaction. Its result chooses among seed selection on
development data, stationarity work, a common-effect investigation, an
ensemble-defined certification case, and moving certification to another
access mode. A confirmation sample count is frozen only after that, and it
is planned over the number of independent compilations as well as trials
per compilation.

The diagnostic selected the stationarity branch, and the
[stationarity case](#stationarity-under-a-stray-detector-veto) below is the
next acquisition.

## Stationarity under a stray-detector veto

The crossed diagnostic selected the stationarity branch on its raw one-click
fractions. Its exploratory reanalysis, `scripts/bdsc_stray_mode_veto.py`
([readout](../../results/quandela/bdsc_stray_mode_veto.json), claim
`qd-belenos-bdsc-stray-mode-veto`), places that change in one detector.
Output mode 5 lies outside every selection and every target support of the
case. Its dark-count rate in each run's receipt (`perfs_at_plan`) is the
largest of any mode: 3137.7 per second before block 1 and 1847.5 before
block 2, while every other mode read at most 80.9.

- **Matched block changes.** Across the 48 matched instances, the mode-5
  share of one-click samples changed by -0.0069 with an SD of 0.0119. All
  other off-support modes together changed by +0.0002 with an SD of 0.0026.
- **Dark-rate tracking.** The block-mean mode-5 share fell from 0.0144 to
  0.0075. The ratio, 0.52, sits near the dark-rate ratio of 0.59.
- **Job-level spread.** The two block-1 jobs share one plan-time reading,
  yet their mean shares differ (0.0123 and 0.0165). A plan-time figure does
  not resolve job-level variation.
- **Perf-exposure diagnostic (no reading).** If acquisition time scaled as
  1 / physical_perf, a fixed dark rate D would make the share rise with
  D / physical_perf. [strategy.md](../notes/quandela/strategy.md) records
  that timing model as unconfirmed, and physical_perf moves with the sample
  budget, so these ranks are reported and decide nothing:
  - within block 1, 0.39 (p 0.006) on 1 / physical_perf;
  - within block 2, -0.13 (p 0.37);
  - pooled on D / physical_perf, 0.19 (p 0.06).
- **Veto result.** With mode 5 vetoed, the heterogeneity of the matched
  changes about their class means falls from 553 to 58.0 on 45 degrees of
  freedom (p 0.09).
  - The two definitions below agree: 57.98 for subtracting mode-5 one-click
    samples and 58.04 for removing the detector from every pattern.
  - The g basis state's block shift reads -0.0007 (z -3.6) instead of
    +0.0035.
  - A common superposition shift of -0.0044 (z -7.2) remains, together with
    the state-by-seed interaction.

Contract C's loss-only identity assumes negligible dark counts, and mode 5
violates that assumption. The veto was chosen after these outcomes were
seen, on runs read descriptively, so it names a hypothesis that the
stationarity case tests on new data.

**The veto definition is frozen on physical grounds before new data.** A
dark click is independent of the prepared state.

- *Alone*, a dark click adds a mode-5 one-click sample to the denominator.
  This is the additive bias.
- *Coincident with a genuine click in mode m*, it turns that sample into a
  two-click pattern. Every mode is thinned by the same factor, so the
  conditional fractions stay unbiased.

The estimators follow from that:

- *Primary (`detector_absent`).* Detector 5 is removed from every detection
  pattern before the one-click rule. The eligible set then does not depend
  on mode 5's rate, and it keeps the coincident trials.
- *Secondary (`subtract`).* Mode-5 one-click samples leave the eligible
  count. It is reported beside the primary.

**The paired falsifier of the dark-click reading** is frozen as
`coincidence_test`. The primary eligible set is the secondary set plus the
coincident trials: patterns with one mode-5 click beside exactly one other
click. The two sets of trials are disjoint within each iteration.

- *Statistic.* For each instance, with c coincident trials, n secondary
  trials and pooled fraction p,
  z = (p_c - p_s) / sqrt(p (1 - p) (1 / c + 1 / n)), where p_c and p_s are
  the selected fractions of the two sets.
- *Pooling.* T is the sum of z^2 over every instance with c > 0 and
  0 < p < 1. It is one statistic, so it needs no multiplicity correction.
- *Calibration.* Coincident counts are as small as one, so a chi-square
  tail does not calibrate T. Under a state-independent dark click, the
  coincident trials are an exchangeable subset of the instance's trials.
  Conditional on each instance's margins, the coincident selected count is
  therefore hypergeometric. The p-value is (1 + #{T* >= T}) / (1 + R) over
  R = 100000 seeded draws of that conditional null (seed 20261023). The
  chi-square tail is reported beside it and decides nothing.
- *Decision.* A resolved reading (p < 0.01) means mode-5 clicks correlate
  with the prepared state and rejects the dark-click reading.
- *Retained data.* T reads 47.7 over 66 instances: conditional p 0.40,
  consistent (the chi-square reference reads 0.96).

The veto names mode 5 by number. The case stops unless mode 5 reads a
plan-time dark-count rate above every one of the other 23 modes, selected
and on-support ones included: a hotter detector would stay inside both veto
estimators.

**A two-block repeat with crossed slots.** Each (template, seed) group runs
in one job slot per block, and the groups of block 1's job 1 run as block
2's job 2 at matched positions (and the reverse).

- *Common shift.* Half the groups move from job 1 to job 2 and half the
  other way. A job-slot effect that adds the same amount to every group
  therefore cancels in the class-mean shift of the superpositions, and that
  shift reads a change between the two acquisition windows. A slot effect
  that differs between groups does not cancel, so this reading assumes an
  additive, group-independent slot effect.
- *Group-by-block contrast.* No group runs in both slots within a block, so
  the class-mean change of the groups that moved from job 1 to job 2, minus
  that of the groups that moved the other way, is confounded: either a slot
  effect or a group-specific change between the windows. It is reported as
  that confounded contrast and decides nothing.

The stationarity case repeats the diagnostic's four frozen requests with
the same seeds, parameters, groups, drawn order, circuit and empty
mitigation list, so it needs no new QRNG read. Only the sample budget
changes, from 40000 to 100000 samples per iteration, with max_shots 120000.
`scripts/bdsc_stationarity.py --check` proves that every other field equals
its source manifest
([case.json](../evidence/bdsc/stationarity/case.json)):

| Block | Jobs | Timing |
|---|---|---|
| S1 | `b1-j1`, then `b1-j2` | first |
| S2 | `b2-j1`, then `b2-j2` | starts at least one hour after S1's last execution ends |

The case does not separate a slow drift from a step change between the two
windows, and it makes no claim of stationarity within one window.

**Preregistered falsifiers and readings,** all under the primary veto.
A test reads resolved at p < 0.01 and consistent at p >= 0.05, as in the
diagnostic.

- **Primary.** The heterogeneity of the S1-to-S2 matched changes about their
  class means reads consistent. A resolved reading falsifies the claim that
  mode 5 carried the instance-specific drift.
- **Dark-click falsifier.** `coincidence_test` on all 96 instances, as
  defined above.
- **Common shift.** The superposition class-mean change S1 to S2, with its
  z, read as a window effect. Whether it repeats the retained -0.0044 in
  sign is reported and decides nothing.
- **Group-by-block contrast.** Reported with its z as a slot or
  group-specific window effect, confounded by design.
- **Reported only.**
  - The raw block change of the mode-5 share against the change of the
    plan-time and post-collection dark-count rates.
  - The mode-5 share against a prediction fixed before submission. The
    plan of 2026-10-23 reads mode 5 at 49520.9 counts/s, against 3137.7 and
    1847.5 before the diagnostic's blocks; every other mode reads at most
    130.6. The share is d / (d + g) for a mode-5 click rate d beside the
    genuine one-click rate g, so a rate-tracking source scales the odds
    s / (1 - s) with the plan-time rate. The retained block-mean shares
    (0.0144 at 3137.7, 0.0075 at 1847.5) then predict 0.17 to 0.19. A share
    near the retained 0.007 to 0.016 means the plan-time figure does not
    track the acquired dark clicks. Either outcome is reported and decides
    nothing. Observed after the fact: b1-j1 read a mean mode-5 share of
    0.093 across its 24 iterations, with a range of 0.019 to 0.276. The
    mean lies between the two predictions, and the spread across settings
    shows that a single job-level odds figure is the wrong form for the
    prediction: the share depends on the setting's genuine one-click rate
    g. About 0.91 of b1-j1's samples stayed eligible under the primary
    veto, against the 0.81 the job-level prediction implied.
  - At that share about 0.81 of each iteration's samples stay eligible
    under the primary veto, so the primary's power against the retained
    residual sits somewhat below the projection's 0.72, which assumed
    every sample eligible.
  - The perf-exposure diagnostic, and the mode-5 share against each job's
    recorded duration per sample, an acquisition exposure that does not
    rest on the unconfirmed physical_perf timing model.
  - The position trend of the mode-5 share in each job. Two diagnostic jobs
    read rank correlations of -0.49 and -0.47.
  - Whether the seed-by-state interaction reproduces at fixed seeds.
  - Whether each returned circuit equals its retained diagnostic
    counterpart.
  - The excess variance tau^2 of the matched changes per class
    (superposition, f, g), raw and under each veto, by the Paule-Mandel
    estimate with its Q-profile 95 % interval, and the share of the raw
    tau^2 that the veto removes. A common tau^2 does not fit the classes:
    the reference errors of f and g lie near 0.0005 and those of the
    superpositions near 0.0035.

**Sensitivity at 100000 samples.** The retained data fix what the primary
test can see
([retained replay](../../results/quandela/bdsc_stationarity_retained.json),
rebuilt by `scripts/bdsc_stationarity.py --check`).

- Under the primary veto the superposition class keeps tau = 0.0021
  (interval to 0.0042), while f and g read tau^2 consistent with zero. The
  veto removes 0.84 of the superpositions' raw tau^2 (lower bound 0.40) and
  all of g's (lower bound 0.98).
- A seeded projection (10000 replicates per scenario, seed 20261023) at
  the retained reference errors scaled to 100000 samples gives the primary
  these readings:
  - with no residual (tau^2 = 0), consistent with probability 0.95;
  - with the retained residual at its point estimate, resolved with
    probability 0.72 (0.19 at 40000 samples).
- A resolved primary therefore separates "mode 5 carried all of the
  instance-specific change" from "a residual superposition change of about
  0.002 remains". The per-class tau^2 states which of the two holds and how
  much the veto removed. It is reported and decides nothing.

**Cost and limits.**

- *Cost.* Each job bills 1 + 1e-6 x 120000 = 1.12 credits, and the four
  total 4.48 credits. The post-calibration repeat of b1-j1 raises the case
  to five jobs and 5.60 credits
  ([calibration hold](../runbooks/bdsc-qualification-case.md#calibration-hold-of-the-stationarity-case)).
  Every retained diagnostic iteration used exactly as
  many shots as samples, so the 1.2 shot margin stops on samples.
- *Duration.* The timing rule (6.3 s plus 26 us per sample per iteration)
  predicts 213.6 s per job, 0.71 of the 300 s limit, and 854.4 s in all.
  The rule is measured only up to 40000 samples per iteration, where the
  four diagnostic jobs ran 164 to 171 s against 176.16 s predicted. A job
  that exceeds its duration fails the samples stop condition and costs that
  job's credits. The written case restates the live `qd_platform.py plan`
  figures.
- *Error calibration.* Standard errors stay reference values under
  independent Bernoulli trials while the provider contract leaves count
  provenance unresolved.
- *Dark-rate timing.* The case records the platform's dark-count reading
  after each collection as well as at plan time.
- *Scope.* A consistent primary reading supports designing a veto-based
  confirmation and certifies nothing.

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
| Per-compilation transfer response carries the superposition scatter | matched seeds across blocks and four seeds per state (diagnostic case) | a matched seed whose response shifts beyond counting puts the scatter in time, not compilation |
| Dark clicks in output mode 5 carry the instance-specific block change | heterogeneity of S1-to-S2 matched changes with detector 5 removed (stationarity case) | a resolved reading rejects it; a resolved coincidence test rejects the dark-click reading |

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
