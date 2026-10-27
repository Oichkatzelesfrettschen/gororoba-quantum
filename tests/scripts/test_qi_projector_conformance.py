"""The preregistered QX tolerances reject deviations without rounding counts."""

from typing import Any

from qi_projector_conformance import replay, screen


def ideal_reports() -> dict[str, Any]:
    return {
        "geometry-z.cq": {
            "replicas": [{"herald_count": 1024, "joint_zero_count": value} for value in (1024, 768, 512)]
        },
        "mutation-z.cq": {"replicas": [{"herald_count": 1024, "joint_zero_count": 1024} for _ in range(3)]},
        "geometry-x.cq": {"replicas": [{"herald_count": 1024, "signed_joint_sum": value} for value in (0, 512, 0)]},
    }


def test_probability_threshold_is_exact() -> None:
    reports = ideal_reports()
    reports["geometry-z.cq"]["replicas"][0]["joint_zero_count"] = 1126
    if not all(check["passed"] for check in screen(reports)):
        raise AssertionError("102/2048 lies within 1/20")
    reports["geometry-z.cq"]["replicas"][0]["joint_zero_count"] = 1127
    if all(check["passed"] for check in screen(reports)):
        raise AssertionError("103/2048 lies outside 1/20")


def test_signed_threshold_is_exact() -> None:
    reports = ideal_reports()
    reports["geometry-x.cq"]["replicas"][0]["signed_joint_sum"] = -204
    if not all(check["passed"] for check in screen(reports)):
        raise AssertionError("204/2048 lies within 1/10")
    reports["geometry-x.cq"]["replicas"][0]["signed_joint_sum"] = -205
    if all(check["passed"] for check in screen(reports)):
        raise AssertionError("205/2048 lies outside 1/10")


def test_retained_run_conforms() -> None:
    report = replay()
    if len(report["checks"]) != 18 or not report["passed"] or not report["zero_recorded_charge"]:
        raise AssertionError("retained run fails its frozen conformance or charge check")
