"""The Garnet QET ladder lowers to native operations that reproduce qet_ladder's laws, and its case replays."""

from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import iqm_jobs
import iqm_qet_ladder as lad
import numpy as np
import pytest

import qet_ladder as ql

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "results/iqm/cases/qet-compensated-ladder"
PHASES = (0.0, 0.7, -0.4)


@pytest.fixture(scope="module")
def device(tmp_path_factory: pytest.TempPathFactory) -> lad.Device:
    folder = tmp_path_factory.mktemp("calibration")
    lad.prepare_calibration(lad.EVIDENCE_CALIBRATION, folder)
    return lad.load_device(str(folder))


def first_pair(device: lad.Device) -> lad.Pair:
    return lad.Pair(0, "QB1", "QB2", device.loci[frozenset(("QB1", "QB2"))])


def test_prx_is_qiskit_rgate() -> None:
    from qiskit.circuit.library import RGate
    from qiskit.quantum_info import Operator

    for theta, phi in ((0.3, 0.7), (math.pi, -1.1), (2.2, 3.0), (-0.6, 1.2)):
        if np.abs(lad.rgate(theta, phi) - Operator(RGate(theta, phi)).data).max() > 1e-14:
            raise AssertionError(f"prx({theta}, {phi}) differs from RGate")


def test_lowered_arms_equal_compensated_ideal(device: lad.Device) -> None:
    deviation = lad.lowering_deviation(first_pair(device), device.timing, PHASES)
    if deviation > 1e-12:
        raise AssertionError(f"lowered arms depart from compensated_ideal by {deviation}")


def test_flipped_frame_sign_fails_the_check(device: lad.Device) -> None:
    deviation = lad.lowering_deviation(first_pair(device), device.timing, PHASES, frame_sign=-1.0)
    if deviation < 1e-3:
        raise AssertionError(f"a flipped virtual-Z frame sign passes with deviation {deviation}")


def test_two_pi_idle_angle_keeps_the_laws(device: lad.Device) -> None:
    pair = first_pair(device)
    for arm in lad.arm_table().values():
        ops = lad.pair_ladder_ops(arm, pair, lad.IDLE_CC_ANGLE_FALLBACK)
        law = lad.qiskit_law(ops, pair)
        if np.abs(law - ql.compensated_ideal(*arm[1:])).max() > 1e-12:
            raise AssertionError(f"{arm[0]} changes under a 2 pi idle cc_prx")


def test_zero_noise_simulator_gives_the_qualification_laws(device: lad.Device) -> None:
    pair = first_pair(device)
    expected = {
        "qual_src1_phi": math.sin(ql.PHI_STAR) ** 2,
        "qual_src0_phi": 0.0,
        "qual_src1_pi": 1.0,
        "qual_src0_pi": 0.0,
    }
    for arm, p1 in expected.items():
        joint = lad.simulate_pair(lad.pair_qual_ops(arm, pair), pair, device.timing, lad.Noise.ideal(pair))
        if abs(float(joint[:, 1].sum()) - p1) > 1e-12:
            raise AssertionError(f"{arm} reads {joint[:, 1].sum()}, not {p1}")


def test_relaxation_channel_equals_the_aer_pass(device: lad.Device) -> None:
    error = lad.aer_relaxation_error(device)
    if error > 1e-9:
        raise AssertionError(f"relaxation_kraus differs from the Aer pass by {error}")


def test_noisy_laws_are_distributions_and_feedback_wait_is_equal(device: lad.Device) -> None:
    pair = first_pair(device)
    noise = lad.noise_of(device, pair, True)
    ends = set()
    for name, arm in lad.arm_table().items():
        ops = lad.pair_ladder_ops(arm, pair)
        law = lad.flat_law(lad.simulate_pair(ops, pair, device.timing, noise))
        if abs(sum(law) - 1) > 1e-12 or min(law) < -1e-15:
            raise AssertionError(f"{name}: the noisy law is not a distribution")
        starts, _ = lad.schedule(ops, device.timing)
        cc = [s for o, s in zip(ops, starts, strict=True) if o["name"] == "cc_prx"]
        measure = [s for o, s in zip(ops, starts, strict=True) if o["name"] == "measure"]
        if len(cc) != 1:
            raise AssertionError(f"{name}: {len(cc)} cc_prx")
        ends.add(round(cc[0] - measure[0], 12))
    # The wait from Alice's measure start to Bob's cc_prx is the measure window plus the control delay in every arm.
    window = sum(device.timing.measure[pair.alice]) + device.timing.control[pair.bob]
    if ends != {round(window, 12)}:
        raise AssertionError(f"feedback waits {sorted(ends)} differ from {window}")


def test_variance_scales_with_shots_and_is_positive(device: lad.Device) -> None:
    pair = first_pair(device)
    noise = lad.noise_of(device, pair, True)
    laws = {
        name: lad.flat_law(lad.simulate_pair(lad.pair_ladder_ops(arm, pair), pair, device.timing, noise))
        for name, arm in lad.arm_table().items()
    }
    dist = lad.dist_of(laws)
    one, many = lad.endpoint_variance(dist, 1.0), lad.endpoint_variance(dist, 1000.0)
    for name in lad.ENDPOINTS:
        if not one[name] > 0 or abs(one[name] / 1000.0 - many[name]) > 1e-12:
            raise AssertionError(f"{name}: variance {one[name]} at 1 shot, {many[name]} at 1000")


def test_induced_matchings_share_no_qubit_or_coupler() -> None:
    edges = [("A", "B"), ("C", "D"), ("B", "C"), ("E", "F")]
    found = {tuple(sorted(m)) for m in lad.induced_matchings(edges)}
    if (0, 1) in found or (0, 2) in found:
        raise AssertionError(f"{found} holds pairs joined by a coupler or sharing a qubit")
    if (0, 3) not in found or (1, 3) not in found or (0, 1, 3) in found:
        raise AssertionError(f"{found} misses a disjoint induced matching")


def test_wilson_interval_matches_scipy() -> None:
    from scipy import stats

    for ones, n in ((0, 500), (50, 500), (500, 500), (7, 30)):
        want = stats.binomtest(ones, n).proportion_ci(method="wilson")
        low, high = lad.wilson(ones, n)
        if abs(low - want.low) > 1e-9 or abs(high - want.high) > 1e-9:
            raise AssertionError(f"wilson({ones}, {n}) = {(low, high)}, scipy {(want.low, want.high)}")


def test_retained_case_is_native_and_within_its_credit_ceiling() -> None:
    case = json.loads((CASE / "cases.json").read_text(encoding="utf-8"))
    device = lad.load_device(str(CASE / "calibration"))
    pairs = [lad.pair_of(p) for p in case["pairs"]]
    for entry in case["jobs"][0]["circuits"]:
        circuit = json.loads((CASE / entry["file"]).read_text(encoding="utf-8"))
        lad.validate_circuit(circuit, device, pairs)
    for job in case["jobs"]:
        _, row, _ = iqm_jobs.load_job(CASE, job["job"])
        for qc, credits in row["max_credits"].items():
            if qc == "garnet" and iqm_jobs.ceiling_credits(row["expected_seconds"], lad.PRICE[qc]) > credits:
                raise AssertionError(f"{job['job']} expects more than {credits} credits on {qc}")
    if case["jobs"][0]["max_credits"]["garnet"] > 4.0 or case["jobs"][1]["max_credits"] != {"garnet:mock": 0.0}:
        raise AssertionError("the credit ceilings leave the approved plan")
    names = {Path(e["file"]).stem for e in case["jobs"][0]["circuits"]}
    if names != set(lad.arm_names()) or len(names) != 22:
        raise AssertionError(f"circuits {sorted(names)}")


def synthetic_run(tmp: Path, shots: int) -> Path:
    run = tmp / "2026-10-26T000000Z-garnet-qet-compensated-ladder-ladder"
    shutil.copytree(CASE, run)
    case = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    measurements, _ = lad.synthetic_measurements(case, shots)
    raw = run / "raw"
    raw.mkdir()
    job = {
        "id": "job-1",
        "status": "completed",
        "metrics": {"billed_seconds": 3.0, "runtime_seconds": 2.5},
        "compilation": {
            "calibration_set_id": case["jobs"][0]["options"]["calibration_set_id"]["garnet"],
            "execution_runtime_estimate_seconds": 5.0,
        },
    }
    files = {
        "job.json": json.dumps(job).encode(),
        "measurements.json": json.dumps(measurements).encode(),
        "measurement_counts.json": b"[]",
    }
    for name, data in files.items():
        (raw / name).write_bytes(data)
    cases_sha = lad.sha256((run / "cases.json").read_bytes())
    (run / "submission.json").write_text(
        iqm_jobs.dump(
            {
                "schema": iqm_jobs.SUBMISSION_SCHEMA,
                "job_id": "job-1",
                "qc": "garnet",
                "job": "ladder",
                "cases_sha256": cases_sha,
                "approval": "approved in test",
                "price_per_second": 0.5,
                "submitted_at": "2026-10-26T00:00:00Z",
            }
        )
    )
    (run / "results.json").write_text(
        iqm_jobs.dump(
            {
                "schema": iqm_jobs.RESULTS_SCHEMA,
                "job_id": "job-1",
                "status": "completed",
                "raw_sha256": {n: lad.sha256(d) for n, d in files.items()},
                "shots_per_circuit": [shots] * 22,
            }
        )
    )
    return run


def test_analysis_recovers_the_ideal_endpoints_from_synthetic_bits(tmp_path: Path) -> None:
    run = synthetic_run(tmp_path, 4000)
    result = lad.analyze([run])
    ideal = json.loads((CASE / "cases.json").read_text(encoding="utf-8"))["ideal"]
    for name in lad.ENDPOINTS:
        got = result["pooled"][name]["mean"]
        if abs(got - ideal["endpoints"][name]) > 2e-3:
            raise AssertionError(f"{name}: recovered {got}, ideal {ideal['endpoints'][name]}")
    for name, p1 in ideal["qualification_p1"].items():
        low, high = result["qualification"][name]["wilson95"]
        if not low - 1e-6 <= p1 <= high + 1e-6:
            raise AssertionError(f"{name}: {p1} outside {low}..{high}")
    if lad.dump(lad.analyze([run])) != lad.dump(result):
        raise AssertionError("the analysis does not replay")


def test_analysis_refuses_a_mock_run(tmp_path: Path) -> None:
    run = synthetic_run(tmp_path, 400)
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    submission["qc"] = "garnet:mock"
    (run / "submission.json").write_text(iqm_jobs.dump(submission))
    with pytest.raises(ValueError, match="analysis reads"):
        lad.analyze([run])


@pytest.mark.audit
def test_retained_case_matches_its_build() -> None:
    lad.check(CASE)
