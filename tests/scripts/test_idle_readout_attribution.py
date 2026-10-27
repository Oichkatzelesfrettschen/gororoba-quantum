"""Planted-law mutation tests of the readout attribution analyzer on the pinned Kingston geometry."""

from __future__ import annotations

import dataclasses
import itertools
from typing import Any

import idle_readout_attribution as ra
import numpy as np
import pytest

import idle_penalty as ip

DT = 4e-9
SHOTS = 4096
# docs/evidence/anu_qrng/draw-2026-10-27T034547Z.json index 0.
BOOTSTRAP_SEED = 16771
REPLICATES = 400


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.fixture(scope="module")
def geo() -> ra.Geometry:
    return ra.pinned_geometry()


def _planted() -> tuple[np.ndarray, np.ndarray, float]:
    k = np.arange(ra.PAIRS)
    a = np.stack([-1.0 - 0.05 * k, -0.5 - 0.02 * k], axis=1)
    c = np.stack([-2.0 + 0.03 * k, -1.0 + 0.01 * k], axis=1)
    a[3, 0] = -18.0  # past half the 25 kHz alias of the long window
    return a, c, -0.8


def _observed(geo: ra.Geometry, laws: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    identity = {name: idx[None, :] for name, idx in ra.strata_of(geo).items()}
    return ra.estimate(geo, ra.contrasts(laws, DT, SHOTS), identity)


def test_geometry_matches_the_design(geo: ra.Geometry) -> None:
    _expect(int(geo.isolated.sum()) == 20 and len(geo.isolated_pairs) == 15, "isolated probes moved")
    _expect(sorted(len(v) for v in ra.strata_of(geo).values()) == [7, 8, 16], "strata moved")


def test_improper_coloring_is_refused() -> None:
    paths = [(0, 1), (2, 3)] + [(10 * k, 10 * k + 1) for k in range(1, ra.PAIRS - 1)]
    couplers = [(0, 1), (1, 2), (2, 3)] + [(10 * k, 10 * k + 1) for k in range(1, ra.PAIRS - 1)]
    original = dict(ra.PARTITIONS)
    try:
        ra.PARTITIONS["p1"] = "AA" + original["p1"][2:]
        with pytest.raises(ValueError, match="conflicting pairs"):
            ra.geometry(paths, couplers)
    finally:
        ra.PARTITIONS.update(original)


def test_exact_laws_recover_every_planted_term(geo: ra.Geometry) -> None:
    a, c, b = _planted()
    est = _observed(geo, ra.synthetic_laws(geo, a, c, b, DT))
    near = np.where(geo.isolated, np.nan, c)
    _expect(abs(est["b"][0] - b) < 1e-9, f"b {est['b'][0]}")
    _expect(float(np.max(np.abs(est["a"][0] - a))) < 1e-9, "a not recovered (alias or estimator)")
    _expect(float(np.nanmax(np.abs(est["c"][0] - near))) < 1e-9, "c not recovered")
    _expect(bool(np.isnan(est["c"][0][geo.isolated]).all()), "c reported on isolated probes")
    _expect(float(np.max(np.abs(est["residual"][0]))) < 1e-9, "additive laws left a residual")


@pytest.mark.parametrize("term", ["a", "c", "b"])
def test_removing_a_planted_term_moves_its_estimate(geo: ra.Geometry, term: str) -> None:
    a, c, b = _planted()
    full = _observed(geo, ra.synthetic_laws(geo, a, c, b, DT))
    a0, c0, b0 = (
        (np.zeros_like(a) if term == "a" else a),
        (np.zeros_like(c) if term == "c" else c),
        (0.0 if term == "b" else b),
    )
    removed = _observed(geo, ra.synthetic_laws(geo, a0, c0, b0, DT))
    gap = np.nanmax(np.abs(np.atleast_1d(full[term][0]) - np.atleast_1d(removed[term][0])))
    _expect(gap > 0.5, f"removing {term} moved its estimate by {gap}")
    _expect(float(np.nanmax(np.abs(np.atleast_1d(removed[term][0])))) < 1e-9, f"removed {term} still estimated")


def test_swapped_class_labels_break_recovery(geo: ra.Geometry) -> None:
    a, c, b = _planted()
    swapped = dataclasses.replace(geo, classes={"p1": geo.classes["p2"], "p2": geo.classes["p1"]})
    laws = ra.synthetic_laws(swapped, a, c, b, DT)
    est = _observed(geo, laws)
    _expect(float(np.max(np.abs(est["a"][0] - a))) > 0.5, "the analyzer ignored the body labels")


def test_pattern_offset_breaks_class_agreement(geo: ra.Geometry) -> None:
    a, c, b = _planted()
    laws = ra.synthetic_laws(geo, a, c, b, DT, pattern_offset_khz={("p1", "a"): 3.0, ("p2", "a"): 3.0})
    out = ra.analyze(geo, laws, DT, SHOTS, BOOTSTRAP_SEED, REPLICATES)
    _expect(not out["b"]["class_agreement"], f"offset passed: {out['b']}")
    _expect(out["attribution"]["verdict"] == "unresolved", out["attribution"]["verdict"])


def test_non_additive_laws_withdraw_the_attribution(geo: ra.Geometry) -> None:
    a, c, b = _planted()
    out = ra.analyze(
        geo, ra.synthetic_laws(geo, a, c, b, DT, during_extra_khz=-2.0), DT, SHOTS, BOOTSTRAP_SEED, REPLICATES
    )
    _expect(out["additivity"]["verdict"] == "non-additive", str(out["additivity"]))
    _expect(out["attribution"]["verdict"] == "withdrawn" and out["withdrawn_labels"], str(out["attribution"]))


def test_attribution_outcomes(geo: ra.Geometry) -> None:
    zeros = np.zeros((ra.PAIRS, 2))
    own = ra.analyze(
        geo, ra.synthetic_laws(geo, zeros - 3.0, zeros - 0.1, -0.05, DT), DT, SHOTS, BOOTSTRAP_SEED, REPLICATES
    )
    _expect(own["attribution"]["verdict"] == "own_partner", str(own["attribution"]))
    opposed = ra.analyze(
        geo, ra.synthetic_laws(geo, zeros - 3.0, zeros + 2.0, -0.5, DT), DT, SHOTS, BOOTSTRAP_SEED, REPLICATES
    )
    _expect(opposed["attribution"]["verdict"] == "opposed", str(opposed["attribution"]))


def test_null_reads_no_effect(geo: ra.Geometry) -> None:
    zeros = np.zeros((ra.PAIRS, 2))
    out = ra.analyze(geo, ra.synthetic_laws(geo, zeros, zeros, 0.0, DT), DT, SHOTS, BOOTSTRAP_SEED, REPLICATES)
    _expect(out["b"]["interval"][0] <= 0 <= out["b"]["interval"][1], str(out["b"]))
    _expect(out["additivity"]["verdict"] == "additive", str(out["additivity"]))
    resolved = int(np.sum(out["labels"]["a"]["resolved"]))
    _expect(resolved <= 2, f"{resolved} a_p resolved under the null")
    _expect(out["attribution"]["verdict"] == "unresolved", str(out["attribution"]))


def test_batched_rows_equal_single_replicate_runs(geo: ra.Geometry) -> None:
    a, c, b = _planted()
    laws = ra.synthetic_laws(geo, a, c, b, DT)
    strata, resampled = ra.bootstrap_inputs(geo, laws, SHOTS, BOOTSTRAP_SEED, 3)
    batch = ra.estimate(geo, ra.contrasts(resampled, DT, SHOTS), strata)
    for row in range(3):
        one = ra.estimate(
            geo,
            ra.contrasts({k: v[row : row + 1] for k, v in resampled.items()}, DT, SHOTS),
            {k: v[row : row + 1] for k, v in strata.items()},
        )
        for key, value in one.items():
            _expect(
                np.array_equal(batch[key][row : row + 1], value, equal_nan=True),
                f"row {row} {key} differs from its batch",
            )


def test_class_strings_and_member_names_have_one_home() -> None:
    import idle_penalty as ip

    _expect(ra.PARTITIONS is ip.PARTITIONS and ra.PATTERNS is ip.PATTERNS, "the analyzer holds its own class strings")
    _expect(ra.half_member is ip.half_member, "the analyzer holds its own member names")
    group = ip.idle_readout_group()
    patterned = {m.name: m.replica_bodies for m in group.members if m.replica_bodies is not None}
    for partition, pattern, probe in itertools.product(ra.PARTITIONS, ra.PATTERNS, ra.ROLES):
        for short in (False, True):
            bodies = patterned[ra.half_member(probe, partition, pattern, "x", short)]
            reading = [
                b for b, cls in zip(bodies, ra.PARTITIONS[partition], strict=True) if cls == ra.PATTERNS[pattern]
            ]
            _expect(all("quiet" not in b for b in reading), "a reading class replica runs a quiet body")
            _expect(sum("quiet" not in b for b in bodies) == len(reading), "a quiet class replica reads")


def _line(start: int, window: int, reads: int, quiet_reader: bool = False) -> tuple[Any, Any]:
    """(probe, reader) instances of one replica: reset, a pulse, the idle, a pulse, the joint read; the reader's
    train sits late in the window as the ALAP schedule puts it."""
    probe = (("reset", 0, start), ("sx", start, start + 10), ("sx", start + 10 + window, start + 20 + window))
    final = ("measure", start + 20 + window, start + 565 + window)
    reader = [("reset", 0, start)]
    if not quiet_reader:
        first = start + 10 + window - reads * 609
        reader += [("measure", first + 609 * r, first + 609 * r + 545) for r in range(reads)]
    return probe + (final,), tuple(reader) + (final,)


def _timelines(starts: list[int], bodies: tuple[str, ...], quiet_reads: int = 0) -> dict[str, list[Any]]:
    name = "idle_meas_half_p1a_x"
    replicas = []
    for start, body in zip(starts, bodies, strict=True):
        quiet = "quiet" in body
        probe, reader = _line(start, ip.MEAS_DT, quiet_reads if quiet else ip.MEAS_COUNT, quiet and not quiet_reads)
        replicas.append((probe, reader))
    reference = [(_line(start, ip.MEAS_DT, 0, True)[0], _line(start, ip.MEAS_DT, 0, True)[1]) for start in starts]
    return {name: replicas, f"idle_ramsey_x_{ip.MEAS_DT}dt": reference}


BODIES = ("idle_meas_during_x", "idle_meas_quiet_x", "idle_meas_during_x")


def test_patterned_exposure_accepts_aligned_classes() -> None:
    timelines = _timelines([600, 600, 600], BODIES)
    reasons = ra.patterned_exposure(timelines, {"idle_meas_half_p1a_x": BODIES})
    _expect(reasons == [], str(reasons))


@pytest.mark.parametrize(
    ("starts", "quiet_reads", "fragment"),
    [
        ([600, 9000, 600], 0, "misses the trains"),
        ([600, 600, 600], 2, "quiet partner reads"),
    ],
)
def test_patterned_exposure_refuses(starts: list[int], quiet_reads: int, fragment: str) -> None:
    timelines = _timelines(starts, BODIES, quiet_reads)
    reasons = ra.patterned_exposure(timelines, {"idle_meas_half_p1a_x": BODIES})
    _expect(any(fragment in reason for reason in reasons), str(reasons))
