# Residual structure in retained hardware records

Two exploratory offline passes over acquisition records this repository already retains. Each pass reads the
retained records only (no provider call, no submission, no random draw), states every falsifier in the script
that tests it, and corrects for the full count of tests it ran. The findings are leads: none is a registered
claim, and `docs/state/research_state.json` cites none of them.

| Pass | Records | Report |
|---|---|---|
| IBM Heron r2 shot-ordered records | 64 acquisitions on ibm_fez and ibm_kingston under `results/live/` | [ibm/REPORT.md](ibm/REPORT.md) |
| Tuna-17 and Quandela (Belenos, Ascella) records | Quantum Inspire and Quandela records read through `qi_records.py` and `qd_records.py` | [tuna-quandela/REPORT.md](tuna-quandela/REPORT.md) |

Each directory holds its scripts, the JSON every script writes, the run logs and, for the IBM pass, the full
p-value lists (`a*_pvalues.json.gz`). `tuna-quandela/a3_belenos_mode_efficiency.json` depends on the numerical
stack in its last digits: the retained file was written under Python 3.14.7, numpy 2.5.4 and scipy 1.18.1, and
14 of its 504 `se_fisher` entries, those of ill-determined modes, differ from the file an earlier stack wrote (values
below 1e-8 against 0.0; `tuna-quandela/REPORT.md`, "Dependence and corrections"). Rerun under those versions, `a1_shot_line_extension.py`, `a2_readout_bracket_drift.py`,
`a4_photon_number_trend.py`, `combine_ledger.py` and `ibm/reader_crosscheck.py` reproduce their retained JSON
byte for byte. The IBM analyses `a1b`, `a2`, `a3`, `a4` and `a5` ran under those versions with their exact-law,
calibration-epoch and shift-null code, `ibm/aggregate.py` ran over their p-value lists, and
`ibm/exact_laws.py` checks its laws against enumeration (`ibm/exact_laws_run.log`); a second run reproduces `a1b` byte for
byte and `a3` to 1e-13 relative (floating-point summation order); `ibm/a1_line_scan.py`,
`ibm/a6_calibration_age.py` and `ibm/a0_catalog.py` were not rerun, and their retained files come from their
original run (`ibm/REPORT.md`, "Scope").

Both directories hold a module named `common.py`, so mypy runs once per directory.
