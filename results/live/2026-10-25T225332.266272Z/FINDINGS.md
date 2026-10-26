# qet-frame-diagnostic on ibm_kingston: findings

Job `dbf8h0fgdj9s73fn24eg` (backup instance `f59f9992321c`) ran the approved case
[UNAPPROVED_CASE.md](UNAPPROVED_CASE.md) on the 14 pairs of the ladder run
[2026-10-25T203822.040562Z](../2026-10-25T203822.040562Z/FINDINGS.md): 24 dynamic PUBs at 8192 shots, charged 55 s
against a predicted 53 s. Pooled values below are means over the 14 replicas with t-intervals (13 dof); pair values
come from `collect.json`.

## Verdicts

| Question | Endpoint | Measured | Verdict |
|---|---|---|---|
| Does Alice's readout cause the phase? | idle minus as-run parity | -0.001 +- 0.004 | no: the phase is present without readout |
| Is the frame the mechanism? | completed-frame parity | 0.965 +- 0.002, above 0.94 on every pair | yes |
| | completed coherence phase against the as-run window phase | 0.998 against 0.862 on [149, 150], 1.059 against 0.939 on [80, 81], 0.555 against 0.477 on [91, 98] | the phase moves onto `<X_A X_B>` |
| Does the X echo refocus the phase? | echo minus completed coherence phase | +0.002 pooled | no; the echo was not in the window (below) |
| Energy margin | completed raw / corrected | -0.137 +- 0.059 / -0.029 +- 0.051 | below zero |
| | echo raw / corrected | -0.212 +- 0.058 / -0.109 +- 0.050 | below zero |
| Information excess (Kabsch) | completed / echo | +0.028 +- 0.041 / +0.021 +- 0.044 | not resolved |

## The scheduler fills the window with idle, never with gates

The service schedule in `raw/` shows, for every arm, that a branch-target qubit's operations preceding an `if_else`
are placed at the broadcast receive, adjacent to the branch:

- the as-run CX's closing `sx` on B plays at cycle 1894;
- the idle variant's closing H on B plays at 1894 (2616 in `idle_long`);
- the echo's two `x` play at 2075 and 2437, after the receive at about 1896, so the 724 dt echo block runs after
  Alice's window instead of beside it.

B therefore idles unechoed from the end of its last pre-window gate (1172 or 1180) to the receive at about 1896, in
every variant. On this stack a circuit cannot place gates on a branch target inside the measure-to-branch window,
and an echo meant to refocus that window needs another mechanism.

## The phase is B's detuning and A-B ZZ over that idle

Model: during the mid-CX wait, H = (delta Z_B + zeta Z_A Z_B) / 2 plus dephasing of B, with A measured before the
wait (as-run) or after it (idle sweep, 361, 722 and 1444 dt). Fitted per pair to the eight deferred-frame parity and
`<Y_B>` values:

| Pair (A, B) | delta (kHz) | zeta (kHz) | dephasing (1/ms) | rms |
|---|---|---|---|---|
| [149, 150] | -53.8 | +11.8 | 82.5 | 0.097 |
| [80, 81] | -54.4 | +14.3 | 129.4 | 0.101 |
| [91, 98] | -27.2 | +7.1 | 47.7 | 0.019 |
| [77, 85] | -12.6 | +2.4 | 39.6 | 0.019 |
| [15, 19] | -11.4 | +2.2 | 14.5 | 0.015 |
| [21, 36] | -11.1 | +3.9 | 18.3 | 0.014 |
| [61, 62] | +11.1 | +1.5 | 16.4 | 0.017 |
| [55, 59] | -10.7 | +3.9 | 24.0 | 0.013 |
| [109, 118] | -6.6 | +6.0 | 13.3 | 0.023 |
| [105, 117] | -6.2 | +4.5 | 21.8 | 0.026 |
| [79, 93] | -4.8 | +2.7 | 21.7 | 0.018 |
| [44, 45] | -3.0 | +2.3 | 16.8 | 0.021 |
| [49, 50] | -1.3 | +3.8 | 33.6 | 0.030 |
| [140, 141] | +0.7 | +3.8 | 18.3 | 0.020 |

[I] The model explains why as-run and idle share their parity (0.616 against 0.604 on [149, 150]) but not their
Bloch length (0.98 against 0.72). Parity depends on Z_A, which both arms share. With A unmeasured, the ZZ term
rotates B by an angle that depends on A's Z branch, and the branch average shrinks B's Bloch vector; with A measured
first, the rotation is coherent within each outcome. The two large-delta pairs fit worst, which leaves room for a
time-varying frequency (a two-level fluctuator) beside the static offset.

## Consequences

- [I] `live_run.noise_simulator` charges relaxation only on gates and explicit delays, so the scheduler's
  measure-to-branch idle is noiseless in every dynamic prediction. It also carries no detuning and no ZZ, which is
  why the predictions missed here.
- [I] The ladder's energy shortfall is therefore a device-frame effect, not feed-forward and not passivity: the
  Kabsch excess, which absorbs any record-independent rotation, sits near zero rather than negative. Recovering the
  margin needs Bob's operation to undo the coherent phase. That is a record-independent Z rotation, which passivity
  permits, chosen per pair from reference-arm data independent of the scored arms.
- [I] For the Pais question nothing changes: no arm in either run lowered Bob's energy below the floor.
