"""The ensemble case's settings, schedule, scores, tests and binding on bounded fixtures."""

from __future__ import annotations

import copy
from typing import Any

import ascella_cz_ensemble_case as case
import ascella_cz_tomography_case as tomo
import numpy as np
import pytest


def generators(count: int) -> list[np.random.Generator]:
    """Independent generators from the case's QRNG fixture value (seed_plan()["fixture"], draw index in SEED_RULE)."""
    _, value = case.seed_plan()["fixture"]
    return [np.random.default_rng(child) for child in np.random.SeedSequence(value).spawn(count)]


def test_every_setting_has_one_correct_outcome_and_matches_its_permanents() -> None:
    for row in case.base_settings():
        outcome = case.correct_outcome(row)
        conditional, accepted = case.exact_outcomes(row)
        if abs(conditional[outcome] - 1.0) > 1e-9 or abs(accepted - 1.0 / 9.0) > 1e-9:
            raise AssertionError(f"{row['name']}: the Ralph CZ misses the ideal outcome {outcome} or 1/9 success")


def test_hofmann_scores_of_the_design_counterexample() -> None:
    """The design's Kraus operator (CZ / 3) diag(1, 0.1, 0.1, 0.1): F' = 0.7995 on both tables violates the bound
    around its process fidelity 0.410, while the rate-weighted scores give [0.214, 0.607]."""
    kraus = tomo.ideal_cz() @ np.diag([1.0, 0.1, 0.1, 0.1]) / 3
    scores = case.map_scores(kraus)
    lower = scores["F_ZX"] + scores["F_XZ"] - 1
    upper = min(scores["F_ZX"], scores["F_XZ"])
    for name, value, expected in (
        ("F'_ZX", scores["F_prime_ZX"], 0.7995),
        ("F'_XZ", scores["F_prime_XZ"], 0.7995),
        ("process fidelity", scores["process_fidelity"], 0.410),
        ("lower", lower, 0.214),
        ("upper", upper, 0.607),
    ):
        if abs(value - expected) > 5e-4:
            raise AssertionError(f"{name} reads {value}, the design states {expected}")
    if not lower <= scores["process_fidelity"] <= upper or scores["F_prime_ZX"] + scores["F_prime_XZ"] - 1 <= 0.410:
        raise AssertionError("the rate-weighted interval misses the fidelity or the per-input bound holds")
    ideal = case.map_scores(tomo.ideal_cz())
    if any(abs(value - 1.0) > 1e-12 for value in ideal.values()):
        raise AssertionError(f"the ideal CZ scores {ideal}")


@pytest.mark.parametrize("job", case.JOBS)
def test_schedule_holds_anchor_positions_balance_and_seed_identity(job: str) -> None:
    case.check_schedule(job)
    rows = case.job_schedule(job)
    other = case.job_schedule(case.JOBS[1 - case.JOBS.index(job)])
    anchors = {(r["setting"], r["compilation_seed"]) for r in rows if r["role"] == "anchor"}
    if anchors != {(r["setting"], r["compilation_seed"]) for r in other if r["role"] == "anchor"} or len(anchors) != 4:
        raise AssertionError("the anchors do not request one seed each, the same in both jobs")
    seeds = {r["compilation_seed"] for r in rows if r["role"] == "ensemble"}
    if seeds & {r["compilation_seed"] for r in other if r["role"] == "ensemble"}:
        raise AssertionError("an ensemble seed serves both jobs")


def test_homogeneity_separates_one_law_from_two() -> None:
    generator = generators(1)[0]
    same = np.asarray([[900, 30, 40, 30]] * 5)
    split = np.asarray([[900, 30, 40, 30]] * 4 + [[700, 230, 40, 30]])
    held = case.homogeneity(same, generator, tables=2000)
    moved = case.homogeneity(split, generator, tables=2000)
    if held["p"] < 0.5 or moved["p"] != 1 / 2001:
        raise AssertionError(f"homogeneity reads p {held['p']} for one law and {moved['p']} for two")
    sparse = case.homogeneity(np.asarray([[500, 0, 3, 0], [480, 0, 5, 0]]), generator, tables=2000)
    if sparse["rows"] != 2 or not 0 < sparse["p"] <= 1:
        raise AssertionError("an empty outcome column breaks the test")


def tally(row: dict[str, Any], eligible: list[int], shots: int = 200000, digest: str = "mesh") -> dict[str, Any]:
    return {
        "setting": row["setting"],
        "role": row["role"],
        "seed_index": row.get("seed_index"),
        "correct_outcome": case.correct_outcome(row),
        "eligible": eligible,
        "shots": shots,
        "digest": f"{digest}-{row['setting']}",
    }


def synthetic_runs(ensemble_law: dict[str, list[int]] | None = None) -> dict[str, list[dict[str, Any]]]:
    """Both jobs at one law per setting; `ensemble_law` replaces the ensemble iterations' counts of named settings."""
    runs = {}
    for job in case.JOBS:
        rows = []
        for row in case.job_schedule(job):
            counts = [0, 0, 0, 0]
            counts[case.correct_outcome(row)] = 1800
            counts[(case.correct_outcome(row) + 1) % 4] = 200
            if ensemble_law and row["role"] == "ensemble" and row["setting"] in ensemble_law:
                counts = ensemble_law[row["setting"]]
            rows.append(tally(row, counts))
        runs[job] = rows
    return runs


def test_drift_reads_only_the_anchor_repeats(monkeypatch: pytest.MonkeyPatch) -> None:
    """An anchor setting's ensemble iterations, served by other meshes, never enter its drift tests."""
    monkeypatch.setattr(case, "MC_TABLES", 2000)
    streams = generators(case.DRIFT_TESTS)
    moved = synthetic_runs({name: [1000, 1000, 0, 0] for name in case.ANCHORS})
    result = case.drift(moved, streams)
    if not result["pooled"] or not all(test["p"] > result["threshold"] for test in result["tests"]):
        raise AssertionError("ensemble iterations of an anchor setting entered its drift tests")
    rows = {len(case.ANCHOR_STARTS)} | {2}
    if {test.get("rows") for test in result["tests"] if "rows" in test} != rows:
        raise AssertionError("a drift table does not hold five positions or two jobs")


def test_drift_unpools_on_a_recalibrated_anchor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(case, "MC_TABLES", 2000)
    runs = synthetic_runs()
    for t in runs[case.JOBS[1]]:
        if t["role"] == "anchor" and t["setting"] == case.ANCHORS[0]:
            t["digest"] = "recompiled"
    result = case.drift(runs, generators(case.DRIFT_TESTS))
    if result["pooled"] or result["same_mesh_across_jobs"][case.ANCHORS[0]]:
        raise AssertionError("an anchor served by another mesh in job-01 still pools the jobs")


def test_scores_and_bound_follow_the_rate_weighting() -> None:
    runs = synthetic_runs()
    groups = case.ensemble_groups(runs)
    prediction = {table: {"F": 0.9, "F_sd": 0.0} for table in case.TABLES}
    scores = case.score_estimates(groups, True, prediction)["pooled"]
    for table in case.TABLES:
        f = scores["tables"][table]["F"]
        if abs(f["mean"] - 0.9) > 1e-12 or f["df"] != 9:
            raise AssertionError(f"{table}: F reads {f['mean']} on {f['df']} degrees of freedom")
        if scores["tables"][table]["difference_from_tomography"]["reading"] != "contains_zero":
            raise AssertionError(f"{table}: a zero difference does not read contains_zero")
    bound = scores["hofmann_interval"]
    if abs(bound["L"] - 0.8) > 1e-12 or abs(bound["U"] - 0.9) > 1e-12:
        raise AssertionError(f"a constant table bounds to {bound}")
    split = case.score_estimates(groups, False, prediction)
    if set(split) != set(case.JOBS) or "hofmann_interval" in split[case.JOBS[0]]:
        raise AssertionError("unpooled jobs report a pooled bound")


def manifest_entries(job: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    settings: list[dict[str, Any]] = []
    for row in case.job_schedule(job):
        settings.append(
            {**row, "correct_outcome": case.correct_outcome(row), "circuit_params": {"x0": float(len(settings))}}
        )
    for setting in settings:
        if setting["role"] == "anchor":
            first = next(s for s in settings if s["role"] == "anchor" and s["setting"] == setting["setting"])
            setting["circuit_params"] = first["circuit_params"]
    entries = [
        {
            "counts": {"1,0,1,0,0,0,0,0,0,0,0,0": 300, "1,0,0,0,0,0,0,0,0,0,0,0": 50},
            "iteration": {"compilation_seed": s["compilation_seed"], "circuit_params": s["circuit_params"]},
            "result_fields": {"nb_shots_used": 9000, "computed_circuit": f"mesh-{s['setting']}"},
        }
        for s in settings
    ]
    return settings, entries


def test_binding_takes_five_anchor_repeats_and_refuses_a_sixth() -> None:
    settings, entries = manifest_entries(case.JOBS[0])
    tallies, missing = case.bind_entries("run", settings, list(reversed(entries)))
    if missing or len(tallies) == 0 or len(tallies) != case.ITERATIONS:
        raise AssertionError(f"{len(tallies)} tallies and {missing} missing from a complete run")
    anchor = next(e for e, s in zip(entries, settings, strict=True) if s["role"] == "anchor")
    ensemble = next(i for i, s in enumerate(settings) if s["role"] == "ensemble")
    extra = [*entries[:ensemble], copy.deepcopy(anchor), *entries[ensemble + 1 :]]
    with pytest.raises(RuntimeError, match="unbound or spent"):
        case.bind_entries("run", settings, extra)
    changed = copy.deepcopy(entries)
    changed[ensemble]["iteration"]["circuit_params"] = {"x0": -1.0}
    with pytest.raises(RuntimeError, match="echoes other params"):
        case.bind_entries("run", settings, changed)
    partial = copy.deepcopy(entries)
    partial[ensemble]["counts"] = {}
    tallies, missing = case.bind_entries("run", settings, partial)
    if missing != 1 or len(tallies) != case.ITERATIONS - 1:
        raise AssertionError("an iteration without counts is not counted as missing")


def test_a_short_iteration_leaves_the_case_undecided() -> None:
    runs = synthetic_runs()
    runs[case.JOBS[0]][7]["eligible"] = [100, 50, 0, 0]
    loaded = [
        {
            "job": job,
            "cases_sha256": "0" * 64,
            "tallies": runs[job],
            "uncounted": 0,
            "perfs": None,
            "status": "completed",
        }
        for job in case.JOBS
    ]
    if case.summarize(loaded)["status"] != "undecided":
        raise AssertionError("an iteration below the eligible floor still decides the case")
    runs[case.JOBS[0]][7]["eligible"] = [1800, 200, 0, 0]
    loaded[1] = {**loaded[1], "status": "canceled"}
    if case.summarize(loaded)["status"] != "undecided":
        raise AssertionError("a canceled job still decides the case")


def test_a_missing_computed_circuit_unpools_the_jobs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(case, "MC_TABLES", 2000)
    runs = synthetic_runs()
    for job in case.JOBS:
        for t in runs[job]:
            if t["role"] == "anchor":
                t["digest"] = None
    result = case.drift(runs, generators(case.DRIFT_TESTS))
    if result["pooled"] or sorted(result["anchors_missing_computed_circuit"]) != sorted(case.ANCHORS):
        raise AssertionError("anchors without a computed_circuit still pool the jobs")
    settings, entries = manifest_entries(case.JOBS[0])
    for entry in entries:
        entry["result_fields"]["computed_circuit"] = "  "
    tallies, _ = case.bind_entries("run", settings, entries)
    if any(t["digest"] is not None for t in tallies):
        raise AssertionError("an empty computed_circuit becomes a mesh digest")


def test_run_status_reads_the_nested_status_field() -> None:
    collected = {"status": {"status": "completed", "duration": 188}, "results": []}
    if case.run_status(collected) != "completed":
        raise AssertionError("run_status misreads a completed job")
    if case.run_status({"status": {"status": "canceled"}}) != "canceled":
        raise AssertionError("run_status drops a terminal status other than completed")
    for shape in ({"status": "completed"}, {}, {"status": {"status": 3}}, {"status": None}):
        if case.run_status(shape) is not None:
            raise AssertionError(f"run_status accepts {shape}")


def test_conditional_tables_keep_both_margins() -> None:
    table = np.asarray([[900, 30, 0, 12], [880, 41, 3, 9], [910, 25, 1, 15]])
    drawn = case.conditional_tables(table, generators(1)[0], 500)
    if (drawn.sum(axis=2) != table.sum(axis=1)).any() or (drawn.sum(axis=1) != table.sum(axis=0)).any():
        raise AssertionError("a conditional table moves a row or column total")
    if (drawn < 0).any() or len({d.tobytes() for d in drawn}) < 100:
        raise AssertionError("the conditional tables are negative or barely vary")


def test_unpooled_jobs_test_mesh_variance_per_job(monkeypatch: pytest.MonkeyPatch) -> None:
    """A shift between the jobs, with five identical meshes in each, rejects nothing once the jobs are unpooled."""
    monkeypatch.setattr(case, "MC_TABLES", 2000)
    runs = synthetic_runs()
    for t in runs[case.JOBS[1]]:
        if t["role"] == "ensemble":
            t["eligible"] = [1500 if k == t["correct_outcome"] else 0 for k in range(4)]
            t["eligible"][(t["correct_outcome"] + 1) % 4] = 500
    groups = case.ensemble_groups(runs)
    streams = generators(2 * case.MESH_TESTS)
    pooled = case.mesh_variance(groups, streams, True)
    split = case.mesh_variance(groups, generators(2 * case.MESH_TESTS), False)
    if not pooled["rejects"] or split["rejects"] or len(split["settings"]) != 2 * case.MESH_TESTS:
        raise AssertionError("a between-job shift reads as mesh variance in the per-job test")


def test_estimate_5_widens_with_the_prediction_uncertainty() -> None:
    estimate = case.mean_interval([0.90, 0.91, 0.89, 0.90, 0.92, 0.88, 0.90, 0.91, 0.89, 0.90])
    exact = case.difference(estimate, 0.88, 0.0)
    noisy = case.difference(estimate, 0.88, 0.02)
    if exact["reading"] != "above_zero" or noisy["reading"] != "contains_zero":
        raise AssertionError(f"the prediction's uncertainty does not widen the difference: {exact}, {noisy}")


def test_certified_float_rounds_exactly_and_refuses_a_straddling_ball() -> None:
    from fractions import Fraction

    from flint import arb, ctx

    ctx.prec = 128
    if case.certified_float(arb(1) / 3) != 1 / 3:
        raise AssertionError("one third does not certify to the nearest float64")
    tie = arb(1) + arb(2) ** -53  # exactly halfway between 1 and its successor: ties go to even
    if case.exact_float(tie) != 1.0:
        raise AssertionError("an exact tie does not round to even")
    straddling = tie + (arb(2) ** -60) * arb("0 +/- 1")
    if case.certified_float(straddling) is not None:
        raise AssertionError("a ball across a rounding boundary certifies")
    values = [arb(v) for v in (0.5, 0.25, 0.75, 1.0, 0.125)]
    exact = Fraction(1, 8) + (Fraction(1, 4) - Fraction(1, 8)) * Fraction(0.1)
    if case.certified_float(case.percentile_ball(values, 2.5)) != float(exact):
        raise AssertionError("the percentile ball does not certify to numpy's linear interpolation, rounded")


def test_certified_prediction_recovers_a_synthetic_fit() -> None:
    """Rates generated by a known Choi coefficient vector come back certified and equal to the float64 computation."""
    coefficients = np.linspace(-1e-3, 2e-3, 256)
    shifts = np.outer(np.ones(256), [0.0, 1e-5, -2e-5, 3e-5])
    columns = tomo.design_matrix() @ (coefficients[:, None] + shifts)
    record, precision = case.certified_prediction(columns)
    choi = tomo.choi_of(coefficients)
    for name, rates in record["rates"].items():
        table, label = name[-2:], name[3:-3]  # "in-<control><target>-<table>"; a "-" state is part of the label
        density = case.input_density(label).T
        floats = [float(np.real(np.trace(np.kron(density, tomo.outcome_projector(table, o)) @ choi))) for o in range(4)]
        if precision != 128 or not np.allclose(rates, floats, rtol=0, atol=1e-15):
            raise AssertionError(f"{name}: certified {rates} against float64 {floats}")
    if not record["ZX"]["F_sd"] > 0.0:
        raise AssertionError("distinct replicates give no spread")


def test_order_statistic_orders_endpoints_exactly() -> None:
    """Endpoints that round to one float64 still sort by their exact values."""
    from flint import arb, ctx

    ctx.prec = 128
    above_one = arb(1) + arb(2) ** -54  # rounds to 1.0 like 1 itself
    smallest = case.order_statistic([above_one, arb(1)], 0)
    if not smallest.contains(arb(1)):
        raise AssertionError("the minimum ball excludes the exact minimum 1")
    tiny_negative = arb(-(2**-1100)) + arb("0 +/- 1e-340")  # a lower endpoint that rounds to -0.0
    if not (case.nonnegative_sqrt(tiny_negative.union(arb(4))) >= 0):
        raise AssertionError("a negative endpoint rounding to -0.0 escapes the nonnegative clamp")


def test_certified_prediction_raises_precision_then_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """A value that fails to certify moves the solve to the next precision, and failing at the last one raises."""
    seen: list[int] = []
    real = case.prediction_balls

    def failing(columns: np.ndarray, precision: int) -> dict[str, Any]:
        seen.append(precision)
        return real(columns, 128)

    calls = {"n": 0}

    def refuse_until(limit: int):
        def certify(value: Any) -> float | None:
            calls["n"] += 1
            return None if len(seen) <= limit else float(value.mid())

        return certify

    columns = (tomo.design_matrix() @ np.linspace(-1e-3, 2e-3, 256))[:, None] + np.asarray([[0.0, 1e-9, 2e-9]])
    monkeypatch.setattr(case, "prediction_balls", failing)
    monkeypatch.setattr(case, "certified_float", refuse_until(2))
    _, precision = case.certified_prediction(columns)
    if seen != [128, 256, 512] or precision != 512:
        raise AssertionError(f"the precision ladder ran {seen} and settled at {precision}")
    seen.clear()
    monkeypatch.setattr(case, "certified_float", refuse_until(3))
    with pytest.raises(RuntimeError, match="straddles"):
        case.certified_prediction(columns)
    if seen != [128, 256, 512]:
        raise AssertionError(f"the refusal ran {seen}")


def test_moved_inputs_reports_rather_than_fails() -> None:
    """A digest that moved is named and removed, so the tolerance comparison sees only the floats."""

    def record(design: str) -> dict[str, Any]:
        digests = {"design_matrix": design, "observed_rate_columns": "same"}
        return {"tomography_prediction": {"F": 0.5, "arithmetic": {"precision_bits": 128, "inputs_sha256": digests}}}

    retained, recomputed = record("a"), record("b")
    if case.moved_inputs(retained, recomputed) != ["design_matrix"]:
        raise AssertionError("a moved input is not named")
    if tomo.first_difference(retained, recomputed) is not None:
        raise AssertionError("the digests still reach the tolerance comparison")


def planned_fixture(job: str, hom: float, explorer: str = "available", jobs: int = 0) -> dict[str, Any]:
    """The fields of a qd_platform.plan record that the submission policy reads."""
    policy = case.submission_policy(job)
    return {
        "case": job,
        "platform": case.PLATFORM,
        "credit_ceiling": policy["credit_ceiling"],
        "per_job_credits": policy["per_job_credits"],
        "expected_seconds": float(policy["expected_seconds"]),
        "perfs_at_plan": {"HOM (%)": hom},
        "status_at_plan": {"explorer": explorer, "processor": "available"},
        "availability_at_plan": {"num_concurrent_jobs": jobs, "num_jobs_in_queue": 0},
    }


def decisive_run(job: str = "job-00", status: str = "completed", short: int = 0) -> dict[str, Any]:
    tallies = [{"eligible": [100, 100, 100, 100]} for _ in range(case.ITERATIONS)]
    for tally in tallies[:short]:
        tally["eligible"] = [50, 50, 50, 49]
    return {"job": job, "status": status, "tallies": tallies, "uncounted": 0}


def test_the_retained_reference_admits_no_hom() -> None:
    """The reference tomography ran at 87.56 %: no HOM is above 90 % and within one point of it."""
    lower, upper = case.hom_band(case.reference_hom())
    if lower < upper or case.submission_policy("job-00")["hom_percent"]["admitted"] != "none":
        raise AssertionError(f"the band ({lower}, {upper}] admits a HOM")
    with pytest.raises(case.qd_platform.PlatformError, match="outside"):
        case.admit("job-00", planned_fixture("job-00", 88.0), case.reference_hom(), None)


@pytest.mark.parametrize(("hom", "admitted"), [(90.0, False), (90.01, True), (91.5, True), (91.51, False)])
def test_hom_band_is_above_the_floor_and_within_a_point(hom: float, admitted: bool) -> None:
    planned = planned_fixture("job-00", hom)
    if admitted:
        case.admit("job-00", planned, 90.5, None)
    else:
        with pytest.raises(case.qd_platform.PlatformError, match="outside"):
            case.admit("job-00", planned, 90.5, None)


def test_running_admits_only_an_idle_token() -> None:
    case.admit("job-00", planned_fixture("job-00", 91.0, "running"), 90.5, None)
    with pytest.raises(case.qd_platform.PlatformError, match="holds jobs"):
        case.admit("job-00", planned_fixture("job-00", 91.0, "running", jobs=1), 90.5, None)
    with pytest.raises(case.qd_platform.PlatformError, match="status"):
        case.admit("job-00", planned_fixture("job-00", 91.0, "maintenance"), 90.5, None)


def test_a_plan_off_the_policy_is_refused() -> None:
    planned = planned_fixture("job-00", 91.0)
    planned["expected_seconds"] = 300.0
    with pytest.raises(case.qd_platform.PlatformError, match="expected_seconds"):
        case.admit("job-00", planned, 90.5, None)


@pytest.mark.parametrize(
    ("predecessor", "match"),
    [
        (None, "requires the collected"),
        (decisive_run(status="canceled"), "not completed"),
        (decisive_run(short=1), "eligible events"),
        (decisive_run(job="job-01"), "not job-00"),
    ],
)
def test_job_01_waits_for_a_decisive_job_00(predecessor: dict[str, Any] | None, match: str) -> None:
    with pytest.raises(case.qd_platform.PlatformError, match=match):
        case.admit("job-01", planned_fixture("job-01", 91.0), 90.5, predecessor)


def test_job_01_admits_after_a_decisive_job_00() -> None:
    case.admit("job-01", planned_fixture("job-01", 91.0), 90.5, decisive_run())


def test_generic_submit_refuses_a_wrapper_case_without_verify(monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    monkeypatch.setattr(case.qd_platform, "load_case", lambda _: ({"submit_wrapper": case.SUBMIT_WRAPPER}, {}, "x"))
    with pytest.raises(case.qd_platform.PlatformError, match="submits only through"):
        case.qd_platform.submit(Path("job-00"), case.PLATFORM, "approval", 1.4, 220, 1.0)


def test_submit_binds_the_admitted_preflight() -> None:
    from qd_schedule import body_digest

    planned = {"cases_sha256": "c", "body": {"process_id": "a", "payload": {"x": 1}}}
    reviewed = {
        "admission": {"admitted": True},
        "cases_sha256": "c",
        "body_sha256_without_process_id": body_digest({"process_id": "b", "payload": {"x": 1}}),
    }
    case.bind_reviewed("job-00", planned, reviewed)
    for change, match in (
        ({"admission": {"admitted": False, "refusal": "HOM"}}, "not admitted"),
        ({"cases_sha256": "d"}, "case changed"),
        ({"body_sha256_without_process_id": body_digest({"payload": {"x": 2}})}, "differs from the preflight"),
    ):
        with pytest.raises(RuntimeError, match=match):
            case.bind_reviewed("job-00", planned, {**reviewed, **change})


def test_column_batches_certify_the_same_values() -> None:
    """A ball survives its pickled parts, and scoring columns apart or together certifies the same floats."""
    from flint import arb, ctx

    ctx.prec = 128
    ball = arb(1) / 3 + arb("0 +/- 1e-30")
    rebuilt = case.from_parts(case.ball_parts(ball))
    if rebuilt.mid() != ball.mid() or not rebuilt.contains(ball):
        raise AssertionError("the rebuilt ball moves its midpoint or loses the enclosure")
    coefficients = np.linspace(-1e-3, 2e-3, 256)
    columns = tomo.design_matrix() @ (coefficients[:, None] + np.outer(np.ones(256), [0.0, 1e-5]))
    together = case.column_balls((columns, 128))
    apart = [case.column_balls((columns[:, [k]], 128)) for k in range(2)]
    for table in case.TABLES:
        joined = [case.certified_float(case.from_parts(v)) for v in together["F"][table]]
        split = [case.certified_float(case.from_parts(part["F"][table][0])) for part in apart]
        if None in joined or joined != split:
            raise AssertionError(f"{table}: batching changes the certified scores {joined} against {split}")


def test_a_ball_across_zero_does_not_certify() -> None:
    """[-2^-1100, 2^-1100] rounds to -0.0 at its lower end and +0.0 at its upper: two float64 encodings."""
    from flint import arb, ctx

    ctx.prec = 128
    if case.certified_float(arb(0, arb(2) ** -1100)) is not None:
        raise AssertionError("a ball across zero certifies one signed zero")
    if case.certified_float(arb(2) ** -1100 * arb("0.5 +/- 0.25")) != 0.0:
        raise AssertionError("a positive ball below the subnormal range does not certify +0.0")
