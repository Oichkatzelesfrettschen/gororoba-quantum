# Signed sedenion kernel probe on IQM Garnet

The registered proposal `proposed-signed-kernel-probe` perturbs the certified
sedenion kernel u = (e4 - e15)/sqrt2 of L(e1+e10) along L(e2):
B(t) = (L(e1) + L(e10) + t L(e2))/(2 + |t|). The dark probability
||B(t)u||^2 = t^2/(2 + |t|)^2 is even in t, while the dilation overlap
Re<v|B(t)|u> = t/(2 + |t|) is odd and first order
([signed_kernel_probe.py](../../gororoba_quantum/signed_kernel_probe.py)).
The probe asks whether hardware carries that sign. On IBM Heron r2 the
signed circuit compiles to 272 CZ and needs about 1.9 million shots, so it
never ran.

## Why Garnet now

- Garnet's square lattice compiles the structure-matched probe
  (`matched_signed_probe`, one parametrized circuit for every t) to 199 CZ
  on QB6, QB7, QB10, QB11, QB12, QB16 and QB17 (transpiler seed 2 of eight,
  chosen for the largest predicted odd part).
- The reset and billing pilot measured 37.5 us per active-reset shot against
  316 us passive ([timing pilot](iqm-garnet-timing-pilot.md)), and IQM bills
  ceil(runtime).
- The same pilot measured one active-reset cycle leaving QB1 6 % excited, so
  the case adds all-zeros heralding, which discards every shot whose
  pre-circuit measurement is not all zeros.

## Case

`scripts/iqm_signed_probe.py build results/iqm/cases/signed-kernel-probe`
compiles the probe, keeps a copy of the calibration it was planned against
(set `9069c4ef`) and writes `cases.json` (sha256 `31cd9df5...`) and
`prediction.json`; gate `core-638` rebuilds it byte for byte from that copy.

| job | arms | circuits x shots | options |
|---|---|---|---|
| `strong` | t = +0.25, -0.25 | 2 x 20000 | active reset 1 cycle, heralding zeros, calibration set `9069c4ef` |
| `weak` | t = +0.05, -0.05 | 10 x 20000 (5 copies per arm) | same |

Each arm reads <Z> of control qubit 6. The odd part (Z(t) - Z(-t))/2
cancels every offset even in t, readout asymmetry included.

**Falsifier.** An odd part of the sign opposite to t, three standard
errors from zero, at either |t|. An odd part within three standard errors of
zero leaves that arm unresolved; the decision carries no equivalence margin,
so no sample size turns a null reading into a falsification.

**Prediction** (`scripts/iqm_sim.py` noise from the calibration copy plus
ALAP idle T1/T2 relaxation, 400000 sampled shots per arm):

| |t| | law t/(2+|t|) | predicted odd part | predicted even offset |
|---|---|---|---|
| 0.25 | 0.1111 | +0.0296 | +0.0293 |
| 0.05 | 0.0244 | +0.0188 | +0.0290 |

Amplitude damping is not unital, so the modeled odd part is not a fixed
visibility times the law: it is a prediction for this compile, and the
model has no coherent error, leakage or crosstalk. At a heralding retention
of 0.6 the strong arms resolve +0.0296 at about 4.6 standard errors and the
weak arms +0.0188 at about 6.5.

**Cost.** `submit` bounds each job by ceil(1.60 s + expected seconds) at the
live price, since IQM bills ceil(runtime) with no job-side cap and its
estimate (a fixed 1.60 s plus each shot's schedule) bounded the runtime of
both unheralded pilot jobs: 2.00 credits (strong, 1.5 s expected) and 5.00 credits
(weak, 7.5 s expected) on Garnet. The job body pins calibration set
`9069c4ef`, so the device compiles against the calibration the prediction
used, or refuses the job once that set is retired. The case permits only
garnet:mock and garnet. A free garnet:mock run of the previous case bytes
(`dd9cdf84`, identical circuits without the pinned set) accepted both jobs
with heralding and active reset (estimates 3.05 s and 8.86 s, 0.00 credits)
and returned about a quarter of the requested shots, since the mock's random
bits pass the herald at random; the server does not top up rejected
shots.

## Hardware results (2026-10-23)

Both jobs ran under the user's approval on calibration set `9069c4ef`, which
the server confirms it compiled against, and charged 4.50 credits
([analysis](../../results/iqm/signed_kernel_probe_analysis.json), claim
`iqm-garnet-signed-kernel-probe`). Heralding kept 55.9 % of shots in both.

| \|t\| | Z(+t) | Z(-t) | odd part | z | decision | predicted odd |
|---|---|---|---|---|---|---|
| 0.25 | +0.0000 | -0.0441 | +0.0220 +- 0.0067 | 3.29 | sign resolved | +0.0296 |
| 0.05 | -0.0060 | -0.0176 | +0.0058 +- 0.0030 | 1.94 | unresolved | +0.0188 |

The signed law is not falsified, and the device carries the sign of t at
|t| = 0.25. The odd parts fit one visibility, odd = V t/(2 + |t|) with
V = 0.206 +- 0.054 (chi-square 0.08 on 1 degree of freedom): two points do
not reject the linear law, and the simulator departs from it at small |t|: its
non-unital relaxation term predicted +0.0188 at |t| = 0.05, 4.4 standard
errors above the measurement. The even offsets (-0.022 and -0.012) have the
opposite sign to the modeled +0.029. The weak job's runtime (6.52 s)
exceeded its estimate (5.89 s), so a heralded job is bounded by the added
1.60 s rather than by the estimate alone.

## Adversarial audit

`scripts/iqm_probe_audit.py` re-derives four bounds on the reading above
([audit](../../results/iqm/signed_kernel_probe_audit.json), gate `core-640`).

**The circuits compute the law.** Every retained circuit, run noiselessly on
its seven qubits, reads exactly t/(2 + |t|) on QB7; the +t and -t circuits
share one gate sequence and differ only in prx angles, and the five weak
copies are identical. The recompile of seed 2 reproduces the retained arms.

**The signed overlap does not test the kernel.** L_e2^T L_e1 and
L_e2^T L_e10 are antisymmetric, so <L_e2 u, L_e1 u> = <L_e2 u, L_e10 u> = 0
for every real u and Re<v|B(t)|u> = t/(2 + |t|) holds for the bright vector
(e4 + e15)/sqrt2, for e4 and for a random unit vector as for the kernel
vector, and for every replacement sign table on {e4, e15}
(`signed-overlap-kernel-independence`). The e1 and e10 paths drop out one by
one through orthogonality, never through their cancellation. The run
therefore establishes that Garnet carries a relative pi phase on the signed
branch through a 199-CZ compile at visibility near 0.2; it does not establish
a property of the sedenion zero divisor. The dark probability t^2/(2 + |t|)^2
and the cancellation observable below depend on the kernel.

**The kernel is the eigenvalue -1 of L_e1^T L_e10.** (L_e1 + L_e10) u = 0
holds exactly when K = L_e1^T L_e10 maps u to -u. K swaps e4 and e15, so the
kernel vector is its -1 eigenvector and the bright vector its +1
eigenvector, and its -1 eigenspace is four-dimensional, the dimension of a
sedenion zero divisor's annihilator. A Hadamard test whose reference branch
applies L_e1 and whose selector holds cos(theta) on e1 and sin(theta) on
e10 reads cos^2(theta) + sin^2(theta) <L_e1 u, L_e10 u>: cos(2 theta) for the
kernel vector, 1 for the bright vector. One flipped L_e10 sign at e4 or e15,
or 755 of 1000 random sign tables, removes the zero at theta = pi/4, so this
observable carries the zero-divisor sign at first order.

**Coherent error enters both parts at first order.** The derivative of the
measured <Z> with respect to each coherent error of the compile
(`iqm-garnet-signed-probe-coherent-response`):

| error | even part per unit error, \|t\| = 0.05 | odd part per unit error, \|t\| = 0.05 |
|---|---|---|
| QB11 prx over-rotation | -8.02 | -0.59 |
| QB11 residual Z after CZ | -1.56 | -0.05 |
| QB12 prx over-rotation | +1.15 | -0.06 |
| QB6 residual Z after CZ | +0.83 | +0.06 |
| QB7 prx over-rotation | -0.77 | -0.04 |
| CZ QB11-QB12 conditional phase | -0.63 | -0.01 |
| QB6 prx over-rotation | +0.10 | -1.07 |
| QB7 residual Z after CZ | 0.00 | -0.22 |

Readout alone predicts an even part of +0.031 (heralded QB7 errors 0.003 and
0.034), so the measured -0.022 and -0.012 put the circuit's own shift at
-0.055 +- 0.007 and -0.045 +- 0.003. The derivatives above belong to the
noiseless circuit. Through the calibration noise model (the audit's
`noisy_response`: exact density-matrix probabilities with each error inserted
after scheduling) every stationary coherent error moves the even part by 5 to
10 % of its noiseless derivative, the damping differing from error to error
(QB11 over-rotation -0.43 against -8.02, QB12 over-rotation +0.002 against
+1.15), so no single visibility rescales them. QB11's over-rotation alone
would have to be 10.5 %; a pure over-rotation of a pi/2 pulse costs about
delta^2/6 of infidelity, so QB11's randomized-benchmarking infidelity of 5e-4
bounds it at 3.5 %, and all 29 error terms aligned at that bound move the even
part by at most 0.032. The circuit-level offset therefore lies outside the
stationary coherent model under this noise model; leakage read as 1,
crosstalk, time-dependent errors and readout under heralding are untested. Every odd-part derivative vanishes at t = 0 and scales with
the signed amplitude a0 = sqrt(|t|/(2 + |t|)), not with t, so a coherent
error never fakes a sign at t = 0 but adds a term proportional to a0 that
carries the sign of t: odd(t) = sign(t) (V a0^2 + K a0). The measured ratio
odd(0.05)/odd(0.25) = 0.26 +- 0.16 lies between the linear law's 0.22 and the
pure a0 scaling's 0.47, so the pooled visibility V = 0.206 assumes the linear
law rather than testing it.

**Design defects for the next case.** The strong job lists its +t circuit
before its -t circuit and the weak job its five +t circuits before its five
-t circuits, so any reading that depends on batch position enters the odd
part: a device with no signed response and a -0.044 shift on the second
circuit reproduces the strong arm's +0.022 exactly. The sign at |t| = 0.25 is
therefore resolved only under the assumption that position does not move the
reading; the -t copies read -0.012, -0.004, -0.015, -0.025 and -0.032 in
list order. The prediction carried no coherent error, so the even offset and
the small-|t| odd part were outside the model by construction.

## Null-controlled follow-up

The calibration model gives the signed probe an odd part of +0.0136 at
t = 0 (exact density matrix, herald-conditioned readout, set `68b0f1d0`),
where the ideal is zero and every first-order coherent error leaves it zero:
the +0 and -0 circuits differ in their rotation angles, so incoherent noise
acts on them differently. Sampled runs split it by channel (gate
depolarizing alone about +0.014, idle relaxation alone about +0.031). That
null offset carries most of the modeled odd part at |t| = 0.05 (+0.0157), and
subtracting it, D(t) = odd(t) - odd(0), leaves +0.0021 at |t| = 0.05 and
+0.0095 at |t| = 0.25, whose ratio 0.221 matches the linear law's 0.222: the
simulator's apparent small-|t| departure was this additive offset. The
retained Garnet run had no t = 0 arm, so its +0.022 at |t| = 0.25 may hold
an offset of the same size.

[iqm_signed_resolve.py](../../scripts/iqm_signed_resolve.py) builds two
null-controlled cases on the retained 199-CZ compile, each listing +t, -t,
-t, +t blocks at |t| and at t = 0 with QB7 readout calibration and prx
trains on QB6 and QB11 in a second job:

| case | blocks | circuits x shots | ceiling | modeled D(t): calibration / with QB11 +2.7 % | planned z at V = 0.206 |
|---|---|---|---|---|---|
| `signed-kernel-null-retest`, \|t\| = 0.25 | 2 | 16 x 20000 + 10 x 4000 | 7.50 credits | +0.0095 / +0.0059 | 4.8 |
| `signed-kernel-weak-resolve`, \|t\| = 0.05 | 16 | 128 x 20000 (two jobs) + 10 x 4000 | 43.50 credits | +0.0021 / +0.0010 | 3.0 |

The decision at each nonzero |t| reads D(t): resolved three standard errors
above zero, falsified three below, unresolved between. The weak resolve
exceeds the account's 24.00 credits. The re-test decides whether Garnet's
|t| = 0.25 sign survives the null subtraction: the model's visibility after
it is 0.05 to 0.09, under which D(0.25) stays within two standard errors
(0.0047), while the retained run's 0.206 puts it near 4.8. cases.json binds each case's
exact prediction by digest, and garnet:mock ran both re-test jobs of the
current bytes (cases.json `ece7a3f2...`; estimates 13.2 s and 2.04 s,
0.00 credits); its chip
model ran 1.5 times Garnet's estimate on the retained probe, whose measured
24.6 us per heralded shot puts the probe job near 9.5 s against its 12 s
ceiling.
