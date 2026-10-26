"""The measurement-sequence scatter floor: qubit rule, per-qubit residual, floor rule and the floor document."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pytest

import diagnostic_experiments as de
import measurement_sequence_analysis as msa
import measurement_sequence_scatter as scatter


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


def chain(n: int) -> dict[str, Any]:
    """A path graph of n qubits where qubit k has readout error 0.001 * (n - k), so later qubits rank first."""
    qubits = {
        q: {"readout_error": 0.001 * (n - q) + 0.001, "sx_error": 2e-4, "t1_s": 2e-4, "t2_s": 1e-4} for q in range(n)
    }
    return {"qubits": qubits, "edges": [[q, q + 1] for q in range(n - 1)], "excluded": []}


def test_self_test_passes() -> None:
    check(scatter.self_test().startswith("measurement-sequence scatter"))


def test_selection_rule_keeps_uncoupled_qubits_in_readout_order() -> None:
    calibration = chain(12)
    kept = scatter.select_extra_qubits(calibration, (), 4)
    check(kept == [11, 9, 7, 5], f"{kept}")
    check(scatter.layout_violations(kept, calibration["edges"], set()) == [])
    kept_main = scatter.select_extra_qubits(calibration, (9,), 3)
    check(kept_main == [11, 6, 4] or kept_main == [11, 7, 5] or 9 not in kept_main, f"{kept_main}")
    check(all(abs(q - 9) > 1 for q in kept_main), "a further qubit is coupled to a main qubit")


def test_selection_rule_applies_every_threshold() -> None:
    calibration = chain(10)
    rows = calibration["qubits"]
    rows[9]["readout_error"] = scatter.READOUT_ERROR_MAX * 1.01
    rows[7]["sx_error"] = scatter.SX_ERROR_MAX * 1.01
    rows[5]["t2_s"] = scatter.COHERENCE_MIN_S * 0.99
    rows[3]["t1_s"] = None
    calibration["excluded"] = [1]
    check(not any(scatter.eligible(rows[q]) for q in (9, 7, 5, 3)))
    kept = scatter.select_extra_qubits(calibration, (), 2)
    check(set(kept).isdisjoint({9, 7, 5, 3, 1}), f"{kept}")
    with pytest.raises(scatter.ScatterError):
        scatter.select_extra_qubits(calibration, (), 9)


def test_layout_violations_name_each_fault() -> None:
    faults = scatter.layout_violations([1, 2, 5, 5], [[1, 2]], {5})
    check(len(faults) == 3, f"{faults}")


def test_residual_of_a_planning_device_is_statistical() -> None:
    contexts = msa.fixture_contexts(msa.FIXTURE_QUBITS, floor=None)
    models = {q: msa.device_model(ctx) for q, ctx in contexts.items()}
    counts = msa.device_counts(models, contexts, msa.FIXTURE_SHOTS)
    rows = []
    for q, ctx in contexts.items():
        final = {k: tuple(v) for k, v in counts[q]["final"].items()}
        rows.append(scatter.diagnostic_row((q, final, ctx)))
    check(all(r["informative"] for r in rows))
    for row in rows:
        check(abs(row["residual"]) < 4 * row["se_statistical"] + 1e-3, f"{row}")
        check(row["se_sx_systematic"] > 0 and row["se_statistical"] > 0)
        check(math.isclose(row["ideal"], de.msq_delay_p0(), abs_tol=1e-15))


def test_unusable_readout_makes_no_floor_contribution() -> None:
    ctx = msa.fixture_contexts(msa.FIXTURE_QUBITS[:1], floor=None)[msa.FIXTURE_QUBITS[0]]
    half = (4096, 8192)
    counts = {name: half for name in [*msa.member_names("unitary", 16, 1), msa.ro0_name(1), msa.t1_names(1)[0]]}
    row = scatter.diagnostic_row((1, counts, ctx))
    check(not row["informative"] and "readout scale" in row["reason"])


def rows_with(residuals: dict[int, float], t2: dict[int, float] | None = None) -> list[dict[str, Any]]:
    return [
        {
            "qubit": q,
            "informative": True,
            "residual": r,
            "se_statistical": 0.002,
            "t2_s": (t2 or {}).get(q, 1e-4 + 1e-6 * q),
            "sx_error": 2e-4,
        }
        for q, r in residuals.items()
    ]


def test_floor_is_the_larger_of_all_and_main_root_mean_square() -> None:
    main = scatter.MSQD_MAIN_QUBITS
    extra = list(range(200, 230))
    residuals = {**dict.fromkeys(main, 0.03), **dict.fromkeys(extra, 0.005)}
    summary = scatter.floor_summary(rows_with(residuals))
    check(summary["rms_main"] > summary["rms_all"], f"{summary}")
    check(summary["floor"] == summary["rms_main"] and math.isclose(summary["floor"], 0.03))
    flat = scatter.floor_summary(rows_with({**dict.fromkeys(main, 0.005), **dict.fromkeys(extra, 0.02)}))
    check(flat["floor"] == flat["rms_all"] > flat["rms_main"])
    check(math.isclose(flat["rms_all_less_statistical_in_quadrature"], math.sqrt(flat["rms_all"] ** 2 - 0.002**2)))
    check(flat["informative"] == 38 and flat["informative_main"] == 8 and flat["informative_extra"] == 30)


def test_floor_withheld_below_the_minimum() -> None:
    summary = scatter.floor_summary(rows_with(dict.fromkeys(range(scatter.MIN_INFORMATIVE - 1), 0.01)))
    check(summary["floor"] is None and "fewer than" in summary["withheld"])
    uninformative = rows_with(dict.fromkeys(range(40), 0.01))
    for row in uninformative[:21]:
        row["informative"] = False
    check(scatter.floor_summary(uninformative)["floor"] is None)


def test_t2_pattern_reads_a_ordered_population() -> None:
    qubits = list(range(30))
    t2 = {q: 1e-4 + 1e-5 * q for q in qubits}
    ordered = scatter.t2_pattern(rows_with({q: (0.02 if q >= 15 else -0.02) for q in qubits}, t2))
    check(ordered["residual_vs_t2"]["rho"] > 0.8 and ordered["residual_vs_t2"]["p_two_sided"] < 1e-3)
    check(ordered["lowest_t2_tercile"]["negative"] == 10 and ordered["highest_t2_tercile"]["positive"] == 10)
    alternating = scatter.t2_pattern(rows_with({q: 0.02 * (-1) ** q for q in qubits}, t2))
    check(abs(alternating["residual_vs_t2"]["rho"]) < 0.2)
    check("withheld" in scatter.t2_pattern(rows_with({q: 0.01 for q in range(5)})))


def test_floor_document_binds_a_run(tmp_path: Path) -> None:
    run = tmp_path / "run"
    run.mkdir()
    qubits = [*de.MSQD_MAIN_QUBITS, *range(200, 230)]
    configuration = {
        "name": de.MSQD_FAMILY,
        "qubits": qubits,
        "main_qubits": list(de.MSQD_MAIN_QUBITS),
        "extra_qubits": qubits[8:],
    }
    record = {
        "family_configuration": configuration,
        "groups": [{"backend": "ibm_kingston"}],
        "experiment_digest": "d" * 64,
    }
    rows = rows_with({q: 0.01 * (-1) ** q for q in qubits})
    scatter_analysis = {
        "schema": scatter.SCHEMA,
        "qubits": {str(r["qubit"]): r for r in rows},
        "floor": scatter.floor_summary(rows),
        "t2_pattern": scatter.t2_pattern(rows),
    }
    (run / "record.json").write_text(json.dumps(record), encoding="utf-8")
    (run / "collect.json").write_text(json.dumps({"family_analysis": {"scatter": scatter_analysis}}), encoding="utf-8")
    document = scatter.floor_document(run)
    check(document["schema"] == msa.SCATTER_FLOOR_SCHEMA and isinstance(document["floor"], float))
    check(math.isclose(document["floor"], 0.01) and document["backend"] == "ibm_kingston")
    check(document["main_qubits"] == list(de.MSQD_MAIN_QUBITS) and len(document["extra_qubits"]) == 30)
    check(len(document["source"]["record_sha256"]) == 64 and document["source"]["experiment_digest"] == "d" * 64)
    configuration["main_qubits"] = [91]
    (run / "record.json").write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(scatter.ScatterError):
        scatter.floor_document(run)


def test_diagnostic_family_contract_and_group_dispatch() -> None:
    configuration = {
        "name": de.MSQD_FAMILY,
        "qubits": [91, 118],
        "prereadout_delay_dt": {"91": 500, "118": 500},
    }
    contracts = de.family_contracts(de.MSQD_FAMILY, 0.08, 0.05, 0.8, configuration)
    check(len(contracts) == 4, f"{len(contracts)}")
    check(de.MSQD_FAMILY in de.FAMILY_NAMES)
    groups = de.record_groups({"family_configuration": configuration})
    check([g.name for g in groups] == ["msqd_static_q91", "msqd_static_q118"])
    check(all(len(g.members) == de.MSQD_MEMBERS_PER_QUBIT for g in groups))
    with pytest.raises(ValueError, match="named qubits"):
        de.family_contracts(de.MSQD_FAMILY, 0.08, 0.05, 0.8, None)
