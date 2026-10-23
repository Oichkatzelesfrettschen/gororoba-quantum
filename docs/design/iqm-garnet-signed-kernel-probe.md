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

**Falsifier.** An odd part of zero, or of the sign opposite to t, at either
|t|, at three standard errors.

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
V = 0.206 +- 0.054 (chi-square 0.08 on 1 degree of freedom), so the hardware
follows the linear law the simulator departs from at small |t|: its
non-unital relaxation term predicted +0.0188 at |t| = 0.05, 4.4 standard
errors above the measurement. The even offsets (-0.022 and -0.012) have the
opposite sign to the modeled +0.029. The weak job's runtime (6.52 s)
exceeded its estimate (5.89 s), so a heralded job is bounded by the added
1.60 s rather than by the estimate alone.
