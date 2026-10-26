"""Contract of the Quandela record watch: the held file names every retained read of the held qpu:belenos state,
and the classifier separates held, changed and missing records."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import qd_record_watch as watch

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "results/quandela/watch/qpu-belenos-held.json"
READS = (
    "results/quandela/runs/2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02/platform-before/catalogue.json",
    "results/quandela/cases/teleportation_rehearsal/job-00/platform-read/catalogue.json",
    "results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00/platform-before/catalogue.json",
    "results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00/platform-after/catalogue.json",
)


def perfs_of(path: str) -> dict[str, object]:
    perfs: dict[str, object] = json.loads((ROOT / path).read_text(encoding="utf-8"))["processors"]["qpu:belenos"][
        "perfs"
    ]
    return perfs


@pytest.mark.parametrize("path", READS)
def test_held_digest_names_every_retained_read_of_the_held_state(path: str) -> None:
    held = json.loads(HELD.read_text(encoding="utf-8"))
    if watch.digest(perfs_of(path)) != held["perfs_sha256"]:
        raise AssertionError(f"{path} departs from the held state")
    if held["figures"] != {"HOM (%)": 83.8, "g2 (%)": 16.7, "Transmittance (%)": 0.05}:
        raise AssertionError(held["figures"])


def test_a_refreshing_read_departs_from_the_held_state() -> None:
    held = json.loads(HELD.read_text(encoding="utf-8"))
    anchor = (
        "results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/platform-after/"
        "catalogue.json"
    )
    record = {"status": "available", "perfs": perfs_of(anchor)}
    if watch.classify(record, held) != "changed":
        raise AssertionError("the 2026-10-24 read classifies as held")


def test_self_test_passes() -> None:
    if watch.self_test() != 0:
        raise AssertionError("the self-test failed")


def test_held_file_takes_the_catalogue_time_unless_an_earlier_read_is_named(tmp_path: Path) -> None:
    catalogue = ROOT / READS[-1]
    out = tmp_path / "held.json"
    watch.write_held(catalogue, "qpu:belenos", out)
    retrieved = json.loads(catalogue.read_text(encoding="utf-8"))["retrieved_utc"]
    if json.loads(out.read_text(encoding="utf-8"))["first_seen_utc"] != retrieved:
        raise AssertionError("the held file ignores the catalogue's retrieval time")
    watch.write_held(catalogue, "qpu:belenos", out, "2026-10-25T18:47:04+00:00")
    if json.loads(out.read_text(encoding="utf-8"))["first_seen_utc"] != "2026-10-25T18:47:04+00:00":
        raise AssertionError("the held file ignores --first-seen")


def test_model_at_matches_the_live_model_on_one_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    import qd_platform
    import qd_teleportation_rehearsal as rehearsal

    perfs = perfs_of(READS[-1])
    monkeypatch.setattr(qd_platform, "get", lambda route, auth=True: {"perfs": perfs})
    if rehearsal.live_model() != rehearsal.model_at(perfs):
        raise AssertionError("live_model and model_at differ on the same perfs object")
