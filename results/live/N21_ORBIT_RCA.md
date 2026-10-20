# N=21 orbit feed-forward: coherent kickback phase RCA

Runs on ibm_fez, physical qubits 142 (control), 136 (work 1), 143 (work 4),
144 (work 16), 4096 shots per PUB.

Status: the phases below are model-dependent fit parameters from these runs'
calibrations, not measured rotations. The orbit law depends on the phases
only through theta = phi1 + phi2, so per-round phases are not separately
identifiable from these distributions. PATCH_WINDOW_FINDINGS.md adds a
same-calibration characterization: product-state Ramsey probes show no
resolved window phase, and that run's orbit distributions change with the
window context, with the one-phase model within one residual dimension of the
causal saturated model. The window attribution below is one candidate, not
an established mechanism, and the echo-contrast comparison (0.17 rad fitted,
contrast nearly unchanged) shows why contrast alone cannot settle orbit
phase.

| Run | Job | Charge | Record |
|---|---|---|---|
| Orbit feed-forward | db6ub8svf2bc73d1rc50 | 4 s | 2026-10-13T080216.451663Z |
| Window arms | db6uqdkvf2bc73d1sc80 | 11 s | 2026-10-13T083417.634585Z |

## Calibration

The first run read the 06:27 UTC calibration three times, the last 2 s before
submission. A snapshot stamped 08:01:23 UTC existed when the job ran at
08:02:44 but published after 08:10; its T1, T2 and assignment values for all
four qubits equal the earlier snapshot's. Backend properties report no qubit
frequency, so no calibration age gives the noise model a coherent-phase term.

## Mechanism fit

`scripts/n21_orbit_rca.py` evolves the logical circuit as an exact five-qubit
density matrix and fits each mechanism plus two depolarizing nuisances to the
eight cells of a pair (6 dof). On the first run a work-superposition phase
lowers the deviance from 65.4 to 2.5; mid-circuit assignment (63.8), reset
failure, window T1 and window dephasing (65.4) leave it unchanged, and
terminal assignment needs 14 and 24 percent error rates.

| Arm | Phase (rad) | 95% profile interval | Signed contrast fb / no-fb (model) | Contrast difference |
|---|---|---|---|---|
| first run, nominal | +0.59 | [0.52, 0.68] | +0.090 / -0.107 (0.000 / -0.207) | 0.197 |
| nominal repeat | +0.70 | [0.58, 0.79] | +0.093 / -0.090 (0.000 / -0.198) | 0.183 |
| window_delay (+415 dt idle) | +0.41 | [0.21, 0.58] | +0.040 / -0.071 | 0.111 |
| extra_readout | +0.63 | [0.47, 0.73] | +0.056 / -0.041 | 0.098 |
| window_echo | +0.17 | [0.05, 0.26] | +0.029 / -0.142 (0.007 / -0.195) | 0.170 |

## Hardware-schedule exposure

Idle time of the work qubits from their last round-1 pulse to their first
round-2 pulse, signed by each echo X, read from each PUB's scheduler timing
(dt = 4 ns):

| Arm | Qubit 136 (work 1) | Qubit 144 (work 16) |
|---|---|---|
| nominal fb / no-fb | 962 / 838 | 1412 / 1288 |
| window_delay | 1377 / 1253 | 1827 / 1703 |
| extra_readout | 1378 / 1254 | 1828 / 1704 |
| window_echo | 13 / 6 | 532 / 525 |

The delay and the extra readout lengthen the window by the same 415 dt. The
echo refocuses 136 completely; 144 keeps 532 dt unrefocused because its
round-1 pulses end 248 dt before the window opens.

## Exact-ISA window exposure

The `piecewise` block of each rca-mechanism-fit.json fits one static
detuning per placed window qubit through the archived ISA itself
(`CompiledLaw`): an exact density matrix on the active wires, with a Z
rotation of rate times length on every idle interval the qubit plays inside
the control's measurement-to-feed-forward window, the two depolarizing rounds
at the first measurement and at the terminal one, and the mid-circuit
assignment flip on every write of the recorded bit before the if_else,
the extra readout's second write included. Each qubit's coupling to the work register
in each recorded branch follows from the circuit, so no single-gap sign is
needed. dt is 4 ns from docs/evidence/heron_platform/targets.json.

Work-only gates inside the window split it: in nominal_feedback (window 1426
to 2394 dt) qubit 136 idles over [1373, 2335] and [2381, 2416], qubit 143
over [1419, 2335] and [2393, 2400], and qubit 144 over [1194, 2606]. The
single gap keeps the first interval of each.

| Exposure (083417, 8 members, 24 cells) | G2 | dof | goodness-of-fit p |
|---|---|---|---|
| no detuning | 180.96 | 22 | < 1e-3 |
| single gap, rates on 136, 143, 144 | 27.29 | 19 | 0.10 |
| piecewise, rates on 136, 143, 144 | 26.75 | 19 | 0.11 |

Per pair (piecewise / single gap): nominal 3.5 / 3.1, window_delay 5.4 /
6.5, extra_readout 12.3 / 12.1, window_echo 5.5 / 5.5; without detuning
71.7, 26.9, 45.6 and 36.8. On 080216 both exposures reach G2 1.80 on 1 dof
against 65.42 on 4 without detuning, with five parameters on six cells.

## Findings

- The phase reproduces on the same qubits across a recalibration (0.59, then 0.70).
- The echo arm's phase is 0.17 [0.05, 0.26], disjoint from nominal: most of
  the phase accrues while the work pair idles during the control's
  measurement and reset. The echo removes the per-arm bias (feed-forward
  signed contrast +0.093 to +0.029, model +0.007) and leaves the contrast
  difference unchanged (0.170 against 0.183).
- Adding 415 dt to the window, by idling or by a second readout, cuts the
  contrast difference to 0.111 and 0.098 against model values near 0.21.
  Reported T2 of 89 to 235 us predicts a loss of a few percent.
- Superseded: an earlier analysis revision fitted one quasi-static Gaussian
  detuning per work qubit jointly to all 32 cells (G2 = 49.9 on 18 dof
  against 22.7 for free per-arm phases and 83.6 for static detuning alone).
  The retained [rca-mechanism-fit.json](2026-10-13T083417.634585Z/rca-mechanism-fit.json)
  records that fit as skipped, because the window state is not a branch
  phase on the work bit for residue 1 and joint probes leave the relative
  sign of qubits 136 and 144 unresolved. The three deviances carry no
  current evidence; the fit of Exact-ISA window exposure replaces them.
- Static detuning on the window qubits, evaluated through the archived
  ISA, explains the 083417 orbit family: G2 falls from 181.0 to 26.8 on 19
  dof with three rates (goodness of fit p = 0.11). The likelihood-ratio
  statistic of 154.2 on 3 added parameters is nominal only, because the
  rates are periodic and their likelihood has several basins.
- Splitting the window at work-only pulses does not change the fit: the
  splits are 35 dt on qubit 136 and 7 dt on 143, the piecewise exposure
  lowers G2 by 0.54 at equal parameter count, and the single gap already
  fits the no_feedback members. The unresolved joint probe came from the
  five-qubit logical model, not from the window's segmentation.
  The single gap also has a basin at G2 27.26, with qubit 143 near -0.75
  rad/us, that the seeded search does not start in, so the piecewise gain
  lies between 0.51 and 0.54.
- The fitted rates are not identified: the two exposures' optima, 0.54
  apart in G2, place qubit 136 at -0.160 and +0.163 rad/us and qubit 143 at
  -3.26 and +0.87 rad/us, so no rate is a measured detuning; the deviances
  and segment tables are the result.
- The extra-readout arm misfits the single-phase model (G2 9.3 on 3 dof),
  so its fitted phase does not support a conclusion; the delay arm is
  borderline (5.6). The preregistered ordering assumed the window preserves
  coherence, which the contrast loss contradicts.
- Mid-circuit assignment explains none of the first run's stratum shift. The
  extra readout overwrote its bit, so readout agreement was not measured.
- A coherent phase does not cancel in the contrast difference; the first
  run's agreement with the model's 0.207 combines a phase with extra loss.

## Open candidates and discriminators

1. Fast, window-length-dependent decoherence of the work pair beyond the
   reported T2, for instance a coherent exchange with spectator 143 (which
   holds the orbit bit for 4) or with the other neighbors 123 and 145.
2. Two opposing phase contributions: a readout-associated shift and a static
   detuning.
3. Decisive characterization: window Ramsey on 136 and 144 separately, as
   static circuits on the same patch, sweeping the idle in steps of about
   one readout, with and without a concurrent control readout, recording
   both phase and coherence. It also measures T2* directly; IBM documents
   its reported T2 as a Hahn-echo value, which an unechoed window does not
   follow.

## Contract forecast on the pre-barrier run

083417 fails admissibility (`admissibility`): the no-feedback members leave
the relative sign of 136 and 144 unresolved, and the window_echo members
couple with signs opposite to the reference. The magnitude contracts below
evaluate it anyway, as a forecast for a barrier-equalized run on this patch
and not as a contract verdict; at alpha 0.0167 each:

| Contract | Statistic | Standard error at 4096 / 27648 shots | Forecast |
|---|---:|---|---|
| extra_readout_contrast (T2 bound 0.127) | -0.057 | 0.015 / 0.006 | fails: magnitude 0.070 |
| window_delay magnitude against nominal (bound 1) | -0.048 | 0.015 / 0.006 | fails: magnitude 0.081 |
| window_echo_restoration | +0.015 | 0.015 / 0.006 | passes, on members whose couplings differ from the reference |

`contrast_magnitude` is the hypot of the two signed contrasts, so a static
detuning, and ZZ coupling among the work qubits (a constant phase on each
one-hot branch), leave it unchanged. The forecast loss of about 45 percent
over 415 dt is decoherence: the reported T2 predicts 2 percent, and the
product-state Ramsey of PATCH_WINDOW_FINDINGS.md (R 0.88 and 0.92 at
7.6 us on 136 and 144) predicts less than the delay arm shows. Two
candidates remain and the next acquisition separates them:

- Qubit 143, the control's neighbor, which carries the orbit amplitude for
  residue 4 and sat in |0> in every product probe, dephases during and after
  the control's readout: a 143 Ramsey decays faster across a measured
  control than across a reset-only reference, and the orbit magnitude falls
  monotonically with added window length.
- The control's state after reset is imperfect: the orbit magnitude falls
  by one step at the first added window and stays flat as it grows.

## Window sweep on a barrier-equalized run

Record 2026-10-19T151959.226467Z, job dbb3auvi0auc7392sfs0, ibm_fez under
the 2026-10-19T07:44:14-07:00 calibration, 14 PUBs of 16384 shots with the
initialization herald, 18 s charged; analysis in
[between-arm.json](2026-10-19T151959.226467Z/between-arm.json). The family
is admissible and both heralds admit (contract shift upper limits 0.0132
orbit, 0.0112 spectator). The placement reuses the four qubits of 083417
with other roles: control 144, work bit 1 on 142, work bit 4 on 143, work
bit 16 on 136, against control 142, 136, 143, 144 there, so neither run
predicts the other.

| Pair | Contrast magnitude |
|---|---:|
| nominal | 0.151 |
| window_delay (+415 dt) | 0.144 |
| window_delay_long (+830 dt) | 0.152 |
| extra_readout | 0.142 |
| window_echo | 0.147 |

Each magnitude carries a standard error near 0.008. Contracts at alpha 0.01:

- window_delay_ramp fails: the doubled delay reads 0.008 above the single
  one, so added window length costs no resolved coherence on this
  assignment, and neither a growing loss nor a one-time step appears.
- extra_readout_contrast fails through the herald margin alone: the
  magnitude lies 0.006 +- 0.008 below its T2 bound before the 0.013 margin.
- window_echo_restoration passes with an upper limit of +0.0002.
- spectator_window_dephasing fails: qubit 143 reads visibility 0.587
  across the measured control and 0.591 across the reset-only reference.
- window_delay_phase_slope fails (statistic 40.4 against 6.63): the two
  coupled qubits, 136 (+) and 142 (-), lengthen by the same 415 dt, so the
  signed exposure stays 519 dt while the fitted phase moves from -1.16 to
  -0.93 rad. A static detuning on the coupled qubits does not describe the
  phase.

The spectator branches differ by -0.114 +- 0.027 rad between the control's
recorded outcomes, a ZZ(144, 143) phase over the window (descriptive). Both
spectator kinds hold 0.59 visibility against 0.99 in the calibration model,
so qubit 143 loses coherence across the window without the control's
measurement, and the branch turn reduces the pooled visibility by under
1 percent. 143's own dephasing and a disturbance from the control's reset
remain the candidates; a 143 Ramsey with an idle control separates them.

The 083417 window loss of about 45 percent does not appear on this
assignment and calibration. The role assignment and the calibration week
both changed between the runs, so a run that holds the control on 142
separates them.

## Readout overlap on the pinned roles

Record 2026-10-19T170620.832658Z, job dbb4se1gv2cc73e7pf40, ibm_fez under
the 2026-10-19T09:47:37-07:00 calibration, 12 PUBs of 8192 shots with the
initialization herald, 9 s charged; analysis in
[between-arm.json](2026-10-19T170620.832658Z/between-arm.json).
`--pin-layout ibm_fez:142,136,143,144` holds 083417's roles: control 142,
work bit 1 on 136, bit 4 on 143, bit 16 on 144. The unbracketed window_delay
pair drops the window barriers and compiles to 083417's window_delay
program: 43 CZ, and the same partial order over every CZ, readout, reset
and delay. Its bracketed twin plays 44 CZ, so the barrier costs one CZ and
biases against an overlap loss. Contracts at alpha 0.0125:

| Contract | Measured | Verdict |
|---|---|---|
| window_overlap_loss | unbracketed 0.094 against bracketed 0.228 (upper limit -0.110) | pass |
| window_delay_pinned_loss | bracketed window_delay 0.228 against nominal 0.235 (upper limit +0.017) | fail |
| spectator_idle_dephasing | qubit 143 visibility 0.611 after an idle of 836 dt against 0.994 at once | pass |
| spectator_readout_dephasing | reset_only 0.593 against idle 0.611 (upper limit +0.010) | fail |

The barrier-free delay arm reproduces 083417's loss (0.094 here, 0.081
there) on today's calibration, and the bracketed arms on the same roles
lose nothing to the added 415 dt. A work CZ(136, 143) that the dependency
order leaves free to run during the control's measure-and-reset span costs
the orbit about 59 percent of its contrast magnitude; the role assignment
does not. The run establishes the overlap cost on this calibration; that the
same overlap produced 083417's loss is the inference its identical program
supports.

The orbit's round-two coherence lives in the work register's |1> +- |4>
superposition, which spans bit 1 (136) and bit 4 (143), so dephasing of
those work qubits during the window lowers the contrast every arm carries.
Qubit 143 loses 38 percent of its Ramsey visibility across an idle with no
readout anywhere, while its reported (echo) T2 of 111 us predicts 3
percent; the control's reset readout adds nothing resolved. During the idle
the control sits in |+> unrecorded, so the loss combines 143's T2* with any
ZZ phase to 142; a 143 Ramsey with the control in |0> separates the two.
The nominal magnitude reads 0.235 on these roles against 0.151 on the
control-144 assignment of 151959.

## Spectator dephasing with the control grounded

Record 2026-10-19T231043.083602Z, job dbba739gv2cc73e81dg0, ibm_fez under
the 2026-10-19T15:07:33-07:00 calibration, 6 PUBs of 8192 shots with the
initialization herald, 5 s charged; analysis in
[between-arm.json](2026-10-19T231043.083602Z/between-arm.json).
`--pin-layout ibm_fez:142,136,143,144` keeps the roles of the readout-overlap
split. Each arm reads qubit 143's Ramsey visibility from its X and Y
expectations: at once (immediate), after the 836 dt idle with the control in
|+> (idle), and after the same idle with the control held in |0>
(idle_ground). Contracts at alpha 0.025, herald shift bound 0.020:

| Contract | Measured | Verdict |
|---|---|---|
| spectator_control_zz | idle 0.616 against idle_ground 0.622 (upper limit +0.021) | fail |
| spectator_ground_idle_dephasing | idle_ground 0.622 against immediate 0.989 (upper limit -0.348) | pass |

Both arms keep only the shots whose initialization herald reads the control
0, and the spectator herald admits those shots; Bonferroni splits the family
alpha 0.05 equally over that admission and both contracts (0.0167 each), and
the herald leaves a 0.0101 margin. A failed spectator_control_zz bounds the ZZ share
rather than excluding it: holding the control in |0> recovers 0.005 of
visibility, and at most 0.042 (the 0.0167 lower confidence limit of the
idle-minus-idle_ground statistic, -0.032, plus the herald margin), against
the 0.367 qubit 143 loses across the idle with the control grounded. A
control-state-dependent coupling to 142 therefore accounts for at most about
11 percent of the window loss. The dominant loss, about 37 percent of the
Ramsey visibility across 836 dt (3.3 us), belongs to 143 itself and not to
its coupling with the control. A pure exponential decay through these two
points would place T2* near 7 us; the delay sweep of the next section
refutes that reading, because the visibility revives at longer idles, so
the 3.3 us loss is the first descent of a coherent beat rather than
dephasing.

## Ramsey delay sweep with the control grounded

Approved dry run 2026-10-20T031107.452802Z (consumed), run
2026-10-20T031212.175942Z, job dbbdog8c77vs73846ceg, ibm_fez, 14 PUBs of
12288 shots with the initialization herald, 15 s charged; preregistered
analysis in [ramsey.json](2026-10-20T031212.175942Z/ramsey.json)
(scripts/n21_spectator_ramsey.py, gate core-603), case in
[N21_SPECTATOR_RAMSEY_CASE.md](N21_SPECTATOR_RAMSEY_CASE.md). The pinned
roles of the previous section hold; qubit 143 idles k windows of 836 dt with
control 142 in |0>, and each delay reads X and Y over the shots whose herald
reads all four pinned qubits 0.

| Idle (us) | 0 | 3.344 | 6.688 | 10.032 | 13.376 | 16.720 | 20.064 |
|---|---|---|---|---|---|---|---|
| Visibility | 0.997 | 0.612 | 0.395 | 0.885 | 0.743 | 0.255 | 0.705 |

Preregistered verdicts, family alpha 0.05 split equally over four tests
(0.0125 each):

| Test | Reading | Verdict |
|---|---|---|
| spectator_herald_admission | every bit (142, 136, 143, 144) passes its excitation-spread bound | admitted |
| decay_shape | free stretch exponent beta 0.5, at the fit's lower bound | neither |
| detuning | 26.3 kHz, interval 25.7 to 27.0 kHz | detuned |
| ringdown_consistency | no fixed beta extrapolates the idle points to t = 0 | not_evaluable |

The shape fit sits on its 0.5 bound, so its Wald interval (0.41 to 0.59)
describes no identified parameter, and the detuning comes from a
single-frequency model the data contradict, so 26.3 kHz is no valid
detuning estimate. The control-only selection reads the same visibilities
within 0.002.

Finding: visibility falls to 0.395 at 6.7 us, revives to 0.885 at 10.0 us,
falls to 0.255 at 16.7 us and revives to 0.705 at 20.1 us. A dephasing
envelope is monotone, so the window loss is coherent beating between two
frequency components of qubit 143, and T2* of 7 us is withdrawn.

Descriptive fit, outside the preregistration: the two-component model
V(t) = |a + (1 - a) exp(2 pi i df t)| exp(-t / T) fits the seven points
with a = 0.65, an envelope T near 126 us and residual sum of squares
3.8e-5. The 3.344 us sampling aliases df: 89.8, 209.3, 388.8 and 508.3 kHz
fit equally, so the splitting is undetermined beyond df = 89.8 + k 299.0
or 209.3 + k 299.0 kHz.

Inference, medium confidence: a 0.65 / 0.35 split between two frequencies
fits charge-parity splitting of 143's transition or a coupling to a
two-level system. A ZZ shift from an excited neighbor is disfavored,
because the all-zero herald selection removes shots with any pinned
neighbor excited and reads the same beat. A dense sweep at about 0.25 us
steps over 0 to 20 us resolves both components and df without aliasing;
repeating it over hours separates a parity splitting from a TLS coupling
by the discriminators of the next section (a parity df moves with the
offset charge, a TLS keeps g fixed). A single-component decay at that
resolution falsifies the beat reading.

## Beat models of qubit 143 (descriptive, post hoc)

Everything in this section is descriptive: the models, the band and the
design were chosen after the sweep was read, outside its preregistration.
[beat-model.json](2026-10-20T031212.175942Z/beat-model.json) holds the
analysis (scripts/n21_q143_beat_model.py; gate core-604 runs its planted
self-check, core-605 regenerates the file byte for byte). The data are the
all-zero herald-selected counts of the 14 PUBs.

**Signal and readout.** Each model predicts S(t) = <X> + i<Y> = A e^(i phi)
e^(-t/T) g(t) (t in us, frequencies in MHz, a level raised by E contributes
e^(-2 pi i E t)). The measured mean is (1 - e0 - e1) mu + (e1 - e0) with
e0 = prob_meas1_prep0 and e1 = prob_meas0_prep1 of qubit 143 (10 and 35
counts of 4096 at execution start), carried as nuisances with their
binomial calibration terms. The likelihood is binomial on every point's
herald-selected zero count.

| Model | g(t) | Parameters |
|---|---|---|
| single | e^(2 pi i f t) | A, T, phi, e0, e1, f (6) |
| static | a e^(2 pi i f1 t) + (1 - a) e^(2 pi i (f1 + df) t), a >= 1/2 | + a, f1, df (8) |
| telegraph | 1^T exp(M t) p, M = 2 pi i diag(f1, f1 + df) + W, p = (a, 1 - a), W stationary at p with total rate gamma | + gamma (9) |
| tls | Lindblad, qubit x TLS, H = fq n_q + ft n_t + g (s+ t- + s- t+), qubit T1 (calibrated) and dephasing, TLS relaxation gamma_tls | + gamma_tls (9) |

Telegraph returns static at gamma = 0 and narrows to the mean line,
e^(2 pi i fbar t - a (1 - a) (2 pi df)^2 t / gamma), at gamma >> 2 pi |df|
(Kubo-Anderson; self-check telegraph_limits). The closed exchange pair puts
weight cos^2 theta and sin^2 theta on its two dressed lines in both TLS
branches, so its Ramsey signal is static with Omega = sqrt(Delta^2 + 4 g^2)
= |df|, Delta = df (2a - 1) and g = |df| sqrt(a (1 - a)), and the TLS
thermal population p drops out exactly (self-check tls: p = 0 and p = 0.3
agree to rounding). A three-level transmon couples |1, 1> to |2, 0>, which
moves the warm signal by 4e-4 over 20 us at an assumed anharmonicity of
-300 MHz, so p stays unidentified and the fits fix p = 0. tls departs from
static only through the dissipative mixing of the dressed lines and, in a
design with a Z read after an X preparation, through the population swap
of depth 4 a (1 - a).

**Lattice.** The idles are k T0, T0 = 836 dt = 3.344 us, f0 = 1 / T0 =
299.04 kHz. Every model's prediction depends on e^(2 pi i f k T0) only
through f mod f0 when the whole spectrum shifts (common mode, exact in all
four models), and static and single also depend on df only mod f0 (exact;
self-check aliases, gap 0). Telegraph and tls break the relative alias only
at order gamma T0. X and Y together fix the sign of df: the heavier line's
phase track is observed, so df -> -df (the twin of the visibility-only fit,
89.8 versus 209.3 kHz) refits worse by 5434 in NLL.

**Fits.** static: a = 0.6438 +- 0.0028, df = -90.00 +- 0.15 kHz (mod
299.04), f1 = 24.88 +- 0.12 kHz (mod 299.04), T = 134 +- 6 us, A at its
bound 1, e0 = 0.0020, e1 = 0.0080; deviance against the saturated model
9.3 on 8 degrees of freedom. The lighter line's Ramsey frequency sits
90.0 kHz below the heavier one's, modulo 299.04 kHz; its level energy
sits that much above.

| Model | NLL - static | 2 dNLL vs static | dAIC | dBIC | Bootstrap p (64 replicates) |
|---|---|---|---|---|---|
| single | +5827.0 | 11654 | +11650 | +11630 | below 1/65 (replicate max 6.9) |
| static | 0 | -- | 0 | 0 | -- |
| telegraph | -0.103 | 0.21 | +1.8 | +11.8 | 0.34 |
| tls | -0.103 | 0.21 | +1.8 | +11.8 | 0.69 |

The likelihood ratios are calibrated by parametric bootstrap from the
fitted null, because single sits inside static at a = 1 with f2
unidentified and static inside telegraph at the boundary gamma = 0.
Telegraph (gamma = 0.0033 per us) and tls (gamma_tls = 0.019 per us) reach
the same NLL at every alias to 1e-3: at these rates each acts as one
differential damping of the two lines, which the data do not resolve.

**Alias table.** Every df in |df| < 2 MHz ties under static (dNLL 0 to
rounding); telegraph and tls separate them by at most 0.07 in NLL. g and
Delta are the tls readings of each alias.

| n | df (kHz) | static dNLL | telegraph dNLL | tls dNLL | g (kHz) | Delta (kHz) |
|---|---|---|---|---|---|---|
| -6 | -1884.3 | 0 | -0.089 | -0.089 | 903.5 | -534.0 |
| -5 | -1585.2 | 0 | -0.090 | -0.090 | 760.1 | -449.3 |
| -4 | -1286.2 | 0 | -0.091 | -0.091 | 616.7 | -364.5 |
| -3 | -987.1 | 0 | -0.093 | -0.093 | 473.4 | -279.7 |
| -2 | -688.1 | 0 | -0.096 | -0.096 | 330.0 | -194.9 |
| -1 | -389.0 | 0 | -0.103 | -0.103 | 186.6 | -110.2 |
| 0 | -90.0 | 0 | -0.090 | -0.090 | 43.2 | -25.7 |
| 1 | 209.0 | 0 | -0.035 | -0.035 | 100.2 | 59.7 |
| 2 | 508.1 | 0 | -0.062 | -0.062 | 243.6 | 144.4 |
| 3 | 807.1 | 0 | -0.070 | -0.070 | 387.0 | 229.2 |
| 4 | 1106.2 | 0 | -0.074 | -0.074 | 530.3 | 314.0 |
| 5 | 1405.2 | 0 | -0.076 | -0.076 | 673.7 | 398.8 |
| 6 | 1704.2 | 0 | -0.077 | -0.077 | 817.1 | 483.6 |

**What the data decide.** Decided: two lines, not one (LR 11654); weights
0.644 / 0.356; the sign of df (lighter line below the heavier one in the
frame's convention); df = -90.00 kHz modulo 299.04 kHz; an envelope of
134 us, near 143's calibrated T2 of 111 us, so both lines stay coherent
over the 20 us sweep. Undecided: which alias n (13 in the band), the
absolute frequencies modulo 299.04 kHz, and static versus telegraph versus
tls (no rate is detected). Charge dispersion (Koch et al. 2007, eq. 2.18)
over f01 4.5 to 5.4 GHz and E_C 0.28 to 0.34 GHz spans 10 kHz to 2.2 MHz,
since Heron r2 properties publish neither frequency nor anharmonicity for
143, so every alias fits the parity magnitude. Equal parity occupation
predicts a = 1/2, and a = 0.644 sits 51 standard errors from it, so a
parity reading needs an occupation imbalance; an exchange-coupled TLS
takes a = (1 + |Delta| / Omega) / 2 without constraint.

**Follow-up design** (design data under follow_up in beat-model.json;
live_run and the planner carry no delay-member builder for it). Expected
log-likelihood ratios come from Asimov counts: the closest alternative's
minimum NLL on the truth's expected counts, which equals the summed
binomial KL divergence. Delays are integer dt; one shot count per PUB.

| Design | Members x shots | Rule (s) | Worst neighboring-alias LLR | tls vs static | static vs tls | telegraph gamma 0.01 / 0.03 / 0.1 per us |
|---|---|---|---|---|---|---|
| run_lattice (reference) | 14 x 12288 | 16.2 | 0 | 0.10 | 0.00002 | 1.9 / 14.3 / 86.4 |
| dense: 0.252 us grid to 35.3 us, X Y | 282 x 512 | 15.1 | 4453 | 0.29 | 0.0000002 | 2.8 / 17.6 / 74.5 |
| coprime_swap: 693 and 819 dt lattices, X Y Z | 69 x 2048 | 14.7 | 1599 | 25645 | 2646 | 1.7 / 11.1 / 46.0 |
| coprime_swap_long: + 60 to 360 us | 81 x 2048 | 21.3 | 1771 | 26976 | 2763 | 3.3 / 14.0 / 46.2 |

coprime_swap is the cheapest design that reaches 50 in every column the
selection rule names: 23 delays (0, multiples of 693 dt to 8316 dt and of
819 dt to 8190 dt; gcd 63 dt = 0.252 us, an unaliased complex band of
3.97 MHz), X and Y after the |+> preparation and Z after an X preparation,
2048 shots each. Its worst alias pair reads posterior odds 10^-694 at
equal priors, the Z swap separates tls from static by 2646 to 25645, and
at the static fit its Wald errors are a +- 0.0037, df +- 0.14 kHz, T +- 5
us. A telegraph rate below about 0.03 per us stays undetected (LLR 11).
The dense grid resolves the aliases but has no Z read and cannot separate
tls from static.

**Cost.** The rule 2.3 s + shots x (rep_delay 50 us + INIT/FINI 8.85 us +
circuit duration) per member gives 16.2 s for the retained run, which was
charged 15 s; its circuits_execution_time of 12.38 s equals shots x
(rep_delay + duration) exactly, and the charge adds 2.62 s. coprime_swap
reads 14.7 s by the rule and 13.8 s by the run's own execution-plus-offset
measure.

**Repeat in time.** Four coprime_swap runs at least 60 min apart (one
calibration cycle each), 58.9 s by the rule. Charge parity predicts a near
the same value each run, df moving with the offset charge within
|eps1 - eps0|, and plain T1 decay in Z. A TLS predicts g = |df| sqrt(a (1 - a))
fixed while Delta = df (2a - 1) and a wander with the TLS frequency, and Z
swap oscillation at Omega = |df| with depth 4 a (1 - a), 0.92 at a = 0.644.
Constant a, df and f1 with no Z swap leave a static splitting the models
here do not name. Each per-run estimate enters a chi-square homogeneity
test against its inverse-variance mean (3 degrees of freedom) at the
follow-up case's family alpha.

## Mitigation

The explicit delay-X-delay-X echo survives transpilation (planning contract)
and removes the per-arm bias. IBM rejects dynamical decoupling on dynamic
circuits, so a placement-aware echo, timed so each work qubit's halves are
balanced from its own last pulse, is the engineering follow-up; 144's
unbalanced 532 dt shows the halves must start at each qubit's own idle start.
