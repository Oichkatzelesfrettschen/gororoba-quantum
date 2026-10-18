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
  premerges against that commit run only the merge tree.
- A host change the key omits shows up as an introduced failure, which
  blocks the merge rather than hiding one. `--no-cache` reruns the base in
  full.
- Skipping unchanged gates is not done yet, and needs each gate's recorded
  read set. Whole-tree record gates reach their inputs through glob,
  directory listing and git, which an import closure misses. Any skip rule
  needs a self-test with a planted missed input.

## Behavioral test suite

The script-gate harness is the next redesign. One process per gate pays for
interpreter start-up and a qiskit import every time, and the long gates
re-derive retained evidence end to end. The target is a normal-Python
behavioral suite:

- pytest with xdist, so modules import once per worker;
- session-scoped fixtures built once;
- each module's self-test body moved into test functions;
- retained-record replays reduced to digest checks in the pull-request
  suite, with the end-to-end replays moved to a nightly job keyed on input
  changes.

Migrate directory by directory. Each migration deletes the gates its tests
replace and shows, with a planted mutant per moved contract, that the new
tests catch what the old gates caught. A pull-request wall budget enforced
from retained durations keeps the suite fast.

## Bytecode cache

Gate commands pass `-B`, which stops Python from writing bytecode but still
lets it read existing bytecode. A cache under `PYTHONPYCACHEPREFIX` moves
every module's bytecode, site-packages included, so a cold prefix recompiles
qiskit, numpy and scipy in every process.

1. Fill the prefix once with `compileall` over the checkout and the
   interpreter's site-packages before the first gate.
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
