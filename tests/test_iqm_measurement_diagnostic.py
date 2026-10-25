"""The unitary-arm diagnostic case: the pair product, the circuits, the model and the three decision patterns."""

from pathlib import Path

import iqm_measurement_diagnostic as case


def test_self_test_holds() -> None:
    if "measurement diagnostic" not in case.self_test():
        raise AssertionError("the self-test summary changed")


def test_retained_case_checks_and_rebuilds(tmp_path: Path) -> None:
    retained = case.ROOT / "results/iqm/cases" / case.CASE
    case.check(retained)
    excerpt = case.seq.load_json(retained / case.EXCERPT)
    for name, text in case.build_files(excerpt).items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    case.check(tmp_path)
