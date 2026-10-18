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

The complete conditional-Ramsey design is preserved on the branch
`archive/tuna-zz-map`, including `scripts/qi_zz_map.py`. Its full form is too
long to acquire under the hardware pause policy. A short reciprocal pilot
regenerated from that generator, preceded by a QX dry run and a written
case, is the next acquisition candidate; it needs owner approval and falls
under the Tuna-17 ownership and submission limits.

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
  refuses a repetition delay below the measured working floor.
- The service enforces the execution ceiling on executor-lock occupancy,
  which exceeds circuit time by a margin that grows at short repetition
  delays. Every ceiling cancellation reports the same max-time error code.
- A per-PUB shot ceiling bounds every tier; a design that needs more shots
  needs a validated multi-PUB estimator.
- The branch `diagnostics/state-prep-excess-target-delay` bounds
  initialization error at any repetition delay. Its docstring still owes
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
