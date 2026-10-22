"""Contract for ci/replay_check.py: floats within the declared tolerance pass, every discrete field compares
exactly, and the replay runs the analyzer's own writer through the {out} placeholder.
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


def test_floats_within_tolerance_and_discrete_fields_exact() -> None:
    retained = {"status": "pass", "cell": 0, "fit": [1.0, 2e-9], "ok": True, "note": None}
    differences = replay_check.differences
    expect(differences(retained, retained | {"fit": [1.0 + 1e-7, 3e-9]}, 1e-6, 1e-8), [])
    expect(differences(retained, retained | {"fit": [1.1, 2e-9]}, 1e-6, 1e-8), [".fit[0]: 1.0 -> 1.1"])
    expect(differences(retained, retained | {"cell": 1}, 1.0, 1.0), [".cell: 0 -> 1"])
    expect(differences(retained, retained | {"status": "fail"}, 1.0, 1.0), [".status: 'pass' -> 'fail'"])
    expect(differences(retained, retained | {"ok": 1}, 1.0, 1.0), [".ok: True -> 1"])
    expect(differences(retained, retained | {"fit": [1.0]}, 1.0, 1.0), [".fit: length 2 -> 1"])
    expect(differences(retained, {**retained, "extra": 1}, 1.0, 1.0), [".: keys ['extra'] on one side only"])


def run(retained: Path, value: object, *bounds: str) -> int:
    writer = f"import json, sys; open(sys.argv[1], 'w').write(json.dumps({value!r}))"
    return replay_check.main([str(retained), *bounds, "--", sys.executable, "-c", writer, "{out}"])


def test_replay_runs_the_writer_and_applies_the_tolerance() -> None:
    with TemporaryDirectory() as directory:
        retained = Path(directory) / "analysis.json"
        retained.write_text(json.dumps({"value": 1.0}))
        expect(run(retained, {"value": 1.0}), 0)
        expect(run(retained, {"value": 1.0 + 1e-12}), 1)
        expect(run(retained, {"value": 1.0 + 1e-12}, "--rel", "1e-9"), 0)
        expect(run(retained, {"value": 2.0}, "--rel", "1e-9"), 1)
        failing = ["--", sys.executable, "-c", "raise SystemExit(3)", "{out}"]
        expect(replay_check.main([str(retained), *failing]), 3)
