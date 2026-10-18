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
Codex review alone, without a completed CI run. The next full CI run on main
is their first gate check, and a red shard there traces to them first.

## Archived stash

The branch `archive/n21-orbit-rca-window-unitary-model` holds a repo-wide
stash entry of the window-unitary model for the orbit root-cause work. The
stash itself remains in place, and the N=21 owner decides whether its content
joins a change or the archive alone carries it.
