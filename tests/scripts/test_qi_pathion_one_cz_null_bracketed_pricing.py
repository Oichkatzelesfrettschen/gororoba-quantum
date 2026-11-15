"""Contracts of the replicate and shot pricing of the bracketed twin layout.

The layout figures are the rows of the CASE.md table ("Designs rejected") copied by hand, the simulation is checked
against the shared rule `decide_estimates` at the previous layout, and the audit-marked test regenerates a stored cell
of docs/evidence/qi-bracketed-pricing/cells.jsonl from its value of the retained QRNG draw.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import qi_pathion_one_cz_null_bracketed_pricing as pricing

import qrng_seeds

ROOT = Path(__file__).resolve().parents[2]
CELLS = ROOT / "docs/evidence/qi-bracketed-pricing/cells.jsonl"
DRAW = "docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json"
# (base replicates, twin replicates, shot factor): batches, waves, jobs, shots, execution seconds low and high,
# from the table.
TABLE = {
    (2, 2, 1.0): (19, 7, 64, 2_555_904, 1_521, 1_676),
    (2, 3, 1.0): (23, 8, 80, 3_080_192, 1_841, 2_027),
    (3, 2, 1.0): (23, 8, 76, 3_244_032, 1_917, 2_113),
    (3, 3, 1.0): (27, 9, 92, 3_768_320, 2_236, 2_465),
    (2, 4, 1.0): (27, 9, 96, 3_604_480, 2_160, 2_378),
    (2, 2, 2.0): (19, 7, 64, 4_980_736, 2_806, 3_108),
    (3, 3, 0.5): (27, 9, 92, 1_949_696, 1_273, 1_391),
    (4, 4, 0.5): (35, 12, 120, 2_555_904, 1_667, 1_821),
}


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.mark.parametrize("option", list(TABLE))
def test_the_layout_of_each_option_is_its_row_of_the_case_table(option: tuple[int, int, float]) -> None:
    batches, waves, jobs, shots, low, high = TABLE[option]
    seen = pricing.layout(*option)
    _expect((seen["batches"], seen["waves"], seen["jobs"], seen["shots"]) == (batches, waves, jobs, shots), f"{seen}")
    _expect(
        abs(seen["sec_low"] - low) < 1 and abs(seen["sec_high"] - high) < 1, f"{seen['sec_low']} {seen['sec_high']}"
    )


def test_the_pricing_decision_agrees_with_the_shared_rule_at_the_previous_layout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    _, counts = pricing.simulate(qrng_seeds.resolve(f"qrng:{DRAW}#911")[0], 2, 2, 1.0, 200, reference=True)
    for world in pricing.WORLD_NAMES:
        for model in pricing.DRIFT_MODELS:
            labels = {k: v for k, v in counts[world][f"{model}/dof"].items() if not k.startswith("trip:")}
            shared = counts[world][f"{model}/ref"]
            _expect(labels == shared, f"{world} {model}: {labels} against the shared rule {shared}")


def test_one_draw_value_gives_one_result_and_another_gives_another(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    first = pricing.simulate(7, 2, 2, 0.5, 60)
    _expect(first == pricing.simulate(7, 2, 2, 0.5, 60), "the same seed gave two results")
    _expect(first[1] != pricing.simulate(8, 2, 2, 0.5, 60)[1], "two seeds gave the same counts")


def test_a_bare_integer_seed_is_refused() -> None:
    with pytest.raises(SystemExit):
        pricing.main(["--seed", "12345", "--base-replicates", "2", "--twin-replicates", "2", "--shot-factor", "1"])


def _cells() -> list[dict[str, Any]]:
    return [json.loads(line) for line in CELLS.read_text(encoding="utf-8").splitlines()]


def test_the_retained_cells_take_values_911_to_919_of_the_draw_once_each_in_index_order() -> None:
    sources = [cell["seed_source"]["sources"][0] for cell in _cells()]
    _expect(sources == [f"qrng:{DRAW}#{index}" for index in range(911, 920)], f"{sources}")
    for cell in _cells():
        _expect(cell["draws"] == 20000, f"{cell['rb']}/{cell['rt']}: {cell['draws']} draws")


@pytest.mark.audit
def test_a_stored_cell_regenerates_from_its_draw_value() -> None:
    cell = next(c for c in _cells() if (c["rb"], c["rt"], c["f"]) == (2, 2, 0.5))
    seed = qrng_seeds.resolve(cell["seed_source"]["sources"][0])[0]
    layout, counts = pricing.simulate(seed, cell["rb"], cell["rt"], cell["f"], cell["draws"])
    _expect(layout == cell["layout"] and counts == cell["counts"], "the regenerated cell differs from the stored one")


# Power in percent, dropout / superposition-only, under the independent and the common-pair drift, from the table.
POWER = {
    (2, 2, 1.0): ("72.2 / 76.9", "82.0 / 86.7"),
    (2, 3, 1.0): ("71.9 / 79.5", "82.8 / 89.7"),
    (3, 2, 1.0): ("71.0 / 78.5", "80.2 / 87.3"),
    (3, 3, 1.0): ("69.9 / 80.1", "80.0 / 89.7"),
    (2, 4, 1.0): ("71.1 / 80.2", "82.9 / 91.1"),
    (2, 2, 2.0): ("51.3 / 65.0", "68.9 / 83.9"),
    (3, 3, 0.5): ("81.6 / 77.3", "86.7 / 81.9"),
    (4, 4, 0.5): ("82.1 / 85.3", "86.9 / 90.0"),
}


def test_the_case_table_is_the_power_of_the_retained_cells() -> None:
    target = {"coin_dropout": "b0_like", "superposition_only": "superposition_only"}
    for cell in _cells():
        option = (cell["rb"], cell["rt"], cell["f"])
        if option not in POWER:
            continue
        seen = tuple(
            " / ".join(
                f"{100 * cell['counts'][w][f'{model}/dof'].get(label, 0) / cell['draws']:.1f}"
                for w, label in target.items()
            )
            for model in pricing.DRIFT_MODELS
        )
        _expect(seen == POWER[option], f"{option}: table {POWER[option]}, cells {seen}")
