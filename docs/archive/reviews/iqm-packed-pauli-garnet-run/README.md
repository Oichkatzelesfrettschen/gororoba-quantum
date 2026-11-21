# Review record: retention of the packed Pauli Garnet run (PR 974)

Reviewers chosen by the owner (2026-11-21): codex (gpt-daybreak-blue-latest, high), grok and agy
(gemini-4-hydrogen-high) on one brief; agy Flash (gemini-3.8-flash-high) and opencode on the free NVIDIA Nemotron model
(`opencode/nemotron-3.5-super-vl-free`, first attempt accepted) as red-teamers. All read head 8a85cd26e. The opencode
run wrote an untracked report file into the worktree against its read-only brief; that file went to the trash and its
report is the run's retained output. The Advisor reviewed last.

| # | Reviewers | Finding | Disposition |
|---|---|---|---|
| 1 | codex, gemini, grok | "The sharp null stands" and "moves the response by 0.0025" overstate a non-rejection | Fixed: "not rejected", the 0.0025 called a point estimate the test does not separate from zero |
| 2 | codex, gemini, grok, Nemotron | The common 0.13 shortfall is attributed to named omitted errors ("comes from", "rather than from the fifth cell"), and the list leaves out coupling and carryover | Fixed: the load cell cannot be its sole source; the record does not apportion the shortfall; the full omission list is named |
| 3 | codex, gemini, Flash, Nemotron | "At most at the 0.003 level" treats point estimates as a bound; the derived load-cell figure has no standard error; cell 1 holds QB12 | Fixed: `docs/evidence/iqm-garnet-packed-pauli-run/readout_split.py` reads every cell and QB12 from the raw bytes with Welch errors; the Result gives each estimate with its error (load cell 0.0118 +- 0.0016, QB12 0.0046 +- 0.0051) and drops the bound |
| 4 | codex, gemini, grok | The case header ("no paid job is submitted") and the procedure line ("every command above is not run") are stale | Fixed: both state the run |
| 5 | codex, gemini, grok | The QB12 sentence cites the Grover and sedenion jobs, which this head does not retain | Fixed: the sentence says those jobs are retained separately with their own reading |
| 6 | codex | The current-head review row is closed by PR 972's review of another head | Fixed: the row is closed for the case and points the retention at this record |
| 7 | codex | Retention and interpretation travel together, against AGENTS.md "Records" | Refuted: the rule names the research_state claim that interprets a run as the later change; this change adds an acquisition row and no claim, as the Garnet grover-line retention (e31ba697d) and the Emerald retention (PR 973) did; the Result section records the preregistered verdict and descriptive readings |
| 8 | codex, Nemotron | No committed replay binds the analysis output | Fixed: gate `core-iqm-packed-pauli-run-replay` runs `analyze --replay` and the readout split against its retained JSON, as the earlier IQM retentions' gates do |
| 9 | codex | "Enforceable cost" is closed although cancellation never fired | Fixed: the row reads open, best effort; the run measured the cost |
| 10 | gemini, grok | "The live default at submission" is not a field of the run records | Fixed: the Result names the 21:43 UTC read of the service default, 20 minutes before submission |
| 11 | gemini, grok | The quoted QB12 errors do not name their metric; `measure.constant` gives 0.0102 and 0.019 | Fixed: the Result names `metrics.ssro.measure_fidelity.constant`; either pair is a few percent, far from the measured fault |
| 12 | gemini | The execution row compares the 68-circuit job with the 36-circuit mock estimate | Fixed: compared with the 68-circuit mock and the compiled estimate |
| 13 | gemini, Flash | `drift_first_vs_last_reference_error` reads carryover from the all-ones reference across the shot boundary as drift | Fixed in the Result as a descriptive reading; the analyzer's field name stays, since a rename changes a merged analyzer's record schema (Boundary: a later analyzer version) |
| 14 | gemini, Flash | The analyzer omits the load cell from the carryover block and pools reference errors over twenty qubits, which hid QB12 | Boundary: the merged analyzer keeps its record schema; the readout split covers both readings for this run, and a later analyzer version can add a per-qubit reference check against the calibration |
| 15 | Flash | The case's seconds model (37.5 us per shot, from a heralded one-circuit pilot) overestimated this job about threefold (12.0 us per circuit-shot measured) | Fixed as a measured reading and an open hypothesis in the Result; the shared constant changes in its own change, since other cases' expected seconds use it |
| 16 | grok | The plan's reconciliation note still says the logical cases are unsubmitted | Fixed in the note. Boundary for `docs/design/packed-pauli-response-current-balance.md` line 8 and the step acceptance text: the design file's sha256 is pinned by `docs/evidence/plan-reconciliation/`, and the acceptance text is the step's scope |
| 17 | grok | The cell-1 buffer level is QB12's marginal | Fixed: the readout split shows QB12 at 0.39 behind cell 1's 0.13, and the Result says so |
| 18 | codex, gemini | Conjectures: reset-residue conditioning, X-quadrature rotation, multi-circuit settling after the all-ones reference, coupler isolation of the load cell | The settling conjecture enters the Result as an open hypothesis with its test; the others stay in the reviewers' reports as leads |

Claims 1 to 3 and 5 of the brief stand as stated; every reviewer confirmed the identities, digests, the sixteen pair
statistics and the p-value, and Flash and grok recomputed the QB12 reference fractions from the raw bytes.
