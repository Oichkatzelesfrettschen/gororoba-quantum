# qet-ladder on ibm_kingston: findings

Job `dbf6hnvpc3tc739mrjlg` ran the approved case of
[2026-10-25T203606.302690Z](../2026-10-25T203606.302690Z/UNAPPROVED_CASE.md) on 2026-10-25 from 20:38:56Z to
20:39:49Z, under the backup instance `f59f9992321c`. It was 19 dynamic PUBs at 8192 shots over 14 disjoint pairs and
was charged 43 s, against a predicted 42 s. The raw shots are under `raw/dbf6hnvpc3tc739mrjlg/`, and `collect.json`
holds the measured and replayed statistics.

## Preregistered verdicts

| Endpoint (mean over 14 replicas, t-interval, 13 dof) | Measured | 95% bound | Model | Rule | Verdict |
|---|---|---|---|---|---|
| raw channel floor margin | -0.160 +- 0.052 | lower -0.252 | +0.057 | lower > 0 | fails |
| product-state margin | -0.307 +- 0.010 | upper -0.289 | -0.283 | upper < 0 | passes |
| margin drop, ground minus product | +0.147 +- 0.046 | lower +0.066 | +0.340 | lower > 0 | passes |
| readout-corrected margin | -0.068 +- 0.043 | lower -0.144 | +0.099 | secondary | negative |
| information excess (Kabsch) | +0.019 +- 0.043 | lower -0.057 | +0.122 | secondary | not resolved |
| contrast (reversed minus feedback, over two) | +0.165 +- 0.016 | lower +0.137 | +0.210 | secondary | positive |

The primary fails: on this device, at this operating point, no pair lowers Bob's local energy below the floor that
binds record-independent operations. Following the case's rule, the failure does not falsify feed-forward, because
the fixed arms sit far from their predicted values: the record-binned match L is 0.164 against a model value of
-0.064.

## What the run localizes

- **Feed-forward executes the selected branch.** The feedback arm's L (0.159) equals the record-binned fixed arms'
  matched L (0.164). Per replica, `q_eff` has a median of -0.049 and an interquartile range of -0.080 to +0.069
  around the ideal 0; one replica's denominator is near zero. The contrast keeps 79 percent of its model value.
  This two-qubit circuit therefore does not reproduce the loss that removed the feedback-dependent structure of the
  N = 21 Kingston run.
- **The excess energy is in the prepared state, before Bob acts.** Alice's `<Z_A>` reads 0.706 against an ideal
  0.707. Bob's `<Z_B>` reads 0.617 against 0.707, the parity `<Z_A Z_B>` 0.874 against 1, `<X_A X_B>` -0.637 against
  -0.707, and Bob's `<Y_B>` +0.148 against 0. In the product-state arms, B in |0> reads `<Z_B>` = 0.991 through
  the same mid-circuit measurement of A.
- **The margin tracks the parity.** Across replicas the raw margin correlates with the parity at 0.961. Two pairs,
  [149, 150] and [80, 81], fall to a parity of 0.61 and 0.56 and margins of -0.46 and -0.72. A linear fit
  extrapolates to a raw margin of +0.013 at perfect parity.
- **Exploratory, not preregistered.** On the 12 pairs with parity above 0.8, the raw margin is -0.088 +- 0.015 and
  the readout-corrected margin -0.008 +- 0.018.
- **Feed-forward latency.** With 14 simultaneous captures, `scripts/heron_feedforward_latency.py` reads 262
  scheduled cycles (1.05 us) from capture end to receive, against 201 for a single capture, and 708 cycles (2.83 us)
  from measure start to the branch.

## Interpretation and next test

[I] B's Z populations and coherence degrade only when B is entangled with A, during a 2.83 us mid-circuit window that
the calibration-noise model does not capture. Readout explains about 0.09 of the 0.22 gap between the measured and
model margins: the corrected margin sits 0.09 above the raw one. The remaining loss sits in the preparation and the
measure-to-branch idle, not in the branch. Two candidates are an error on B induced by A's readout that depends on
A's state, and coherent error from the entangling preparation compounded over the idle. A static control separates
them: the same preparation, with a delay equal to the 708-cycle window in place of Alice's measurement, read in the
ZZ, XX and Y_B bases.

[I] For the Pais question this run changes nothing. No arm went below the floor without information, and the
informed arm did not either. The device's realization of the passivity theorem holds, with a margin consumed by
preparation error.
