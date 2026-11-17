"""Contracts of the twin simulation log of the Tuna-17 one-CZ null series for every low-CZ template.

c2_one_cz_twins.txt lists b0 and the three 6-CZ blocks k4, k8 and k12 in section 1 (the twins) and in section 2 (the
sized mechanisms). Each template of `oc.LOW_NAMES` is read against the predicted contrasts the case preregisters,
so a log that moves one block while the others keep their cells fails here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import qi_pathion_one_cz_null_cases as oc

ROOT = Path(__file__).resolve().parents[2]
TWIN_LOG = ROOT / "docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_twins.txt"
MECHANISMS = {
    "over_rotation": "X-axis error",
    "coin_dropout": "selector dropout",
    "q12_correlation": "selector flip",
}
# The log rounds each contrast to four decimals; the predicted 6-CZ contrasts are the rounded k4 cells.
TOLERANCE = 4e-4
CELL = r"([+-]\d\.\d+) / ([+-]\d\.\d+)"


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _section2() -> dict[str, dict[str, tuple[float, float]]]:
    table: dict[str, dict[str, tuple[float, float]]] = {}
    for line in TWIN_LOG.read_text(encoding="utf-8").splitlines():
        match = re.match(rf"^  (\S.*?)\s{{2,}}((?:{CELL}\s*){{4}})$", line)
        if match:
            cells = re.findall(CELL, match.group(2))
            table[match.group(1)] = dict(zip(oc.TEMPLATES, ((float(a), float(b)) for a, b in cells), strict=True))
    return table


def _row(prefix: str) -> dict[str, tuple[float, float]]:
    return next(cells for label, cells in _section2().items() if label.startswith(prefix))


@pytest.mark.parametrize("name", oc.LOW_NAMES)
@pytest.mark.parametrize("key", list(MECHANISMS))
def test_each_low_cz_template_reads_the_predicted_contrasts_of_each_mechanism(key: str, name: str) -> None:
    want = oc.PREDICTED[key]
    s, t = _row(MECHANISMS[key])[name]
    _expect(abs(s - want["s_k"]) < TOLERANCE, f"{key} {name}: base {s} against {want['s_k']}")
    _expect(abs(t - want["t_k"]) < TOLERANCE, f"{key} {name}: twin {t} against {want['t_k']}")


def test_the_log_states_that_k8_and_k12_equal_k4_and_every_row_does() -> None:
    _expect("k8 and k12 equal k4 to four decimals" in TWIN_LOG.read_text(encoding="utf-8"), "the log's statement")
    table = _section2()
    _expect(len(table) >= 9, f"{len(table)} mechanism rows read")
    for label, cells in table.items():
        for name in oc.LOW_NAMES[1:]:
            _expect(cells[name] == cells[oc.LOW_NAMES[0]], f"{label}: {name} {cells[name]} against {cells['k4']}")


@pytest.mark.parametrize("name", oc.TEMPLATES)
def test_each_template_twin_pair_keeps_the_template_cz_count_and_a_fair_selector(name: str) -> None:
    text = TWIN_LOG.read_text(encoding="utf-8")
    cz = json.loads(
        (ROOT / "results/quantum_inspire/cases" / oc.TUNA_SERIES / "batch-00/cases.json").read_text(encoding="utf-8")
    )["templates"][name]["cz"]
    for coin in (0, 1):
        match = re.search(
            rf"  {name} coin {coin}: removed .*, CZ (\d+) \(template (\d+)\), ideal coin read {coin}\.000, "
            r"ideal P\(s=0\) 0\.5000",
            text,
        )
        if match is None:
            raise AssertionError(f"{name} coin {coin} has no section 1 row")
        _expect(int(match.group(1)) == int(match.group(2)) == cz, f"{name} coin {coin}: CZ {match.groups()} not {cz}")
