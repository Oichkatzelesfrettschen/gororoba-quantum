# Phase-compensated QET ladder on IQM Garnet: findings

Job `01a1767a-8993-7687-b1c3-e8097fb8b712` ran the approved case of
[docs/design/iqm-garnet-qet-compensated-ladder.md](../../../../docs/design/iqm-garnet-qet-compensated-ladder.md)
on calibration set `7b30f37a`:
- **Circuits.** 24 circuits x 1600 shots under passive reset, five packed pairs, with cc_prx feedback.
- **Cost.** It charged 6.5 credits (13 s billed against the compiled estimate of 13.4 s; runtime 12.4 s). Every
  circuit returned 1600 shots.
- **Acceptance.** The `garnet:mock` job `01a1767a-1251-74d5-9f23-203585ad8770` accepted the same circuits.
- **Analysis.** [analysis.json](analysis.json) is `scripts/iqm_qet_ladder.py analyze` of this directory, the
  preregistered decisions, which read no model value.

[O] marks a measured value, [I] an inference.

## Preregistered decisions (all five pairs primary)

| Hypothesis | Measured | Verdict |
|---|---|---|
| H1, information excess | mean +0.073, one-sided 95 % bounds [-0.070, +0.216] | unresolved |
| H2, channel floor margin | mean -0.423, upper bound -0.266 | fails |
| H3, cc_prx(2 phi*) angle | 2 of 5 pairs inside 2 phi* +- 0.15 rad | QB7-QB6 and QB8-QB13 scored |
| H4, window phase magnitude | mean 0.549 rad, lower bound 0.272 | coherent phase of Kingston's order |

The secondary tests over the two H3-scored pairs read H1 unresolved, H2 fails and H4 unresolved. No pair's
reference phase lies beyond the 1.05 rad compensation reach.

## Per pair

| Pair (Alice-Bob) | Excess (predicted) | Margin (predicted) | Unitary floor (predicted) | Reference phase | Fitted cc_prx angle, 99 % |
|---|---|---|---|---|---|
| QB4-QB1 | +0.005 (+0.128) | -0.307 (-0.099) | 0.254 (0.211) | -0.630 | 0.736 [0.665, 0.811] |
| QB7-QB6 | +0.005 (+0.134) | -0.410 (-0.266) | 0.423 (0.381) | -0.325 | 0.714 [0.641, 0.792] |
| QB8-QB13 | +0.186 (+0.110) | -0.313 (-0.171) | 0.557 (0.279) | +0.649 | 0.672 [0.595, 0.754] |
| QB16-QB17 | -0.100 (+0.109) | -0.708 (-0.194) | 0.731 (0.259) | -0.938 | 0.704 [0.607, 0.810] |
| QB19-QB18 | +0.268 (+0.114) | -0.378 (-0.221) | 0.680 (0.294) | -0.204 | 0.729 [0.648, 0.816] |

The per-pair shot-noise standard error of the excess is 0.064 to 0.071.

## Reading

- [O] **The excess scatters across pairs.** Its spread between pairs is 0.150 (standard deviation over five),
  2.3 times the per-pair shot noise. QB19-QB18 (+0.268, 3.9 sigma) and QB8-QB13 (+0.186, 2.7 sigma) show the
  record-steered energy drop that no record-independent unitary on Bob reaches. QB4-QB1 and QB7-QB6 read zero, and
  QB16-QB17 reads -0.100. The case's power statement held only without such spread; at a spread of 0.12 it gave H1
  a power of 0.50, and H1 is unresolved.
- [O] **The vacuum test fails by a wide margin.** H2 fails at -0.42 against a predicted -0.19, because the
  reference states sit far above the vacuum value: unitary floors 0.25 to 0.73 against 0.21 to 0.38 predicted. The
  Kingston floor was 0.18. [I] Garnet's preparation and window errors exceed the calibration model's depolarizing,
  readout and T1/T2 terms by a factor of about two in floor. The model predicted excess within 0.13 on every pair
  but misses the scatter.
- [O] **The window phase recurs on a second platform.** The reference phases run from -0.94 to +0.65 rad, and their
  magnitude exceeds 0.2 rad at 95 %. The window is Alice's readout and the 290 ns feedback delay, about 1.1 us. The
  compensation gain (selected minus uncompensated margin) is +0.091 +- 0.083 (t95 over pairs).
  - [I] A coherent phase on Bob during Alice's readout is common to Heron r2 (`if_else` broadcast, 2.8 us window)
    and Garnet (cc_prx, about 1.1 us window), so it is not specific to IBM's feed-forward path.
  - [I] It accrues faster per microsecond on Garnet.
- [O] **The conditional rotation is present at the planned angle.** The raw pooled P(1) after a |1> source is
  0.0968 (Wilson 95 % [0.0905, 0.1034]) against the ideal sin^2 phi* = 0.100. After a |0> source it is 0.0089. Raw
  P(1) after a pi rotation is 0.826; after a |0> source with the pi arm, 0.018.
  - [I] The readout-corrected angles sit 4 to 14 percent above 2 phi* (mean 0.711 against 0.644), so three pairs miss
    H3's band. Bob's P(0|1) comes from the |11> calibration arm at 0.097 to 0.194, which also absorbs preparation and
    relaxation error before readout. Correcting by it inflates the corrected P(1), so the band failure most likely
    reflects that calibration choice rather than an over-rotating cc_prx. Confidence moderate: no arm separates the
    two.

## Boundary

One job, one calibration, five pairs. Energies are expectations of the encoded two-qubit Hamiltonian, not field
stress-energy. The prediction omits coherent window phase, crosstalk, measurement-induced dephasing and non-QND
readout; it is reported beside the measurement and enters no decision.
