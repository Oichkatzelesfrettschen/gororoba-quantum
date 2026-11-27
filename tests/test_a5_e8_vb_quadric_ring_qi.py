"""The check of the E8-bar -> VB quadric-ring record over Q(i), on a fixture built from the module's expected values.

The retained record replays on demand through the gate core-a5-e8-vb-quadric-ring-qi of ci/gates.json.
"""

import copy
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "docs/evidence/a5-kernel-attachments/e8_vb_quadric_ring_qi.py"


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("a5_e8_vb_quadric_ring_qi", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fixture(mod: ModuleType) -> dict[str, Any]:
    reductions = [{"prime": 32029, "root": 9115, "echelon_equal": True}]
    binding = {"relations": 21, "relations_sha256": "0" * 64, "reductions": reductions}
    return {"cell": copy.deepcopy(mod.EXPECTED), "binding": binding}


def test_the_fixture_passes() -> None:
    mod = load()
    if mod.problems(fixture(mod)):
        raise AssertionError(mod.problems(fixture(mod)))


MUTATIONS = {
    "a section longer than the degree": lambda r: r["cell"].update(length=8, cohen_macaulay=False),
    "a ring that is not reduced": lambda r: r["cell"].update(reduced=False),
    "another degree": lambda r: r["cell"].update(degree=8),
    "relations that do not reduce onto the retained K2": lambda r: r["binding"]["reductions"][0].update(
        echelon_equal=False
    ),
    "a missing reduction": lambda r: r["binding"].update(reductions=[]),
    "twenty relations": lambda r: r["binding"].update(relations=20),
    "a missing cell": lambda r: r.pop("cell"),
}


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_a_changed_record_is_reported(name: str) -> None:
    mod = load()
    record = fixture(mod)
    MUTATIONS[name](record)
    if not mod.problems(record):
        raise AssertionError(f"{name}: the changed record passes")
