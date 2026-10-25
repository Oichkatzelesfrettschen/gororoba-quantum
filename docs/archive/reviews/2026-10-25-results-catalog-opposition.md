# Results catalog proposals: opposition review and alternatives

This review reads main at `d53a2fe` (after PR #490) against two externally
produced proposals for preserving, normalizing and indexing the repository's
results:

- the data audit bundle `gororoba-quantum-data-audit` (REPORT.md, a SQLite
  catalog and three build scripts, pinned to `791935a`);
- the storage section of a pasted review summary that accompanied the
  DAS MERGUS monograph. It proposes three persistent layers: original
  evidence, an exact typed interpretation of every JSON value, and SQL,
  Parquet, Zarr/HDF5 and FTS5 navigation, with PROV, RO-Crate and BagIt
  named as interchange targets.

Both proposals are brainstorms rather than plans. They name formats before
they name a query a maintainer runs today. This review argues against each
layer from measured properties of the tree, and then ranks the alternatives.
Every measurement below was taken on `d53a2fe` with the commands recorded
in the PR that adds this file.

## Measured facts that decide the argument

| Property | Measurement | Consequence |
|---|---|---|
| Registry size | 276 acquisitions, 233 claims (`scripts/research_state.py --check`) | The audit's 267 and 221 at `791935a` were correct and went stale within one day |
| Tracked tree | 19,012 files; 15,298 under `results/` and `docs/evidence/`; 7,357 `.json` | The audit counted 16,998 files; a committed whole-tree inventory goes stale on nearly every merge |
| JSON numeric fidelity | 13,489,251 number lexemes; 0 change value under `json.loads` with `repr(float)` round trip; integers parse exactly | Python consumers lose nothing; only non-Python readers (JavaScript, jq, DuckDB `DOUBLE`) face the 16 integers above 2^53 |
| Nonstandard JSON | 3 `Infinity` tokens in one retained v3 record | Writer already refuses nonfinite values; the reader parses v3 exactly (`tests/scripts/test_qi_bdsc_pauli_analysis_json.py`) |
| Dense arrays | no tracked `.npy`, `.npz`, `.h5` or Zarr store | HDF5/Zarr have no present input |
| Largest raw files | 44.1 MB IBM `raw/<job>/pub_00.json` bitstring arrays; 40.1 MB `record.json` | GitHub warns at 50 MB and refuses pushes over 100 MB; growth of one run, not of the catalog, sets the hard limit |
| Evidence volume | `results/` 1.3 GB, `docs/evidence/` 126 MB apparent size | Repository size, not query speed, is the scaling pressure |
| Existing indexers | `research_state.py` (1,682 lines, four provider adapters), `evidence_closure.py` (1,119), `reconcile_qpu_inventory.py`, `inventory_retained_runs.py`, `observe_qpu_job_inventory.py`, `plan_inventory.py` | The tree already holds six partial indexes; a seventh adds a reconciliation surface unless it replaces or composes them |
| Collector overwrite | Kaggle `collect` overwrote (fixed in #490); Quantum Inspire `_retain_json` refuses a conflicting recollection; `live_run.py --collect` never rewrites `raw/`; Quandela keeps raw result bytes; IQM `snapshot` prunes by design, as a mirror of platform state whose history git holds | The append-only property now holds for every job-result collector checked; the Quandela claim rests on its docstring and `write_json(exclusive=)` and was not traced through every call |

## Opposition, layer by layer

**Exact typed interpretation of every JSON value.** The proposal guards
against binary64 rounding of numeric lexemes. Every float the repository
wrote came from Python's `json.dumps`, which emits the shortest string that
round-trips, and the scan above finds no lexeme whose value changes. Integers
are arbitrary precision in Python. Signed zero survives `float`. The layer
therefore buys protection for consumers the repository does not have, at the
cost of a second representation of every value that must stay in sync. A
narrower rule covers the real risk: a JSON record that a non-Python tool will
read carries integers above 2^53 as strings, and the provider bytes stay
authoritative. Falsifier: one tracked lexeme, or one provider response the
collectors parse, whose value changes under `float`.

**SQLite/FTS5 catalog as a persistent layer.** SQLite file bytes depend on
the library version, as the audit itself states, so the file cannot be a
reviewed artifact; it is a cache. A committed JSON export of it inherits the
staleness measured above and the merge conflicts that
`docs/state/hypercomplex-libraries/libraries.json` already causes on every
PR that adds a Python file. Full-text search over 19,012 paths is a `git
grep` the maintainer already has. The catalog earns its place only for joins
nobody can do by grep: job to acquisition to claim to raw file. That join is
small (hundreds of rows), and the registry plus the provider adapters
already compute it during `--check`. Falsifier: a maintainer question that
needs a join across more than two of those tables and that the existing
scripts cannot answer in one command.

**Parquet and DuckDB for outcome tables.** No cross-run analytical query is
named, and every analysis in `scripts/` loads its own raw files with numpy.
DuckDB reads JSON and JSON Lines directly (`read_json_auto`), so a
cross-run query can run over the retained files with no conversion step.
Parquet becomes justified when a measured query over raw shots is slow;
none has been measured. The real case for a packed format is the GitHub
100 MB ceiling on a single raw file. That case concerns how future
collections write raw shots, not a derivative layer over old ones.

**Zarr and HDF5.** The repository retains no dense arrays. A Kaggle
statevector run already returns summaries, because 30 qubits of complex128
is 16 GiB. These formats answer a question the corpus does not pose.

**PROV, RO-Crate and BagIt.** The repository has no external consumer of a
provenance graph today. RO-Crate and BagIt matter at publication: a release
deposited with a DOI. Maintaining them continuously duplicates
`research_state.json`, which already records evidence, gates, dependencies
and supersession. A release-time exporter from the registry produces the
same crate on demand.

**Three persistent layers in general.** Each persistent derived layer adds a
freshness obligation and a gate. The repository's own history shows the cost:
the `tests` check now carries retained-inventory freshness, seed provenance,
library inventory and receipt ledgers. A layer that is regenerated rather
than committed carries no such obligation.

## Where the proposals are right

- **Occurrence identity separate from content identity.** Git supplies
  content identity (blob id) and path occurrence (tree entry). It does not
  supply retrieval events. #490 adds them for Kaggle, and the other job
  collectors already refuse to overwrite. The principle holds, and it is now
  implemented where it was missing.
- **Population denominators.** Requested, returned, accepted and eligible
  counts are distinct quantities. This belongs in each provider's analysis
  contract, where `collect.json` and the adjudication records already
  separate them, not in a catalog.
- **Independent archival copies.** This is the strongest proposal and the
  cheapest. The only copies are GitHub and the workstation clones. A
  checksum detects loss but repairs none.
- **Raw-shot encoding for wide registers.** A 156-bit outcome stored as a
  character string costs eight times its packed size. That ratio meets the
  GitHub file ceiling first.

## Alternatives, ranked

| Option | What it adds | Maintenance | Answers |
|---|---|---|---|
| A. Independent archive | Software Heritage "save code now" for the public repository (content-addressed SWHIDs), plus a periodic `git bundle` verified by `git bundle verify` on separate media; a Zenodo release with a DOI at each publication point | One command per release; no gate | Loss of GitHub or the workstation |
| B. Query command, no committed index | `scripts/results_index.py` composing `research_state` adapters, `kaggle_run.receipt_chain` and `qi_platform.run_directories`; prints JSON or Markdown for run, job, acquisition, claim and raw-path joins; optional `--sqlite PATH` and DuckDB views under `~/.cache/gororoba-quantum/` | Tests only; nothing to regenerate | Discovery and provenance joins |
| C. Packed raw shots for new collections | A versioned raw-shot format (packed bits plus width, register order and PUB shape) written beside the existing JSON for new IBM collections, with an exact round-trip test; old bytes untouched | One writer, one reader, one test | GitHub size ceiling; BitArray shape loss named by the audit |
| D. Per-run sidecar manifests | `manifest-sha256.txt` in each run directory at collection time (BagIt payload manifest format), never regenerated | Written once per run | Integrity of a run copied outside git |
| E. Generated committed catalog (audit plan) | JSON Lines exports, generated Markdown navigation, freshness gate | Regeneration on every retained run; merge conflicts across concurrent PRs | Browsable navigation in the repository |
| F. Status quo | nothing | none | Leaves archival and the size ceiling open |

Recommendation: A first, because it is the only option that protects
against loss; then B, because it delivers the joins the catalog promised
with no artifact to keep fresh; and C before the next wide IBM acquisition.
D is cheap but overlaps git once a run is committed; it pays only for copies
outside git. E is deferred until B shows which views maintainers actually
open. Parquet, Zarr, PROV and continuous RO-Crate stay out until a named
query or consumer exists.

Falsifiers for this ranking:

- a recurring maintainer question that B cannot answer in one command;
- a measured analysis whose runtime is dominated by JSON parsing of raw
  shots;
- a non-Python consumer of the records;
- an archival restore that `git bundle` or Software Heritage cannot
  reproduce.

## Scope

The review covers the storage and indexing proposals only. The scientific
claims of the DAS MERGUS monograph and companion are checked separately in
`2026-10-25-das-mergus-algebra-review.md` and
`2026-10-25-das-mergus-data-review.md` beside this file. Checks that did
not run: the Quandela collector was read at its `collect` docstring and
`write_json` helper rather than traced call by call; the audit's
`catalog.sqlite` was neither opened nor queried; and none of the audit's
build scripts was executed.
