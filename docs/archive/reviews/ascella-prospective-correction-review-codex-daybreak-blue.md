## Adversarial review

Artifact: three-commit Python acquisition and statistical-analysis change at `044995233`. Fields: experimental design, statistical inference, numerical reproducibility, and retained-request integrity. The review covered the complete branch diff and named retained runs.

### SERIOUS — The advertised 98% interval has an unstated estimand

[ascella_correction_score.py](scripts/ascella_correction_score.py:147) resamples the 56 observed `(d,t)` mesh pairs while holding the fitted table and each mesh’s observed counts fixed. The resulting 6.16–16.21 interval is therefore a conditional, exchangeable-mesh sensitivity interval. It is not a 98% interval for these 56 fixed meshes, repeated counting, or a newly estimated table. The documentation simultaneously disclaims reach beyond the 56 seeds at [long-horizon-first-principles.md:103](docs/evidence/ascella-order-coefficients/long-horizon-first-principles.md:103), leaving the bootstrap without a clearly stated sampling population.

The retained data reproduce `R = 10.3708776`, 6.15580–16.20551, and the plug-in noise ratio 10.89385. An independent 20,000-replicate multinomial resimulation that refits the job-02/job-03 table and redraws job-09 counts produced a 98% predictive range of 3.87–7.91; every replicate still exceeded 2. The conclusion survives, but the published interval does not represent those uncertainty sources.

Fix: name the exchangeable-seed superpopulation explicitly or replace the interval with a hierarchical/parametric bootstrap that resamples the heteroscedastic counts in all three jobs and refits the table.

### SERIOUS — “Almost entirely counting noise” is numerically false

[long-horizon-first-principles.md:80](docs/evidence/ascella-order-coefficients/long-horizon-first-principles.md:80) says the remaining variance is “almost entirely counting noise.” The residual variance is `1.13460e-5`; job-09 counting variance contributes `4.64865e-6` (41%), while recorded table noise contributes `6.15263e-6` (54%). Only their sum explains almost all the residual.

Fix: say “almost entirely job-09 counting noise plus table-estimation noise.” Describe 10.89 as a plug-in noise benchmark, not a physical noise limit. “About 90%” is otherwise correct: `1 - 1/R = 90.36%`, strictly for these 56 seeds of `theta2-x-arm0`.

### SLOPPY — The power results are model-conditional, not calibrated power

[ascella_correction_score.py:267](scripts/ascella_correction_score.py:267) assigns one scalar Gaussian table variance and one scalar counting variance to every mesh. Job-09’s individual counting variances span `3.19e-6`–`5.80e-6` with 10.3% coefficient of variation. The assumed mean, `4.912e-6`, is reasonably conservative against the observed `4.649e-6`, but `S=t-n` also omits fitted-slope uncertainty and the covariance created by centering. The scenario shares in [correction-power.json:7](docs/evidence/ascella-order-coefficients/correction-power.json:7) are reproducible sensitivity calculations, not empirically calibrated operating characteristics.

Fix: simulate per-mesh multinomials from retained counts, refit the slope and offsets, and report Monte Carlo uncertainty for the 400-replicate shares.

### Checks that found nothing

Commit `2698c83c9` froze the table, code, rule, thresholds, draw indices, and plan at 04:18:25 UTC; job-09 was submitted at 04:29:01 UTC; outcome commit `e27f23bf1` followed at 04:43:02 UTC. Later edits changed admission bookkeeping and receipts, not the reading. Job-09’s 64 name-to-seed mappings equal job-02’s, its 56-mesh order exactly follows the draw, and its submitted body equals the frozen body apart from Perceval’s permitted `process_id`. Empty `admit_statuses` leaves earlier jobs unchanged.

The request check, table/score/power replays, job-08/job-09 reading, and all three earlier long-horizon readings passed byte-identically. Ruff lint and format checks passed; the focused tests passed 2/2 after warming writable caches. `git diff --check` passed. The checkout contains no PR-body artifact, so the network-prohibited review could not verify hosted PR prose.

Verdict: the prospective result is sound for exactly 56 repeated seeds of one Ascella setting, and the `R > 2` decision remains robust. The uncertainty label and noise-floor prose require correction before the branch can support stronger statistical language.

