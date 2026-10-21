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
decoder, at the same rate, under additive Gaussian noise. The simulation
used precomputed annihilator matrices and vectorized Monte Carlo. Scope of
the test: 40 of the 84 messages simulated (40 messages x 400 trials x 8
noise levels); error metric is symbol error rate (fraction of trials where
the decoded label differs from the sent label).

Every number below is unreplayed: the simulation script, its annihilator
matrices and its seeds are absent from the repository and from the build
host, so the table and the tie and signature counts are reported values
without a retained implementation. A committed replay with fixed seeds
under `docs/evidence/c5_zero_divisor_code/` and a checksum ledger would
admit them; until then the falsification stands as unverified (issue #314 carries the falsifier).

## Result: falsified, within the tested scope

| noise sigma | algebraic + annihilation (C5) | algebraic + matched filter | random + matched filter |
|---|---|---|---|
| 0.01 | 0.762 | 0.275 | 0.000 |
| 0.05 | 0.755 | 0.275 | 0.000 |
| 0.10 | 0.753 | 0.275 | 0.000 |
| 0.20 | 0.800 | 0.316 | 0.046 |
| 0.50 | 0.949 | 0.777 | 0.714 |

C5 fails at near-zero noise (symbol error rate 0.76) where random coding is
perfect (0.00). The gap is not close and not a tuning problem.

## Structural cause

- Mean 3.9 exact annihilator ties per codeword: each transmitted blade is
  killed exactly by ~4 of the 84 annihilators, so argmin decoding ties ~5
  ways on almost every message.
- Only 35 distinct annihilator-set signatures exist among the 84 codewords.
- Only 57 distinct transmitted blades (27 duplicates from the edge-to-blade
  mapping). The 0.275 matched-filter floor is the measured symbol error rate
  at near-zero noise on the tested 40-message subset; the non-injective
  encoding bounds the achievable rate below what 84 distinct codewords
  would support, since duplicate transmissions are indistinguishable by any
  decoder.

A rescue was attempted: decoding by full 84-dimensional annihilation profile
instead of argmin. It also fails (symbol error rate 0.575 at zero noise;
the signatures collide).

## Scope of the no-go

The falsification covers the tested configuration only: the 84-label
encoder with its 57 distinct transmitted blades, the incoherent null-argmin
decoder, and the 84-profile decoder, under additive Gaussian noise at the
tested sigma levels. Within that configuration, the exactness of the nulls
is inseparable from their ambiguity: the symmetry that makes a_i * b_i = 0
exact guarantees each blade a crowd of exact annihilators. This is a
property of the tested encoder/decoder pair, established by counting, not
a simulation artifact.

It does not establish that null-based communication is structurally
impossible in general. The tested decoders are incoherent: they discard
phase and output-mode information. A different decoder family is a
different experiment.

## Measurement hierarchy: coherent readouts exceed incoherent probes

The coherent projector Pi_+=(I+iJ)/2 with J=L_{e_8} discriminates the
complex states |psi+>=(u+ic)/sqrt(2) and |psi->=(u-ic)/sqrt(2) with
probabilities exactly 1 and 0 (verified exact), while all 21 incoherent
product-energy probes return identical values on both states.

Two qualifications are required. First, psi+ and psi- are complex
superpositions, not real zero divisors; Pi_+ is a coherent algebraic
projector, not an annihilator test. It is therefore not an instance of
null-based communication in C5's sense and does not falsify the C5 result
above. Second, Pi_+ does not recover the real frame angle: it returns 1/2
on every real frame state b(theta).

What Pi_+ establishes is that the C5 failure is a decoder failure, not an
information-destruction result. The zero-divisor structure's information
survives the algebra: for the logical subspace C=span{u,c}, the map
L_a|_C/sqrt(mu_a) is an isometric embedding whenever mu_a>0, so the
coherent output preserves the encoded qubit even when scalar success
probabilities contain no information about it. The incoherent
null-argmin readout discards information that a coherent algebraic
measurement retains. Coherent algebraic measurements strictly exceed
incoherent probes in resolving power on zero-divisor-adjacent structure.

## What survives

The antenna metaphor retires as a code but remains valid as description: the
sigma_min rose is a radiation pattern, the 168 ruling planes are null
directions, sigma_min is channel gain. The receive half was always the real
half — the dark ports are null-attenuation measurements, and that stands.
The zero divisors remain pathology with structure, not machinery.

## Distribution-shift note

Per the standing rule, a same-calibration simulation win would not have
counted as a real falsifier either. Here the tested code fails at zero
noise, so no shift axis rescues that configuration: the failure is in the
encoder/decoder pair itself, visible before any hardware variation enters.
