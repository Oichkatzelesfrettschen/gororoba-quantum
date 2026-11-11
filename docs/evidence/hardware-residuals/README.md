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
stack in its last digits: under Python 3.14.7, numpy 2.5.4 and scipy 1.18.1 the `se_fisher` entries of
ill-determined modes read about 1e-10 where the retained file, written under the versions its report names,
reads 0.0. Rerun under those versions, `a1_shot_line_extension.py`, `a2_readout_bracket_drift.py`,
`a4_photon_number_trend.py`, `combine_ledger.py`, `ibm/reader_crosscheck.py` and `ibm/aggregate.py` reproduce
their retained JSON byte for byte; the six IBM analyses `a1` to `a6` and `a0_catalog.py` were not rerun.

Both directories hold a module named `common.py`, so mypy runs once per directory.
