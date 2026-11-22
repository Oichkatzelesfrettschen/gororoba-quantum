# Positional and shot-block reading of the Garnet Grover depth arms

`positions.py` reads the retained Grover job of the Garnet follow-up
(`results/iqm/runs/2026-11-21T220358Z-garnet-grover-depth-sedenion-walsh-grover`) and writes `positions.json`. It is
written after the analysis of the job and decides nothing; gate `core-iqm-garnet-followup-replay` reruns it and compares
the bytes.

The readout-corrected 101 depth statistic f = lambda_3 - lambda_2^2 / lambda_1 read -0.121 +- 0.041 against zero. The
depth arms k = 2 and 3 are single circuits at positions 15 and 16 of 36, and k = 1 pools four copies at 0, 13, 22 and
35, so a response that changes with position or time enters f.

- The k = 1 copies give a weighted slope of -0.000303 +- 0.000317 per position in the raw
  marked frequency.
- The raw f is -0.12224. Moving the k = 2 and 3 arms to the copies' mean position along the fitted line gives
  -0.12281; along the line at plus and minus three standard errors of the slope, -0.12103 and
  -0.1246. A linear positional drift therefore accounts for at most 0.003 of the bend.
- The four shot blocks of each depth arm agree with their pooled frequency (Pearson 6.7 for k = 2 and
  0.9 for k = 3, 3 degrees of freedom), so no transient within the job explains it.

The drift alternative of the design's open hypothesis is closed on these bytes; the coherent-error account stays open
([iqm-garnet-grover-depth-sedenion-walsh](../../design/iqm-garnet-grover-depth-sedenion-walsh.md)).

```sh
"$PYTHON" -B -W error docs/evidence/iqm-garnet-grover-positions/positions.py OUT.json
```
