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

## Belenos photonic campaign

- On Q1's served mesh, the sample budget of a job's opening entry separates
  failing jobs from passing ones, in both the single and the iterated form.
  A failing opening holds its wrong state until the job loads another mesh,
  and a low-budget opening lets the large entry right after it pass. The
  split is descriptive, because the rule was read off the jobs it counts. The contingency table, the covariate check and
  the falsification plan are in
  `docs/notes/quandela/belenos-first-load-hypothesis-2026-10-18.md`, and
  the campaign record is in `docs/notes/quandela/strategy.md`.
- The jobs left, in order:
  1. A back-to-back pair at one hour on Q1's mesh. One job opens low and
     follows with consecutive large entries; the other opens large. The
     pair separates budget from time of day and tests persistence without
     a refresh.
  2. An intermediate-budget opening that locates the threshold. An
     intermediate reading there is inconclusive.
  3. An opening on another mesh followed by a high-budget entry on Q1's mesh,
     which tests prevention.
- Stop the series on a void or intermediate reading. Each job waits for a
  written case and the user's approval. No case directory exists for these
  jobs yet:
  - `scripts/qd_belenos_mesh.py` generates case directories;
  - `scripts/qd_belenos_cone.py` reads them out;
  - new compilation seeds come from the retained ANU draws.
- Iterated jobs pay one per-job charge however many entries they hold, and
  each entry costs a fixed few seconds whatever its budget. Pack every
  question into the entries of one job, up to the credit cap the user sets.
- Warming up on another mesh before entries on Q1's mesh is a candidate
  procedure only. It becomes the campaign procedure when the third job
  passes.
- The complete-mesh stale-load sweep lives only in the strategy record. A
  replayable sweep artifact is owed under `docs/evidence/quandela/`. The
  partial or mixed configuration fit has not been run. Both are offline
  and need no credit.
- The origin of the bursty off-cone one-click background on the low-index
  modes is open. The light-cone reading excludes those clicks from every
  score.
