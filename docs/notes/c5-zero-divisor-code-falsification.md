# C5: zero-divisor code — falsified thought experiment (2026-10-19)

## The conjecture

The 84 zero-divisor pairs of the sedenion census form a classical code.
Message i selects the pair (a_i, b_i) with a_i * b_i = 0; the transmitter
sends the signed blade b_i; the receiver tests the 84 candidate annihilators
a_j and decodes ihat = argmin_j ||a_j * v||. In the noiseless case the
correct annihilator gives exactly zero (algebraic null, infinite contrast)
while wrong annihilators give generically nonzero products. The 84 messages
carry ~6.4 bits in 16 dimensions. The Belenos mesh had already demonstrated
the receive half: per-edge dark-port rates (dark_a ~ 0.028-0.069) are
null-attenuation measurements on 84 channels.

## The falsifier

$0 simulation, defined before running: the 84-pair annihilation code must
beat a random 84-codeword spherical code in 16 dimensions with a matched-filter
decoder, at the same rate, under additive Gaussian noise. Script:
`~/workspace/c5-sim/sim_c5.py` (precomputed annihilator matrices, vectorized
Monte Carlo, 40 messages x 400 trials x 8 noise levels).

## Result: falsified

| noise sigma | algebraic + annihilation (C5) | algebraic + matched filter | random + matched filter |
|---|---|---|---|
| 0.01 | 0.762 | 0.275 | 0.000 |
| 0.05 | 0.755 | 0.275 | 0.000 |
| 0.10 | 0.753 | 0.275 | 0.000 |
| 0.20 | 0.800 | 0.316 | 0.046 |
| 0.50 | 0.949 | 0.777 | 0.714 |

C5 fails at near-zero noise (BER 0.76) where random coding is perfect (BER 0.00).
The gap is not close and not a tuning problem.

## Structural cause

- Mean 3.9 exact annihilator ties per codeword: each transmitted blade is
  killed exactly by ~4 of the 84 annihilators, so argmin decoding ties ~5
  ways on almost every message.
- Only 35 distinct annihilator-set signatures exist among the 84 codewords.
- Only 57 distinct transmitted blades (27 duplicates from the edge-to-blade
  mapping), which floors even matched-filter decoding at 0.275.

A rescue was attempted: decoding by full 84-dimensional annihilation profile
instead of argmin. It also fails (BER 0.575 at zero noise; the signatures
collide).

## The no-go

The exactness of the nulls is inseparable from their ambiguity. The symmetry
that makes a_i * b_i = 0 exact guarantees each blade a crowd of exact
annihilators. Infinite-contrast nulls and undecodable messages are the same
phenomenon. This is a structural property of the construction, established by
counting, not a simulation artifact.

## What survives

The antenna metaphor retires as a code but remains valid as description: the
sigma_min rose is a radiation pattern, the 168 ruling planes are null
directions, sigma_min is channel gain. The receive half was always the real
half — the dark ports are null-attenuation measurements, and that stands.
The zero divisors remain pathology with structure, not machinery.

## Distribution-shift note

Per the standing rule, a same-calibration simulation win would not have
counted as a real falsifier either. Here the code fails at zero noise, so no
shift axis can rescue it: the no-go holds in every session, on every mesh,
by counting.
