# C5: zero-divisor code -- reported falsification withdrawn, replayed decoder failure (2026-10-19)

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

Replay status (issue #314): the seeded replay under
`docs/evidence/c5_zero_divisor_code/` builds the code from `cd_core`'s sign
table. The literal first-partner encoder was fixed before computing; the
injective perfect-matching encoder is a control added after the
first-partner results were seen. The "Reported result" table below keeps the
original values. The replay verdict and structural cause sections quote
`result.json`; the scope, measurement-hierarchy and later sections are not
replayed by this bundle. Replay command:
`PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/c5_zero_divisor_code/replay.py --check`.

## Replay verdict: the reported falsification is withdrawn

Issue #314's rule withdraws the falsification if the decoder matches or
beats random coding at low noise or if the counts differ. The counts differ
under every tested encoder, so the reported falsification, with its counts,
its 0.275 matched-filter floor and its 0.575 profile rate, is withdrawn.

| quantity | reported | first_partner | matching |
|---|---|---|---|
| C5 symbol error rate, sigma 0.01, 40-message subset | 0.762 | 0.760 | 0.762 |
| C5 symbol error rate, sigma 0.01, all 84 messages | -- | 0.750 | 0.751 |
| random + matched filter, sigma 0.01 | 0.000 | 0.000 | 0.000 |
| algebraic + matched filter, sigma 0.01, all 84 | -- | 0.667 | 0.000 |
| algebraic + matched filter, sigma 0.01, subset | 0.275 | 0.750 | 0.000 |
| 84-profile decoder, sigma 0, subset | 0.575 | 0.750 | 0.600 |
| mean annihilator ties | 3.9 | 4.0 | 4.0 |
| distinct signatures | 35 | 28 | 42 |
| distinct blades | 57 | 28 | 84 |

The replay supports a narrower, new finding. Under the post-hoc matching
control, with 84 distinct blades, the matched filter decodes every message
at low noise while the null-argmin decoder errs at 0.751 over all 84
messages at sigma 0.01 (0.762 on the 40-message subset), against 0.000 for
random coding. The first-partner encoder alone cannot show this, because its
28 blades bound every decoder at 1 - 28/84 = 0.667 over all 84 messages.

## Reported result (withdrawn as a replayable record)

The original run reported the table below from an encoder the note never
recorded. Its C5 column lies within about two standard errors of the
replayed subset rates; its matched-filter column reproduces under neither
replayed encoder.

| noise sigma | algebraic + annihilation (C5) | algebraic + matched filter | random + matched filter |
|---|---|---|---|
| 0.01 | 0.762 | 0.275 | 0.000 |
| 0.05 | 0.755 | 0.275 | 0.000 |
| 0.10 | 0.753 | 0.275 | 0.000 |
| 0.20 | 0.800 | 0.316 | 0.046 |
| 0.50 | 0.949 | 0.777 | 0.714 |

C5 fails at near-zero noise (symbol error rate 0.76) where random coding is
perfect (0.00); the replay finds the same gap on its own encoders.

## Structural cause (replayed)

Every signed two-support left factor of `cd_core`'s corpus annihilates
exactly 4 partners, and the relation is symmetric, so every transmitted
partner blade has exactly 4 exact annihilators among the 84 left factors.
At sigma 0 the decoder ties 4 ways and resolves to the lowest index, which
errs on 56 of 84 messages (0.667, both encoders). With noise the four exact
nulls stay near zero and argmin no longer singles out the sender's
annihilator: the all-84 rate stays between 0.746 and 0.751 at sigma 0.001
to 0.1 under both tested encoders. The reported 3.9 mean ties, 35 signatures and 57 distinct
blades do not arise under the replayed definitions (4.0, 28 or 42, 28 or
84).

The C5 score itself is degenerate. The 84 left factors form 42 pairs that
share the Gram matrix `L_a^T L_a`, and `||L_a v||^2 = v^T L_a^T L_a v`, so
both factors of a pair score every received vector alike at every sigma.
argmin resolves an exact floating-point tie to the lower index, so the
higher member of such a pair is decoded only where rounding favors it.

The rescue decoder, which matches the full 84-component annihilation
profile against each message's noiseless profile, also fails: messages
sharing a signature collide, 0.500 over all 84 messages and 0.600 on the
subset at sigma 0 under the matching encoder (42 signatures).

## Scope of the no-go

The replayed failure covers the two tested partner-blade encoders of the 84
left factors, the incoherent null-argmin decoder and the 84-profile
decoder, under additive Gaussian noise at the tested sigma levels. Within
that scope the exactness of the nulls is inseparable from their ambiguity:
the symmetry that makes a_i * b_i = 0 exact gives each blade 4 exact
annihilators. Other encoders are untested.

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
half -- the dark ports are null-attenuation measurements, and that stands.
The zero divisors remain pathology with structure, not machinery.

## Distribution-shift note

Per the standing rule, a same-calibration simulation win would not have
counted as a real falsifier either. Here the tested code fails at zero
noise, so no shift axis rescues that configuration: the failure is in the
encoder/decoder pair itself, visible before any hardware variation enters.
