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


def test_field_rules_bound_likelihoods_in_nats() -> None:
    retained = {"fits": {"tls": {"nll": 132959.0, "e0": 0.0044}}, "rows": [{"alias_llr": 1558.9}]}
    rules = (("*.nll", 0.0, 1.0), ("*_llr", 0.0, 1.0))
    differences = replay_check.differences
    drifted = {"fits": {"tls": {"nll": 132959.6, "e0": 0.0044044}}, "rows": [{"alias_llr": 1558.4}]}
    expect(differences(retained, drifted, 1e-3, 1e-4, "", rules), [])
    missed = {"fits": {"tls": {"nll": 132966.0, "e0": 0.0044}}, "rows": [{"alias_llr": 1558.9}]}
    expect(differences(retained, missed, 1e-3, 1e-4, "", rules), [".fits.tls.nll: 132959.0 -> 132966.0"])
    expect(replay_check.rule("*.nll=0,1"), ("*.nll", 0.0, 1.0))


def test_skipped_paths_drop_from_both_sides() -> None:
    retained = {"analyzer_closure": {"sha256": "aa"}, "fit": 1.0}
    fresh = {"analyzer_closure": {"sha256": "bb"}, "fit": 1.0}
    differences = replay_check.differences
    expect(differences(retained, fresh, 0.0, 0.0), [".analyzer_closure.sha256: 'aa' -> 'bb'"])
    expect(differences(retained, fresh, 0.0, 0.0, "", (), (".analyzer_closure",)), [])
    expect(differences(retained, {"fit": 1.0}, 0.0, 0.0, "", (), (".analyzer_closure",)), [])
    expect(differences(retained, {"fit": 2.0}, 0.0, 0.0, "", (), (".analyzer_closure",)), [".fit: 1.0 -> 2.0"])


def test_select_compares_one_subtree() -> None:
    table = {"schema": "t", "rows": [{"llr": 1.0}, {"llr": 2.0, "pairs": [3, 4]}]}
    expect(replay_check.subtree(table, ".rows[1].pairs[0]"), 3)
    with TemporaryDirectory() as directory:
        retained, fresh = Path(directory) / "table.json", Path(directory) / "row.json"
        retained.write_text(json.dumps(table))
        fresh.write_text(json.dumps({"llr": 2.0, "pairs": [3, 4]}))
        expect(replay_check.compare(retained, fresh, 0.0, 0.0, select=".rows[1]"), [])
        expect(
            replay_check.compare(retained, fresh, 0.0, 0.0, select=".rows[0]"), [".: keys ['pairs'] on one side only"]
        )


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
        expect(run(retained, {"value": 1.5}, "--rel", "1e-9", "--field", ".value=0,0.5"), 0)
        baseline = Path(directory) / "baseline.json"
        baseline.write_text(json.dumps({"value": 1.0 + 1e-6}))
        exact = ["--baseline", str(baseline), "--rel", "1e-5"]
        expect(run(retained, {"value": 1.0 + 1e-6}, *exact), 0)
        expect(run(retained, {"value": 1.0 + 2e-6}, *exact), 1)
        expect(run(retained, {"value": 1.0 + 1e-6}, "--baseline", str(baseline), "--rel", "1e-7"), 1)
        failing = ["--", sys.executable, "-c", "raise SystemExit(3)", "{out}"]
        expect(replay_check.main([str(retained), *failing]), 3)
