"""The platform-bound Belenos diagnostic pair admits only its own case record and states the current billing rule."""

from __future__ import annotations

import hashlib
import json
import shutil
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
    with pytest.raises(ValueError, match="built from another case record"):
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
