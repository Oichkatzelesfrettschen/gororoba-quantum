"""The successor binding run's calibration coverage check against the null's rehearsal record."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import msq_successor_coverage as cov

FIXTURE = Path(__file__).resolve().parent / "data/msq_successor_null/record"
FAMILY = "measurement-sequence-relaxation"


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


def copy(tmp_path: Path, label: str, *, family: str = FAMILY, width: int | None = None) -> Path:
    """A copy of the null's test record carrying the family name a dry-run record holds and the trim drops,
    optionally cut to its first `width` layout qubits."""
    out = tmp_path / label
    shutil.copytree(FIXTURE, out)
    record = json.loads((out / "record.json").read_text())
    record["family_configuration"]["name"] = family
    if width is not None:
        record["family_configuration"]["qubits"] = record["family_configuration"]["qubits"][:width]
    (out / "record.json").write_text(json.dumps(record))
    return out


def layout() -> list[int]:
    return [int(q) for q in json.loads((FIXTURE / "record.json").read_text())["family_configuration"]["qubits"]]


def properties(record_dir: Path) -> dict[str, object]:
    record = json.loads((record_dir / "record.json").read_text())
    path = record_dir / "envelope-snapshots" / f"{record['envelope']['planning_snapshot_sha256']}.json"
    return dict(json.loads(path.read_text())["properties"])


def drifted(tmp_path: Path, qubits: int | list[int], name: str, scale: float) -> Path:
    """A copy of the test record whose snapshot scales a quantity of one or several qubits, under its own digest."""
    out = copy(tmp_path, "run")
    record = json.loads((out / "record.json").read_text())
    old = out / "envelope-snapshots" / f"{record['envelope']['planning_snapshot_sha256']}.json"
    snapshot = json.loads(old.read_text())
    for qubit in [qubits] if isinstance(qubits, int) else qubits:
        if name == "sx_error":
            items = next(
                g["parameters"] for g in snapshot["properties"]["gates"] if g["gate"] == "sx" and g["qubits"] == [qubit]
            )
            target = "gate_error"
        else:
            items, target = snapshot["properties"]["qubits"][qubit], name
        next(item for item in items if item["name"] == target)["value"] *= scale
    data = json.dumps(snapshot).encode()
    digest = hashlib.sha256(data).hexdigest()
    old.unlink()
    (out / "envelope-snapshots" / f"{digest}.json").write_bytes(data)
    record["envelope"]["planning_snapshot_sha256"] = digest
    (out / "record.json").write_text(json.dumps(record))
    return out


def test_the_rehearsal_covers_itself(tmp_path: Path) -> None:
    rehearsal = copy(tmp_path, "rehearsal")
    check(cov.violations(rehearsal, rehearsal, 1.01) == [])
    check(cov.main([str(rehearsal), str(rehearsal), "--factor", "1.01"]) == 0)


def test_one_qubit_drifting_inside_the_pool_range_passes(tmp_path: Path) -> None:
    rehearsal = copy(tmp_path, "rehearsal")
    pool = {q: cov.calibration(properties(FIXTURE), q) for q in layout()}
    for name in cov.DRIFTING:
        qubit = min(pool, key=lambda q: pool[q][name])
        check(cov.violations(rehearsal, drifted(tmp_path / name, qubit, name, 1.6), 1.5) == [], name)


def test_a_device_wide_shift_beyond_the_factor_refuses_on_the_median(tmp_path: Path) -> None:
    rehearsal = copy(tmp_path, "rehearsal")
    for name in cov.QUANTITIES:
        inside = drifted(tmp_path / f"{name}-inside", layout(), name, 1.3)
        check(cov.violations(rehearsal, inside, 1.5) == [], name)
        for scale in (1.6, 1 / 1.6):
            found = cov.violations(rehearsal, drifted(tmp_path / f"{name}-{scale:.3f}", layout(), name, scale), 1.5)
            refused = any(line.startswith(f"layout median {name} ") for line in found)
            check(refused == (scale > 1 or name in cov.DRIFTING), f"{name} x{scale:.3f}: {found}")


def test_a_value_beyond_the_widened_layout_range_refuses(tmp_path: Path) -> None:
    rehearsal, qubit = copy(tmp_path, "rehearsal"), layout()[0]
    pool = [cov.calibration(properties(FIXTURE), q) for q in layout()]
    scale = 3.0 * max(c["T1"] for c in pool) / cov.calibration(properties(FIXTURE), qubit)["T1"]
    found = cov.violations(rehearsal, drifted(tmp_path, qubit, "T1", scale), 2.0)
    check(any(line.startswith(f"q{qubit} T1 ") and "widened rehearsal range" in line for line in found))


def test_a_readout_error_refuses_only_above_the_widened_layout_maximum(tmp_path: Path) -> None:
    rehearsal, qubit = copy(tmp_path, "rehearsal"), layout()[0]
    pool = [cov.calibration(properties(FIXTURE), q) for q in layout()]
    for name in cov.READOUT:
        own = cov.calibration(properties(FIXTURE), qubit)[name]
        high = drifted(tmp_path / f"{name}-high", qubit, name, 3.0 * max(c[name] for c in pool) / own)
        check(
            any(
                line.startswith(f"q{qubit} {name} ") and "maximum" in line
                for line in cov.violations(rehearsal, high, 2.0)
            )
        )
        check(cov.violations(rehearsal, drifted(tmp_path / f"{name}-zero", qubit, name, 0.0), 1.01) == [], name)


def test_a_width_or_family_other_than_the_rehearsal_refuses(tmp_path: Path) -> None:
    rehearsal = copy(tmp_path, "rehearsal")
    check(any("layout width" in line for line in cov.violations(rehearsal, copy(tmp_path, "narrow", width=8), 2.0)))
    other = copy(tmp_path, "other", family="measurement-sequence-envelope")
    check(any(line.startswith("family ") for line in cov.violations(rehearsal, other, 2.0)))


def test_a_shot_count_other_than_the_rehearsal_refuses(tmp_path: Path) -> None:
    rehearsal, run = copy(tmp_path, "rehearsal"), copy(tmp_path, "run")
    record = json.loads((run / "record.json").read_text())
    record["shots"] = int(record["shots"]) // 2
    (run / "record.json").write_text(json.dumps(record))
    check(any(line.startswith("shots ") for line in cov.violations(rehearsal, run, 2.0)))
    check(cov.main([str(rehearsal), str(run), "--factor", "2"]) == 1)


def test_an_unreadable_record_and_a_factor_of_one_exit_two(tmp_path: Path) -> None:
    rehearsal = copy(tmp_path, "rehearsal")
    check(cov.main([str(rehearsal), str(tmp_path / "missing"), "--factor", "2"]) == 2)
    check(cov.main([str(rehearsal), str(rehearsal), "--factor", "1"]) == 2)


def test_an_experiment_digest_other_than_the_rehearsal_refuses(tmp_path: Path) -> None:
    rehearsal, run = copy(tmp_path, "rehearsal"), copy(tmp_path, "run")
    for path, digest in ((rehearsal, "a" * 64), (run, "b" * 64)):
        record = json.loads((path / "record.json").read_text())
        record["experiment_digest"] = digest
        (path / "record.json").write_text(json.dumps(record))
    check(any(line.startswith("experiment digest ") for line in cov.violations(rehearsal, run, 2.0)))
    check(cov.violations(rehearsal, rehearsal, 2.0) == [])


def test_a_duration_outside_the_pool_range_refuses(tmp_path: Path) -> None:
    rehearsal, qubit = copy(tmp_path, "rehearsal"), layout()[0]
    pool = [cov.durations(properties(FIXTURE), q)["readout_length"] for q in layout()]
    scale = 1.01 * max(pool) / cov.durations(properties(FIXTURE), qubit)["readout_length"]
    found = cov.violations(rehearsal, drifted(tmp_path, qubit, "readout_length", scale), 2.0)
    check(any(line.startswith(f"q{qubit} readout_length ") for line in found), f"{found}")


def summary(snapshot: str, width: int, shots: int) -> dict[str, object]:
    """A null summary holding one passing record of every arm on the given snapshot, width and shots."""
    case = {"fires": 0, "exposed_fires": 0, "targets": {"target": True}}
    return {
        "records": [
            {
                "arm": arm,
                "snapshot_sha256": snapshot,
                "layout_width": width,
                "shots": shots,
                "cases": {"all": dict(case)},
            }
            for arm in cov.nl.ARMS
        ]
    }


def test_the_null_summary_must_cover_the_rehearsal_without_a_fire_or_missed_target(tmp_path: Path) -> None:
    rehearsal = copy(tmp_path, "rehearsal")
    record = json.loads((rehearsal / "record.json").read_text())
    snapshot, width, shots = (
        record["envelope"]["planning_snapshot_sha256"],
        int(record["family_configuration"]["layout_width"]),
        int(record["shots"]),
    )
    check(cov.violations(rehearsal, rehearsal, 1.01, summary(snapshot, width, shots)) == [])
    check(
        any(
            "has no record" in line
            for line in cov.violations(rehearsal, rehearsal, 1.01, summary("0" * 64, width, shots))
        )
    )
    check(
        any(
            "has no record" in line
            for line in cov.violations(rehearsal, rehearsal, 1.01, summary(snapshot, width, shots + 1))
        )
    )
    for key, value, words in (("fires", 1, "fired"), ("targets", {"target": False}, "missed target")):
        bad = summary(snapshot, width, shots)
        records = bad["records"]
        if not isinstance(records, list):
            raise TypeError("summary records")
        records[0]["cases"]["all"][key] = value
        found = cov.violations(rehearsal, rehearsal, 1.01, bad)
        check(any(words in line for line in found), f"{key}: {found}")
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(summary(snapshot, width, shots)))
    check(cov.main([str(rehearsal), str(rehearsal), "--factor", "1.01", "--null", str(path)]) == 0)
