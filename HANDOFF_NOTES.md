# Handoff notes

## Gate list on main

- Every gate runs its command once in normal Python. Ruff rule S101 rejects
  `assert`, so a check raises explicitly and holds under `python -O` as well.
  Files whose bytes retained evidence pins by sha256 keep their asserts under
  per-file ignores in pyproject.toml.
- The assert-ban change merged with no hosted review and before its CI ran.
  The first CI run on main exercises the reduced gate list. A failure there
  belongs to that change and is fixed in the next one. A Codex review of the
  merged diff is still owed.
- Historical review notes and retained CI timing records still name the
  deleted `-O` twin gates, as recorded.

## Premerge base cache

- `ci/premerge_gates.py` caches the base tree's passing fast gates under
  `${XDG_CACHE_HOME:-$HOME/.cache}/gororoba-quantum/premerge`.
  - The key covers the base commit, the interpreters and their
    distributions, the PATH tools and the gate environment.
  - Failures are never cached and rerun on the base through
    `ci/run_gates.py --gates`.
- The first premerge against a new main commit runs both trees. Later
  premerges under the same key run the merge tree plus a base rerun of
  each merge failure the cached passes do not cover.
- A host change the key omits shows up as an introduced failure, which
  blocks the merge rather than hiding one. `--no-cache` reruns the base in
  full.
- `ci/run_gates.py --changed-files` already skips full-tier gates whose
  declared inputs are unchanged. Skipping unchanged pull-request-tier gates
  is not done yet, and needs each gate's recorded read set. Whole-tree
  record gates reach their inputs through glob, directory listing and git,
  which an import closure misses. Any skip rule needs a self-test with a
  planted missed input.

## Behavioral test suite

The script-gate harness is the next redesign. Each gate starts its own
process, so every Python gate pays for interpreter start-up and each one
that imports qiskit pays for that import again. The long gates re-derive
retained evidence end to end. The target is a normal-Python behavioral
suite:

- pytest with xdist, so modules import once per worker;
- expensive fixtures built once per input digest into a shared file cache
  that every xdist worker reads, since pytest builds a session fixture once
  per worker, with the per-worker setup measured against the budget;
- each module's self-test body moved into test functions;
- an end-to-end replay runs in a pull request whose changes reach its
  code or declared inputs, as full-tier selection does now; the other
  pull requests check only the retained digests, and a nightly job runs
  every replay.

Migrate directory by directory. Each migration deletes the gates its tests
replace and shows, with a planted mutant per moved contract, that the new
tests catch what the old gates caught. A pull-request wall budget enforced
from retained durations keeps the suite fast.

## Bytecode cache

Most Python gate commands pass `-B` or set `PYTHONDONTWRITEBYTECODE=1`. Both
stop Python from writing bytecode but still let it read existing bytecode. A
cache under `PYTHONPYCACHEPREFIX` moves every module's bytecode, site-
packages included, so a cold prefix recompiles qiskit, numpy and scipy in
every process.

1. Fill the prefix once with `compileall --invalidation-mode checked-hash`
   over the checkout and the interpreter's site-packages before the first
   gate. Hash validation keeps restored bytecode valid across checkouts,
   which give every source a new modification time.
2. Restore the prefix between CI runs.
3. Keep the change only if a shard's summed gate CPU time falls with a cold
   prefix included.

## Quantum work owned elsewhere

- Session ibmquantum-12 owns every N=21 item: the initialization-herald
  case, its dry runs and approval, the superseded window-bracket case PR,
  and the herald admission-rule issue.
- The experiment source digest changed with the assert-ban merge, so the
  next herald dry run starts from current main. A record approved before
  that merge refuses at submission.
- The analyzer `scripts/n21_orbit_rca.py` names a deleted gate in one
  docstring. The owner fixes it in the change that rebinds the case's
  analyzer digest.
- The correlated-initialization issue stays open. It closes on the
  joint-coincidence reading of the herald run, compared against the
  independent-marginal prediction.


ET row integration provides exact signed fixtures, coherent row circuits, reusable operator compilation, complete acquisition controls, collection reconstruction, and calibrated paired inference. The experiment contract and replay commands are documented in gororoba_quantum/ET_ROWS.md and docs/evidence/et_rows/README.md. The evidence bundle retains the frozen Heron planning record and native circuit archive.

ET hardware acquisition remains held. The retained Heron qualification refuses the fixed campaign on quota and calibrated inference grounds. Further acquisition requires adequate calibration precision, statistical power, and available allowance, followed by approval of the concrete execution case. Doubling, Tuna native synthesis, and optical transformation conformance retain separate qualification gates. The shutdown reconciliation preserves the incoming optimizer exception check; a fresh CI replay of the shutdown merge remains deferred.

## Nullity-twelve local dimension at the {a, 0} witnesses

The local dimension of D_(5,12) at a nonzd-axis witness {e_i, 0} lies
between the family dimension and the tangent bound, and no retained
certificate decides it. The composite of the two exact half turns over the
{a, 0} family leaves the locus, so it supplies no piece of the larger
dimension; a single turn keeps the nullity only from family points whose
octonion halves are parallel among the points evaluated. The evidence lives
in `docs/evidence/rank_locus_rotation_composite/` and the outcome under the
third computation of `docs/notes/rank_locus_two_dimension_gap.md`.

Two routes remain. The first writes equations that cut out D_(5,12) near
{e_i, 0}: the centered Schur complement of the second-order record carried
to the orders its vacuous tests leave open, which bounds the local dimension
from above where a tangent cone cannot. The second constructs a curve or
parameter family through the witness that is not a product of half turns
and certifies its nullity exactly along its parameters, which bounds it from
below.

The tangent bound off the witness stratum rests on point evaluations. A
symbolic or stratified rank argument over C_4^perp extends it to the whole
family. The related-triple orbit statements are first-order tangent spaces
at sampled points; invariance of the family span under every generator is
unchecked, and no parameter reduction depends on it.

The nullity-eight and nullity-four families keep the same open question,
and the same two routes apply to them.

## Global classification of the nullity-twelve stratum

Roadmap item 3 at nullity twelve (inventory of the known pieces, their
pairwise incidences, and a covering argument) waits on the local-dimension
question above, since the {a, 0} piece enters the inventory at whatever
dimension that question settles. The step plan is in
`docs/local/plans/pr206-f4-r1-restart.md`, section C.

## Tuna-17 coupler interaction map

The retained coupler map on main, generated by
`scripts/qi_coupler_zz_map.py`, measures every Tuna-17 coupling edge from
both ends in one bipartite assignment plus a role swap; it is the coupler
result of record. The static-neighbor conditional-Ramsey design on the
branch `archive/tuna-zz-map` (`scripts/qi_zz_map.py`) is an independent
cross-check whose added observables are explicit neighbor states 0 and 1,
both probe directions per edge and joint pair readout calibration. Its full
form is too long to acquire under the hardware pause policy. A short pilot
from it is justified only by a question those observables answer and the
retained map leaves open; it needs a QX dry run, a written case and owner
approval under the Tuna-17 ownership and submission limits.

## Untouched branch

`tuna/bipartite-walsh-and-lcu-packing` carries Design B and the
usable-graph analysis, which fold into the next Tuna note.

## N=21 feedback program

- The feedback-encoded N=21 endpoint produced a null on Kingston. The
  calibration model predicted a contrast the device did not deliver, so
  added shots narrow the null without explaining it. The next acquisition
  is the orbit root-cause diagnostic, not a repeat of the endpoint.
- The orbit diagnostic separates window dephasing, coherent window phase and
  extra-readout backaction through its delay, echo and extra-readout arms.
  An all-null result leaves mid-circuit assignment error, conditional
  dispatch failure and common dephasing indistinguishable, and that outcome
  calls for a truth-labeled measurement or dispatch control.
- The retained orbit dry run predates the assert-ban merge and carries the
  planner's timing error, so it is retired as an approval target. A fresh
  dry run from current main at the short repetition delay replaces it, with
  its shot tier chosen by the between-arm contracts rather than the large
  absolute contrast.
- The planner prices a shot from the measurement alone plus a classical
  latency term. The backend schedule instead holds the IBM initialization
  and finalization blocks and no latency term, and the per-shot circuit
  time equals the repetition delay plus the scheduled duration. The planner
  fix prices from the scheduled duration, drops the latency term, sizes the
  execution ceiling as circuit time plus executor-lock overhead, and
  refuses a repetition delay below the measured working floor. This planner
  change is unresolved: `QPU_OPTIMIZATION.md` still adds a declared
  feed-forward latency allowance, and the short-delay and failed-job records
  that support the revision are unretained. The next acquisition keeps the
  documented model until those records and their analysis land on main.
- The service enforces the execution ceiling on executor-lock occupancy,
  which exceeds circuit time by a margin that grows at short repetition
  delays. Every ceiling cancellation reports the same max-time error code.
- A per-PUB shot ceiling bounds every tier; a design that needs more shots
  needs a validated multi-PUB estimator.
- `scripts/state_prep_excess.py` on main bounds initialization error at
  any repetition delay. Its docstring still owes
  the statement that finalization opens with a measurement stimulus, so the
  affine bound holds with the pre-finalization population.
- The branch `live/rep-delay-zero-control-records` holds a local, unpushed
  commit with the state-prep control parameter extractor, its sidecars and
  the short-delay and failed control runs. Its inventory gates fail until
  the service inventory records the failed jobs, which waits on settled
  charges and a failed-job inventory extension built on the named-account
  overflow branch. Its findings note still argues a timeout-code distinction
  the retained jobs refute, and its review threads ask for failed-run
  retention and a repetition-delay floor guard.
- `scripts/n21_orbit_rca.py` names a deleted gate in one docstring; the fix
  lands with the rebind of the herald case's analyzer digest.
- The handed-over window-bracket pull request closes as superseded once its
  open review thread is answered.
- Program analysis and both reviews live in `docs/local/reviews/`, and the
  submit scripts and admitted qubit lists in `docs/local/n21-handover/`.


ET approval preflight uses deduplicated parallel ideal validation. The focused approval and optimizer-rejection regressions pass. A complete runner dry run and continuous integration replay remain pending for the integrated changes. The retained native evidence remains bound to its recorded source commit.

## Belenos photonic campaign

- On Q1's served mesh, the sample budget of a job's opening entry separates
  failing jobs from passing ones, in both the single and the iterated form.
  A failing opening holds its wrong state until the job loads another mesh,
  and a low-budget opening lets the large entry right after it pass. The
  split is descriptive, because the rule was read off the jobs it counts. The contingency table, the covariate check and
  the falsification plan are in
  `docs/notes/quandela/belenos-first-load-hypothesis-2026-10-18.md`, and
  the campaign record is in `docs/notes/quandela/strategy.md`.
- The jobs left, in order, each its own job, collected and read before the
  next is planned:
  1. A back-to-back pair at one hour on Q1's mesh, low opening first. The
     first job opens low and follows with consecutive large entries; the
     second opens large. The pair separates budget from time of day and
     tests persistence without a refresh.
  2. The threshold job: an intermediate-budget opening. It runs only when
     the low-opening job passes and the large-opening job fails; any other
     pair outcome makes the axis time or service state and drops it. An
     intermediate reading here is inconclusive.
  3. The prevention job: an opening on the reference mesh followed by a
     high-budget entry on Q1's mesh.
- Stop the series on a void or intermediate reading. Each job waits for a
  written case and the user's approval. No case directory exists for these
  jobs yet:
  - `scripts/qd_belenos_mesh.py` generates case directories;
  - `scripts/qd_belenos_cone.py` reads them out;
  - every job uses the fixed reproduction seeds that serve Q1's mesh and the
    reference mesh, recorded in the strategy note. Fresh ANU draws are
    reserved for exploratory meshes, since a new seed can serve an
    unexplored mesh and void a mesh-specific reading.
- Iterated jobs pay one per-job charge however many entries they hold, and
  each entry costs a fixed few seconds whatever its budget. Only a job's
  first entry observes the opening state, so packing fills a job with the
  repeated entries and controls of its own arm, never with another arm's
  opening question.
- Warming up on another mesh before entries on Q1's mesh is a candidate
  procedure only. It becomes the campaign procedure when the prevention job
  passes.
- The complete-mesh stale-load sweep lives only in the strategy record. A
  replayable sweep artifact is owed under `docs/evidence/quandela/`. The
  partial or mixed configuration fit has not been run. Both are offline
  and need no credit.
- The origin of the bursty off-cone one-click background on the low-index
  modes is open. The light-cone reading excludes those clicks from every
  score.

## N=21 feed-forward on other backends

`docs/notes/n21_feedforward_backends.md` ranks the services that can run the
feedback-encoded N=21 circuit and closes on owner actions. Open Quantum's IQM
Garnet and Emerald lead the ranking and wait on two inputs: the backends
accepting jobs again, and a square-lattice routing of the circuit, which no
branch holds. The routed entangling-gate count decides whether the Spark
balance meets the family's Hoeffding contract. A one-circuit Garnet probe
comes first: it tests `cc_prx` at a quarter turn, the QASM lowering of the
feedback key, one key driving both the reset and the S-dagger, and whether
mid-circuit bits return in counts. Amazon Braket's guide excludes control of
a qubit after an active reset, so Braket stays out unless a reset-free
variant of the circuit exists. IBM's larger Open Plan allowance opens only
after the account logs the runtime its prerequisite names. The N=21 owner
holds this program; each acquisition needs its own written case.

## Unretained dry-run console logs

`results/live/unretained-dry-run-logs/` keeps the console output of dry runs
whose audit records no longer exist, indexed by sha256 in its README. A
dry-run record cannot be regenerated, because it reads each backend's live
Target at run time, so run output belongs in the tree and never in a scratch
or trash location. A global `*.log` ignore rule on the build host drops log
files from `git add` without a message; `git add -f` and a tree listing of
the commit confirm retention.

## Merges without CI

The feed-forward backend note and the dry-run log directory merged on
Codex review alone, without a completed CI run. Several other changes on
main also wait for their first full CI run, so a red shard traces to the
failing gate's declared inputs, not to any one of those merges.

## Archived stash

The branch `archive/n21-orbit-rca-window-unitary-model` points at the stash
commit itself, so a fresh clone recovers the window-unitary model for the
orbit root-cause work from that branch's tip diff against its first parent.
The local stash entry stays as well. The N=21 owner decides whether the
content joins a change or the archive alone carries it.
