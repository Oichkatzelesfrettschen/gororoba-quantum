## Verdict

[proved] **Request changes.** The retained records support several descriptive structures, but the PR overstates statistical calibration for Poisson, periodogram, stacked-column, replicate-t, and circular-shift tests. Repository policy also rejects four serial CPU-bound loops.

## Ranked findings

1. **High: the “exact Poisson” claim is false.**

   [proved] [IBM REPORT.md:3](docs/evidence/hardware-residuals/ibm/REPORT.md:3) calls the laws exact. The same-shot pair count uses a Poisson tail at `a3_coupler_distance.py:17-19`, although conditioning on fixed margins gives a hypergeometric law per PUB and a convolution across PUBs.

   [proved] The lag count has overlapping adjacency indicators and only a Poisson approximation; its docstring itself says “close to Poisson” before calling the test exact at `a4_lag1_memory.py:9-16`. Run counts likewise overlap and are compared with Poisson at `a5_run_length.py:9-16`.

   [proved] The exactness labels and printed p-values therefore fail. The large descriptive effects may remain. Cheapest checks: hypergeometric convolution for pair scans; exact conditional adjacency/run distributions or dynamic programming conditional on `(N,K)` for lag and run tests.

2. **High: IBM items 6 and 7 use pseudoreplicated PUBs.**

   [proved] The spatial t tests treat 12 PUBs as independent replicates at `a3_coupler_distance.py:8-15`, while the report says those PUBs come from three calibration epochs and that items 4–7 are dependent at `REPORT.md:9`.

   [hypothesis] Replacing 12 PUBs with three epoch-level units is unlikely to preserve the reported global `10^-7.1` distance-gradient significance. The monotone descriptive gradient may remain.

   [proved] Cheapest decisive check: aggregate each distance and dispersion statistic within each of the three epochs, then run the test on three epoch means. Report the three values even if inferential power is inadequate.

3. **High: the periodogram tails do not accommodate the drift and memory found in the same records.**

   [proved] `a1_line_scan.py:50-89,129-135` uses exponential, Gamma, Fisher maximum, and neighbor-ratio laws derived from independent stationary ordinates. The records themselves exhibit slow drift and lag dependence at `REPORT.md:13-15,95-124`.

   [proved] The bulk ordinate fractions at `REPORT.md:44` validate marginal calibration, not the extreme maximum or local-ratio tails under colored binary noise. The hash permutation at `a1_line_scan.py:174-203` destroys the drift and memory that a stricter null must preserve.

   [proved] The 60 Hz and 29.7 Hz single-column significance therefore remains uncalibrated under an appropriate colored-noise null. Cheapest check: deterministic moving-block or phase-preserving surrogates, recomputing only the preregistered bins near 60 and 29.7 Hz.

4. **High: stacked-column p-values are anti-conservative.**

   [proved] `a1b_job_stack.py:7-15` says positive column correlation makes Gamma/F p-values conservative. Positive correlation increases the variance and upper tail of the sum, making the independent-column tail anti-conservative. The report correctly says so at `REPORT.md:51`.

   [proved] The quoted stack probabilities down to `10^-128` do not survive as calibrated p-values. The 69 and 37 single-column hits remain the stronger evidence.

   [proved] Cheapest check: treat each PUB, register, or independently justified column cluster as one unit and combine cluster-level statistics, or estimate the stack null with block surrogates shared across all columns.

5. **High: IBM “memory” and “leakage-proxy” mechanisms are not identified.**

   [proved] The lag test conditions on exchangeable rows at `a4_lag1_memory.py:9-16`, while the same data reject exchangeability through drift. Persistence at lags 2–3 does not correct the lag-1 null.

   [proved] The heavy-run Poisson/geometric law at `a5_run_length.py:9-18` excludes the drift and lag dependence already detected. The report appropriately admits that slow drift can explain the excess at `REPORT.md:124`.

   [proved] “Temporal dependence” survives descriptively; “one-shot memory” and “sticky hidden state” do not survive as identified mechanisms. Cheapest checks: block-local permutation or a nonstationary Bernoulli/Markov null for lag; fit transition rates on one half and test run tails on the other.

6. **Medium: analysis 2’s dispersion law omits observed temporal autocorrelation.**

   [proved] `a2_burst.py:83-95` treats shots as independent after estimating block-local marginals. Its circular shifts are used only for adjacency/window statistics at lines 119–174, not dispersion.

   [proved] Four shifted configurations estimate only a mean and are then assigned a Poisson tail; they do not provide an exact circular-shift null distribution.

   [hypothesis] Some of the five global dispersion survivors may disappear under columnwise shifts applied to the dispersion statistic. That deterministic shift distribution is the cheapest decisive check.

7. **Medium: Tuna/Quandela tests retain important dependence and model approximations.**

   [proved] Tuna line-frequency tests treat jobs as independent binomial/Fisher units at `a1_shot_line_extension.py:123-159`, although jobs share families, circuits, and acquisition series.

   [proved] Tuna drift sums squared qubit-group z values even though qubits share shots; the code admits this at `a2_readout_bracket_drift.py:171-184` and the report at `REPORT.md:87`.

   [proved] Belenos residual p-values subtract two Pearson statistics at `a3_belenos_mode_efficiency.py:198-240`; the source and report label the result approximate. Marginal survivors near the cutoff need a nested multinomial/log-linear likelihood-ratio check.

   [proved] `A3.plan_t_out` combines consecutive contrasts that share runs and explicitly calls its Stouffer result optimistic at `a3_belenos_mode_efficiency.py:559-573`. The row is BH-only and already fails Bonferroni.

   [proved] BH dependence assumptions are unestablished because all-mode/excluded-mode rows are paired and consecutive contrasts share runs. Bonferroni remains dependence-safe only where each underlying p-value is valid.

8. **Medium: the Belenos implementation contradicts its falsifier.**

   [proved] The docstring promises Fisher intervals “widened by the sessions’ own jackknife spread” at `a3_belenos_mode_efficiency.py:3-9`. The calculation instead multiplies Fisher covariance by Pearson overdispersion at lines 389–416; the jackknife values are only serialized at lines 349–360.

   [proved] The model-based rows are excluded from the corrected ledger at lines 575–609, limiting the ledger consequence, but the falsifier and implementation still disagree.

9. **Medium: serial CPU-bound loops violate repository policy.**

   [proved] Independent expensive work runs serially in:

   - `tuna-quandela/a3_belenos_mode_efficiency.py:50-99` (`mesh.propagate`) and `341-348` (session fits).
   - `tuna-quandela/a4_photon_number_trend.py:221-232,253-263` (two complete job-analysis passes).
   - `ibm/verify_60hz.py:16-38` (independent job FFTs).

   [proved] These loops must use `gororoba_quantum/parallel.py`.

10. **Low: error handling and dead calculations need cleanup.**

   [measured] Bandit reports B110 at `tuna-quandela/readout_data.py:55-62`: the fallback submission parse catches `Exception` and silently passes. A malformed Tuna record can disappear without a problem row when backend identity cannot be recovered.

   [proved] `a4_lag1_memory.py:136-137` immediately overwrites `b_mem`; the first calculation has no effect.

   [proved] `a1_shot_line_extension.py:294-297` immediately overwrites `primary_logp`; the first comprehension has no effect.

## Claim-by-claim disposition

1. [computed] The retained `a1_line_scan.json` has exactly 69 Bonferroni hits near 60 Hz in seven Kingston jobs. The deterministic `jq` check returned slots 3.315892, 3.378384, and 3.689168 ms; bins 815, 830/831, and 907; frequencies 59.9804–60.0526 Hz.

   [proved] A single fixed bin and a single returned-shot period are falsified across designs, conditional on the slot model. The corresponding list periods are about 5.03, 4.93, and 4.52 shots.

   [proved] Physical wall-clock 60 Hz remains a hypothesis because `common.py:19-25` and `REPORT.md:5` say returned order is unguaranteed and the execution-time agreement validates duration, not interleaving. Timestamps or a controlled slot-period intervention are decisive.

2. [computed] The JSON has exactly 37 hits near 29.7 Hz in six jobs: bin 411 for four 3.378384 ms runs, bin 449 at 3.689168 ms, and bin 1051 at 4.316112 ms.

   [proved] `REPORT.md:12` explicitly preserves the 9.97-shot list-position alternative, notes that only four columns lie outside the repeated design, and leaves the origin open. The text does not overclaim.

3. [computed] `jq` on `aggregate.json` returned 627,453 tests, cutoff `-7.098611195769065`, 3,023 Bonferroni survivors, and 5,247 BH survivors. Per-analysis test counts and survivors exactly match `REPORT.md:24-35`.

   [computed] The category table also matches: 60 Hz `[298,46]` phase/other and `[33,0]` population; 29.7 Hz `[216,37]` and `[30,13]`.

   [computed] Every reported item 3–8 numerical result checked against its cited JSON was present. `REPORT.md:9` correctly labels items 4–7 dependent.

4. [proved] Poisson-binomial describes each shot’s multiplicity under independent columns, but plug-in marginals, autocorrelated shots, and Poisson tail-count approximations remain. Exponential/F laws are asymptotic stationary laws; replicate t tests require independent PUBs; four circular shifts plus a Poisson tail are not an exact shift distribution. The independence failures are named above.

5. [computed] `ledger_all.json` returned 90 tests, 65 BH survivors, and 58 Bonferroni survivors: A1 `9/7/7`, A2 `7/4/4`, A3 `61/54/47`, A4 `13/0/0` for tests/BH/Bonferroni.

   [computed] The 54 A3 BH survivors comprise 30 `all_modes`, 23 `stray_modes_0_1_5_excluded`, and `A3.plan_t_out`. `REPORT.md:49-64` labels the all-mode and stray-mode behavior as known/re-detected and bounds its interpretation.

6. [proved] Apart from the listed statistical/docstring defects, source tracing found the scripts compute their described statistics. The listed serial loops violate the mandatory parallelism rule.

   [measured] Searches under `docs/evidence/hardware-residuals` returned exit 1 for email, CRN, local absolute path, AWS/GitHub/OpenAI key, private-key, assigned-secret, and network-client-import patterns.

7. [proved] `README.md:17-19` limits byte reproduction to Tuna/Quandela A1, A2, A4, ledger combination, IBM reader crosscheck, and aggregation; it expressly says IBM A0–A6 were not rerun and excludes Belenos A3 from byte identity.

   [computed] The retained Belenos JSON contains 504 `se_fisher` entries: 11 zero and 4 nonzero below `1e-8`.

   [proved] `README.md:15-17` says the retained file used versions “its report names,” but `tuna-quandela/REPORT.md` names no Python, NumPy, or SciPy versions. The producing numerical stack must be recorded there or the wording corrected.

   [measured] Byte reproduction was not rerun because every available filesystem, including `/tmp`, was read-only; running producer scripts would violate the brief.

## Public-repository and verification disposition

[proved] **No retained file must leave the public repository** under the identifier/path/credential rules. The bounded searches found no credential, account or instance identifier, CRN, email address, local absolute path, private key, or network access path.

[measured] Ruff check passed; Ruff format reported all 22 Python files formatted; scoped mypy passed all 22 changed scripts. Full mypy reached the unrelated existing `gororoba_quantum/qrng_seeds.py:145` error.

[measured] `git diff --check origin/main...HEAD` passed. Tracked worktree diff and index diff remained empty; HEAD remained `c079ce0db9fb72bfcfa2b8488190a5a5f789e9a2`. The pre-existing untracked `docs/archive/reviews/2026-11-10-hardware-residuals/` remained present and untouched.

[measured] Review goal completed in 759 seconds; tracker usage was 308,220 tokens.

