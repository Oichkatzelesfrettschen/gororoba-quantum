# Quantum ledger reconciliation

The [observation](observation.json) binds the research registry, A5 ledger and
IBM Fez descriptive analysis to SHA256 identities at source revision
`3573d1cae5cf5c39daed452c213a13479f0914c3`. The census precedes admission of
this report, so later ledger builds also count the report's evidence files.
The [architecture](../../design/quantum-evidence-ledger.md) defines the source
boundaries, and the [runbook](../../runbooks/results-index.md#quantum-evidence-ledger)
gives the queries.

## Measured denominator

| Surface | Retained count | Meaning |
| --- | ---: | --- |
| Research claims | 340 | All ten evidence classes, including proposals and withdrawals |
| Registered acquisitions | 482 | IBM 70, Quantum Inspire 197, Quandela 166, IQM 49 |
| Indexed run directories | 585 | Registered provider runs plus 103 Kaggle compute sessions |
| A5 findings | 295 | Separate algebraic status and coefficient-field scope |
| Census artifacts | 29,068 | Tracked results, evidence and proof files plus claim documents elsewhere |
| Raw-directory members | 3,414 | Files, including metadata and indexes; not independent observations |
| Distinct pinned source files | 730 | 674 JSON files and 56 other source files |
| Claims naming a replay gate | 199 | Available procedures; their execution is a separate fact |
| Claims without pinned evidence | 44 | Some carry proof documents or deterministic gates instead |
| Artifacts without a direct claim or indexed-run link | 19,381 | Includes case definitions, proposals, algebra and implementation evidence |
| Execution-record candidates outside indexed runs | 310 | Explicit record fields govern classification, rather than directory age |

Every census path exists in the observed checkout. Every claim evidence file
and document is tracked. Those observations cover file presence and tracking;
the registry and provider adapters check their declared integrity contracts.
The census does not certify every artifact's scientific interpretation.

## Acquisitions awaiting a claim citation

The two Ascella CZ tomography reference acquisitions
`qd-qpu-ascella-cz-tomography-reference-job-00` and
`qd-qpu-ascella-cz-tomography-reference-job-01`, and the simulator replay of
the Ascella signed-coherence acquisition
`qd-sim-ascella-signed-coherence-job-02-sim-replay`, have retained run records
and lack claim citations in the observed registry. The ledger preserves all
three as uninterpreted acquisitions. A claim needs the analysis's actual
endpoint, assumptions and boundary before those records can support it.

The initial 310 execution candidates require separate treatment from those three
registered acquisitions. The ledger reuses `evidence_closure.classify_record`
for IBM records and retains each file identity and explicit classification.
An unsupported provider schema stays identified for a dedicated reader.
Absence of a submission field establishes only the contents of the retained
record; it does not prove absence of historical execution.

## Repaired discovery boundary

The [resolution](resolution.json) records five submitted Quandela cases that
the adapter's `results/quandela/runs/` scan omitted. Their receipts live under
`results/quandela/cases/`. `qd_records.read_run` validates the existing case,
circuit, submission, collection and raw-result bindings for all five. Three
hardware results and one simulator result are completed; the two-photon
hardware case is canceled with zero returned samples. The adapter now discovers
case directories carrying a submission receipt, while unsubmitted cases remain
outside the acquisition set. The registry adds five acquisitions at their
existing paths, bringing the registered total to 487 and Quandela's share to 171.

The five acquisitions remain uninterpreted in the claim registry. The eight
unclaimed acquisitions therefore consist of the initial three and the five
recovered records. Registration repairs discoverability and integrity coverage;
a scientific claim still needs its actual analysis and inference boundary.
The reconciled view holds 590 run directories or compute sessions and 29,071
artifacts, including the three reconciliation evidence files. Direct claim or
run ownership now covers 47 additional preexisting artifacts; 19,337 artifacts
remain outside those two relations, including the three new report files.

The IBM candidate with job ID `dbhkprlep8hs73amc680` resolves against
`results/live/qpu-job-retention-audit.f59f9992321c.json`: the audit records
`unexecuted_cancellation`, `CANCELLED`, zero settled seconds and a null run.
The index exposes that account observation separately from acquisitions.
The classification removes a false missing-acquisition interpretation without
inventing a measurement. Two submission-start records and thirteen legacy
records retain unresolved dispatch histories; the retained fields do not
establish a terminal outcome.

## Verification observations

The host uses Python 3.14.9, NumPy 2.5.4, SciPy 1.18.1 and SQLite 3.54.0.
Ruff runs at the repository pin 0.17.4. Mypy runs at pin 2.4.1 through
`ci/pinned_tool.py`; the installed host mypy reports 2.4.0.

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export GOROROBA_WORKERS=2 OPENBLAS_NUM_THREADS=1
"$PYTHON" -B -W error scripts/research_state.py --check
"$PYTHON" -B -W error scripts/results_index.py --json ledger
"$PYTHON" -B docs/evidence/a5-exceptional-fibers/ledger.py --check --summary
timeout -k 10 120 "$PYTHON" -B -W error -O \
  docs/evidence/ibm-fez-actor-pilot/analyze.py --check
"$PYTHON" -B -m pytest tests/scripts/test_results_index.py \
  tests/scripts/test_research_state_add_acquisitions.py \
  tests/scripts/test_research_state_unexecuted.py \
  tests/gororoba_quantum/test_quantum_ledger.py -m 'not audit' -n 0 -q
```

Initial registry validation passes for 340 claims and 482 acquisitions. The A5 check
passes for all 295 rows; that check verifies schema, evidence paths and
supersession, rather than replaying mathematical proofs. The IBM Fez replay
reconstructs 24 conditions from 73,728 shots and matches the retained analysis
bytes, including schedule identity. The replay remains descriptive: physical
shot alignment, independence and causation retain the analysis's stated limits.
The focused fixture suite passes 26 tests, including acquisition discovery and
unexecuted-cancellation handling. The fixture mutations reject
altered evidence bytes, invalid class/status pairs, dependency cycles, invalid
JSON Pointers and path escapes. Provider-qualified lookup separates colliding
job identifiers.

The broad host type check stops with 16 syntax errors in the installed
`PyQt6/QtGui.pyi` stubs. The touched-file type check passes. The repository's
locked CI environment uses Python 3.14.7 and passes the full type lane across
931 source files. Its selected test run passes 27 tests, including the
retained-tree join audit, in 28.56 seconds. The audit records identical Git
worktree status before and after constructing the validated index. The
following commands reproduce those two checks:

```sh
env -u PYTHON GOROROBA_WORKERS=2 sh ci/pr_checks.sh types
env -u PYTHON GOROROBA_WORKERS=2 sh ci/pr_checks.sh tests \
  tests/scripts/test_results_index.py \
  tests/scripts/test_research_state_add_acquisitions.py \
  tests/scripts/test_research_state_unexecuted.py \
  tests/gororoba_quantum/test_quantum_ledger.py -m 'audit or not audit'
```

The Markdown checker resolves every relative link and anchor in 1,159 tracked
Markdown files. Ruff check and format checks pass for the six touched Python
files. The remaining pull-request suite and contract lane run through hosted CI;
the local selected run makes no claim about tests outside its selection.

## Remaining scientific scope

The ledger performs integrity validation and exposes the registered replay
commands. The other registered numerical replays are **not run** in this
reconciliation. Fresh Rocq compilation, new simulations and new provider
acquisitions are **not run** because the work concerns retained evidence.

The source-native observation query reaches each JSON schema without
inventing a common estimator. A uniform endpoint table still requires
family-specific contracts for numerator, denominator, uncertainty, calibration,
dependence, selection and falsifier. The existing pathion evidence-table module
demonstrates that contract on its declared families. The ledger's gap lists
expose the remaining obligations and keep an absent qualification distinct
from a failed experiment.
