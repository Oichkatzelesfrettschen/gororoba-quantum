"""Contracts of the per-placement analysis of a pathion_wide_coset run (scripts/pathion_wide_coset_analysis.py).

A synthetic collect.json holds the group's ideal laws pushed through a different asymmetric readout channel on every
placement, with an archived routed circuit that measures each placement's clbits into scrambled physical qubits. The
script must invert each placement with its own confusion matrices, recover the ideal sums, and report the case's rules.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import numpy as np
import pathion_wide_coset_analysis as analysis
from qiskit import QuantumCircuit, qpy
from qiskit.circuit import ClassicalRegister, QuantumRegister

import pathion_parallel_coset as ppc
import pathion_wide_coset as pw
import run_archive

GROUP = pw.pathion_wide_coset_group()
IDEAL = {member.name: member.ideal for member in GROUP.members}
REPLICAS = 3
PUB = "synthetic_pub_01"
# Physical qubit measured into clbit c of placement r, deliberately out of order.
WRITERS = {r: [10 * r + 3, 10 * r + 1, 10 * r + 2, 10 * r] for r in range(REPLICAS)}


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _calibration() -> dict[str, dict[str, float]]:
    out = {}
    for r in range(REPLICAS):
        for c, qubit in enumerate(WRITERS[r]):
            out[str(qubit)] = {
                "prob_meas1_prep0": 0.004 + 0.002 * r + 0.001 * c,
                "prob_meas0_prep1": 0.02 + 0.01 * r + 0.005 * c,
                "readout_error": 0.01,
            }
    return out


def _entry() -> dict:
    calibration = _calibration()
    measured = {}
    for name, ideal in IDEAL.items():
        laws = []
        for r in range(REPLICAS):
            law = ideal.copy()
            for c, qubit in enumerate(WRITERS[r]):
                values = calibration[str(qubit)]
                law = ppc.apply_readout_clbit(law, c, values["prob_meas1_prep0"], values["prob_meas0_prep1"])
            laws.append([float(p) for p in law])
        measured[name] = laws
    executed = {name: {"pub": PUB, "placed_qubit_calibration": calibration} for name in IDEAL}
    return {"group": analysis.GROUP, "backend": "synthetic", "measured": measured, "executed": executed}


def _circuit() -> QuantumCircuit:
    qubits = QuantumRegister(10 * REPLICAS)
    registers = [ClassicalRegister(4, f"g0_r{r}_c") for r in range(REPLICAS)]
    qc = QuantumCircuit(qubits, *registers, name=PUB)
    for r in range(REPLICAS):
        for c, qubit in enumerate(WRITERS[r]):
            qc.measure(qubits[qubit], registers[r][c])
    return qc


def test_replica_writers_read_the_archived_measurement_map_and_confusion_falls_back() -> None:
    _expect(analysis.replica_writers(_circuit()) == WRITERS, f"{analysis.replica_writers(_circuit())}")
    _expect(analysis.confusion({"5": {"readout_error": 0.03}}, 5) == (0.03, 0.03), "symmetric fallback")
    _expect(analysis.confusion({"5": {"prob_meas1_prep0": 0.01, "prob_meas0_prep1": 0.02}}, 5) == (0.01, 0.02), "pair")


def test_per_placement_inversion_recovers_the_ideal_sums_and_the_raw_sums_are_biased() -> None:
    entry = _entry()
    writers = {PUB: WRITERS}
    corrected = analysis.intervals(analysis.placement_summaries(entry, writers, corrected=True))
    raw = analysis.intervals(analysis.placement_summaries(entry, writers, corrected=False))
    ideal = {"n64": 0, "o64": 28, "m64": -2, "n128": 0, "o128": 60, "m128": -2}
    for key, value in ideal.items():
        _expect(abs(corrected[f"wide_{key}_nullity_estimate"]["mean"] - value) < 1e-9, f"{key}: corrected")
    _expect(raw["wide_n128_nullity_estimate"]["mean"] > 0.1, "the raw null sum carries the readout bias")
    results = analysis.rules(raw, corrected)
    failed = [title for title, ok, _ in results if not ok]
    _expect(not failed, f"rules failing on the corrected ideal data: {failed}")
    _expect(len(results) == 6 + 2 + 2 + 4 + 6 + 2 + 1, f"{len(results)} rule readings")


def test_rules_fail_on_a_shifted_target_a_missing_separation_and_a_low_visibility_block() -> None:
    entry = _entry()
    corrected = analysis.intervals(analysis.placement_summaries(entry, {PUB: WRITERS}, corrected=True))
    raw = analysis.intervals(analysis.placement_summaries(entry, {PUB: WRITERS}, corrected=False))

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
    entry = _entry()
    stats = analysis.intervals(analysis.placement_summaries(entry, {PUB: WRITERS}, corrected=True))
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
    corrected = analysis.placement_summaries(entry, {PUB: WRITERS}, corrected=True)
    pooled = {key: float(np.mean([s[key] for s in corrected])) for key in corrected[0]}
    entry["measured_summary_readout_corrected"] = pooled
    (tmp_path / "collect.json").write_text(json.dumps([{"jobs": {}}, entry]))
    (tmp_path / "record.json").write_text(
        json.dumps({"groups": [{"group": analysis.GROUP, "summary_readout_corrected": pooled}]})
    )
    buffer = io.BytesIO()
    qpy.dump([_circuit()], buffer)
    run_archive.write_archive(tmp_path, buffer.getvalue(), materialize=True)
    result = analysis.analyze_run(tmp_path)
    _expect(result["pooled_difference"] < 1e-9, f"pooled difference {result['pooled_difference']}")
    _expect(abs(result["corrected"]["wide_o64_nullity_estimate"]["mean"] - 28.0) < 1e-9, "o64 corrected")
