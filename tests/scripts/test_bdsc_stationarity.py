import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]

import bdsc_stationarity as st  # noqa: E402


def test_requests_equal_their_sources_apart_from_the_budgets() -> None:
    found = st.sources()
    for job in st.JOBS:
        manifest = json.loads((st.CASES_DIR / job / "cases.json").read_text())
        source = found[job]["manifest"]
        if st.request_differences(manifest, source) or manifest["settings"] != source["settings"]:
            raise AssertionError(job)
        if manifest["max_samples"] != st.TRIALS * len(source["settings"]):
            raise AssertionError(manifest["max_samples"])
        edited = {**manifest, "mitigations": ["DetectorBalancing"]}
        if st.request_differences(edited, source) != ["mitigations"]:
            raise AssertionError("an edited policy reads equal to the source")


def test_case_record_prices_each_job_within_the_per_job_ceiling() -> None:
    record = json.loads(st.CASE.read_text())
    resources = record["resources"]
    if not (resources["credits_per_job"] <= 1.2 and max(resources["seconds_per_job_estimate"].values()) < 300):
        raise AssertionError(resources)


def test_plan_check_requires_mode_5_above_every_other_mode() -> None:
    rates = [10.0] * 24
    rates[st.STRAY] = 3000.0
    if st.dark_rates({st.DARK: rates}, "plan")[st.STRAY] != 3000.0:
        raise AssertionError("a dominant mode 5 is refused")
    rates[3] = 3000.0
    try:
        st.dark_rates({st.DARK: rates}, "plan")
    except ValueError:
        return
    raise AssertionError("a tie with another mode passes")


def test_excess_variance_recovers_zero_and_an_injected_variance() -> None:
    rng = np.random.default_rng(7)
    se = 0.003
    flat = [(float(v), se) for v in rng.normal(0.0, se, 400)]
    zero = st.class_excess_variance(flat)
    if zero["tau2_interval_95"][0] != 0.0:
        raise AssertionError(zero)
    tau = 0.004
    spread = [(float(v), se) for v in rng.normal(0.0, math.hypot(se, tau), 400)]
    read = st.class_excess_variance(spread)
    low, high = read["tau2_interval_95"]
    if not (low <= tau**2 <= high and low <= read["tau2"] <= high):
        raise AssertionError(read)


def test_batched_projection_returns_the_scalar_bits() -> None:
    rng = np.random.default_rng(11)
    items = []
    for n, k in ((48, 3), (7, 7), (12, 1)):
        se = [float(v) for v in rng.uniform(1e-4, 5e-3, n)]
        classes = [i % k for i in range(n)]
        tau2 = [0.0 if c == 0 else float(rng.uniform(0.0, 1e-5)) for c in classes]
        draws = rng.standard_normal((300, n))
        draws[0] = 0.0
        draws[1] = 37.5
        items.append((se, classes, tau2, draws))
    for item in items:
        scalar, batched = st._projected_q(item), st._projected_q_batch(item)
        if [q.hex() for q in scalar] != [q.hex() for q in batched]:
            differing = sum(a != b for a, b in zip(scalar, batched, strict=True))
            raise AssertionError(f"{differing} of {len(scalar)} replicates differ")


def test_calibration_contrast_changes_read_a_common_shift_per_class() -> None:
    indices = [i["index"] for i in st.diag.instances() if i["job"] == "b1-j1"]
    before = {i: {"selected": 40000, "eligible": 100000, "circuit_sha256": "a"} for i in indices}
    after = {i: {"selected": 41000, "eligible": 100000, "circuit_sha256": "a"} for i in indices}
    changes = st.instance_changes(before, after)
    if len(changes) != 24 or not all(abs(c["change"] - 0.01) < 1e-12 for c in changes):
        raise AssertionError(changes)
    shifts = st.class_shifts(changes)
    if not all(abs(s["mean"] - 0.01) < 1e-12 and s["z"] > 3 for s in shifts.values()):
        raise AssertionError(shifts)
    try:
        st.instance_changes(before, {i: after[i] for i in indices[1:]})
    except ValueError:
        return
    raise AssertionError("runs with different instances pass")


def test_group_by_block_reads_the_sign_of_a_slot_effect() -> None:
    first_job = {(i["template"], i["slot"]): i["job"] for i in st.diag.instances() if i["block"] == 1}
    changes = [
        {
            "template": template,
            "slot": slot,
            "label": label,
            "change": 0.01 if job == "b1-j1" else 0.0,
            "se": 0.003,
            "same_returned_circuit": True,
        }
        for (template, slot), job in first_job.items()
        for label in st.diag.SUPERPOSITIONS
    ]
    read = st.group_by_block(changes)
    if not (abs(read["contrast"] - 0.01) < 1e-12 and read["z"] > 3):
        raise AssertionError(read)
