# Residual structure in retained hardware records

Two exploratory offline passes over acquisition records this repository already retains. Each pass reads the
retained records only (no provider call, no submission, no random draw), states every falsifier in the script
that tests it, and corrects for the full count of tests it ran. The findings are leads: none is a registered
claim, and `docs/state/research_state.json` cites none of them.

| Pass | Records | Report |
|---|---|---|
| IBM Heron r2 shot-ordered records | 64 acquisitions under `results/live/` (74 jobs: ibm_kingston 49, ibm_fez 23, ibm_marrakesh 2, per `ibm/catalog.json`) | [ibm/REPORT.md](ibm/REPORT.md) |
| Tuna-17 and Quandela (Belenos, Ascella) records | Quantum Inspire and Quandela records read through `qi_records.py` and `qd_records.py` | [tuna-quandela/REPORT.md](tuna-quandela/REPORT.md) |

Each directory holds its scripts, the JSON every script writes, the run logs and, for the IBM pass, the full
p-value lists (`a*_pvalues.json.gz`). `tuna-quandela/a3_belenos_mode_efficiency.json` depends on the numerical
stack in its last digits: the retained file was written under Python 3.14.7, numpy 2.5.4 and scipy 1.18.1, and
14 of its 504 `se_fisher` entries, those of ill-determined modes, differ from the file an earlier stack wrote (values
below 1e-8 against 0.0; `tuna-quandela/REPORT.md`, "Dependence and corrections"). Rerun under those versions, `a1_shot_line_extension.py`, `a2_readout_bracket_drift.py`,
`a4_photon_number_trend.py`, `combine_ledger.py` and `ibm/reader_crosscheck.py` reproduce their retained JSON
byte for byte. The IBM analyses `a1`, `a1b`, `a2`, `a3`, `a4` and `a5` ran under those versions with their exact-law,
calibration-epoch and shift-null code, `ibm/aggregate.py` ran over their p-value lists, and
the self-test of `ibm/exact_laws.py` checks the adjacency, run-count, same-shot hypergeometric and cross-lag moment
laws, the two-unit convolutions of the adjacency and run-count laws and the Chernoff bound against enumeration of every arrangement at small sizes
(`ibm/exact_laws_run.log`; the module docstring lists the cases, and the circular-shift law of `ibm/a2_burst.py` is
outside it). A second run reproduces `a1b` byte for byte (the rerun after the label change differs from the retained
file in the two `basis` strings only) and `a3` to 1e-13 relative (cause not tested); `a2` has no second run;
`a4` and `a5` have one each (`a4` after its Poisson tails gained the -300 floor, `a5` after its empty-law and
zero-mean guards), and each reproduced its JSON and log byte for byte and its p-value list in content (a rerun writes a new gzip
header time). `ibm/a1_line_scan.py` ran once more after its narrow-line amplitude took the
white-normalized ordinate (counts and p-value list unchanged); `ibm/a6_calibration_age.py` and `ibm/a0_catalog.py` were not rerun, and their retained files come from their
original run (`ibm/REPORT.md`, "Scope").

Both directories hold a module named `common.py`, so mypy runs once per directory.

`tuna-quandela/common.py --self-test` checks the weighted chi-square saddlepoint tail against `scipy.stats.chi2.logsf`
(from `tuna-quandela/`: `"$PYTHON" -B common.py --self-test`).

## Admission contract for another acquisition

The retained reports select leads; they do not authorize another provider run or turn a lead into a claim. Before an
acquisition is proposed, its written case names one claim, the contrast that can refute it, the independent unit, the
null that preserves the dependence already observed, and the decision threshold including every planned comparison.
An acquisition that cannot separate the alternatives below remains exploratory.

| Lead | Claim a prospective run could identify | Required discriminating design and decision |
|---|---|---|
| IBM 60 Hz returned-array line | A wall-clock disturbance near 60 Hz modulates the measured channel, rather than a fixed position in the submitted or returned shot list. | Freeze the band at 59.85 to 60.15 Hz before acquisition. Interleave at least two independently justified shot-slot periods while holding the circuit family fixed. A wall-clock effect keeps frequency in the frozen band and changes cycles per shot; a list-position effect keeps cycles per shot and moves in Hz. Calibrate the band with a shared moving-block or phase-preserving surrogate applied to every column of a job, and take jobs or independently scheduled acquisition blocks, not columns, as inferential units. |
| IBM 29.70 Hz returned-array line | A recurring wall-clock disturbance near 29.70 Hz is present outside the design in which the band was found. | Freeze the band at 29.55 to 29.85 Hz and the same slot-period intervention before collection. The primary endpoint is the preregistered band statistic in new designs; no recentering on the new maximum is allowed. Use the same dependence-preserving job-level null and correction family as the 60 Hz test. |
| Tuna-17 line or drift lead | The feature repeats across acquisition series rather than across dependent jobs or qubits of one series. | Freeze the band and statistic from the retained lead. Randomize or interleave the planned settings within each new series, use acquisition series as the independent unit, and preserve within-job shot and cross-qubit dependence in the null. A job-level or qubit-level p-value alone cannot admit the claim. |
| Belenos or Ascella efficiency residual | One named mechanism--uniform loss, detector imbalance, programmed-mesh offset, or mitigation--changes the result. | Run an interleaved factorial comparison with photon number, a balanced logical-output permutation, programmed mesh (target plus signed offset or inverse control), and mitigation (none versus the named method) fixed before collection. Record total detected-photon yield separately from the conditional output distribution. Uniform loss changes yield without a detector- or logical-mode pattern; detector imbalance follows the physical detector under logical permutations; a mesh offset follows the programmed logical transformation and reverses under the signed mesh control; mitigation is identified only by its randomized within-mesh contrast and interaction terms. A design missing one of these controls reports an exploratory association only. |

Frequency in hertz additionally requires an ordering bridge. The retained IBM records supply equal shots per PUB, one
executor chunk per job, chunk start and stop times, and a slot-duration model that reproduces aggregate execution
time, but IBM does not guarantee returned shot order and the records contain no per-shot timestamps. Those facts
establish frequency only conditional on consecutive returned rows being consecutive physical shots with the modeled
slot. A prospective physical-frequency claim therefore also requires provider documentation or retained timestamps
that establish this correspondence. Without that bridge, even a successful slot-period intervention is reported as a
periodicity of the returned array, not as a physical wall-clock frequency.
