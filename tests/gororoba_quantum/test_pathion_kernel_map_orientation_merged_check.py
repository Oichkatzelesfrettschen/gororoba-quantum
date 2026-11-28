"""Contract of the xtwin gate-sequence guard of scripts/pathion_kernel_map_orientation_merged_check.py.

The statistic D (control minus exchange) cancels errors that act before the xtwin frame only when both members
compile to one non-rz gate sequence, so the admission check refuses a plan whose xtwin member diverges
(docs/design/pathion-kernel-map-orientation-merged.md, "Gate order of the exchange member").
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _require[T](value: T | None, message: str) -> T:
    if value is None:
        raise AssertionError(message)
    return value


def _check_module() -> ModuleType:
    path = ROOT / "scripts" / "pathion_kernel_map_orientation_merged_check.py"
    spec = importlib.util.spec_from_file_location("pathion_kernel_map_orientation_merged_check", path)
    spec = _require(spec, f"cannot load {path}")
    loader = _require(spec.loader, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_guard_admits_equal_xtwin_and_control_sequences_and_rejects_a_divergent_plan() -> None:
    check = _check_module()
    sx = ("sx", (3,))
    cz = ("cz", (3, 4))
    names = [
        f"kmo_{role}_{tag}_{arm}"
        for role in ("ctrl", "xtwin")
        for tag in ("e1pe26", "e1pe18")
        for arm in ("plus", "minus")
    ]
    equal = {name: [sx, cz, sx] for name in names}
    _expect(check.gate_sequence_failures(equal) == [], "equal sequences were refused")
    divergent = dict(equal)
    divergent["kmo_xtwin_e1pe26_minus"] = [cz, sx, sx]
    found = check.gate_sequence_failures(divergent)
    _expect(
        found == ["kmo_xtwin_e1pe26_minus: non-rz gate sequence differs from kmo_ctrl_e1pe26_minus"],
        f"the divergent xtwin member was not named: {found}",
    )
    missing = {name: seq for name, seq in equal.items() if name != "kmo_xtwin_e1pe18_plus"}
    _expect(
        check.gate_sequence_failures(missing) == ["kmo_xtwin_e1pe18_plus: missing from the compiled plan"],
        "a missing xtwin member was not named",
    )


def test_tile_guard_rejects_a_region_off_the_template() -> None:
    check = _check_module()
    run = ROOT / "results" / "live" / "2026-11-28T041415.297826Z"
    record = json.loads((run / "record.json").read_text())
    message = "a placed region does not carry the tile template on device couplers"
    _expect(
        message not in check.failures(record, check.MIN_REGIONS, check.CEILING_SECONDS),
        "the retained pinned record carries the template on every region",
    )
    broken = copy.deepcopy(record)
    group = next(g for g in broken["groups"] if g["group"] == check.GROUP)
    group["tile_template"]["assignments"][3]["template_on_couplers"] = False
    _expect(
        message in check.failures(broken, check.MIN_REGIONS, check.CEILING_SECONDS),
        "a region off the template passes the admission check",
    )
