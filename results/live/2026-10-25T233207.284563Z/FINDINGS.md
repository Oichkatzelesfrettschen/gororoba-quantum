# qet-compensated-ladder at a 50 us repetition delay: findings

Job `dbf934fgdj9s73fn3blg` (backup instance `f59f9992321c`) ran the approved case of
[2026-10-25T230238.648709Z](../2026-10-25T230238.648709Z/UNAPPROVED_CASE.md) on the 14 pairs of the ladder and frame
runs: 18 dynamic PUBs at 8192 shots and a 50 us repetition delay, charged 12 s against a predicted 12 s. Pooled
values are means over the 14 replicas with t-intervals (13 dof).

## Verdicts

| Endpoint | Measured | 95% bound | Model | Verdict |
|---|---|---|---|---|
| Information excess at each pair's selected alpha | +0.107 +- 0.006 | lower +0.096 | +0.129 | positive: the record lowers Bob's energy below every record-independent unitary |
| Channel floor margin at the selected alpha (primary) | -0.073 +- 0.015 | lower -0.100 | +0.063 | fails |
| Uncompensated margin (alpha = 0) | -0.157 +- 0.059 | | +0.063 | |
| Compensation gain, selected minus uncompensated | +0.084 +- 0.049 | lower -0.003 | | not resolved pooled; large on the three high-phase pairs |
| Reference unitary floor (Bob's best uninformed L) | 0.177 +- 0.013 | | 0.063 | the prepared state starts 0.18 above the vacuum value |

The ideal information excess is E_B = 0.115. Each pair's alpha was fixed by its own completed-frame reference arms
before its feedback arms were scored. The excess compares the record-steered rotation with the best record-independent
unitary in the same compensated frame, so its 0.107 is the QET signature at about 93 percent of ideal. The ladder and
frame runs compared uncompensated feedback against a floor that already contained the compensation, which explains
their unresolved excess.

The channel floor margin, the energy-below-vacuum test, fails because the reference state's energy sits 0.18 above the
ground value (Kabsch floor 0.177 against a model 0.063). The cause is incoherent preparation and idle loss, the
dephasing and residual ZZ fitted in [the frame findings](../2026-10-25T225332.266272Z/FINDINGS.md), plus readout. It
is not feed-forward and not information.

## Per pair

| Pair | Reference phase | Selected alpha | Selected margin | Uncompensated margin |
|---|---|---|---|---|
| [149, 150] | -1.002 | +0.9 | -0.074 | -0.508 |
| [80, 81] | -1.141 | +1.2 | -0.198 | -0.774 |
| [91, 98] | -0.522 | +0.6 | -0.085 | -0.197 |
| [79, 93] | -0.150 | 0.0 | +0.012 | +0.012 |
| [15, 19] | -0.209 | +0.3 | -0.004 | +0.013 |
| [109, 118] | -0.130 | 0.0 | -0.012 | -0.012 |
| [105, 117] | -0.140 | 0.0 | -0.029 | -0.029 |
| [61, 62] | +0.232 | -0.3 | -0.036 | -0.084 |
| [140, 141] | +0.010 | 0.0 | -0.053 | -0.053 |
| [55, 59] | -0.232 | +0.3 | -0.070 | -0.087 |
| [44, 45] | -0.057 | 0.0 | -0.112 | -0.112 |
| [49, 50] | -0.048 | 0.0 | -0.117 | -0.117 |
| [21, 36] | -0.261 | +0.3 | -0.118 | -0.068 |
| [77, 85] | -0.299 | +0.3 | -0.122 | -0.185 |

The reference phases reproduce the frame diagnostic's completed-frame values to within 0.1 rad about 40 minutes
later (for example -1.002 against -0.998 on [149, 150]), so B's offsets are stable on that timescale.

## Repetition delay

Against the frame diagnostic at 250 us, on the same pairs and about 25 minutes earlier, 11 of the 14 pairs show no
change in B's |1> assignment error, the completed-frame parity or `<X_A X_B>` beyond shot noise. Three pairs moved:

- [140, 141]: B's P(0 | 1) rose from 0.041 to 0.094 and the parity fell from 0.971 to 0.948;
- [79, 93]: B's P(0 | 1) rose from 0.014 to 0.040;
- [77, 85]: the parity fell from 0.948 to 0.921.

[I] At 50 us the service's measure-and-conditional-x reset at the head of every shot carries the preparation, so the
shorter delay costs nothing on most pairs and up to 0.05 in |1> assignment on a few. Those few may be calibration
drift; one job cannot separate the two. The charge fell from about 276 us to 81 us per shot.
