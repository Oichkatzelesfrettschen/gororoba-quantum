"""Carried chip architecture for seeded Belenos cases: plan admission when the live record omits specs.architecture,
and the collect-time coupler check (qd_platform.live_architecture, couplers_state, collect)."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import qd_belenos_mesh as mesh  # noqa: E402
import qd_platform  # noqa: E402

import qd_records  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


CHIP = mesh.CHIP
OFFCONE = ROOT / "results/quandela/cases/belenos_offcone_mechanisms/job-00"
CATALOGUE = mesh.load_catalogue()
RETAINED = CATALOGUE["processors"][CHIP]["specs"]["architecture"]
OTHER = CATALOGUE["processors"]["qpu:ascella"]["specs"]["architecture"]


def live(blob: Any) -> dict[str, Any]:
    return {"status": "available", "specs": {"architecture": blob}}


def test_a_live_record_without_specs_architecture_is_admitted_on_the_carried_catalogue() -> None:
    expected = {
        "architecture_source": "carried",
        "architecture_catalogue_sha256": hashlib.sha256(mesh.CATALOGUE.read_bytes()).hexdigest(),
        "architecture_sha256": hashlib.sha256(RETAINED.encode()).hexdigest(),
        "architecture_observed_utc": CATALOGUE["architecture_observed_utc"][CHIP],
    }
    records: tuple[dict[str, Any], ...] = (
        {"specs": {}},
        {"specs": None},
        {},
        {"specs": {"architecture": None}},
    )
    for record in records:
        require(
            qd_platform.live_architecture(record, CHIP) == expected,
            "qd_platform.live_architecture(record, CHIP) == expected",
        )


def test_a_live_record_with_the_retained_couplers_keeps_the_comparison_and_names_its_source() -> None:
    got = qd_platform.live_architecture(live(RETAINED), CHIP)
    require(
        got is not None and got["architecture_source"] == "live",
        'got is not None and got["architecture_source"] == "live"',
    )


def test_a_live_blob_that_differs_refuses() -> None:
    with pytest.raises(qd_platform.PlatformError, match="differs from the retained catalogue"):
        qd_platform.live_architecture(live(OTHER), CHIP)


def test_another_platform_is_untouched() -> None:
    require(
        qd_platform.live_architecture({"specs": {}}, "sim:belenos") is None,
        'qd_platform.live_architecture({"specs": {}}, "sim:belenos") is None',
    )


def test_a_retained_catalogue_without_its_stamp_or_chip_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    for change in (
        lambda c: c["architecture_observed_utc"].pop(CHIP),
        lambda c: c["architecture_observed_utc"].update({CHIP: "yesterday"}),
        lambda c: c["processors"][CHIP]["specs"].pop("architecture"),
    ):
        catalogue = json.loads(json.dumps(CATALOGUE))
        change(catalogue)
        monkeypatch.setattr(mesh, "load_catalogue", lambda c=catalogue: c)
        with pytest.raises(qd_platform.PlatformError):
            qd_platform.live_architecture({"specs": {}}, CHIP)


def test_a_mesh_case_still_refuses_a_record_without_specs_architecture() -> None:
    with pytest.raises(qd_platform.PlatformError, match="no specs.architecture"):
        qd_platform.live_mesh({"specs": {}}, {"architecture": {}}, CHIP)


def submission_for(source: str = "carried") -> dict[str, Any]:
    return {"architecture_source": source, "architecture_sha256": hashlib.sha256(RETAINED.encode()).hexdigest()}


@pytest.mark.parametrize(
    ("record", "submission", "want"),
    [
        (live(RETAINED), submission_for(), "live-match"),
        (live(OTHER), submission_for(), "live-differ"),
        ({"specs": {}}, submission_for(), "unread"),
        ({"specs": {"architecture": None}}, submission_for("live"), "unread"),
        (live(RETAINED), {**submission_for(), "architecture_sha256": "0" * 64}, "unread"),
    ],
)
def test_couplers_state_branches(record: dict[str, Any], submission: dict[str, Any], want: str) -> None:
    state = qd_platform.couplers_state(submission, CHIP, lambda: record)
    require(state["couplers_checked"] == want, 'state["couplers_checked"] == want')
    require(
        state["architecture_source"] == submission["architecture_source"],
        'state["architecture_source"] == submission["architecture_source"]',
    )


def collect_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, record: dict[str, Any]) -> Path:
    case = tmp_path / "job-00"
    case.mkdir()
    for name in ("cases.json", "circuit.json"):
        shutil.copy(OFFCONE / name, case / name)
    manifest, _, digest = qd_platform.load_case(case)
    receipt = {
        "schema": qd_platform.SUBMISSION_SCHEMA,
        "cases_sha256": digest,
        "job_id": "job-a",
        "platform": CHIP,
        **submission_for(),
    }
    (case / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")

    def request(method: str, route: str, auth: bool = True, body: Any = None, raw: bool = False) -> Any:
        if route.endswith("/status"):
            return {"status": "completed", "shots": 10}
        if route.endswith("/data"):
            return {"job_id": "job-a"}
        if route.endswith("/result"):
            return b"{}"
        if route == qd_platform.platform_route(CHIP):
            return record
        if route == "/api/tokens/usage/report":
            return []
        raise AssertionError(route)

    monkeypatch.setattr(qd_platform, "request", request)
    monkeypatch.setattr(qd_platform, "result_summary", lambda *a, **k: {"samples": 1})
    require(manifest["platforms"] == [CHIP], 'manifest["platforms"] == [CHIP]')
    return case


@pytest.mark.parametrize(("blob", "want"), [(RETAINED, "live-match"), (None, "unread")])
def test_collect_writes_couplers_checked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, blob: str | None, want: str
) -> None:
    case = collect_fixture(tmp_path, monkeypatch, live(blob))
    collected = qd_platform.collect(case, 0.0, 5.0)
    require(
        collected["couplers_checked"] == want and collected["architecture_source"] == "carried",
        'collected["couplers_checked"] == want and collected["architecture_source"] == "carried"',
    )
    require(
        json.loads((case / "results.json").read_text(encoding="utf-8"))["couplers_checked"] == want,
        'json.loads((case / "results.json").read_text(encoding="utf-8"))["couplers_checked"] == want',
    )


def test_collect_fails_on_differing_live_couplers_after_retaining_the_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = collect_fixture(tmp_path, monkeypatch, live(OTHER))
    with pytest.raises(qd_platform.PlatformError, match="live-differ"):
        qd_platform.collect(case, 0.0, 5.0)
    require((case / "raw/result.json").read_bytes() == b"{}", '(case / "raw/result.json").read_bytes() == b"{}"')
    require(
        json.loads((case / "results.json").read_text(encoding="utf-8"))["couplers_checked"] == "live-differ",
        'json.loads((case / "results.json").read_text(encoding="utf-8"))["couplers_checked"] == "live-differ"',
    )
    with pytest.raises(qd_platform.PlatformError, match="live-differ"):
        qd_platform.collect(case, 0.0, 5.0)


def test_the_reader_refuses_live_differ_and_an_unchecked_carried_run() -> None:
    check = qd_records.check_couplers
    carried = {"architecture_source": "carried"}
    check("run", submission_for(), {**carried, "couplers_checked": "live-match"})
    check("run", submission_for(), {**carried, "couplers_checked": "unread", "compiled_couplers_checked": "match"})
    check("run", {}, {})
    for collected in (
        {**carried, "couplers_checked": "live-differ"},
        carried,
        {"architecture_source": "live", "couplers_checked": "unread"},
        {**carried, "couplers_checked": "unread", "compiled_couplers_checked": "differ"},
    ):
        with pytest.raises(qd_records.RecordError):
            check("run", submission_for(), collected)


# ---- coupler identity, strict field, recollection and plan() integration ----

ELEMENTS = mesh.decode(RETAINED)
MUTANT = "mutant-architecture"


def mutated(kind: str) -> list[Any]:
    """The retained architecture's elements with one phase-shifter or ordering change."""
    out = list(ELEMENTS)
    index = next(i for i, e in enumerate(out) if e[0] == "ps")
    k, m, p = out[index]
    if kind == "ps-mode":
        out[index] = (k, m + 1, p)
    elif kind == "ps-symbol":
        out[index] = (k, m, str(p) + "x")
    else:
        require(out[index - 1][0] == "bs" and out[index - 1] != out[index], "an adjacent coupler precedes the phase")
        out[index - 1], out[index] = out[index], out[index - 1]
    return out


@pytest.fixture
def mutant(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> str:
    """MUTANT decodes to the retained architecture with the requested change; every other text decodes as before."""
    real = mesh.decode
    elements = mutated(request.param)
    monkeypatch.setattr(mesh, "decode", lambda text: elements if text == MUTANT else real(text))
    return MUTANT


MUTANT_KINDS = pytest.mark.parametrize("mutant", ["ps-mode", "ps-symbol", "order"], indirect=True)


@MUTANT_KINDS
def test_couplers_differ_reads_phase_shifter_modes_symbols_and_order(mutant: str) -> None:
    require(qd_platform.couplers_differ(mutant), "qd_platform.couplers_differ(mutant)")
    require(not qd_platform.couplers_differ(RETAINED), "not qd_platform.couplers_differ(RETAINED)")
    with pytest.raises(qd_platform.PlatformError, match="differs from the retained catalogue"):
        qd_platform.live_architecture(live(mutant), CHIP)
    state = qd_platform.couplers_state(submission_for(), CHIP, lambda: live(mutant))
    require(state["couplers_checked"] == "live-differ", 'state["couplers_checked"] == "live-differ"')


@pytest.mark.parametrize("blob", [123, ["a"], {"x": 1}, True, 0.5, ""])
def test_a_present_architecture_that_is_not_a_non_empty_string_refuses(blob: Any) -> None:
    with pytest.raises(qd_platform.PlatformError, match="specs.architecture"):
        qd_platform.chip_architecture(live(blob))
    with pytest.raises(qd_platform.PlatformError, match="specs.architecture"):
        qd_platform.live_architecture(live(blob), CHIP)
    with pytest.raises(qd_platform.PlatformError, match="specs.architecture"):
        qd_platform.couplers_state(submission_for(), CHIP, lambda: live(blob))


def test_an_absent_or_null_architecture_is_no_architecture() -> None:
    records: tuple[Any, ...] = ({}, {"specs": {}}, {"specs": None}, {"specs": {"architecture": None}}, "x")
    for record in records:
        require(qd_platform.chip_architecture(record) is None, "qd_platform.chip_architecture(record) is None")


def plan_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, record: dict[str, Any]) -> Path:
    case = tmp_path / "job-00"
    case.mkdir(parents=True)
    for name in ("cases.json", "circuit.json"):
        shutil.copy(OFFCONE / name, case / name)
    row = {"status": "available", "max_duration": 300, "price_per_shot": 1e-6, "type": "qpu"}
    counters = {"max_concurrent_jobs": 1, "max_jobs_in_queue": 1, "num_concurrent_jobs": 0, "num_jobs_in_queue": 0}
    built = {"estimated_shots": 1, "body": {}, "versions": {}, "payload_version_basis": "declared"}
    monkeypatch.setattr(qd_platform, "explorer_row", lambda platform: row)
    monkeypatch.setattr(qd_platform, "get", lambda route, auth=True: record)
    monkeypatch.setattr(qd_platform, "availability", lambda: counters)
    monkeypatch.setattr(qd_platform, "payload", lambda *a, **k: built)
    return case


def test_plan_records_the_architecture_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for blob, source in ((RETAINED, "live"), (None, "carried")):
        case = plan_fixture(tmp_path / str(source), monkeypatch, live(blob))
        planned = qd_platform.plan(case, CHIP, 1.12, 100.0, 1.0)
        require(planned["architecture_source"] == source, 'planned["architecture_source"] == source')
        require(
            planned["architecture_sha256"] == hashlib.sha256(RETAINED.encode()).hexdigest(),
            "the plan records the retained architecture digest",
        )


@MUTANT_KINDS
def test_plan_refuses_a_live_architecture_with_other_phase_shifters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutant: str
) -> None:
    case = plan_fixture(tmp_path, monkeypatch, live(mutant))
    with pytest.raises(qd_platform.PlatformError, match="differs from the retained catalogue"):
        qd_platform.plan(case, CHIP, 1.12, 100.0, 1.0)


RETAINED_RUN = ROOT / "results/quandela/cases/belenos_offcone_mechanisms/job-00"


def copied_run(tmp_path: Path) -> Path:
    run = tmp_path / "job-00"
    shutil.copytree(RETAINED_RUN, run)
    return run


def edit_collection(run: Path, **changes: Any) -> None:
    path = run / "results.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    record.update(changes)
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def test_validate_run_reads_the_coupler_fields_of_a_retained_run(tmp_path: Path) -> None:
    run = copied_run(tmp_path)
    require(qd_records.read_run(run).facts["couplers_checked"] == "unread", "the retained run reads unread")
    for changes in (
        {"couplers_checked": "live-differ"},
        {"couplers_checked": None},
        {"architecture_source": "live"},
        {"compiled_couplers_checked": "differ"},
    ):
        edit_collection(run, **changes)
        with pytest.raises(qd_records.RecordError, match="couplers_checked|architecture_source"):
            qd_records.read_run(run)
        shutil.copy(RETAINED_RUN / "results.json", run / "results.json")


def test_validate_run_surfaces_the_compiled_coupler_check(tmp_path: Path) -> None:
    run = copied_run(tmp_path)
    edit_collection(run, compiled_couplers_checked="match")
    require(qd_records.read_run(run).facts["compiled_couplers_checked"] == "match", "facts name the compiled check")


def result_bytes_of_job() -> bytes:
    return (RETAINED_RUN / "raw/result.json").read_bytes()


def test_the_retained_runs_compiled_couplers_match_the_planned_architecture() -> None:
    for job in ("job-00", "job-01", "job-02"):
        run = OFFCONE.parent / job
        submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
        state = qd_platform.compiled_couplers_state(submission, (run / "raw/result.json").read_bytes())
        require(state == "match", f"{job} compiled couplers read {state}")


def test_compiled_couplers_read_unread_without_a_comparable_result_or_plan() -> None:
    submission = {**submission_for(), "platform": CHIP}
    for result in (None, b"{}", b"not json", b'{"results": "[]"}', b'{"results": "{}"}'):
        state = qd_platform.compiled_couplers_state(submission, result)
        require(state == "unread", f"{result!r} reads {state}")
    other = {**submission, "architecture_sha256": "0" * 64}
    require(
        qd_platform.compiled_couplers_state(other, result_bytes_of_job()) == "unread", "an unplanned digest is unread"
    )


@pytest.fixture
def changed_compiled_bs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every returned computed_circuit decodes with its first coupler angle moved by 1e-3."""
    real = mesh.decode

    def decode(text: str) -> list[Any]:
        elements = real(text)
        if not mesh.unzip(text).startswith(":PCVL:ACircuit:"):
            return elements
        index = next(i for i, e in enumerate(elements) if e[0] == "bs")
        k, m, p = elements[index]
        return [*elements[:index], (k, m, (p[0] + 1e-3, *p[1:])), *elements[index + 1 :]]

    monkeypatch.setattr(mesh, "decode", decode)


def test_a_changed_compiled_coupler_reads_differ(changed_compiled_bs: None) -> None:
    run = OFFCONE
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    state = qd_platform.compiled_couplers_state(submission, result_bytes_of_job())
    require(state == "differ", f"a moved coupler reads {state}")


def collect_real_result(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, record: dict[str, Any]) -> Path:
    case = collect_fixture(tmp_path, monkeypatch, record)
    real = qd_platform.request

    def request(method: str, route: str, auth: bool = True, body: Any = None, raw: bool = False) -> Any:
        return result_bytes_of_job() if route.endswith("/result") else real(method, route, auth, body, raw)

    monkeypatch.setattr(qd_platform, "request", request)
    return case


def test_collect_records_the_compiled_coupler_check(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    case = collect_real_result(tmp_path, monkeypatch, live(None))
    collected = qd_platform.collect(case, 0.0, 5.0)
    require(collected["compiled_couplers_checked"] == "match", 'collected["compiled_couplers_checked"] == "match"')
    stored = json.loads((case / "results.json").read_text(encoding="utf-8"))
    require(stored["compiled_couplers_checked"] == "match", "the record keeps the compiled check")


def test_collect_fails_on_changed_compiled_couplers_after_keeping_the_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, changed_compiled_bs: None
) -> None:
    case = collect_real_result(tmp_path, monkeypatch, live(None))
    with pytest.raises(qd_platform.PlatformError, match="compiled_couplers_checked differ"):
        qd_platform.collect(case, 0.0, 5.0)
    require((case / "raw/result.json").read_bytes() == result_bytes_of_job(), "the raw bytes are kept")
    stored = json.loads((case / "results.json").read_text(encoding="utf-8"))
    require(stored["compiled_couplers_checked"] == "differ", "the record keeps differ")


def test_a_recollection_cannot_replace_a_fresh_live_differ_with_a_retained_unread(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = collect_fixture(tmp_path, monkeypatch, live(None))
    require(qd_platform.collect(case, 0.0, 5.0)["couplers_checked"] == "unread", "the first read is unread")
    request = qd_platform.request

    def other_chip(method: str, route: str, auth: bool = True, body: Any = None, raw: bool = False) -> Any:
        return live(OTHER) if route == qd_platform.platform_route(CHIP) else request(method, route, auth, body, raw)

    monkeypatch.setattr(qd_platform, "request", other_chip)
    with pytest.raises(qd_platform.PlatformError, match="live-differ"):
        qd_platform.collect(case, 0.0, 5.0)
    stored = json.loads((case / "results.json").read_text(encoding="utf-8"))
    require(stored["couplers_checked"] == "live-differ", "the record now reads live-differ")
    monkeypatch.setattr(qd_platform, "request", request)
    with pytest.raises(qd_platform.PlatformError, match="live-differ"):
        qd_platform.collect(case, 0.0, 5.0)


def test_a_recollection_keeps_a_read_state_when_the_platform_omits_the_field(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = collect_fixture(tmp_path, monkeypatch, live(RETAINED))
    require(qd_platform.collect(case, 0.0, 5.0)["couplers_checked"] == "live-match", "the first read matches")
    request = qd_platform.request

    def omitted(method: str, route: str, auth: bool = True, body: Any = None, raw: bool = False) -> Any:
        return live(None) if route == qd_platform.platform_route(CHIP) else request(method, route, auth, body, raw)

    monkeypatch.setattr(qd_platform, "request", omitted)
    require(qd_platform.collect(case, 0.0, 5.0)["couplers_checked"] == "live-match", "a read state is kept")


@MUTANT_KINDS
def test_collect_fails_on_a_live_architecture_with_other_phase_shifters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutant: str
) -> None:
    case = collect_fixture(tmp_path, monkeypatch, live(mutant))
    with pytest.raises(qd_platform.PlatformError, match="live-differ"):
        qd_platform.collect(case, 0.0, 5.0)
    stored = json.loads((case / "results.json").read_text(encoding="utf-8"))
    require(stored["couplers_checked"] == "live-differ", 'stored["couplers_checked"] == "live-differ"')
