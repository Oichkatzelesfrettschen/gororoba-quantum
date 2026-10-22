"""Contract for ci/replay_check.py: every value compares exactly outside the skipped identity paths, and the
replay runs the analyzer's own writer through the {out} placeholder.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import replay_check


def expect(found: Any, wanted: Any) -> None:
    if found != wanted:
        raise AssertionError(f"{found!r} != {wanted!r}")


def test_every_value_compares_exactly() -> None:
    retained = {"status": "pass", "cell": 0, "fit": [1.0, 2e-9], "ok": True, "note": None}
    differences = replay_check.differences
    expect(differences(retained, dict(retained)), [])
    expect(differences(retained, retained | {"fit": [1.0 + 2**-52, 2e-9]}), [f".fit[0]: 1.0 -> {1.0 + 2**-52!r}"])
    expect(differences(retained, retained | {"cell": 1}), [".cell: 0 -> 1"])
    expect(differences(retained, retained | {"cell": 0.0}), [".cell: 0 -> 0.0"])
    expect(differences({"x": 0.0}, {"x": -0.0}), [".x: 0.0 -> -0.0"])
    expect(differences({"x": float("nan")}, {"x": float("nan")}), [])
    expect(differences(retained, retained | {"status": "fail"}), [".status: 'pass' -> 'fail'"])
    expect(differences(retained, retained | {"ok": 1}), [".ok: True -> 1"])
    expect(differences(retained, retained | {"fit": [1.0]}), [".fit: length 2 -> 1"])
    expect(differences(retained, {**retained, "extra": 1}), [".: keys ['extra'] on one side only"])


def test_skipped_paths_drop_from_both_sides() -> None:
    retained = {"analyzer_closure": {"sha256": "aa"}, "fit": 1.0}
    fresh = {"analyzer_closure": {"sha256": "bb"}, "fit": 1.0}
    differences = replay_check.differences
    expect(differences(retained, fresh), [".analyzer_closure.sha256: 'aa' -> 'bb'"])
    expect(differences(retained, fresh, "", (".analyzer_closure",)), [])
    expect(differences(retained, {"fit": 1.0}, "", (".analyzer_closure",)), [])
    expect(differences(retained, {"fit": 2.0}, "", (".analyzer_closure",)), [".fit: 1.0 -> 2.0"])


def run(retained: Path, value: object, *options: str) -> int:
    writer = f"import json, sys; open(sys.argv[1], 'w').write(json.dumps({value!r}))"
    return replay_check.main([str(retained), *options, "--", sys.executable, "-c", writer, "{out}"])


def test_replay_runs_the_writer_and_skips_identity() -> None:
    with TemporaryDirectory() as directory:
        retained = Path(directory) / "analysis.json"
        retained.write_text(json.dumps({"value": 1.0, "analyzer_sha256": "aa"}))
        expect(run(retained, {"value": 1.0, "analyzer_sha256": "aa"}), 0)
        expect(run(retained, {"value": 1.0, "analyzer_sha256": "bb"}), 1)
        expect(run(retained, {"value": 1.0, "analyzer_sha256": "bb"}, "--skip", ".analyzer_sha256"), 0)
        expect(run(retained, {"value": 1.0 + 1e-12, "analyzer_sha256": "aa"}), 1)
        failing = ["--", sys.executable, "-c", "raise SystemExit(3)", "{out}"]
        expect(replay_check.main([str(retained), *failing]), 3)
