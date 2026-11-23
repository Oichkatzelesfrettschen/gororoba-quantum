# Review record: claim for the Emerald third-length verdicts

Reviewers (2026-11-22): codex on gpt-daybreak-blue at high as reviewer; opencode on opencode-go/deepseek-v4-pro as red-teamer (owner's substitute for agy, whose quota reads exhausted until about 2026-11-28). Raw reports stay outside the tree.

| # | Reviewer | Finding | Disposition |
|---|---|---|---|
| 1 | codex, opencode | The statement matches the analysis record number for number; both cited sha256 digests match; the verdict is the preregistered one | Confirmed |
| 2 | codex, opencode | The on-line verdict holds with and without the curvature correction (cohort z +1.36 corrected, -1.75 uncorrected, both inside 3) and under an anchor-derived curvature scale; the correction's covariance is propagated | Confirmed |
| 3 | opencode | The boundary rounded execution to 9.50 s and left "expected" unqualified | Fixed: 9.505 s against the case's expected range |
| 4 | codex | Byte replay of the analysis differs in 63 floating scalars by at most 1.3e-14 under a different numerical stack | Boundary: every verdict and reported digit agrees; on the compute host's pinned stack `iqm_idle_schedule_probe.py analyze --replay` reproduces the record byte for byte at b70d6216c; no gate in ci/gates.json replays this analysis |
