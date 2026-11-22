"""The six-seed-slot Belenos diagnostic: layout, case record, power statement, builder and analyzer."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import bdsc_cases
import bdsc_certificate as cert
import bdsc_diagnostic as frozen
import bdsc_diagnostic_v2 as layout
import bdsc_diagnostic_v2_analysis as reader
import bdsc_diagnostic_v2_case as builder
import pytest
import qd_platform as qd
from scipy.stats import chi2

ROOT = builder.ROOT
diag = layout.diag
acquisition = builder.case
analysis = reader.analysis
PLATFORM = "qpu:belenos"
JOBS = ("b1-j1", "b1-j2", "b2-j1", "b2-j2")
# The retained original diagnostic manifests name this ANU draw; the successor refuses to claim it.
RETAINED_DRAW = ROOT / "docs/evidence/anu_qrng/draw-2026-10-22T110545Z.json"
BASIS = {"f": 0.003, "g": 0.986}
SUPERPOSITION = (BASIS["f"] + BASIS["g"]) / 2


class Drawn:
    """A scratch tree under the ignored docs/local: one synthetic QRNG draw and the built tree."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.draw = bdsc_cases.synthetic_draw(root, layout.DRAW_VALUES // 2)
        self.tree = root / "qpu-belenos"
        acquisition.write(self.tree, PLATFORM, self.draw)

    @property
    def case(self) -> Path:
        return self.tree / "case.json"

    def manifests(self) -> dict[str, dict[str, Any]]:
        return {job: json.loads((self.tree / job / "cases.json").read_bytes()) for job in JOBS}


@pytest.fixture(scope="module")
def drawn() -> Iterator[Drawn]:
    scratch = ROOT / "docs/local"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        yield Drawn(Path(directory))


def label(setting: dict[str, Any]) -> str:
    return next(key for key, tag in bdsc_cases.LABEL_TAGS.items() if setting["name"].endswith(f"-{tag}"))


def response(common: float = 0.0, het: float = 0.0) -> Callable[[dict[str, Any]], float]:
    """The diagnostic self-test's selected-fraction model: a common residual or a heterogeneous block-2 shift."""

    def at(setting: dict[str, Any]) -> float:
        lab = label(setting)
        if lab in BASIS:
            return BASIS[lab]
        sign = 1 if (setting["slot"] + (setting["preparation"] == cert.PREPARATION_DESCRIPTIONS[0])) % 2 else -1
        return SUPERPOSITION + common + het * sign * (setting["block"] - 1)

    return at


def runs_for(
    root: Path, manifests: dict[str, dict[str, Any]], model: Callable[[dict[str, Any]], float], **kw: Any
) -> list[Path]:
    root.mkdir()
    return diag.synthetic_runs(root, manifests, model, **kw)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_the_fork_leaves_the_frozen_module_at_four_slots_and_every_copy_reads_six() -> None:
    if frozen.SLOTS != 4 or frozen.DRAW_VALUES != 100 or frozen.outward_slots(1) != (0, 1):
        raise AssertionError("the frozen module changed")
    scope = layout.SCOPE
    if (scope["SLOTS"], scope["DRAW_VALUES"]) != (6, 150):
        raise AssertionError("the fork does not hold six slots and 150 draw values")
    replaced = {"case_record", "outward_slots"}
    functions = [n for n, v in vars(frozen).items() if getattr(v, "__module__", None) == frozen.__name__]
    shared = sorted(n for n in functions if scope[n] is vars(frozen)[n])
    if shared != sorted(layout.KEEP):
        raise AssertionError(f"functions shared with the frozen module: {shared}")
    stale = [n for n in functions if n not in layout.KEEP | replaced and scope[n].__globals__ is not scope]
    if stale:
        raise AssertionError(f"functions that read the frozen globals: {stale}")


def test_the_layout_holds_four_jobs_of_36_iterations_in_matched_blocks() -> None:
    items = diag.instances()
    if len(items) != 144 or Counter(i["job"] for i in items) != {job: 36 for job in JOBS}:
        raise AssertionError("the layout is not 4 jobs of 36 iterations")
    groups = {job: diag.job_groups(job) for job in JOBS}
    if any(len(g) != 6 for g in groups.values()) or groups["b1-j2"] != groups["b2-j1"]:
        raise AssertionError("a job does not hold 6 groups or b2-j1 does not repeat b1-j2")
    if groups["b1-j1"] & groups["b1-j2"] or groups["b1-j1"] != groups["b2-j2"]:
        raise AssertionError("the blocks do not swap their group assignment")
    if len(diag.matched_pairs()) != 36:
        raise AssertionError("the matched pairs are not the 36 instances of b1-j2")
    orders = {diag.order_index(i["index"]) for i in items}
    if max(orders) != 71 or len(orders) != 72:
        raise AssertionError("a block-2 instance does not take its block-1 match's order value")


def test_the_estimate_fits_the_job_limit_and_the_bill_is_unchanged() -> None:
    record = diag.case_record()
    resources = record["resources"]
    seconds = resources["seconds_per_job_estimate"]
    if abs(seconds - 36 * (frozen.SECONDS_PER_ITERATION + frozen.SECONDS_PER_SAMPLE * frozen.TRIALS)) > 1e-9:
        raise AssertionError("the estimate does not follow the timing rule")
    if not seconds < bdsc_cases.MAX_DURATION or resources["credits"] != 4.32:
        raise AssertionError(f"{seconds} s per job or {resources['credits']} credits")
    if record["design"]["instances"] != 144 or {j["iterations"] for j in record["jobs"]} != {36}:
        raise AssertionError("the record's counts")
    if record["qrng"]["values"] != 150:
        raise AssertionError("the record asks for another draw size")


def test_the_case_record_differs_from_the_frozen_one_only_in_counts_and_wording() -> None:
    old, new = frozen.case_record(), diag.case_record()
    changed = {key for key in old if old[key] != new[key]}
    if changed != {"schema", "authorization", "design", "jobs", "resources", "qrng", "analysis"}:
        raise AssertionError(f"changed keys {sorted(changed)}")
    if set(new) != set(old):
        raise AssertionError("the successor adds or drops a top-level key")
    authorization = new["authorization"]
    if "covers its QRNG read" in authorization or "free ANU" not in authorization:
        raise AssertionError("the authorization still says approval covers the QRNG read")
    text = json.dumps({k: v for k, v in new.items() if k != "jobs"})
    for stale in ("four seeds", "of the four seeds", "32 residuals", "(3 df each)", "(9 df each)", "0 to 3", "value 4 + i"):
        if stale in text:
            raise AssertionError(f"stale wording {stale!r}")
    if "(5 df each)" not in text or "(15 df each)" not in text or "all 48 residuals" not in text:
        raise AssertionError("the new degrees of freedom and residual count are absent")


def test_the_power_statement_matches_the_chi_square_it_inverts() -> None:
    statement = diag.case_record()["analysis"]["power"]
    for key, slots in (("six_slots", 6), ("frozen_four_slots", 4)):
        rows = statement[key]
        if rows != layout.power_rows(slots):
            raise AssertionError(f"{key} is not the power function's output")
        for name, row in rows.items():
            scale = layout.STATE_COUNT if name == "seed_common" else 1
            for power, ratio in zip(layout.POWERS, row["detectable_seed_sd_over_se"].values(), strict=True):
                shift = 1 + scale * ratio**2
                got = float(chi2.sf(chi2.isf(frozen.ALPHA, row["df"]) / shift, row["df"]))
                if abs(got - power) > 0.01:
                    raise AssertionError(f"{key}/{name}: power {got} at the ratio {ratio}, expected {power}")
    for name, row in statement["six_slots"].items():
        for power, ratio in row["detectable_seed_sd_over_se"].items():
            if not ratio < statement["frozen_four_slots"][name]["detectable_seed_sd_over_se"][power]:
                raise AssertionError(f"{name}: six slots do not detect a smaller seed SD at {power}")
    if (statement["six_slots"]["seed_superposition"]["df"], statement["frozen_four_slots"]["seed_superposition"]["df"]) != (
        80,
        48,
    ):
        raise AssertionError("the seed_superposition degrees of freedom")


def test_a_platform_outside_the_request_is_refused() -> None:
    for platform in ("sim:belenos", "sim:ascella", "qpu:ascella"):
        with pytest.raises(ValueError, match="not an admitted platform"):
            acquisition.documents(platform)


def test_manifests_hold_36_iterations_cite_indices_inside_the_draw_and_bind_the_record(drawn: Drawn) -> None:
    values = json.loads(drawn.draw.read_text(encoding="utf-8"))["values"]
    case_sha = digest(drawn.case)
    cited = set()
    for job, manifest in drawn.manifests().items():
        if manifest["platforms"] != [PLATFORM] or manifest["acquisition_admission"] != "ready":
            raise AssertionError(f"{job}: platform or admission")
        if manifest["iterations"] != 36 or len(manifest["settings"]) != 36 or manifest["max_shots"] != 36 * 80000:
            raise AssertionError(f"{job}: iterations or shots")
        if manifest["diagnostic_case_sha256"] != case_sha or manifest["draft"] is not False:
            raise AssertionError(f"{job}: the manifest does not name the record or is a draft")
        if sorted(manifest["successor_sources"]) != list(builder.SOURCES):
            raise AssertionError(f"{job}: bound sources")
        for setting in manifest["settings"]:
            seed, order = setting["draw_indices"]["seed"], setting["draw_indices"]["order"]
            if not (0 <= seed < 6 <= order < 150) or setting["compilation_seed"] != values[seed]:
                raise AssertionError(f"{job}/{setting['name']}: cited indices or seed")
            cited.update((seed, order))
    if cited != set(range(6)) | set(range(6, 6 + 72)):
        raise AssertionError("the manifests cite another index set than 6 seeds and 72 order values")


def test_a_draw_is_claimed_by_every_other_case(drawn: Drawn, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    own = (drawn.tree,)
    acquisition.check(drawn.tree, drawn.draw, roots=own)
    foreign = tmp_path / "foreign"
    shutil.copytree(drawn.tree / "b1-j1", foreign / "b1-j1")
    manifest = json.loads((foreign / "b1-j1/cases.json").read_bytes())
    manifest["diagnostic_case_sha256"] = "0" * 64
    (foreign / "b1-j1/cases.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="another case already draws from this record"):
        acquisition.documents(PLATFORM, drawn.draw, roots=(foreign,))
    with pytest.raises(ValueError, match="another case already draws from this record"):
        acquisition.documents(PLATFORM, RETAINED_DRAW)
    monkeypatch.setattr(bdsc_cases, "MANIFEST_ROOTS", own)
    with pytest.raises(ValueError, match="another case already draws from this record"):
        frozen.documents(drawn.draw)


def test_a_draw_of_fewer_than_150_values_is_refused(tmp_path: Path) -> None:
    scratch = ROOT / "docs/local"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        short = bdsc_cases.synthetic_draw(Path(directory), 50)
        with pytest.raises(ValueError, match="need 150"):
            acquisition.documents(PLATFORM, short)


def test_check_round_trips_and_refuses_a_changed_record_or_a_tree_under_the_original(
    drawn: Drawn, tmp_path: Path
) -> None:
    acquisition.check(drawn.tree, drawn.draw)
    copy = tmp_path / "copy"
    shutil.copytree(drawn.tree, copy)
    (copy / "case.json").write_bytes((copy / "case.json").read_bytes() + b" ")
    with pytest.raises(ValueError, match="differs from a fresh build"):
        acquisition.check(copy, drawn.draw)
    with pytest.raises(ValueError, match="original diagnostic tree"):
        acquisition.write(frozen.CASES_DIR / "successor-probe", PLATFORM, drawn.draw)


@pytest.mark.parametrize(
    ("model", "branch"),
    [
        pytest.param(response(common=-0.03), "common-effect", id="common residual"),
        pytest.param(response(het=0.012), "stationarity", id="heterogeneous block shift"),
    ],
)
def test_a_synthetic_run_reads_the_branch_its_design_predicts(
    drawn: Drawn, tmp_path: Path, model: Callable[[dict[str, Any]], float], branch: str
) -> None:
    report = analysis.readout(runs_for(tmp_path / "runs", drawn.manifests(), model), drawn.case, validate=False)
    if report["branch"] != branch:
        raise AssertionError(f"read {report['branch']}, expected {branch}")
    if report["platform"] != PLATFORM or report["case_sha256"] != digest(drawn.case):
        raise AssertionError("the report does not name its platform and case record")


def test_the_readers_refuse_each_others_runs(drawn: Drawn, tmp_path: Path) -> None:
    runs = runs_for(tmp_path / "runs", drawn.manifests(), response())
    with pytest.raises(ValueError, match="built from another case record"):
        frozen.readout(runs, validate=False)
    frozen_manifests = {
        job: json.loads(files["cases.json"])
        for job, files in frozen.documents(drawn.draw).items()
        if isinstance(files, dict)
    }
    other = runs_for(tmp_path / "other", frozen_manifests, response())
    with pytest.raises(ValueError, match="binds no successor sources"):
        analysis.readout(other, drawn.case, validate=False)
    changed = tmp_path / "changed.json"
    changed.write_bytes(drawn.case.read_bytes() + b" ")
    with pytest.raises(ValueError, match="differs from a fresh build"):
        analysis.readout(runs, changed, validate=False)
    with pytest.raises(ValueError, match="needs every job"):
        analysis.readout(runs[:3], drawn.case, validate=False)


def test_the_matched_check_names_a_returned_circuit_that_changed(drawn: Drawn, tmp_path: Path) -> None:
    by_job = {run.name: run for run in runs_for(tmp_path / "same", drawn.manifests(), response())}
    if analysis.matched_check(by_job["b1-j2"], by_job["b2-j1"], drawn.case, validate=False) != []:
        raise AssertionError("equal returned circuits read as a mismatch")

    def recompile(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
        if job == "b2-j1":
            result["iterations"][0]["result_fields"]["computed_circuit"] += " recompiled"

    changed = runs_for(tmp_path / "changed", drawn.manifests(), response(), edit=recompile)
    by_job = {run.name: run for run in changed}
    lines = analysis.matched_check(by_job["b1-j2"], by_job["b2-j1"], drawn.case, validate=False)
    if len(lines) != 1 or "b2-j1 returned another circuit" not in lines[0]:
        raise AssertionError(f"the matched check read {lines}")


LOADED = """
import sys
from pathlib import Path
sys.path[:0] = ["gororoba_quantum", "scripts"]
import bdsc_diagnostic_v2_analysis
import bdsc_diagnostic_v2_case as case
case.case.documents("qpu:belenos")
root = Path.cwd().resolve()
print("\\n".join(sorted(
    str(Path(m.__file__).resolve().relative_to(root))
    for m in sys.modules.values()
    if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to(root)
)))
"""


def test_the_bound_sources_cover_every_repository_module_the_readout_imports() -> None:
    found = subprocess.run(
        [sys.executable, "-I", "-c", LOADED], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    missing = sorted(set(found) - set(builder.SOURCES))
    if missing:
        raise AssertionError(f"imported repository modules outside SOURCES: {missing}")
    unused = sorted(set(builder.SOURCES) - set(found) - {"scripts/anu_qrng.py"})
    if unused:
        raise AssertionError(f"SOURCES names files that the readout does not import: {unused}")


def source_copy(tmp_path: Path) -> Path:
    copy = tmp_path / "tree"
    for name in builder.SOURCES:
        (copy / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, copy / name)
    return copy


@pytest.mark.parametrize("name", builder.SOURCES)
def test_a_changed_bound_source_is_refused(drawn: Drawn, tmp_path: Path, name: str) -> None:
    manifest = drawn.manifests()["b1-j1"]
    if manifest["successor_sources"] != acquisition.source_digests():
        raise AssertionError("the manifest does not bind the digests of the tree")
    copy = source_copy(tmp_path)
    qd.verify_successor_sources(manifest, copy)
    target = copy / name
    target.write_bytes(target.read_bytes() + b"\n# changed\n")
    with pytest.raises(qd.PlatformError, match=f"reviewed source changed: {name}"):
        qd.verify_successor_sources(manifest, copy)


# Counts that fix every fraction by hand: f and g at 0.003 and 0.986 of 40000 trials, each superposition at 0.4945.
FIXED_HITS = {"f": 120, "g": 39440, "+": 19780, "-": 19780, "+i": 19780, "-i": 19780}


def fixed_counts(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
    selected = manifest["selected_modes"][0]
    other = next(mode for mode in range(cert.MODES) if mode not in manifest["selected_modes"])
    for setting, iteration in zip(manifest["settings"], result["iterations"], strict=True):
        hits = FIXED_HITS[label(setting)]
        hit, miss = ["0"] * cert.MODES, ["0"] * cert.MODES
        hit[selected], miss[other] = "1", "1"
        iteration["counts"] = {",".join(hit): hits, ",".join(miss): frozen.TRIALS - hits}


def assert_fixed_readout(report: dict[str, Any]) -> None:
    """The fields that follow from FIXED_HITS by hand, independent of the analysis code.

    Every instance repeats its block-1 match, so each block change is 0; each superposition sits at 19780 / 40000 =
    0.4945, 0.0055 below the r-hat of 0.5 of equal perf_f and perf_g; the 48 residuals (2 blocks x 2 templates x 6
    seeds x 2 families) are differences of equal fractions, hence 0; no test sees dispersion, so every reading is
    consistent and the branch is ensemble-candidate."""
    expected_fraction = 19780 / 40000
    problems = []
    if report["branch"] != "ensemble-candidate":
        problems.append(f"branch {report['branch']}")
    if set(report["readings"].values()) != {"consistent"}:
        problems.append(f"readings {report['readings']}")
    if len(report["residuals"]) != 48 or any(row["value"] != 0.0 for row in report["residuals"]):
        problems.append("residuals")
    if len(report["block_changes"]) != 72 or any(row["change"] != 0.0 for row in report["block_changes"]):
        problems.append("block changes")
    if report["returned_circuit_repeats"] != 72 or report["residuals_beyond_margin"] != 0:
        problems.append("repeats or margin count")
    if report["leak_outliers"]:
        problems.append("leaks")
    shifts = report["calibration_shift"]
    if [shifts[k]["n"] for k in ("superposition", "f", "g")] != [48, 12, 12] or shifts["superposition"]["mean"] != 0.0:
        problems.append("calibration shift")
    if [report["tests"][k]["df"] for k in ("seed_superposition", "seed_common", "seed_interaction")] != [80, 20, 60]:
        problems.append("degrees of freedom")
    deviations = report["perf_ratio"]["deviations"]
    if len(deviations) != 96 or any(abs(row["fraction"] - expected_fraction) > 1e-12 for row in deviations):
        problems.append("superposition fractions")
    if (
        abs(report["perf_ratio"]["deviation_rms"] - 0.0055) > 1e-12
        or report["perf_ratio"]["r_hat_summary"]["mean"] != 0.5
    ):
        problems.append("perf ratio")
    if problems:
        raise AssertionError(f"the readout departs from the hand-computed fields: {problems}")


def test_the_readout_of_fixed_counts_matches_the_hand_computed_fields(drawn: Drawn, tmp_path: Path) -> None:
    runs = runs_for(tmp_path / "runs", drawn.manifests(), response(), edit=fixed_counts)
    assert_fixed_readout(analysis.readout(runs, drawn.case, validate=False))


def test_a_planted_readout_defect_departs_from_the_hand_computed_fields(
    drawn: Drawn, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    runs = runs_for(tmp_path / "runs", drawn.manifests(), response(), edit=fixed_counts)
    analyse, observations = layout.SCOPE["analyse"], layout.SCOPE["observations"]

    def wrong_branch(observed: dict[int, dict[str, Any]]) -> dict[str, Any]:
        return {**analyse(observed), "branch": "common-effect"}

    def one_click_lost(manifest: dict[str, Any], result: dict[str, Any], trials: int = frozen.TRIALS) -> Any:
        items = observations(manifest, result, trials)
        first = min(items)
        items[first] = {**items[first], "selected": items[first]["selected"] - 40}
        return items

    for name, mutation in (("analyse", wrong_branch), ("observations", one_click_lost)):
        with monkeypatch.context() as patched:
            patched.setitem(layout.SCOPE, name, mutation)
            report = analysis.readout(runs, drawn.case, validate=False)
        with pytest.raises(AssertionError, match="departs from the hand-computed fields"):
            assert_fixed_readout(report)


def test_the_forked_self_test_passes_at_six_slots() -> None:
    if layout.SCOPE["self_test"]() != 0:
        raise AssertionError("the diagnostic self-test fails at six slots")
