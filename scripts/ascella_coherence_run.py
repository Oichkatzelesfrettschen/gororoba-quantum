"""Registered analysis of a collected run of the Ascella signed-coherence request.

--run DIR analyzes a collected run directory: its cases.json must be the
frozen request's bytes, and each results.json iteration is attributed to the
setting at its position only when it carries counts and echoes that setting's
circuit_params. Every returned state must span twelve modes; occupation-sum-one
states are eligible and vacuum and multiple-occupation states are tallied as
exclusions. ascella_coherence_analysis.analyze decides the 27 endpoints, and
the record lands in DIR/analysis.json, which a rerun must reproduce byte for
byte.

Usage:
  "$PYTHON" scripts/ascella_coherence_run.py --run DIR
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import ascella_coherence_analysis as analysis

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "results/quandela/cases/ascella_signed_coherence/job-00/cases.json"
PARAMETER_TOLERANCE = 1e-12


def attributed(
    manifest: dict[str, Any], results: dict[str, Any]
) -> tuple[list[list[int] | None], dict[str, list[int]]]:
    """Twelve-mode eligible counts per iteration from a collected results.json, and the per-iteration exclusions.

    An entry without counts (error, malformed or missing) leaves its position
    None. A counted entry whose echoed circuit_params differ from its setting's
    raises, because counts at the wrong position would enter another
    setting's statistic.
    """
    entries = results.get("iterations")
    if not isinstance(entries, list) or len(entries) > analysis.ENTRIES:
        raise ValueError(f"results.json carries {type(entries).__name__} iterations, not up to {analysis.ENTRIES}")
    rows: list[list[int] | None] = [None] * analysis.ENTRIES
    exclusions = {"vacuum": [0] * analysis.ENTRIES, "multiple": [0] * analysis.ENTRIES}
    for position, (entry, setting) in enumerate(zip(entries, manifest["settings"], strict=False)):
        if "counts" not in entry:
            continue
        echoed = entry.get("iteration", {}).get("circuit_params")
        expected = setting["circuit_params"]
        if not isinstance(echoed, dict) or sorted(echoed) != sorted(expected):
            raise ValueError(f"iteration {position}: circuit_params do not name {setting['name']}'s parameters")
        for name, value in expected.items():
            if not math.isclose(echoed[name], value, rel_tol=0.0, abs_tol=PARAMETER_TOLERANCE):
                raise ValueError(f"iteration {position}: {name} is {echoed[name]}, not {setting['name']}'s {value}")
        vector = [0] * analysis.MODES
        for state, count in entry["counts"].items():
            occupation = [int(n) for n in state.split(",")]
            if len(occupation) != analysis.MODES:
                raise ValueError(
                    f"iteration {position}: state {state} spans {len(occupation)} modes, not {analysis.MODES}"
                )
            photons = sum(occupation)
            if photons == 1:
                vector[occupation.index(1)] += count
            else:
                exclusions["vacuum" if photons == 0 else "multiple"][position] += count
        rows[position] = vector
    return rows, exclusions


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze_run(directory: Path) -> dict[str, Any]:
    """The registered analysis of a collected run directory of the frozen request."""
    cases = directory / "cases.json"
    if cases.read_bytes() != FROZEN.read_bytes():
        raise ValueError(f"{cases} is not the frozen request {FROZEN.relative_to(ROOT)}")
    manifest = json.loads(cases.read_text(encoding="utf-8"))
    results = json.loads((directory / "results.json").read_text(encoding="utf-8"))
    rows, exclusions = attributed(manifest, results)
    eligible = [None if row is None else sum(row) for row in rows]
    return {
        "schema": "ascella-signed-coherence-analysis-v1",
        "job_id": results.get("job_id"),
        "status": (results.get("status") or {}).get("status"),
        "partial": results.get("partial"),
        "mode_counts": rows,
        "eligible": eligible,
        "exclusions": exclusions,
        "outside_logical_block": [None if row is None else sum(row[4:]) for row in rows],
        "analysis": analysis.analyze(manifest, rows),
        "source_sha256": {
            name: sha256_file(directory / name) for name in ("cases.json", "results.json", "submission.json")
        }
        | {
            "scripts/ascella_coherence_run.py": sha256_file(Path(__file__)),
            "scripts/ascella_coherence_analysis.py": sha256_file(Path(analysis.__file__)),
        },
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] != "--run":
        raise SystemExit(f"usage: ascella_coherence_run.py --run DIR, not {argv}")
    directory = Path(argv[1])
    record = analyze_run(directory)
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    out = directory / "analysis.json"
    # A retained analysis is evidence: a rerun reproduces it and never rewrites it.
    if out.exists() and out.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{out} differs from the recomputed analysis")
    out.write_text(text, encoding="utf-8")
    summary = record["analysis"]
    print(f"{directory.name}: complete {summary['complete']}, {summary.get('verdicts', summary.get('reason'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
