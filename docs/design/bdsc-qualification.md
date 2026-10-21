# Belenos dark-subspace certificate: provider qualification

The 160-setting certificate of [bdsc.md](../notes/quandela/bdsc.md) needs
three provider contracts that no retained run establishes: one measurement
effect shared by every preparation, a declared level of the acquisition
chain that its confidence analysis attaches to, and an acceptance effect
proportional to the identity or bounded away from it. M2 to M4 of the
qualification table stay blocked until each contract is supported. This
document states each contract, the qualification measurement that tests
it, and the claim each outcome supports. No acquisition is authorized by
it; each run below waits for its own written case.

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

Basis-state injection into a fixed unitary is insufficient on its own:
basis probabilities fix the diagonal of F, and the bank's real and
imaginary pairs carry the off-diagonals. The questions for Quandela are
whether a requested full transformation can be preserved, whether a native
architecture configuration can run without state-specific optimization, and
whether coherent inputs can be injected independently of the readout. No
`no_transpile` parameter is documented, and none is assumed.

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
