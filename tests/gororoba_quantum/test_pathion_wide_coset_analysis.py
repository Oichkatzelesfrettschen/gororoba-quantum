"""Contracts of the per-placement analysis of a pathion_wide_coset run (scripts/pathion_wide_coset_analysis.py).

A synthetic collect.json holds the group's body laws (each placement's own block) pushed through a different asymmetric
readout channel on every placement, with an archived routed circuit that measures each placement's clbits into
scrambled physical qubits. The script must invert each placement with its own confusion matrices, score each block
against its own ideal law, recover the whole-operand sums, give each estimate a shot-noise interval that matches a
simulation, and report the case's rules.
"""

from __future__ import annotations

import io
import json
import math
from pathlib import Path

import numpy as np
import pathion_wide_coset_analysis as analysis
from qiskit import QuantumCircuit, qpy
from qiskit.circuit import ClassicalRegister, QuantumRegister

import pathion_parallel_coset as ppc
import pathion_wide_coset as pw
import run_archive

GROUP = pw.pathion_wide_coset_group()
IDEAL = {name: law for name, _, law in GROUP.body_templates}
BODIES = {member.name: member.replica_bodies or () for member in GROUP.members}
REPLICAS = pw.PLACEMENTS
PUBS = {name: f"synthetic_pub_{index:02d}" for index, name in enumerate(BODIES)}
SHOTS = 200_000
# Sampling seed of the multinomial draws: index 3 of the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json.
SIMULATION_SEED = 64049
# Physical qubit measured into clbit c of placement r, deliberately out of order.
WRITERS = {r: [10 * r + 3, 10 * r + 1, 10 * r + 2, 10 * r] for r in range(REPLICAS)}
IDEAL_SUM = {"n64": 0, "o64": 28, "m64": -2, "n128": 0, "o128": 60, "m128": -2}


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _calibration() -> dict[str, dict[str, float]]:
    out = {}
    for r in range(REPLICAS):
        for c, qubit in enumerate(WRITERS[r]):
            out[str(qubit)] = {
                "prob_meas1_prep0": 0.004 + 0.0005 * r + 0.001 * c,
                "prob_meas0_prep1": 0.02 + 0.002 * r + 0.005 * c,
                "readout_error": 0.01,
            }
    return out


def _entry(sample: np.random.Generator | None = None) -> dict:
    """The collect entry; with a generator each law is the multinomial sample of SHOTS shots of the channel's law."""
    calibration = _calibration()
    measured = {}
    for name, bodies in BODIES.items():
        laws = []
        for r in range(REPLICAS):
            law = IDEAL[bodies[r]].copy()
            for c, qubit in enumerate(WRITERS[r]):
                values = calibration[str(qubit)]
                law = ppc.apply_readout_clbit(law, c, values["prob_meas1_prep0"], values["prob_meas0_prep1"])
            if sample is not None:
                law = sample.multinomial(SHOTS, law / law.sum()) / SHOTS
            laws.append([float(p) for p in law])
        measured[name] = laws
    executed = {name: {"pub": PUBS[name], "shots": SHOTS, "placed_qubit_calibration": calibration} for name in BODIES}
    return {"group": "pathion_wide_coset", "backend": "synthetic", "measured": measured, "executed": executed}


def _circuit(name: str) -> QuantumCircuit:
    qubits = QuantumRegister(10 * REPLICAS)
    registers = [ClassicalRegister(4, f"g0_r{r}_c") for r in range(REPLICAS)]
    qc = QuantumCircuit(qubits, *registers, name=name)
    for r in range(REPLICAS):
        for c, qubit in enumerate(WRITERS[r]):
            qc.measure(qubits[qubit], registers[r][c])
    return qc


def _writers() -> dict[str, dict[int, list[int]]]:
    return {pub: WRITERS for pub in PUBS.values()}


def _stats(entry: dict, *, corrected: bool) -> dict:
    return analysis.operand_stats(analysis.placement_readings(entry, _writers(), GROUP, corrected=corrected))


def test_replica_writers_read_the_archived_measurement_map_and_confusion_falls_back() -> None:
    _expect(analysis.replica_writers(_circuit("c")) == WRITERS, f"{analysis.replica_writers(_circuit('c'))}")
    _expect(analysis.confusion({"5": {"readout_error": 0.03}}, 5) == (0.03, 0.03), "symmetric fallback")
    _expect(analysis.confusion({"5": {"prob_meas1_prep0": 0.01, "prob_meas0_prep1": 0.02}}, 5) == (0.01, 0.02), "pair")


def test_readout_matrix_is_the_inverse_of_the_channel() -> None:
    e01, e10 = [0.004, 0.006, 0.01, 0.02], [0.02, 0.03, 0.015, 0.05]
    law = IDEAL["wide_o64_k0_minus"]
    noisy = law.copy()
    for c in range(4):
        noisy = ppc.apply_readout_clbit(noisy, c, e01[c], e10[c])
    restored = analysis.readout_matrix(e01, e10) @ noisy
    _expect(float(np.abs(restored - law).max()) < 1e-12, "the matrix does not invert the channel")


def test_per_placement_inversion_recovers_the_ideal_sums_and_the_raw_sums_are_biased() -> None:
    entry = _entry()
    corrected, raw = _stats(entry, corrected=True), _stats(entry, corrected=False)
    for key, value in IDEAL_SUM.items():
        _expect(abs(corrected[f"wide_{key}_nullity_estimate"]["mean"] - value) < 1e-9, f"{key}: corrected")
    _expect(raw["wide_n128_nullity_estimate"]["mean"] > 0.1, "the raw null sum carries the readout bias")
    _expect(abs(corrected["wide_d128_target_minus_null"]["mean"] - 60.0) < 1e-9, "o128 against its null control")
    results = analysis.rules(raw, corrected)
    failed = [title for title, ok, _ in results if not ok]
    _expect(not failed, f"rules failing on the corrected ideal data: {failed}")
    _expect(len(results) == 6 + 2 + 2 + 4 + 6 + 2 + 1, f"{len(results)} rule readings")


def test_each_block_is_scored_against_its_own_ideal_not_its_neighbors() -> None:
    entry = _entry()
    readings = analysis.placement_readings(entry, _writers(), GROUP, corrected=True)
    rows = readings["o128"]
    ideals = {row["block"]: row["ideal"] for row in rows}
    _expect(sorted(ideals.values()) == [3.0] * 4 + [4.0] * 12, f"{sorted(ideals.values())}")
    for row in rows:
        _expect(abs(row["nullity"] - row["ideal"]) < 1e-9, f"{row['block']}: {row['nullity']} against {row['ideal']}")
    wrong = {n: [list(map(float, IDEAL[BODIES[n][(r + 1) % REPLICAS]])) for r in range(REPLICAS)] for n in BODIES}
    shifted = analysis.placement_readings({**entry, "measured": wrong}, _writers(), GROUP, corrected=False)["o128"]
    _expect(any(abs(row["nullity"] - row["ideal"]) > 0.5 for row in shifted), "a shifted placement is not detected")


def test_the_sixty_four_dimensional_operands_average_their_two_copies() -> None:
    corrected = _stats(_entry(), corrected=True)
    readings = analysis.placement_readings(_entry(), _writers(), GROUP, corrected=True)["o64"]
    _expect([r["block"] for r in readings[:8]] == [r["block"] for r in readings[8:]], "copies hold different blocks")
    blocks = analysis.block_means(readings)
    _expect(len(blocks) == 8 and all(row["copies"] == 2 for row in blocks.values()), "block copies")
    first = next(iter(blocks))
    _expect(abs(corrected[f"{first}_nullity_estimate"]["se"] ** 2 - blocks[first]["nullity_variance"]) < 1e-15, "se")
    _expect(
        analysis.copy_agreement(
            {
                "o64": readings,
                "n64": analysis.placement_readings(_entry(), _writers(), GROUP, corrected=True)["n64"],
                "m64": analysis.placement_readings(_entry(), _writers(), GROUP, corrected=True)["m64"],
            }
        )[0][1],
        "copy agreement",
    )


def test_delta_method_standard_error_matches_the_multinomial_simulation() -> None:
    plus, minus = IDEAL["wide_o128_k0_plus"], IDEAL["wide_o128_k0_minus"]
    shots = 20_000
    lightly_noisy = [0.8 * law + 0.2 / 16 for law in (plus, minus)]
    reading = analysis.block_reading((lightly_noisy[0], lightly_noisy[1]), (plus, minus), (shots, shots), None)
    sampler = np.random.default_rng(SIMULATION_SEED)
    values = []
    for _ in range(400):
        draws = [sampler.multinomial(shots, law) / shots for law in lightly_noisy]
        values.append(ppc.estimate(draws[0], draws[1], plus, minus)["nullity_estimate"])
    observed = float(np.std(values, ddof=1))
    predicted = math.sqrt(reading["nullity_variance"])
    _expect(abs(predicted / observed - 1.0) < 0.15, f"delta method {predicted:.4f} against simulation {observed:.4f}")


def test_interval_covers_the_ideal_sum_on_sampled_laws_and_widens_with_fewer_shots() -> None:
    entry = _entry(np.random.default_rng(SIMULATION_SEED))
    corrected = _stats(entry, corrected=True)
    for key, value in IDEAL_SUM.items():
        stat = corrected[f"wide_{key}_nullity_estimate"]
        _expect(stat["lo"] <= value <= stat["hi"], f"{key}: {value} outside [{stat['lo']:.3f}, {stat['hi']:.3f}]")
    for op in ("o64", "o128"):
        stat = corrected[f"wide_{op}_nullity_estimate"]
        _expect(0.0 < stat["se"] < 0.1, f"{op}: standard error {stat['se']}")
    fewer = json.loads(json.dumps(entry))
    for executed in fewer["executed"].values():
        executed["shots"] = SHOTS // 100
    wide = _stats(fewer, corrected=True)["wide_o128_nullity_estimate"]["se"]
    narrow = corrected["wide_o128_nullity_estimate"]["se"]
    _expect(abs(wide / narrow - 10.0) < 0.5, f"standard error ratio {wide / narrow:.2f} for a hundredth of the shots")


def test_rules_fail_on_a_shifted_target_a_missing_separation_and_a_low_visibility_block() -> None:
    entry = _entry()
    corrected, raw = _stats(entry, corrected=True), _stats(entry, corrected=False)

    def shifted(stats: dict, key: str, delta: float) -> dict:
        out = {k: dict(v) for k, v in stats.items()}
        for field in ("mean", "lo", "hi"):
            out[key][field] += delta
        return out

    bad = analysis.rules(raw, shifted(corrected, "wide_o128_nullity_estimate", 1.5))
    _expect(("whole-operand nullity o128", False) in [(t, ok) for t, ok, _ in bad], "a shift beyond 1.0 fails")
    bad = analysis.rules(raw, shifted(corrected, "wide_d64_target_minus_mutation", -5.0))
    _expect(("mutation d64", False) in [(t, ok) for t, ok, _ in bad], "a lost separation fails")
    bad = analysis.rules(shifted(raw, "wide_o64_k0_visibility", -1.0), corrected)
    _expect(("visibility floor", False) in [(t, ok) for t, ok, _ in bad], "a block below 0.5 fails")


def test_device_agreement_subtracts_the_model_gap_and_allows_the_offset_per_block() -> None:
    stats = _stats(_entry(), corrected=True)
    key = "wide_o128_nullity_estimate"
    gap = {f"wide_{op.key}_nullity_estimate": 0.0 for op in pw.WIDE_OPERANDS}
    _expect(all(ok for _, ok, _ in analysis.device_agreement(stats, stats, gap)), "identical runs agree")
    other = {k: dict(v) for k, v in stats.items()}
    other[key]["mean"] += 0.7
    results = {t: ok for t, ok, _ in analysis.device_agreement(stats, other, gap)}
    _expect(results["device agreement o128"], "a 0.7 gap is inside the allowance of 0.8")
    other[key]["mean"] += 0.7
    results = {t: ok for t, ok, _ in analysis.device_agreement(stats, other, gap)}
    _expect(not results["device agreement o128"], "a 1.4 gap exceeds 0.8")
    results = {t: ok for t, ok, _ in analysis.device_agreement(stats, other, {**gap, key: -1.4})}
    _expect(results["device agreement o128"], "the model gap is subtracted")


def test_analyze_run_reads_the_archive_and_agrees_with_the_pooled_value(tmp_path: Path) -> None:
    entry = _entry()
    corrected = _stats(entry, corrected=True)
    pooled = {key: stat["mean"] for key, stat in corrected.items()}
    entry["measured_summary_readout_corrected"] = pooled
    (tmp_path / "collect.json").write_text(json.dumps([{"jobs": {}}, entry]))
    (tmp_path / "record.json").write_text(
        json.dumps({"groups": [{"group": "pathion_wide_coset", "summary_readout_corrected": pooled}]})
    )
    buffer = io.BytesIO()
    qpy.dump([_circuit(pub) for pub in PUBS.values()], buffer)
    run_archive.write_archive(tmp_path, buffer.getvalue(), materialize=True)
    result = analysis.analyze_run(tmp_path)
    _expect(result["pooled_difference"] < 1e-9, f"pooled difference {result['pooled_difference']}")
    _expect(abs(result["corrected"]["wide_o64_nullity_estimate"]["mean"] - 28.0) < 1e-9, "o64 corrected")
    _expect(any("placement" in line for line in analysis.report_readings(result)), "per-placement report")
