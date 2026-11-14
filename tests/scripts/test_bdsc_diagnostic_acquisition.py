"""The platform-bound Belenos diagnostic pair admits only its own case record and states the current billing rule."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import bdsc_cases
import bdsc_certificate as cert
import bdsc_diagnostic as diag
import bdsc_diagnostic_acquisition_analysis as analysis
import bdsc_diagnostic_acquisition_case as acquisition
import pytest
import qd_platform as qd
from billing_rule_v2 import RULE

ROOT = acquisition.ROOT
# The retained original diagnostic manifests name this ANU draw; the successor refuses to claim it.
RETAINED_DRAW = ROOT / "docs/evidence/anu_qrng/draw-2026-10-22T110545Z.json"
# Selected-fraction model of the diagnostic's own self-test: f and g sit at their output efficiencies and the four
# superposition states at their mean.
BASIS = {"f": 0.003, "g": 0.986}
SUPERPOSITION = (BASIS["f"] + BASIS["g"]) / 2


class Drawn:
    """A scratch tree under the ignored docs/local: one synthetic QRNG draw and each platform's built tree."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.draw = bdsc_cases.synthetic_draw(root, diag.DRAW_VALUES // 2)
        self.trees: dict[str, Path] = {}
        for platform in acquisition.PLATFORMS:
            self.trees[platform] = root / platform.replace(":", "-")
            acquisition.write(self.trees[platform], platform, self.draw)

    def case(self, platform: str) -> Path:
        return self.trees[platform] / "case.json"

    def manifests(self, platform: str) -> dict[str, dict[str, Any]]:
        return {
            job: json.loads((self.trees[platform] / job / "cases.json").read_bytes())
            for job in ("b1-j1", "b1-j2", "b2-j1", "b2-j2")
        }


@pytest.fixture(scope="module")
def drawn() -> Iterator[Drawn]:
    # The QRNG record must sit inside the repository, so the synthetic one goes under the ignored docs/local.
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
    root: Path, platform: str, manifests: dict[str, dict[str, Any]], model: Callable[[dict[str, Any]], float], **kw: Any
) -> list[Path]:
    """Synthetic collected runs on `platform` (synthetic_runs names qpu:belenos; `edit` replaces it)."""
    root.mkdir()

    def edit(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
        result["data"]["platform_name"] = platform
        submission["platform"] = platform
        if "edit" in kw:
            kw["edit"](job, manifest, result, submission)

    return diag.synthetic_runs(root, manifests, model, edit=edit)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_the_case_record_changes_only_the_billing_rule_and_names_the_platform() -> None:
    original = diag.case_record()
    for platform in acquisition.PLATFORMS:
        successor = acquisition.case_record(platform)
        if successor["resources"]["billing_rule"] != RULE:
            raise AssertionError("the case record does not state the current billing rule")
        if successor["acquisition"]["platform"] != platform:
            raise AssertionError("the case record does not name its platform")
        successor.pop("acquisition")
        successor["resources"]["billing_rule"] = original["resources"]["billing_rule"]
        if successor != original:
            raise AssertionError("the successor record changed a field besides the billing rule and the platform")


def test_a_platform_outside_the_circuit_is_refused() -> None:
    for platform in ("sim:ascella", "qpu:ascella", "sim:slos"):
        with pytest.raises(ValueError, match="not an admitted platform"):
            acquisition.documents(platform)


def test_manifests_admit_one_platform_ready_and_bind_the_successor_record(drawn: Drawn) -> None:
    original = {
        job: json.loads(files["cases.json"])
        for job, files in diag.documents(drawn.draw).items()
        if isinstance(files, dict)
    }
    record = json.loads(drawn.draw.read_text(encoding="utf-8"))["values"]
    for platform in acquisition.PLATFORMS:
        case_sha = digest(drawn.case(platform))
        if case_sha == hashlib.sha256((json.dumps(diag.case_record(), indent=1) + "\n").encode()).hexdigest():
            raise AssertionError("the successor record has the original record's digest")
        for job, manifest in drawn.manifests(platform).items():
            if manifest["platforms"] != [platform] or manifest["acquisition_admission"] != "ready":
                raise AssertionError(f"{job}: platform or admission")
            if manifest["diagnostic_case_sha256"] != case_sha or manifest["draft"] is not False:
                raise AssertionError(f"{job}: the manifest does not name the successor record or is a draft")
            # Every seed and order value is the draw value at the cited index.
            for setting in manifest["settings"]:
                if setting["compilation_seed"] != record[setting["draw_indices"]["seed"]]:
                    raise AssertionError(f"{job}/{setting['name']}: seed differs from its cited draw index")
            # The scientific content equals the original's for the same draw, setting by setting.
            if manifest["settings"][0] != original[job]["settings"][0]:
                raise AssertionError(f"{job}: the first setting differs from the original's for the same draw")


def test_a_draw_is_claimed_by_every_other_case_and_by_no_manifest_of_the_same_record(
    drawn: Drawn, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The successor's own manifests, retained under a manifest root, do not block a rebuild of the same request.
    own = (drawn.trees["sim:belenos"],)
    acquisition.check(drawn.trees["sim:belenos"], drawn.draw, roots=own)
    # The other platform's tree is another case record: it claims the draw, so each tree takes its own draw.
    with pytest.raises(ValueError, match="another case already draws from this record"):
        acquisition.documents("sim:belenos", drawn.draw, roots=(drawn.trees["qpu:belenos"],))
    # A manifest of another case record that names the draw claims it.
    foreign = tmp_path / "foreign"
    shutil.copytree(drawn.trees["qpu:belenos"] / "b1-j1", foreign / "b1-j1")
    manifest = json.loads((foreign / "b1-j1/cases.json").read_bytes())
    manifest["diagnostic_case_sha256"] = "0" * 64
    (foreign / "b1-j1/cases.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="another case already draws from this record"):
        acquisition.documents("sim:belenos", drawn.draw, roots=(foreign,))
    # The original diagnostic is another case: its manifests claim the retained draw against the successor, and the
    # successor's manifests claim a draw against the original.
    with pytest.raises(ValueError, match="another case already draws from this record"):
        acquisition.documents("qpu:belenos", RETAINED_DRAW)
    monkeypatch.setattr(bdsc_cases, "MANIFEST_ROOTS", own)
    with pytest.raises(ValueError, match="another case already draws from this record"):
        diag.documents(drawn.draw)


def test_check_round_trips_and_refuses_a_changed_record_or_a_tree_under_the_original(
    drawn: Drawn, tmp_path: Path
) -> None:
    acquisition.check(drawn.trees["qpu:belenos"], drawn.draw)
    copy = tmp_path / "copy"
    shutil.copytree(drawn.trees["qpu:belenos"], copy)
    (copy / "case.json").write_bytes((copy / "case.json").read_bytes() + b" ")
    with pytest.raises(ValueError, match="differs from a fresh build"):
        acquisition.check(copy, drawn.draw)
    with pytest.raises(ValueError, match="original diagnostic tree"):
        acquisition.write(diag.CASES_DIR / "successor-probe", "qpu:belenos", drawn.draw)


@pytest.mark.parametrize("platform", acquisition.PLATFORMS)
@pytest.mark.parametrize(
    ("model", "branch"),
    [
        # A common shift of the superposition fractions by -0.03 leaves the seed and block components at counting
        # noise and moves every residual past the 0.02 margin.
        pytest.param(response(common=-0.03), "common-effect", id="common residual"),
        # A block-2 shift of +/-0.012 with zero mean over the (template, seed) groups is a heterogeneous change.
        pytest.param(response(het=0.012), "stationarity", id="heterogeneous block shift"),
    ],
)
def test_a_synthetic_run_reads_the_branch_its_design_predicts(
    drawn: Drawn, tmp_path: Path, platform: str, model: Callable[[dict[str, Any]], float], branch: str
) -> None:
    runs = runs_for(tmp_path / "runs", platform, drawn.manifests(platform), model)
    report = analysis.readout(runs, drawn.case(platform), validate=False)
    if report["branch"] != branch:
        raise AssertionError(f"{platform} read {report['branch']}, expected {branch}")
    if report["platform"] != platform or report["case_sha256"] != digest(drawn.case(platform)):
        raise AssertionError("the report does not name its platform and case record")


def test_the_successor_reads_a_run_as_the_original_reads_its_own(drawn: Drawn, tmp_path: Path) -> None:
    """The same draw and counts, once under each case record, give the same analysis outside the added fields."""
    model = response(common=-0.03)
    successor_runs = runs_for(tmp_path / "successor", "qpu:belenos", drawn.manifests("qpu:belenos"), model)
    original_manifests = {
        job: json.loads(files["cases.json"])
        for job, files in diag.documents(drawn.draw).items()
        if isinstance(files, dict)
    }
    (tmp_path / "original").mkdir()
    original_runs = diag.synthetic_runs(tmp_path / "original", original_manifests, model)
    expected = diag.readout(original_runs, validate=False)
    found = analysis.readout(successor_runs, drawn.case("qpu:belenos"), validate=False)
    del found["platform"], found["case_sha256"]
    if json.dumps(found, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise AssertionError("the successor analysis differs from the original's on the same counts")
    # Each reader refuses the other's runs: the manifests name another case record.
    with pytest.raises(ValueError, match="built from another case record"):
        diag.readout(successor_runs, validate=False)
    with pytest.raises(ValueError, match="binds no successor sources"):
        analysis.readout(original_runs, drawn.case("qpu:belenos"), validate=False)


def test_a_run_of_another_platform_or_record_is_refused(drawn: Drawn, tmp_path: Path) -> None:
    sim_runs = runs_for(tmp_path / "sim", "sim:belenos", drawn.manifests("sim:belenos"), response())
    with pytest.raises(ValueError, match="submitted to 'sim:belenos'"):
        analysis.readout(sim_runs, drawn.case("qpu:belenos"), validate=False)
    qpu_runs = runs_for(tmp_path / "qpu", "qpu:belenos", drawn.manifests("sim:belenos"), response())
    with pytest.raises(ValueError, match="submitted to 'qpu:belenos'"):
        analysis.readout(qpu_runs, drawn.case("sim:belenos"), validate=False)
    changed = tmp_path / "changed.json"
    changed.write_bytes(drawn.case("sim:belenos").read_bytes() + b" ")
    with pytest.raises(ValueError, match="differs from a fresh build"):
        analysis.readout(sim_runs, changed, validate=False)
    # A run that holds three of the four jobs does not read.
    with pytest.raises(ValueError, match="needs every job"):
        analysis.readout(sim_runs[:3], drawn.case("sim:belenos"), validate=False)


def test_the_matched_check_names_a_returned_circuit_that_changed(drawn: Drawn, tmp_path: Path) -> None:
    runs = runs_for(tmp_path / "same", "sim:belenos", drawn.manifests("sim:belenos"), response())
    by_job = {run.name: run for run in runs}
    case = drawn.case("sim:belenos")
    if analysis.matched_check(by_job["b1-j2"], by_job["b2-j1"], case, validate=False) != []:
        raise AssertionError("equal returned circuits read as a mismatch")

    def recompile(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
        if job == "b2-j1":
            result["iterations"][0]["result_fields"]["computed_circuit"] += " recompiled"

    runs = runs_for(tmp_path / "changed", "sim:belenos", drawn.manifests("sim:belenos"), response(), edit=recompile)
    by_job = {run.name: run for run in runs}
    lines = analysis.matched_check(by_job["b1-j2"], by_job["b2-j1"], case, validate=False)
    if len(lines) != 1 or "b2-j1 returned another circuit" not in lines[0]:
        raise AssertionError(f"the matched check read {lines}")


def test_a_single_run_admits_for_a_rehearsal_that_holds_fewer_than_every_job(drawn: Drawn, tmp_path: Path) -> None:
    runs = runs_for(tmp_path / "runs", "sim:belenos", drawn.manifests("sim:belenos"), response())
    case = drawn.case("sim:belenos")
    if analysis.admit(runs[:1], case, validate=False) != ["b1-j1"]:
        raise AssertionError("the first job does not admit alone")
    manifest = json.loads((runs[0] / "cases.json").read_bytes())
    manifest["draw"]["sha256"] = "0" * 64
    (runs[0] / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n")
    with pytest.raises(ValueError, match="cases.json changed"):
        analysis.admit(runs[:1], case, validate=False)


LOADED = """
import sys
from pathlib import Path
sys.path[:0] = ["gororoba_quantum", "scripts"]
import bdsc_diagnostic_acquisition_analysis
import bdsc_diagnostic_acquisition_case as case
case.documents("sim:belenos")
root = Path.cwd().resolve()
print("\\n".join(sorted(
    str(Path(m.__file__).resolve().relative_to(root))
    for m in sys.modules.values()
    if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to(root)
)))
"""


def test_the_bound_sources_cover_every_repository_module_the_readout_imports() -> None:
    """A fresh interpreter that imports the analyzer and builds a request loads no repository file outside SOURCES."""
    found = subprocess.run(
        [sys.executable, "-I", "-c", LOADED], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split()
    missing = sorted(set(found) - set(acquisition.SOURCES))
    if missing:
        raise AssertionError(f"imported repository modules outside SOURCES: {missing}")
    # draw_values imports anu_qrng when a build or a readout reads a draw, which this undrawn build does not.
    unused = sorted(set(acquisition.SOURCES) - set(found) - {"scripts/anu_qrng.py"})
    if unused:
        raise AssertionError(f"SOURCES names files that the readout does not import: {unused}")


def source_copy(tmp_path: Path) -> Path:
    """The bound files under a scratch tree, which a test mutates instead of the repository."""
    copy = tmp_path / "tree"
    for name in acquisition.SOURCES:
        (copy / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, copy / name)
    return copy


@pytest.mark.parametrize("name", acquisition.SOURCES)
def test_a_changed_bound_source_is_refused(drawn: Drawn, tmp_path: Path, name: str) -> None:
    manifest = drawn.manifests("sim:belenos")["b1-j1"]
    if manifest["successor_sources"] != acquisition.source_digests():
        raise AssertionError("the manifest does not bind the digests of the tree")
    copy = source_copy(tmp_path)
    qd.verify_successor_sources(manifest, copy)
    target = copy / name
    target.write_bytes(target.read_bytes() + b"\n# changed\n")
    with pytest.raises(qd.PlatformError, match=f"reviewed source changed: {name}"):
        qd.verify_successor_sources(manifest, copy)


def test_the_analyzer_refuses_a_run_when_its_readout_source_changed(drawn: Drawn, tmp_path: Path) -> None:
    runs = runs_for(tmp_path / "runs", "sim:belenos", drawn.manifests("sim:belenos"), response())
    case = drawn.case("sim:belenos")
    copy = source_copy(tmp_path)
    if analysis.admit(runs[:1], case, validate=False, root=copy) != ["b1-j1"]:
        raise AssertionError("an unchanged tree does not admit")
    readout = copy / "scripts/bdsc_diagnostic.py"
    readout.write_bytes(readout.read_bytes().replace(b"def readout(", b"def readout_changed(", 1))
    with pytest.raises(qd.PlatformError, match="reviewed source changed: scripts/bdsc_diagnostic.py"):
        analysis.admit(runs[:1], case, validate=False, root=copy)
    with pytest.raises(qd.PlatformError, match="reviewed source changed: scripts/bdsc_diagnostic.py"):
        analysis.readout(runs, case, validate=False, root=copy)


# Counts that fix every fraction by hand: f and g at their output efficiencies 0.003 and 0.986 of 40000 trials, each
# superposition at 0.4945, in both blocks, every template and every seed slot.
FIXED_HITS = {"f": 120, "g": 39440, "+": 19780, "-": 19780, "+i": 19780, "-i": 19780}


def fixed_counts(job: str, manifest: dict[str, Any], result: dict[str, Any], submission: dict[str, Any]) -> None:
    selected = manifest["selected_modes"][0]
    other = next(mode for mode in range(cert.MODES) if mode not in manifest["selected_modes"])
    for setting, iteration in zip(manifest["settings"], result["iterations"], strict=True):
        hits = FIXED_HITS[label(setting)]
        hit, miss = ["0"] * cert.MODES, ["0"] * cert.MODES
        hit[selected], miss[other] = "1", "1"
        iteration["counts"] = {",".join(hit): hits, ",".join(miss): diag.TRIALS - hits}


def assert_fixed_readout(report: dict[str, Any]) -> None:
    """The fields that follow from FIXED_HITS by hand, independent of the analysis code.

    Every instance repeats its block-1 match, so each block change is 0; each superposition sits at 19780 / 40000 =
    0.4945, which is 0.0055 below the r-hat of 0.5 that equal perf_f and perf_g give (0.078 / (0.078 + 0.078)); the 32
    residuals (2 blocks x 2 templates x 4 seeds x 2 families) are differences of equal fractions, hence 0; no test sees
    dispersion, so every reading is consistent and the branch is ensemble-candidate."""
    expected_fraction = 19780 / 40000
    problems = []
    if report["branch"] != "ensemble-candidate":
        problems.append(f"branch {report['branch']}")
    if set(report["readings"].values()) != {"consistent"}:
        problems.append(f"readings {report['readings']}")
    if len(report["residuals"]) != 32 or any(row["value"] != 0.0 for row in report["residuals"]):
        problems.append("residuals")
    if len(report["block_changes"]) != 48 or any(row["change"] != 0.0 for row in report["block_changes"]):
        problems.append("block changes")
    if report["returned_circuit_repeats"] != 48 or report["residuals_beyond_margin"] != 0:
        problems.append("repeats or margin count")
    if report["leak_outliers"]:
        problems.append("leaks")
    shifts = report["calibration_shift"]
    if [shifts[k]["n"] for k in ("superposition", "f", "g")] != [32, 8, 8] or shifts["superposition"]["mean"] != 0.0:
        problems.append("calibration shift")
    deviations = report["perf_ratio"]["deviations"]
    if len(deviations) != 64 or any(abs(row["fraction"] - expected_fraction) > 1e-12 for row in deviations):
        problems.append("superposition fractions")
    if (
        abs(report["perf_ratio"]["deviation_rms"] - 0.0055) > 1e-12
        or report["perf_ratio"]["r_hat_summary"]["mean"] != 0.5
    ):
        problems.append("perf ratio")
    if problems:
        raise AssertionError(f"the readout departs from the hand-computed fields: {problems}")


@pytest.mark.parametrize("platform", acquisition.PLATFORMS)
def test_the_readout_of_fixed_counts_matches_the_hand_computed_fields(
    drawn: Drawn, tmp_path: Path, platform: str
) -> None:
    runs = runs_for(tmp_path / "runs", platform, drawn.manifests(platform), response(), edit=fixed_counts)
    assert_fixed_readout(analysis.readout(runs, drawn.case(platform), validate=False))


def test_a_planted_readout_defect_departs_from_the_hand_computed_fields(
    drawn: Drawn, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    platform = "qpu:belenos"
    runs = runs_for(tmp_path / "runs", platform, drawn.manifests(platform), response(), edit=fixed_counts)
    case = drawn.case(platform)
    analyse = diag.analyse
    observations = diag.observations

    def wrong_branch(observed: dict[int, dict[str, Any]]) -> dict[str, Any]:
        return {**analyse(observed), "branch": "common-effect"}

    def one_click_lost(manifest: dict[str, Any], result: dict[str, Any], trials: int = diag.TRIALS) -> Any:
        items = observations(manifest, result, trials)
        first = min(items)
        items[first] = {**items[first], "selected": items[first]["selected"] - 40}
        return items

    for name, mutation in (("analyse", wrong_branch), ("observations", one_click_lost)):
        with monkeypatch.context() as patched:
            patched.setattr(diag, name, mutation)
            report = analysis.readout(runs, case, validate=False)
        with pytest.raises(AssertionError, match="departs from the hand-computed fields"):
            assert_fixed_readout(report)
