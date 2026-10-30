# N=21 orbit detuning-sign test: findings

The orbit's relative phase turns at the frame offset of the work bit for 16 minus that of the work bit for 1, with
its sign, on every replica that resolves it. The no-feedback residual of the window-dose sweep (Kingston job
`dbg04idjm0ks73efj0j0`) is therefore a precession of the two work qubits' frequencies off the frames the gates track,
and the Hahn echo refocuses it.

## Run

ibm_kingston job `dbge2jpj4t8s73ac6fk0` on the primary instance, planned at calibration 2026-10-27T09:07:55-07:00 and
executed under 2026-10-27T10:34:08-07:00 (`collect.json`), under the
approved envelope [n21-orbit-detuning-sign-envelope.md](../../../docs/design/n21-orbit-detuning-sign-envelope.md).
`scripts/n21_detuning_sign_run.sh --submit` planned `2026-10-27T173041.727190Z` on the calibration in force, the
preflight admitted it, and this run submitted it: 19 replicas, 56 PUBs of 4,096 shots in one dynamic job at the
20 us repetition delay, `dose_roles` one = 0 and sixteen = 3. The service billed 17 s against the planner's 15.35 s.
`scripts/n21_detuning_sign.py` wrote [detuning-sign-decisions.json](detuning-sign-decisions.json) from the raw
registers, and gate `core-n21-detuning-sign-replay` replays it.

## Decisions

| Decision | Result | Verdict |
|---|---|---|
| D1, slope of f_orbit on f_sixteen - f_one through the origin | 1.010, 95 percent interval [0.977, 1.043], 18 replicas, chi2 106.8 on 17 | holds |
| D1, free-intercept fit (reported) | slope 1.021, intercept -0.30 kHz | |
| D2, sign agreement among resolved replicas | 17 of 17 | holds |
| D3, echo within three standard errors of the undosed phase | 17 of 17 moved replicas, none with an unresolved echo | holds |

## Replicas

Rates in kHz with their standard errors; the echo column is the echo phase minus the undosed phase in radians.

| qubit for 1 | qubit for 16 | f_one | f_sixteen | f_sixteen - f_one | f_orbit | echo return |
|---|---|---|---|---|---|---|
| 151 | 148 | -2.12 ± 0.07 | +1.62 ± 0.07 | +3.74 | +3.86 ± 0.63 | -0.068 ± 0.163 |
| 107 | 117 | -4.16 ± 0.05 | -13.79 ± 0.07 | -9.63 | -9.49 ± 0.32 | -0.051 ± 0.075 |
| 3 | 0 | -0.09 ± 0.06 | -3.84 ± 0.09 | -3.75 | -5.62 ± 0.17 | -0.026 ± 0.085 |
| 19 | 13 | -7.84 ± 0.07 | +2.27 ± 0.05 | +10.12 | +10.03 ± 0.14 | -0.050 ± 0.069 |
| 59 | 73 | -11.09 ± 0.05 | -2.08 ± 0.06 | +9.00 | +9.01 ± 0.18 | -0.023 ± 0.076 |
| 63 | 77 | -7.55 ± 0.10 | -1.65 ± 0.05 | +5.90 | +5.41 ± 0.22 | -0.040 ± 0.108 |
| 80 | 83 | -6.77 ± 0.06 | +11.69 ± 0.06 | +18.46 | +18.04 ± 0.36 | +0.110 ± 0.087 |
| 99 | 93 | +30.24 ± 1.39 | -3.25 ± 0.06 | -33.49 | -34.59 ± 1.61 | +0.096 ± 0.104 |
| 47 | 44 | +3.79 ± 0.05 | -12.67 ± 0.07 | -16.46 | -16.99 ± 0.32 | -0.138 ± 0.077 |
| 34 | 31 | -1.46 ± 0.06 | +12.00 ± 0.08 | +13.46 | +13.55 ± 0.17 | +0.088 ± 0.070 |
| 58 | 69 | +2.82 ± 0.11 | +2.82 ± 0.06 | -0.00 | -0.18 ± 0.25 | -0.057 ± 0.088 |
| 21 | 42 | -19.93 ± 0.06 | -3.31 ± 0.06 | +16.62 | +16.76 ± 0.39 | -0.024 ± 0.118 |
| 111 | 118 | -4.76 ± 0.06 | -3.37 ± 0.07 | +1.39 | +1.29 ± 0.19 | -0.235 ± 0.114 |
| 132 | 135 | +7.66 ± 0.07 | -2.61 ± 0.11 | -10.28 | -10.42 ± 0.39 | +0.253 ± 0.130 |
| 29 | 26 | +9.57 ± 0.20 | -14.92 ± 0.08 | -24.49 | -25.90 ± 0.93 | +0.003 ± 0.139 |
| 144 | 141 | +2.49 ± 0.05 | +5.22 ± 0.08 | +2.73 | +3.49 ± 0.21 | +0.144 ± 0.089 |
| 103 | 116 | +0.99 ± 0.07 | -12.02 ± 0.05 | -13.01 | -12.88 ± 0.32 | +0.119 ± 0.091 |
| 8 | 5 | -8.65 ± 0.07 | +3.07 ± 0.08 | +11.72 | +11.52 ± 0.72 | +0.296 ± 0.189 |
| 88 | 91 | -1.99 ± 0.60 | -6.59 ± 0.07 | -4.59 | unresolved | unresolved |

The pair 58 and 69 carries equal Ramsey offsets, 2.82 kHz each, so the account predicts no orbit precession, and
the orbit reads -0.18 ± 0.25 kHz: the relative phase follows the difference of the offsets, not either offset alone.
The pair 88 and 91 resolves its orbit amplitude at the first two doses only, fewer than the four a rate needs, and
the decisions leave it out of all three.

## Limits

The slope's chi2 of 106.8 on 17 degrees of freedom puts the scatter about the line at 2.5 times the shot noise in
standard deviation; the interval carries the factor sqrt(chi2/df). The largest residual is the pair 3 and 0, whose
orbit turns at -5.62 ± 0.17 kHz against -3.75 predicted. The orbit and Ramsey members run as separate PUBs, so a
qubit frequency that wanders by a few hundred hertz between them would produce this excess; the run cannot separate
that from a shift the orbit's own gates impose on one qubit. A repeat that interleaves each dose's orbit and Ramsey
shots, or one on a later calibration, would decide it.

## Corrections

The first decomposition of the window-dose sweep placed the dose-time excitation on initial-layout positions 1 and
3; the compiled program holds it on positions 0 and 3, which are not adjacent. Static ZZ coupling stays excluded
because each replica holds one excitation with its neighbors in |0> and no replica neighbors another, and the
idle-penalty Ramsey comparison, built on positions 1 and 3, is withdrawn.

## Retention

The primary inventory observed at 2026-10-28T00:29:17Z lists the job settled at 17 s, and the regenerated retention
audit binds its raw archive. The research registry holds the run as acquisition `kingston-n21-detuning-sign` under
claim `kingston-n21-detuning-sign-precession`.
