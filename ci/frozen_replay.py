"""Run a retained analyzer closure: ``"$PYTHON" ci/frozen_replay.py CLOSURE_DIR SCRIPT [ARGS...]``.

CLOSURE_DIR holds the bytes of the scripts/ files a record's approval bound
(policy.design ramsey_analyzer_closure; a segmented closure also binds
gororoba_quantum/ and has no frozen form here), under a directory named scripts so
qpu_planning.analyzer_closure keys them as the record does. qpu_planning reads
SCRIPTS_DIR and RAMSEY_ANALYZER at call time, so pointing them at CLOSURE_DIR
makes the retained analyzer hash itself and accept its own record, while the
live scripts/ go on changing. SCRIPT runs as __main__ with CLOSURE_DIR first on
sys.path; the gororoba_quantum/ modules, which no closure binds, come from the
tree.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import qpu_planning  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        raise SystemExit("frozen_replay: name CLOSURE_DIR and SCRIPT")
    closure, script = Path(argv[0]).resolve(), Path(argv[1]).resolve()
    if script.name != "n21_spectator_ramsey.py":
        raise SystemExit(
            "frozen_replay: only a Ramsey closure (scripts/ alone, qpu_planning.ramsey_analyzer_closure) replays"
        )
    if closure.name != "scripts" or script.parent != closure:
        raise SystemExit(f"frozen_replay: {script} is not a script of the closure directory {closure} (named scripts)")
    qpu_planning.SCRIPTS_DIR = closure
    qpu_planning.RAMSEY_ANALYZER = closure / "n21_spectator_ramsey.py"
    sys.path.insert(0, str(closure))
    sys.argv = [str(script), *argv[2:]]
    runpy.run_path(str(script), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
