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


def unconditional_half_first(arm: tuple, pair: lad.Pair, frame_sign: float = 1.0) -> list[dict]:
    """pair_ladder_ops with Bob's unconditional prx moved ahead of the cc_prx, the order ASAP plays early."""
    ops = lad.pair_ladder_ops(arm, pair, frame_sign=frame_sign)
    for i in range(len(ops) - 1):
        if ops[i]["name"] == "cc_prx" and ops[i + 1]["name"] == "prx" and ops[i + 1]["locus"] == [pair.bob]:
            ops[i], ops[i + 1] = ops[i + 1], ops[i]
            break
    return ops


def test_window_phase_after_readout_needs_the_conditional_half_first(device: lad.Device) -> None:
    deviation = lad.lowering_deviation(first_pair(device), device.timing, PHASES, ops_of=unconditional_half_first)
    if deviation < 1e-3:
        raise AssertionError(f"splitting Bob's rotation around the readout window passes with {deviation}")


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


def test_passive_reset_starts_in_the_ground_state_and_runs_longer(device: lad.Device) -> None:
    pair = first_pair(device)
    if any(v != 0.0 for v in lad.noise_of(device, pair, False, passive=True).init.values()):
        raise AssertionError("passive reset carries an initial excitation beside the unheralded readout errors")
    active = lad.shot_seconds_of(device, [pair], False, lad.IDLE_CC_ANGLE)
    passive = lad.shot_seconds_of(device, [pair], False, lad.IDLE_CC_ANGLE, passive=True)
    if not math.isclose(passive - active, lad.PASSIVE_SHOT_SECONDS - lad.SHOT_BASE_SECONDS, rel_tol=1e-12):
        raise AssertionError(f"passive shot {passive} against active {active}")


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
    if case["jobs"][0]["max_credits"]["garnet"] > 8.0 or case["jobs"][1]["max_credits"] != {"garnet:mock": 0.0}:
        raise AssertionError("the credit ceilings leave the approved plan")
    # Bob's drive takes Alice's feedback label, and the station admits one label per drive AWG per segment.
    for job in case["jobs"]:
        if job["options"]["active_reset_cycles"] is not None or job["options"]["heralding_mode"] != "none":
            raise AssertionError(f"{job['job']} runs active reset or heralding beside cc_prx feedback")
    names = {Path(e["file"]).stem for e in case["jobs"][0]["circuits"]}
    if names != set(lad.arm_names()) or len(names) != 24:
        raise AssertionError(f"circuits {sorted(names)}")


def case_shots() -> int:
    """The ladder job's shots: an unheralded run returns exactly that many per circuit."""
    return int(json.loads((CASE / "cases.json").read_text(encoding="utf-8"))["jobs"][0]["shots"])


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
                "shots_per_circuit": [shots] * 24,
            }
        )
    )
    return run


def test_analysis_recovers_the_ideal_endpoints_from_synthetic_bits(tmp_path: Path) -> None:
    run = synthetic_run(tmp_path, case_shots())
    result = lad.analyze([run])
    ideal = json.loads((CASE / "cases.json").read_text(encoding="utf-8"))["ideal"]
    for name in lad.ENDPOINTS:
        got = result["pooled"][name]["mean"]
        # Synthetic counts round every outcome to the nearest shot, so the recovery error falls as 1/shots;
        # endpoints_of_run is checked exactly against the counts in --self-test.
        if abs(got - ideal["endpoints"][name]) > 10 / case_shots():
            raise AssertionError(f"{name}: recovered {got}, ideal {ideal['endpoints'][name]}")
    for name, p1 in ideal["qualification_p1"].items():
        low, high = result["qualification"][name]["wilson95"]
        if not low - 1e-6 <= p1 <= high + 1e-6:
            raise AssertionError(f"{name}: {p1} outside {low}..{high}")


def pair_endpoints(case: dict, measurements: list, index: int) -> dict:
    """One pair's endpoints from an artifact, without the shot-noise variance endpoints_of_run adds."""
    names = [Path(c["file"]).stem for c in case["jobs"][0]["circuits"]]
    by_name = dict(zip(names, measurements, strict=True))
    counts = {name: lad.ladder_counts(by_name[name], index) for name in lad.arm_table()}
    return lad.summarize({f"{lad.GROUP}_{name}": c / c.sum() for name, c in counts.items()})


def test_analysis_maps_each_pair_and_key_to_its_own_law() -> None:
    """Counts drawn from each pair's predicted noisy law, where the second Alice readout differs from the first,
    recover that pair's predicted endpoints; swapping the alice and afinal keys or two pairs moves them."""
    case = json.loads((CASE / "cases.json").read_text(encoding="utf-8"))
    prediction = json.loads((CASE / "prediction.json").read_text(encoding="utf-8"))
    laws = [row["laws"] for row in prediction["pairs"]]
    measurements, _ = lad.synthetic_measurements(case, 5000, laws)
    for pair, row in zip(case["pairs"], prediction["pairs"], strict=True):
        got = pair_endpoints(case, measurements, pair["index"])
        for name in lad.ENDPOINTS:
            if abs(got[name] - row["endpoints"][name]) > 4e-3:
                raise AssertionError(f"{row['pair']}: {name} {got[name]} against {row['endpoints'][name]}")
    swapped = [{**c, "alice0": c["afinal0"], "afinal0": c["alice0"]} if "afinal0" in c else c for c in measurements]
    # Bob's rotation follows the recorded bit, so the feedback energy, read through Alice's final bit,
    # changes when the two readouts trade places.
    moved = pair_endpoints(case, swapped, 0)["selected_excess"]
    if abs(moved - pair_endpoints(case, measurements, 0)["selected_excess"]) < 1e-3:
        raise AssertionError("swapping Alice's two readouts leaves the information excess unchanged")
    pairs_swapped = [
        {
            **c,
            **{f"{k}0": c[f"{k}1"] for k in ("alice", "afinal", "bob") if f"{k}1" in c},
            **{f"{k}1": c[f"{k}0"] for k in ("alice", "afinal", "bob") if f"{k}0" in c},
        }
        for c in measurements
    ]
    first = pair_endpoints(case, pairs_swapped, 0)["selected_margin"]
    if abs(first - prediction["pairs"][0]["endpoints"]["selected_margin"]) < 5e-3:
        raise AssertionError("swapping two pairs' keys leaves pair 0's margin at its own prediction")


def test_a_cc_prx_that_never_fires_lowers_the_all_pairs_excess() -> None:
    """A pair whose cc_prx never fires runs the fixed -phi* rotation, a record-independent unitary, so its excess
    falls to the unitary floor's and the all-pairs H1 mean drops below the ideal."""
    case = json.loads((CASE / "cases.json").read_text(encoding="utf-8"))
    table = lad.arm_table()
    ideal = {name: list(ql.compensated_ideal(*arm[1:])) for name, arm in table.items()}
    broken = {
        name: list(ql.compensated_ideal(arm[1], arm[2], "plus" if arm[3] == "feedback" else arm[3], arm[4], arm[5]))
        for name, arm in table.items()
    }
    laws = [broken if pair["index"] == 0 else ideal for pair in case["pairs"]]
    measurements, _ = lad.synthetic_measurements(case, 5000, laws)
    result = lad.endpoints_of_run(case, measurements)
    if result["pairs"][0]["endpoints"]["selected_excess"] > 1e-3:
        raise AssertionError(f"a never-firing cc_prx keeps excess {result['pairs'][0]['endpoints']['selected_excess']}")
    primary = result["decisions"]["all_pairs"]["h1_information_excess"]
    if not primary["mean"] < ql.E_B - 0.02 or primary["pairs"] != len(case["pairs"]):
        raise AssertionError(f"the all-pairs H1 test does not carry the broken pair: {primary}")


def test_analysis_refuses_a_mock_run(tmp_path: Path) -> None:
    run = synthetic_run(tmp_path, case_shots())
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    submission["qc"] = "garnet:mock"
    (run / "submission.json").write_text(iqm_jobs.dump(submission))
    with pytest.raises(ValueError, match="analysis reads"):
        lad.analyze([run])


@pytest.mark.audit
def test_retained_case_matches_its_build() -> None:
    lad.check(CASE)
