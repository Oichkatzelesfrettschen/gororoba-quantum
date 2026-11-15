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
    (2, 2, 0.5): (19, 7, 64, 1_343_488, 878, 960),
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


def test_the_pricing_indices_never_meet_the_operating_characteristic_indices_of_the_case() -> None:
    # The draw belongs to the case manifest, so the seed ledger takes no row for 911 to 919; this check keeps them
    # apart from the case's own values 920 to 922.
    import qi_pathion_one_cz_null_bracketed_cases as bracketed

    used = [int(c["seed_source"]["sources"][0].rpartition("#")[2]) for c in _cells()]
    _expect(len(set(used)) == len(used), f"a draw value serves two cells: {used}")
    _expect(not set(used) & set(bracketed.OC_SEED_INDICES.values()), f"{used} meet {bracketed.OC_SEED_INDICES}")
    _expect(all(c["seed_source"]["sources"][0].startswith(f"qrng:{bracketed.OC_DRAW}#") for c in _cells()), "draw")


def test_a_replicated_kind_keeps_its_own_gate_when_the_other_has_one_replicate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    seen: list[tuple[float, float]] = []
    real = pricing.decide

    def recording(rows: Any, base_gate: float, twin_gate: float) -> Any:
        seen.append((base_gate, twin_gate))
        return real(rows, base_gate, twin_gate)

    monkeypatch.setattr(pricing, "decide", recording)
    pricing.simulate(7, 1, 3, 0.5, 2)
    _expect(bool(seen) and all(base == 1e300 and twin < 1e300 for base, twin in seen), f"gates {seen[:2]}")
    seen.clear()
    pricing.simulate(7, 3, 1, 0.5, 2)
    _expect(bool(seen) and all(base < 1e300 and twin == 1e300 for base, twin in seen), f"gates {seen[:2]}")


def test_the_plan_names_the_nine_retained_cells_in_index_order_and_write_refuses_to_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    kept = [(c["rb"], c["rt"], c["f"]) for c in _cells()]
    _expect([entry[:3] for entry in pricing.CELL_PLAN] == kept, f"the plan {pricing.CELL_PLAN} differs from {kept}")
    _expect(pricing.CELL_DRAW == DRAW and pricing.CELL_FIRST_INDEX == 911, "the plan names another draw or first index")
    monkeypatch.setattr(pricing, "cell_lines", lambda: ['{"stub": true}'])
    target = tmp_path / "cells.jsonl"
    _expect(pricing.main(["--write", str(target)]) == 0, "write failed")
    _expect(target.read_text(encoding="utf-8") == '{"stub": true}\n', "the written text differs")
    with pytest.raises(FileExistsError):
        pricing.main(["--write", str(target)])


def test_check_regenerates_every_row_and_names_a_changed_one(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    ref = next(c for c in _cells() if (c["rb"], c["rt"], c["f"]) == (2, 2, 0.5))
    seed = qrng_seeds.resolve(ref["seed_source"]["sources"][0])[0]
    layout, counts = pricing.simulate(seed, 2, 2, 0.5, 40)
    cell = {**ref, "draws": 40, "layout": layout, "counts": counts}
    good = tmp_path / "cells.jsonl"
    good.write_text(json.dumps(cell) + "\n", encoding="utf-8")
    _expect(pricing.replay(good) == [], "a regenerated row was reported as different")
    counts["coin_dropout"]["contrast/dof"]["b0_like"] = counts["coin_dropout"]["contrast/dof"].get("b0_like", 0) + 1
    bad = tmp_path / "bad.jsonl"
    bad.write_text(json.dumps({**cell, "counts": counts}) + "\n", encoding="utf-8")
    _expect(len(pricing.replay(bad)) == 1, "a changed count was not reported")
    _expect(pricing.main(["--check", str(bad)]) == 1 and pricing.main(["--check", str(good)]) == 0, "exit codes")


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
    (2, 2, 0.5): ("73.9 / 58.8", "80.4 / 62.1"),
    (3, 3, 0.5): ("81.6 / 77.3", "86.7 / 81.9"),
    (4, 4, 0.5): ("82.1 / 85.3", "86.9 / 90.0"),
}


def test_the_case_table_is_the_power_of_the_retained_cells() -> None:
    _expect(set(POWER) == {(c["rb"], c["rt"], c["f"]) for c in _cells()}, "the table and the cells name other options")
    target = {"coin_dropout": "b0_like", "superposition_only": "superposition_only"}
    for cell in _cells():
        option = (cell["rb"], cell["rt"], cell["f"])
        seen = tuple(
            " / ".join(
                f"{100 * cell['counts'][w][f'{model}/dof'].get(label, 0) / cell['draws']:.1f}"
                for w, label in target.items()
            )
            for model in pricing.DRIFT_MODELS
        )
        _expect(seen == POWER[option], f"{option}: table {POWER[option]}, cells {seen}")
