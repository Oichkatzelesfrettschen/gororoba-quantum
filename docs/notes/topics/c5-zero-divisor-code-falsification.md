# C5: zero-divisor code -- falsification confirmed by seeded replay (2026-10-19)

## The conjecture

The 84 zero-divisor pairs of the sedenion census form a classical code.
Message i selects the pair (a_i, b_i) with a_i * b_i = 0; the transmitter
sends the signed blade b_i; the receiver tests the 84 candidate annihilators
a_j and decodes ihat = argmin_j ||a_j * v||. In the noiseless case the
correct annihilator gives exactly zero (algebraic null, infinite contrast)
while wrong annihilators give generically nonzero products. The 84 messages
carry ~6.4 bits in 16 dimensions (log2 84; the 57 distinct blades carry at
most log2 57 = 5.8). The Belenos mesh had already demonstrated
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
table. Its codebook is the 84 standard zero-divisor pairs of Reggiani's
Table 1 (`docs/notes/papers/2411.18881.md`), which the conjecture's "84
zero-divisor pairs" names; two codebooks that re-pair the 84 distinct left
factors stay as alternatives. The "Reported result" table below keeps the
original values. The replay verdict and structural cause sections quote
`result.json`; the scope, measurement-hierarchy and later sections are not
replayed by this bundle. Replay command:
`PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/c5_zero_divisor_code/replay.py --check`.

## Replay verdict: the falsification is confirmed

Issue #314's rule confirms the falsification if the replay reproduces a C5
symbol error rate near 0.76 at sigma 0.01 against 0.00 for random coding
and the tie, signature and distinct-blade counts exactly. The Table 1
codebook meets every criterion: its subset C5 rate lies 0.013 below the
reported 0.762, against a spread of 0.039 over 40-message draws
(`ser_40_draw_sd`), and its 3.94 mean ties round to the reported 3.9.

| quantity | reported | replayed (table1) |
|---|---|---|
| C5 symbol error rate, sigma 0.01, 40-message subset | 0.762 | 0.749 |
| C5 symbol error rate, sigma 0.01, all 84 messages | -- | 0.743 |
| random + matched filter, sigma 0.01 | 0.000 | 0.000 |
| mean annihilator ties, sender excluded | 3.9 | 3.94 |
| distinct signatures | 35 | 35 |
| distinct blades | 57 | 57 |

The algebraic matched-filter floor (0.375 on the replay's subset, 0.321
over all 84, against the reported 0.275) and the profile rate (0.625
against 0.575) depend on the unrecorded 40-message draw. The reported
values lie within what table1 allows (draws holding 11 of its 27
blade-colliding messages and 23 of its 49 profile errors), while neither
re-paired codebook can give the 0.275 matched-filter floor; they enter no
verdict.

## Reported result

The original run reported the table below. Its C5 and random-coding
columns agree with the replay (C5 0.749 to 0.752 at sigma 0.01 to 0.1,
0.787 at 0.2 and 0.950 at 0.5 on the replay's subset); its matched-filter
column depends on the unrecorded subset.

| noise sigma | algebraic + annihilation (C5) | algebraic + matched filter | random + matched filter |
|---|---|---|---|
| 0.01 | 0.762 | 0.275 | 0.000 |
| 0.05 | 0.755 | 0.275 | 0.000 |
| 0.10 | 0.753 | 0.275 | 0.000 |
| 0.20 | 0.800 | 0.316 | 0.046 |
| 0.50 | 0.949 | 0.777 | 0.714 |

C5 fails at near-zero noise (symbol error rate 0.76) where random coding is
perfect (0.00); the replay reproduces the gap.

## Structural cause (replayed)

The 84 Table 1 pairs hold only 34 distinct annihilators: the decoder's 84
candidates repeat, so the messages that share an annihilator score every
received vector identically. Each of the 34 annihilators is its own class
of the Gram matrix `L_a^T L_a`, and `||L_a v||^2 = v^T L_a^T L_a v`, so the
decoder returns at most 34 distinct messages and errs on at least 50 of 84
(0.595) at every sigma. The exact nulls add the rest: every transmitted
blade has 1 or 2 exact annihilators among the 34 distinct ones, 2 to 7
among the 84 rows (4.94 on average, the sender included), which tie at
sigma 0 and stay near zero with noise, so argmin rarely singles out the
sender. The encoder loses information as well: 27 messages send a blade
another message sends, which bounds every decoder at 0.321 over all 84. The all-84 rate is 0.798 at
sigma 0 and 0.743 to 0.745 at sigma 0.001 to 0.1.

The failure does not rest on the repeated annihilators alone. The
re-paired codebooks send one message per distinct left factor; there every
blade has exactly 4 exact annihilators and the 84 left factors fall into 42
Gram pairs, and C5 still errs at 0.751 over all 84 at sigma 0.01 under the
injective matching, where the matched filter decodes every message.

The rescue decoder, which matches the full 84-component annihilation
profile against each message's noiseless profile, also fails: messages
sharing a signature collide, 0.583 over all 84 messages at sigma 0 under
Table 1 (35 signatures).

## Scope of the no-go

The replayed failure covers the Table 1 codebook and the two re-paired
codebooks, the incoherent null-argmin decoder and the 84-profile decoder,
under additive Gaussian noise at the tested sigma levels. Within that scope
the exactness of the nulls is inseparable from their ambiguity: the
relation that makes a_i * b_i = 0 exact gives each blade more than one
exact annihilator, as distinct vectors (re-paired codebooks) or as repeated
rows (Table 1). Other codebooks are untested.

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

What Pi_+ establishes is that the C5 failure beyond Table 1's 27 blade
collisions is a decoder failure, not an information-destruction result;
the injective matching codebook, whose matched filter decodes every
message, isolates it. The zero-divisor structure's information
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
