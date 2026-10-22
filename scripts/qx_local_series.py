"""Run every circuit of a written case series on local qxelarator and store the shots as a run directory.

Each batch-NN/ directory of CASE_DIR is copied to OUT_DIR/batch-NN/ with its cases.json and circuits,
and raw/<file>.json holds the shot list of each circuit: qxelarator's histogram expanded in sorted
bit-string order, one character per declared qubit with qubit 0 rightmost. The run needs no account
and no network, and it submits nothing; qxelarator is the local twin of the hosted QX emulator
(docs/notes/quantum_inspire/qx-runs.md), so the shots check cQASM syntax, register shape and the
noiseless law of the circuits and say nothing about a device. It runs under the Quantum Inspire
interpreter, which carries qxelarator and only the standard library is imported here.

Usage: $HOME/.local/share/quantuminspire/venv/bin/python -I scripts/qx_local_series.py CASE_DIR OUT_DIR SHOTS
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


def run_series(case_dir: Path, out_dir: Path, shots: int) -> int:
    import qxelarator

    count = 0
    for batch in sorted(p for p in case_dir.glob("batch-*") if p.is_dir()):
        target = out_dir / batch.name
        if target.exists():
            raise SystemExit(f"{target} exists; remove it before a new dry run")
        shutil.copytree(batch, target)
        manifest = json.loads((batch / "cases.json").read_text(encoding="utf-8"))
        (target / "raw").mkdir()
        for row in manifest["circuits"]:
            result = qxelarator.execute_string((batch / row["file"]).read_text(encoding="utf-8"), iterations=shots)
            if result.shots_done != shots:
                raise SystemExit(f"{row['file']}: {result.shots_done} shots done of {shots}")
            expanded = [bits for bits, n in sorted(result.results.items()) for _ in range(n)]
            (target / "raw" / f"{row['file']}.json").write_text(json.dumps(expanded) + "\n", encoding="utf-8")
            count += 1
    return count


def main() -> int:
    if len(sys.argv) != 4 or not sys.argv[3].isdigit():
        raise SystemExit(__doc__)
    count = run_series(Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]))
    print(f"qx local series: {count} circuits run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
