# Residual structure in retained IBM Heron r2 acquisitions: first exploratory pass

Scope. Six offline analyses of the shot-ordered records under `results/live/` (64 acquisitions, 74 jobs, 2,232 PUB files, 107,631 classical bit columns on ibm_fez and ibm_kingston). No provider call, submission, credential read or random draw. Every null is analytic (exact Poisson, Poisson-binomial, exponential or F periodogram law, t over replicates) or a deterministic circular shift or hash reordering. Scripts, JSON results and full p-value lists (`a*_pvalues.json.gz`) sit in `docs/evidence/hardware-residuals/ibm/`; `aggregate.py` applies one global correction. Python 3.14.9, numpy 2.5.4, scipy 1.18.1, repository commit 1e302aed1, run from the repository root with `GOROROBA_WORKERS=4` under an 8 GiB `systemd-run` scope.

Limits. IBM documents shot order as unguaranteed and the records keep chunk start and stop times only, so a null bounds structure that survives the service's ordering. Frequencies in Hz use the documented column-wise slot (docs/notes/ibm_quantum/repetition-rate-execution.md): consecutive shots of one PUB lie `sum over the job's PUBs of (rep_delay + circuit_duration x 4 ns)` apart. That sum predicts `circuits_execution_time_ns` to within 0.001 (ratio 1.0000006 to 1.00094) in all 74 jobs; every job holds one executor chunk and equal shots per PUB. The execution-time sum checks the per-circuit period, not the interleaving order. All 74 jobs run with twirling and dynamical decoupling disabled (`options.twirling`, `options.dynamical_decoupling`), so the runtime adds no designed shot grouping.

## Ranked list of what survived correction

Global correction: 627,453 tests, Bonferroni line log10 p = -7.10 (alpha 0.05), 3,023 tests pass, 5,247 pass Benjamini-Hochberg. Items 4 to 7 read the same 12 wide ground-prepared ibm_kingston state-prep runs (66 to 149 qubits, 16,384 or 32,768 shots, three calibration epochs) and are not independent.

1. **A 60.00 Hz line in the shot record of seven ibm_kingston jobs** (observed). Peak bins convert to 59.98 to 60.05 Hz at 0.07 Hz resolution with slot periods 3.316, 3.378 and 3.689 ms, so the bin differs per slot while the frequency does not (bins 815, 830/831, 907 of 4096). 69 single columns pass their own Bonferroni line, 7 to 18 per slot, all at 10^-13 or below; amplitude 0.066 to 0.142 in P(1), median 0.099. Job-stack p = 10^-45, 10^-19, 10^-9.8, 10^-8.7, 10^-8.0 (five pass the global line), 10^-6.7, 10^-5.9. It appears in 46 of 298 PUB rows of the superposition-state circuits (Ramsey and x/y measurement families) and in 0 of 33 rows of ground, excited, relaxation and cz-kick circuits at p < 10^-3, pointing at a phase (qubit-frequency) coupling (inferred; the population-only sample is small).
2. **A 29.70 Hz line, six ibm_kingston jobs** (idle, n21-orbit and measurement-sequence families). Job-stack p = 10^-128, 10^-120, 10^-62, 10^-18, 10^-14 at slot 3.378 ms (five jobs of one 44-PUB design: a list-position period of 9.97 shots, bin 411 of 4096, is not excluded within that design); 29.714 Hz at bin 449 in three PUB columns at slot 3.689 ms (10^-8.2 to 10^-7.4) and 29.725 Hz at bin 1051 of 8192 in one column at slot 4.316 ms (10^-7.7); the 10.238 ms job stack reads 10^-5.9 and fails the global line. Bins that differ per slot argue for a physical frequency, but outside 3.378 ms only four columns pass. It is not a 60 Hz subharmonic (2 x 29.70 = 59.4) and it also appears in population circuits (13 of 30 population-only PUB rows against 37 of 216 other rows at p < 10^-3). Origin open.
3. **Slow drift in shot order, wide-spread.** 1,192 channels pass the global line in the drift band (k = 1 to 8 cycles per N shots); 8.9 percent of channels sit below p = 0.05 (5 expected), 2.2 percent below 10^-3; the rms modulation of P(1) among the strongest 500 reaches 0.36 (median 0.096).
4. **Per-qubit lag-1 memory, the qubit-147 successor effect generalized** (ibm_kingston state-prep). 6 to 105 of 66 to 149 qubits per PUB read a 1 more often right after a 1; every significant qubit is positive (0 negative in 12 PUBs); the memory persists at lags 2 and 3. The repository's own q147 value reproduces with the same detector (0.0825 against 0.0200).
5. **Heavy-tailed run lengths of 1 outcomes in ground-prepared reads** (same runs): runs of 5 or more ones occur 53 times (prep0) and 67 times (x_history) the geometric rate, and 1.27 and 1.48 times what a memory-free continuation allows. The top 10 percent of columns hold 96 and 83 percent of the excess (leakage-proxy reading, inferred; a slow drift lengthens runs too).
6. **Same-shot error correlation that decays with coupler distance** (same runs): mean Pearson r 0.0051 at 1 hop, 0.0024 at 2, 0.0008 at 3 to 4, 0.0001 at 11 or more; the gradient survives removal of every individually significant pair. One coupled pair (58, 71) reads 4 to 8 times its independence mean in every run on three dates.
7. **Same-shot dispersion** of the error count: ratio 1.014 to 1.074 in the 12 PUBs (5 pass the global line), the whole-register view of item 6.
8. **A correlated coupled pair on ibm_fez (qubits 7 and 8):** 24 joint errors against 3.2 expected over the 73,728 pilot shots, 10^-12.7. One pair of 11,628.

Fell short of the global line: the ibm_fez distance gradient (10^-3.0, passes its analysis-level line), the calibration-age slope (10^-3.0), and every pilot statistic of analyses 2, 4 and 5.

## Multiplicity ledger (printed by `aggregate.py`)

| Analysis | Tests | Analysis Bonferroni line (log10) | Pass analysis line | Pass global line (-7.10) | Global BH |
|---|---:|---:|---:|---:|---:|
| 1 column line scan | 348,882 | -6.84 | 1,686 | 1,631 | 3,262 |
| 1b job stack | 222 | -3.65 | 58 | 48 | 59 |
| 2 burst | 180 | -3.56 | 9 | 5 | 9 |
| 3 coupler distance | 90,804 | -6.26 | 60 | 51 | 142 |
| 4 lag-1 memory | 182,967 | -6.56 | 424 | 409 | 593 |
| 5 run length | 4,397 | -4.94 | 1,033 | 879 | 1,182 |
| 6 calibration age | 1 | -1.30 | 1 | 0 | 0 |
| total | 627,453 | -7.10 global | | 3,023 | 5,247 |

Global survivors by family: analysis 1 white line 321, narrow line 118, drift 1,192; 1b white stack 27, narrow stack 16, 60 Hz stack 5; 2 dispersion 5, tail 0, clustering 0; 3 pilot pair 1, state-prep pairs 48, state-prep 1-hop bin 1, trimmed state-prep trend 1; 4 state-prep diagonal 364, state-prep cross 45, pilot 0; 5 columns 869, groups 8, continuation 2. Analysis 1b re-reads the data of analysis 1 and counts as extra tests, which is conservative.

## Analysis 1. Shot-order line scan across all 64 acquisitions

Falsifier (`a1_line_scan.py`, fixed before the run). Per channel (each bit column, the parity of each multi-bit register, the sum of all bits of a PUB with 16 or more columns) the normalized periodogram of shot order is an exponential law under independent shots. Fisher's max-ordinate law gives a white-line p-value; the ratio of an ordinate to the mean of its 64 neighbors is `(1 + r/64)^-64` under a locally flat spectrum, giving a narrow-line p-value; the lowest eight bins are Gamma(8,1), giving a drift p-value. "No structure" means all three stay above 0.05/348,882 and the bulk follows the exponential law. A Hoeffding-bound variant guards the white statistic. Channels with fewer than 30 minority shots are not tested.

Data. 64 acquisitions, 74 jobs, 2,232 PUB files; 116,294 channels tested (86,700 bit columns, 28,088 parities, 1,506 PUB sums); 21,417 skipped. Reader: `common.load_pub` with the index digest check; `reader_crosscheck.json` shows all 104 registers of four runs identical to `n21_exact_planning.retained_registers`.

Result.
- Bulk calibration over 384,624,572 ordinates: fractions above c = 3.0, 4.605, 6.908 are 0.04980, 0.01010, 0.00108 against 0.04979, 0.01000, 0.00100.
- Controls: a reordering of the 149-qubit prep0 PUB by the splitmix64 hash of the shot index reads 6.4 percent of 141 columns below 0.05 (line) and 5.7 percent (drift), against 14.2 and 20.6 percent unscrambled. A multiplicative index scramble is no control: a dilation only permutes periodogram bins, which the first attempt showed. A pulse comb of added probability 1.6 and 0.4 percent is recovered at a multiple of its fundamental at 10^-139 and 10^-21.
- Narrow lines (122 pass the analysis line, 118 the global line): 69 at 59.98-60.05 Hz in seven jobs, 37 at 29.70-29.72 Hz in six jobs, 16 elsewhere: 52.8-53.2 Hz (two jobs), 42.21 Hz, 127.0 and 139.8 Hz (one job each), and bins at exactly 0.125 and 0.25 cycles per shot (period 8 and 4 shots) in one register of one pathion-map job, a list-position periodicity that twirling does not explain (all jobs untwirled; inferred circuit or replica packing).
- White lines: 332 pass the analysis line (5.59 percent of channels below 0.05, 0.71 percent below 0.001), mostly the slow Ramsey-phase oscillations of n21-orbit runs at 1 to 2 Hz.
- Drift: 1,232 pass the analysis line; 375 of the strongest 500 on ibm_kingston, 125 on ibm_fez.
- Detectable sinusoidal modulation of P(1) at the Bonferroni line (50 percent power): median 0.049, 10th to 90th percentile 0.019 to 0.083, which bounds amplitudes of the null columns.

Job stack (`a1b_job_stack.py`). All PUBs of a job share N and the slot, so one bin is one physical frequency for every column. Stacking normalized ordinates (Gamma(C,1) white; F(2C,128C) neighbor ratio) gives one test per job and family (222 tests). Seven jobs show 60 Hz (a targeted window of +-0.15 Hz, post hoc, counted) and six show 29.70 Hz. Stacked columns of one PUB can share a noise source, so stack p-values are anti-conservative for wide registers; single-column hits carry the unstacked evidence.

Verdict: **structure found** (items 1 to 3; minor lines at 53 Hz and above).

## Analysis 2. Burst multiplicity and temporal clustering

Falsifier (`a2_burst.py`). Per PUB with at least 24 ground-prepared columns, block-local (512-shot) marginals set a Poisson-binomial null. Five tests: dispersion of the error count; upper-tail counts at two thresholds fixed from the marginals (expected 5 and 0.5 shots); adjacency at lag 1 and within lags 1 to 16 of the 1 percent highest-scoring shots against a circular-shift null that keeps each column's own time structure. 180 tests.

Data. The 153 sensors of 24 ibm_fez actor PUBs (73,728 shots, error = outcome xor prepared bit, all sensors prepared in |0>) and the ground-prepared first read of 12 wide ibm_kingston state-prep PUBs. Not run: the 156-bit and 58-bit PUBs of `results/live/kingston-wide-control-result` (512 shots, no record of the prepared state); the footprint-connectivity statistic (no PUB shows a tail above the independence law, so no footprint exists to test).

Result.
- ibm_fez pilot (named target): pooled dispersion ratio 1.0077 +- 0.0057 (95 percent upper bound 1.019); the 24 PUBs span 0.88 to 1.07 with 1 below 0.05 (1.2 expected); pooled upper-tail count 107 against 90.6; adjacency 0.85 times the shift null. The descriptive excess at five or more errors in `docs/evidence/ibm-fez-actor-pilot/findings.md` disappears under block-local marginals.
- ibm_kingston extension: dispersion ratio 1.014 to 1.074 (median 1.046, per-PUB SE 0.009 to 0.013, z 1.5 to 6.7); 11 of 12 below 0.05; 8 pass the analysis line, 5 the global line. Pooled upper-tail count 2.18 times the Poisson-binomial value; no PUB passes at the lower threshold. Adjacency is 3.79 times the permutation mean but 1.43 times the circular-shift null; no PUB passes, so per-qubit memory explains the adjacency.

Verdict: pilot **null (bound: dispersion ratio below 1.019; no clustering of high-multiplicity shots beyond per-qubit memory)**; ibm_kingston extension **structure found** (same-shot cross-qubit covariance, about 4.6 percent of register variance).

## Analysis 3. Error correlation against coupler distance (ibm_fez actor pilot)

Falsifier (`a3_coupler_distance.py`). The Pearson r of two error columns has mean 0 and SD N^-1/2 under independence. Per PUB and hop bin (1, 2, 3, 4, 5, 6, 7, 8-10, 11 or more on the 176 undirected couplers that the 352 directed cz entries give; diameter 32 hops) the mean r is one replicate; the PUBs are the replicates (t test), so qubit sharing drops out. Tests per dataset: 9 bins, slope across bins, near (1 hop) minus far (6 or more), each also on a variant that removes every individually significant pair, plus one exact Poisson test per qubit pair on the pooled joint count. 90,804 tests.

Data. ibm_fez actor pilot: 24 PUBs, 153 sensors, 73,728 shots, 11,628 pairs. Extension: 12 ibm_kingston state-prep PUBs (2,145 to 11,026 pairs each).

Mean r (95 percent interval):

| Hops | ibm_fez pilot | ibm_kingston state-prep | state-prep, significant pairs removed |
|---:|---|---|---|
| 1 | 0.00119 [0.00054, 0.00185] | 0.00507 [0.00418, 0.00595] | 0.00282 |
| 2 | 0.00041 [-0.00021, 0.00103] | 0.00242 [0.00189, 0.00295] | 0.00211 |
| 3 | 0.00019 [-0.00041, 0.00080] | 0.00078 [0.00048, 0.00107] | 0.00078 |
| 4 | 0.00033 [-0.00013, 0.00080] | 0.00084 [0.00050, 0.00117] | 0.00083 |
| 5 | -0.00028 [-0.00074, 0.00018] | 0.00060 [0.00026, 0.00094] | 0.00055 |
| 6 | -0.00003 [-0.00049, 0.00043] | 0.00065 [0.00036, 0.00093] | 0.00058 |
| 7 | 0.00020 [-0.00023, 0.00063] | 0.00039 [0.00011, 0.00066] | 0.00039 |
| 8-10 | 0.00007 [-0.00014, 0.00027] | 0.00018 [0.00006, 0.00031] | 0.00017 |
| 11+ | 0.00002 [-0.00012, 0.00016] | 0.00012 [0.00002, 0.00022] | 0.00011 |

Slope per bin: pilot -0.00010 [-0.00016, -0.00005] (10^-3.0); state-prep -0.00046 [-0.00054, -0.00038] (10^-7.1; 10^-7.2 trimmed). Near minus far: pilot +0.00116 [0.00053, 0.00178] (10^-3.1); state-prep +0.00489 [0.00399, 0.00578] (10^-6.9; +0.00265 trimmed, 10^-5.9). The pilot's 1-hop r is 0.23 times the state-prep value. Pair scan: the pilot's pooled pair statistics are calibrated (z SD 1.0046, observed over expected 1.0039). Pairs passing the global line: ibm_fez (7,8) with 24 joint errors against 3.2 (10^-12.7), and 48 ibm_kingston pair tests on (58,71), (61,62), (62,63), (154,155) and others, all one hop apart; ibm_fez (132,133), 8 against 0.9 (10^-5.0), does not pass.

Corrected significance. Pilot gradient: passes the 22-test analysis line (10^-2.64) at 10^-3.0, fails the global line. State-prep: bin 1 (10^-7.14) and the trimmed slope (10^-7.24) pass globally, the untrimmed slope (10^-7.08) and contrast (10^-6.9) sit at it.

Verdict: pilot pair (7,8) **structure found**; pilot distance trend **null at the global line (bound: 1-hop r 0.0012 [0.0005, 0.0019]; at 2 or more hops |r| below 0.0010 per bin)**; ibm_kingston extension **structure found** (distance-decaying correlation replicated on 12 PUBs). Not run: attribution to readout-resonator sharing or coupler crosstalk (no readout-feedline map in the repository).

## Analysis 4. Cross-qubit lag-1 memory

Falsifier (`a4_lag1_memory.py`). The count C_ji of (error of j at shot n, error of i at shot n+1) has exact mean (K_j K_i - J_ji)/N under a uniform reordering of whole shot rows (J_ji the same-shot joint count). One exact two-sided Poisson test per ordered pair, diagonal included. Survivors are re-evaluated at lags 2 and 3 (drift decays slowly, one-shot memory at once); a chain prediction (same-shot correlation times per-qubit memory) separates a directed cross-qubit effect from two known effects. 182,967 tests.

Data. ibm_fez actor pilot pooled per ordered pair over 24 PUBs (23,409 pairs; list neighbors lie one 8-circuit slot, 308 to 468 us, apart). Extension: 12 ibm_kingston state-prep PUBs, one PUB per job, so list neighbors are consecutive shots 31 to 261 us apart.

Positive control. Three static PUBs in one job, qubit 147: P(prep0 at s+1 = 1 | remeasure first read at s = 1) = 0.0825 against 0.0200 after a 0 (count 187 against an exchangeable mean of 55.0, z = 17.8; the repository's README gives 0.0825, 0.020, z = 18.7); the one-shot-earlier arm reads 55 against 55.0.

Result.
- ibm_fez pilot (named target): 0 of 153 qubits pass; diagonal z mean 0.0007, SD 0.98; median conditional-to-marginal ratio 0.90; coupled pairs read 0.996 times the mean. One ordered pair (123 to 86, 8 against 0.71, 10^-5.8, flat at lags 2 and 3) sits at the analysis line (-5.67) and below the global line. A qubit with the median pooled event count (13 expected) would need a ratio of 2.6 to pass.
- ibm_kingston extension: significant per-qubit memory in 26, 7, 32, 16, 15, 16 qubits (prep0 PUBs) and 6, 55, 105, 41, 43, 43 qubits (x_history PUBs); 0 negative. The median ratio is 1.3 to 1.9 (prep0) and 4.3 to 13.8 (x_history) at 20 to 50 us repetition delay, 0.65 to 0.79 at 250 us. Among significant qubits the lag-1 excess over the mean is 5.6 to 10.4 times, lag 2 is 1.0 to 7.2 and lag 3 is 0.7 to 5.1 (lags 2 and 3 are free of the lag-1 selection); the decay per lag is about 0.55 at 61 us and 0.7 at 31 us spacing, a lifetime near 90 to 110 us. Coupled pairs read 1.12 to 1.65 times the reordering mean at lag 1 (0.91 and 1.01 at 261 us), others 0.99 to 1.01; the chain prediction explains 85 to 100 percent of that (observed over chain 0.87 to 1.16, median 1.06). 409 tests pass the global line, none from the pilot.

Verdict: pilot **null (bound: per-qubit memory ratio below about 2.6 to 4 at 300 us spacing)**; ibm_kingston extension **structure found** (the q147 effect generalizes to 6 to 105 qubits per PUB). The mechanism is open (hypothesis: a 90 to 110 us decay lifetime is comparable to T1; untested).

## Analysis 5. Run-length structure of ground-prepared reads (leakage proxy)

Falsifier (`a5_run_length.py`). For a column of N reads with K ones the expected count of runs of at least L ones is exact: `E_L = (N-L+1) F_L - (N-L) F_{L+1}`, with F_L a ratio of falling factorials. One-sided Poisson tests per column (L = 2, 3, 5), per group (L = 2, 3, 4, 5), and a memory-free continuation test per group (runs of 3 or more against sum R2^2/R1, binomial variance). 4,397 tests. Reads are two-level (`meas_type` classified), so a hidden state outside the qubit subspace shows only as a sticky 1.

Data. 1,459 columns: the 153 pilot sensors pooled over 24 PUBs (3,672 columns), and the ground-prepared first read of every qubit of 14 state-prep PUBs (653 prep0, 647 x_history, 6 remeasure columns).

Observed over geometric expectation (Garwood 95 percent):

| Group | runs >= 2 | runs >= 3 | runs >= 4 | runs >= 5 | continuation ratio (z) |
|---|---|---|---|---|---|
| ibm_fez pilot | 0.992 [0.967, 1.018] | 0.922 [0.832, 1.018] | 0.912 [0.645, 1.251] | 1.25 [0.46, 2.71] | 0.84 (-3.75) |
| state-prep prep0 | 1.712 [1.683, 1.741] | 6.67 [6.50, 6.85] | 20.5 [19.8, 21.2] | 53.1 [50.9, 55.3] | 1.27 (+25.7) |
| state-prep x_history | 1.986 [1.957, 2.016] | 8.43 [8.24, 8.62] | 26.1 [25.4, 26.9] | 66.7 [64.4, 69.1] | 1.48 (+49.5) |
| state-prep remeasure (6 columns) | 1.15 [1.01, 1.31] | 2.29 [1.52, 3.30] | 3.8 [0.8, 11.2] | 19 [0.5, 108] | 1.86 (+3.4) |

In the pilot 7 of 459 column tests fall below 0.05 and none passes. In state-prep 497 of 1,959 prep0 and 1,041 of 1,941 x_history column tests fall below 0.05; 292 and 731 pass the analysis line. The top 10 percent of columns hold 96 percent (prep0) and 83 percent (x_history) of the positive excess of runs of 5 or more. Controls: the hash-order reordering of a prep0 PUB reads 1.4 percent of 148 columns below 0.05 (a conservative discrete test) against 31.8 percent unscrambled; six inserted runs of 20 ones in a scrambled column are flagged at 10^-10. Global line: 869 column tests, 8 group tests and 2 continuation tests pass.

Verdict: pilot **null (bound: runs of 2 or more within 0.97 to 1.02 of geometric, runs of 3 or more below 1.02 times)**; ibm_kingston extension **structure found** (run lengths far beyond a geometric law and a first-order Markov chain, concentrated in a few qubits). A slow drift of the marginal lengthens runs too, so the data separate neither a sticky hidden state nor drift (analysis 1 shows drift on the same data).

## Analysis 6. Calibration-age dependence of readout excess

Falsifier (`a6_calibration_age.py`). Excess y = f - e10 per qubit, f the excited fraction of the ground-prepared read, e10 = `prob_meas1_prep0` of the plan snapshot (a multiple of 1/4096). Because f carries initialization excitation and readout error, y is the ground-read excess. Regress y on plan-snapshot age in hours with qubit and (arm x repetition delay) fixed effects, cluster-robust over plan-snapshot stamps (t, dof = clusters - 1). Skill test: a fresher snapshot must predict f better. "No age dependence" means the slope interval contains 0 at the global correction.

Data. 13 state-prep runs (14 PUBs, 1,306 qubit-run rows): plan ages 0.30 to 3.70 h, five distinct plan stamps (ages 0.38, 0.41, 0.46, 0.84, 3.70 h, all ibm_kingston). Not usable: the two runs with 18 h old snapshots (2026-11-07 pathion maps) hold no ground-prepared column; idle_ground PUBs have no recorded bit-to-qubit map (candidate maps correlate with e10 at -0.23 and +0.08); baseline_ground is one 6-qubit run; the actor pilot keeps calibration medians only, at snapshot age 0.23 to 0.24 h.

Result.
- e10 of the plan snapshot equals the execution snapshot to the last digit in all 12 runs that carry both (maximum difference 0.0), including pairs 0.6 h and 3.3 h apart. The skill test is **not run** (no distinct reference), and a snapshot stamp is not the age of its readout numbers.
- Slope of ground-read excess: +0.00159 per hour, analysis-level 95 percent interval [0.00107, 0.00210], t = 8.49, 4 degrees of freedom, p = 10^-3.0. At the global alpha the interval is [-0.0158, +0.0190] per hour (t critical 93.1). Leave-one-stamp-out slopes are +0.00135, +0.00139, +0.00542 (dropping the 3.70 h stamp), +0.00175, +0.00159 per hour, all positive.
- Excess is near 0 at 50 and 250 us repetition delay (-0.0007 to +0.0011) and +0.0018 to +0.0096 at 20 us; the 3.70 h stamp is also a 69-qubit session at 20 us, so age is confounded with date and repetition delay.

Verdict: **null (bound: at the global correction the slope lies within -0.016 to +0.019 per hour over 0.3 to 3.7 h; no bound exists for older snapshots because no retained record pairs one with a ground-prepared read)**. The nominal positive slope with a stable sign in all leave-one-out fits is a lead to test on a design that varies age within one session.

## Observed versus inferred

Observed: the exponential-law calibration of the periodogram bulk; lines at 60.00 Hz (three slots) and 29.70 Hz (three slots, weakly outside one); the same-shot dispersion and distance gradient; the per-qubit lag-1 memory with lag-2 and lag-3 decay; the run-length excess and its concentration; the e10 equality between snapshots; the q147 positive control. Inferred: that 60.00 Hz is line-frequency pickup into the qubit frequency (US mains frequency; phase-sensitive circuits only); that the 29.70 Hz source is environmental; that the run-length excess is a leakage-like hidden state (it equally fits slow drift); that the memory timescale relates to T1.

## Checks not run

Direct two-excited-level (|2>) population or IQ data (`meas_type` is classified in every record); footprint connectivity of bursts; the readout-feedline attribution of one-hop pairs; the wide-control PUBs (no prepared state); phase coherence of the lines across PUBs against wall-clock offsets (Ramsey response phases are unknown); the fresh-versus-stale skill test; age data from idle_ground and baseline_ground; any family outside the ground-prepared sets beyond analysis 1; replication of the lag and run-length structure on another backend (all wide ground-prepared PUBs except the pilot are ibm_kingston).

## Files

`common.py` (reader, timing gate, helpers; non-finite p-values are written as -300), `a0_catalog.py`, `a1_line_scan.py`, `a1b_job_stack.py`, `a2_burst.py`, `a3_coupler_distance.py`, `a4_lag1_memory.py`, `a5_run_length.py`, `a6_calibration_age.py`, `aggregate.py`, `reader_crosscheck.py`; results `catalog.json`, `a1_line_scan.json`, `a1b_job_stack.json`, `a2_burst.json`, `a3_coupler_distance.json`, `a4_lag1_memory.json`, `a5_run_length.json`, `a6_calibration_age.json`, `aggregate.json`, `reader_crosscheck.json`; p-value lists `a*_pvalues.json.gz`; logs `a*_run.log`. All under `docs/evidence/hardware-residuals/ibm/`.
