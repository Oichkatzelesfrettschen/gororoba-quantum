"""Contract for qd_surface: value classes, field diff states (absent, new, changed), figure diff and exit status."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import qd_surface  # noqa: E402


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def record(**specs: object) -> dict[str, object]:
    return {
        "status": "available",
        "perfs": {"HOM (%)": 88.8, "Dark counts (detection/s)": [1.0, 2.0]},
        "specs": {
            "architecture": "<chip>" * 20,
            "detector": "threshold",
            "constraints": {"max_photon_count": 12},
            **specs,
        },
    }


def surface(**records: dict[str, object]) -> dict[str, object]:
    rows = [{"name": name, "type": "qpu"} for name in records]
    return qd_surface.build(rows, records, "2026-11-27T23:42:00+00:00")


def test_classify_names_each_value_class() -> None:
    cases: list[tuple[object, str]] = [
        (None, "null"),
        (True, "bool"),
        (3, "int"),
        (1.5, "float"),
        ("", "empty"),
        ("a", "str"),
    ]
    cases += [([], "empty"), ([1], "list"), ({}, "empty"), ({"k": 1}, "object")]
    for value, expected in cases:
        check(qd_surface.classify(value) == expected, f"{value!r}")


def test_surface_keeps_figures_and_drops_long_fields() -> None:
    entry = surface(p=record())["platforms"]["p"]  # type: ignore[index]
    check(entry["fields"]["specs.architecture"] == "str", "contract broken")
    check("specs.architecture" not in entry["figures"], "contract broken")
    check(entry["figures"]["perfs.HOM (%)"] == 88.8, "contract broken")
    check(entry["fields"]["perfs.Dark counts (detection/s)"] == "list", "contract broken")


def test_equal_surfaces_have_no_difference() -> None:
    base = surface(p=record())
    check(qd_surface.diff(base, base) == {"fields": [], "figures": []}, "contract broken")


def test_absent_new_and_changed_fields() -> None:
    base = surface(p=record(commands="x" * 10))
    specs = record(default_mitigations=["m"], detector=None)
    specs["specs"].pop("architecture")  # type: ignore[attr-defined]
    live = surface(p=specs)
    states = {(row[1], row[2]) for row in qd_surface.diff(base, live)["fields"]}
    check(("specs.architecture", "absent") in states, "contract broken")
    check(("specs.commands", "absent") in states, "contract broken")
    check(("specs.default_mitigations", "new") in states, "contract broken")
    check(("specs.detector", "changed") in states, "contract broken")


def test_figure_change_is_not_a_field_change() -> None:
    live = record()
    live["perfs"]["HOM (%)"] = 90.1  # type: ignore[index]
    result = qd_surface.diff(surface(p=record()), surface(p=live))
    check(result["fields"] == [], "contract broken")
    check(result["figures"] == [("p", "perfs.HOM (%)", "88.8", "90.1")], "contract broken")


def test_platform_listing_changes() -> None:
    result = qd_surface.diff(surface(p=record(), q=record()), surface(p=record(), r=record()))
    check({(row[0], row[2]) for row in result["fields"]} == {("q", "absent"), ("r", "new")}, "contract broken")


def test_main_exit_status_follows_the_field_surface(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    base, same, drift = tmp_path / "base.json", tmp_path / "same.json", tmp_path / "drift.json"
    base.write_text(json.dumps(surface(p=record())), encoding="utf-8")
    same.write_text(json.dumps(surface(p=record())), encoding="utf-8")
    lost = record()
    lost["specs"].pop("architecture")  # type: ignore[attr-defined]
    drift.write_text(json.dumps(surface(p=lost)), encoding="utf-8")
    check(qd_surface.main(["diff", "--baseline", str(base), "--live", str(same)]) == 0, "contract broken")
    check(qd_surface.main(["diff", "--baseline", str(base), "--live", str(drift)]) == 1, "contract broken")
    check("| `p` | `specs.architecture` | absent | str | - |" in capsys.readouterr().out, "contract broken")


def test_load_refuses_another_schema(tmp_path: Path) -> None:
    other = tmp_path / "other.json"
    other.write_text(json.dumps({"schema": "x"}), encoding="utf-8")
    with pytest.raises(SystemExit):
        qd_surface.load(other)
