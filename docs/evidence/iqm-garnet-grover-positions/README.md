# Positional and shot-block reading of the Garnet Grover depth arms

`positions.py` reads the retained Grover job of the Garnet follow-up
(`results/iqm/runs/2026-11-21T220358Z-garnet-grover-depth-sedenion-walsh-grover`) and writes `positions.json`. It is
written after the analysis of the job and decides nothing; gate `core-iqm-garnet-followup-replay` reruns it and compares
the bytes.

The preregistered 101 depth statistic f = lambda_3 - lambda_2^2 / lambda_1 read -0.122 +- 0.039 from raw frequencies
against the model's 0.010 (z -3.4; the readout-corrected f reads -0.121 +- 0.041). The depth arms k = 2 and 3 are
single circuits at positions 15 and 16 of 36, and k = 1 pools four copies at 0, 13, 22 and 35, so a response that
changes with position or time enters f.

- Linear drift: the k = 1 copies give a weighted slope of -0.000303 +- 0.000317 per position in the raw
  marked frequency. Moving the k = 2 and 3 arms to the copies' mean position along the fitted line changes the raw f
  from -0.12224 to -0.12281, and along the line at plus and minus three standard errors to -0.12103 and
  -0.1246: a linear positional drift accounts for at most 0.003 of the bend.
- Symmetric drift: the inner copies (positions 13 and 22) minus the outer ones (0 and 35), pooled over every four-copy
  arm of both marks, read -0.00053 +- 0.00364, so a drift symmetric about the job's center is absent at
  that resolution.
- Time in the job: the four shot blocks of each depth arm agree with their pooled frequency (Pearson 6.7 for
  k = 2 and 0.9 for k = 3, 3 degrees of freedom).

A step or a circuit-specific effect at positions 15 and 16 stays open, since the depth arms there are single circuits;
the coherent-error account stays open too ([iqm-garnet-grover-depth-sedenion-walsh](../../design/iqm-garnet-grover-depth-sedenion-walsh.md)).

```sh
"$PYTHON" -B -W error docs/evidence/iqm-garnet-grover-positions/positions.py OUT.json
```
