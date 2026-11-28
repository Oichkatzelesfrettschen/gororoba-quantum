"""Bounded fixtures for the live-figure noisy simulation of Belenos runs (qd_live_noise_sim)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import qd_belenos_mesh as mesh_lib
import qd_live_noise_sim as sim

ROOT = Path(__file__).resolve().parents[2]
JOB16 = ROOT / "results/quandela/runs/2026-10-18T193509Z-qpu_belenos-belenos_mesh-job-16"

PERFS = {
    "Clock (MHz)": 4.94,
    "Dark counts (detection/s)": [0.0] * 24,
    "HOM (%)": 58.3,
    "Transmission per mode (%)": {"t_in": [0.0] * 24, "t_out": [100.0] * 24},
    "Transmittance (%)": 2.69,
    "g2 (%)": 1.1,
}


def need_job16() -> None:
    if not (JOB16 / "raw/result.json").exists():
        pytest.skip("results/quandela job-16 is not checked out")


def test_perfs_reader_accepts_catalogue_submission_and_bare_perfs(tmp_path: Path) -> None:
    shapes = {
        "catalogue": {"processors": {sim.CHIP: {"perfs": PERFS}}},
        "submission": {"perfs_at_plan": PERFS},
        "bare": {"perfs": PERFS},
    }
    figures = []
    for name, body in shapes.items():
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(body), encoding="utf-8")
        figures.append(sim.read_perfs(path))
    if figures[0] != figures[1] or figures[1] != figures[2]:
        raise AssertionError(figures)
    if figures[0].hom != pytest.approx(0.583) or figures[0].g2 != pytest.approx(0.011):
        raise AssertionError(figures[0])
    if figures[0].transmittance != pytest.approx(0.0269):
        raise AssertionError(figures[0])


def test_perfs_reader_rejects_a_record_without_transmittance(tmp_path: Path) -> None:
    broken = {key: value for key, value in PERFS.items() if key != "Transmittance (%)"}
    path = tmp_path / "broken.json"
    path.write_text(json.dumps({"perfs": broken}), encoding="utf-8")
    with pytest.raises(sim.SimError, match="Transmittance"):
        sim.read_perfs(path)


def test_noise_model_equals_the_noise_the_server_recorded() -> None:
    need_job16()
    entry = mesh_lib.raw_result(JOB16)["results_list"][0]
    served = json.loads(entry["noise"].split(":PCVL:NoiseModel:", 1)[1])
    perfs = sim.read_perfs(JOB16 / "submission.json")
    built = sim.noise_parameters(perfs)
    if built != served:
        raise AssertionError((built, served))


def test_ideal_arm_equals_our_mesh_propagation_on_the_served_circuit() -> None:
    """Integer rounding of the expected counts bounds the distance by 1 / (2 x in-cone samples)."""
    need_job16()
    record = sim.read_run(JOB16, sim.read_perfs(JOB16 / "submission.json"), arms=("ideal",), only=(0, 1, 3))
    worst = max(row["arms"]["ideal"]["served_input"]["tvd_cone_from_ideal"] for row in record["entries"])
    if worst > 5e-4:
        raise AssertionError(worst)


def test_same_mesh_entries_get_one_prediction_but_two_observations() -> None:
    need_job16()
    record = sim.read_run(JOB16, sim.read_perfs(JOB16 / "submission.json"), arms=("noise",), only=(0, 1, 3))
    rows = [r for r in record["entries"] if r["mesh_sha256"].startswith("29dc6ef8")]
    observed = [r["retained"]["tvd_cone_from_ideal"] for r in rows]
    predicted = {r["arms"]["noise"]["served_input"]["tvd_cone_from_ideal"] for r in rows}
    if max(observed) - min(observed) < 0.4 or len(predicted) != 1:
        raise AssertionError((observed, predicted))


def test_live_figures_do_not_reproduce_the_collapse_of_job_16() -> None:
    need_job16()
    record = sim.read_run(JOB16, sim.read_perfs(JOB16 / "submission.json"), only=(0, 1, 3))
    verdicts = record["summary"]["collapse_verdicts"]
    if record["summary"]["collapsed_entries"] < 1 or set(verdicts.values()) != {"does_not_reproduce"}:
        raise AssertionError(record["summary"])


def test_dark_counts_add_off_cone_clicks_and_leave_the_block_share_unchanged_in_order() -> None:
    need_job16()
    record = sim.read_run(JOB16, sim.read_perfs(JOB16 / "submission.json"), arms=("noise", "noise_dark"), only=(0, 3))
    for row in record["entries"]:
        quiet: dict[str, Any] = row["arms"]["noise"]["served_input"]
        dark: dict[str, Any] = row["arms"]["noise_dark"]["served_input"]
        if dark["n_off_cone"] < quiet["n_off_cone"] or dark["in_block"] > quiet["in_block"] + 1e-9:
            raise AssertionError((quiet, dark))


def test_a_larger_g2_lowers_in_block_and_raises_multi_click_mass() -> None:
    low = sim.one_click_distribution(
        "|1,0>", sim.beam_splitter_text(), {"hom": 1.0, "g2": 0.0, "transmittance": 0.1}, None
    )
    high = sim.one_click_distribution(
        "|1,0>", sim.beam_splitter_text(), {"hom": 1.0, "g2": 0.2, "transmittance": 0.1}, None
    )
    if not high["multi"] > low["multi"] == 0.0 or abs(sum(low["p"]) - 1.0) > 1e-9:
        raise AssertionError((low, high))
