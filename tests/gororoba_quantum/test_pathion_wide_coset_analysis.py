"""Contracts of the per-placement analysis of a pathion_wide_coset run (scripts/pathion_wide_coset_analysis.py).

A synthetic collect.json holds the group's body laws (each placement's own block) pushed through a different asymmetric
readout channel on every placement, with an archived routed circuit that measures each placement's clbits into
scrambled physical qubits. The script must invert each placement with its own confusion matrices, score each block
against its own ideal law, recover the whole-operand sums, give each estimate a shot-noise interval that matches a
simulation, and report the case's rules. The interval covers the covariance between the placements of one PUB: shot
tables with a shared-uniform coupling hold every placement's marginal law fixed while the joint coupling varies, and
the covariance interval must match the sampling spread of the whole-operand sum where the independent-placement
interval misses it.
"""

from __future__ import annotations

import functools
import hashlib
import io
import json
import math
import shutil
from pathlib import Path

import numpy as np
import pathion_wide_coset_analysis as analysis
import pytest
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
SHOTS = 20_000
# Sampling seed of the multinomial draws: index 3 of the ANU QRNG draw
# docs/evidence/anu_qrng/draw-2026-11-07T051516Z.json.
SIMULATION_SEED = 64049
# Seeds of the shot tables and of the coupled-placement Monte Carlo: indices 0 and 1 of the ANU QRNG draw
# docs/evidence/anu_qrng/draw-2026-11-08T140050Z.json.
TABLE_SEED = 48953
COUPLING_SEED = 31431
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


@functools.cache
def _channel_laws() -> dict[str, np.ndarray]:
    """Each member's exact law at every placement: the block's ideal law through that placement's readout channel.

    The result is shared between tests and read-only."""
    calibration = _calibration()
    laws = {}
    for name, bodies in BODIES.items():
        rows = []
        for r in range(REPLICAS):
            law = IDEAL[bodies[r]].copy()
            for c, qubit in enumerate(WRITERS[r]):
                values = calibration[str(qubit)]
                law = ppc.apply_readout_clbit(law, c, values["prob_meas1_prep0"], values["prob_meas0_prep1"])
            rows.append(law / law.sum())
        laws[name] = np.array(rows)
    return laws


def _entry(tables: dict[str, np.ndarray] | None = None) -> dict:
    """The collect entry: the exact channel laws, or with shot tables each law is its table's empirical law."""
    laws = _channel_laws()
    measured = {}
    for name, rows in laws.items():
        if tables is not None:
            rows = np.array(
                [np.bincount(tables[name][:, r], minlength=16) / len(tables[name]) for r in range(REPLICAS)]
            )
        measured[name] = [[float(p) for p in row] for row in rows]
    shots = SHOTS if tables is None else len(next(iter(tables.values())))
    calibration = _calibration()
    executed = {name: {"pub": PUBS[name], "shots": shots, "placed_qubit_calibration": calibration} for name in BODIES}
    return {
        "group": "pathion_wide_coset",
        "backend": "synthetic",
        "job_id": "synthetic_job",
        "measured": measured,
        "executed": executed,
    }


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


def _coupled_outcomes(
    rng: np.random.Generator,
    laws: np.ndarray,
    order: np.ndarray,
    lead: tuple[int, ...],
    rho: float,
    antithetic: bool = False,
) -> np.ndarray:
    """Shots of all placements of one PUB, shape (*lead, placements), each placement keeping its own marginal law.

    A shot is coupled with probability rho. A coupled shot draws one common uniform and every placement maps it
    through the inverse cdf of its own law over its outcomes sorted by ``order`` (increasing influence), so the
    influence values are comonotone across placements. With ``antithetic`` the placements pair up (2j, 2j + 1): a
    coupled shot draws one uniform per pair and the odd placement maps 1 - u, so each pair's influence values are
    countermonotone and the pairs are independent. An uncoupled shot maps one uniform per placement. All uniforms are
    drawn before any is mapped."""
    placements = laws.shape[0]
    group = np.arange(placements) // 2 if antithetic else np.zeros(placements, dtype=int)
    common = rng.random((*lead, int(group.max()) + 1))[..., group]
    own = rng.random((*lead, placements))
    coupled = (rng.random(lead) < rho)[..., None]
    flip = (np.arange(placements) % 2 == 1) if antithetic else np.zeros(placements, dtype=bool)
    uniform = np.where(coupled, np.where(flip, 1.0 - common, common), own)
    out = np.empty((*lead, placements), dtype=np.int64)
    for p in range(placements):
        cdf = np.cumsum(laws[p][order[p]])
        cdf[-1] = 1.0
        out[..., p] = order[p][np.minimum(np.searchsorted(cdf, uniform[..., p], side="right"), 15)]
    return out


@functools.cache
def _tables(rho: float = 0.0, *, seed: int = TABLE_SEED, shots: int = SHOTS, antithetic: bool = False) -> dict:
    """Shot tables of every member, (shots, placements); rho couples the placements of each PUB."""
    laws = _channel_laws()
    rng = np.random.default_rng(seed)
    orders = _influence_orders()
    return {name: _coupled_outcomes(rng, laws[name], orders[name], (shots,), rho, antithetic) for name in BODIES}


@functools.cache
def _influence_orders() -> dict[str, np.ndarray]:
    """Per member and placement, the outcomes sorted by the gradient of the corrected N_hat at the exact laws."""
    readings = analysis.placement_readings(_entry(), _writers(), GROUP, corrected=True)
    orders = {}
    for op in pw.WIDE_OPERANDS:
        for arm, label in enumerate(("plus", "minus")):
            orders[pw.member_name(op, label)] = np.array(
                [np.argsort(row["gradient"][0, arm, :], kind="stable") for row in readings[op.key]]
            )
    return orders


def _readings(entry: dict, *, corrected: bool) -> dict:
    return analysis.placement_readings(entry, _writers(), GROUP, corrected=corrected)


def _stats_with(entry: dict, tables: dict, *, corrected: bool) -> dict:
    readings = _readings(entry, corrected=corrected)
    return analysis.operand_stats(readings, analysis.shot_covariances(readings, tables))


def _stats(entry: dict, *, corrected: bool) -> dict:
    """Stats of an entry whose means are exact; the covariance comes from independent shot tables."""
    return _stats_with(entry, _tables(), corrected=corrected)


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
    entry = _entry()
    tables = _tables()
    readings = _readings(entry, corrected=True)
    covariances = analysis.shot_covariances(readings, tables)
    corrected = analysis.operand_stats(readings, covariances)
    rows = readings["o64"]
    _expect([r["block"] for r in rows[:8]] == [r["block"] for r in rows[8:]], "copies hold different blocks")
    weights = analysis.block_weights(rows)
    _expect(len(weights) == 8 and all(w.sum() == 1.0 and (w > 0).sum() == 2 for w in weights.values()), "copies")
    first = next(iter(weights))
    expected = sum(w**2 * r["nullity_variance"] for w, r in zip(weights[first], rows, strict=True))
    _expect(abs(corrected[f"{first}_nullity_estimate"]["marginal_se"] ** 2 - expected) < 1e-15, "marginal se")
    agreement = analysis.copy_agreement(readings, covariances)
    _expect([title for title, _, _ in agreement] == [f"copy agreement {k}64" for k in "nom"], f"{agreement}")
    _expect(all(ok for _, ok, _ in agreement), "ideal copies disagree")
    shifted = {**readings, "o64": [*rows[:8], *({**r, "nullity": r["nullity"] + 1.0} for r in rows[8:])]}
    verdicts = dict((t, ok) for t, ok, _ in analysis.copy_agreement(shifted, covariances))
    _expect(not verdicts["copy agreement o64"], "shift")


def test_the_shot_covariance_diagonal_is_the_independent_placement_variance() -> None:
    tables = _tables(0.6)
    entry = _entry(tables)
    for corrected in (True, False):
        readings = _readings(entry, corrected=corrected)
        covariances = analysis.shot_covariances(readings, tables)
        for op in pw.WIDE_OPERANDS:
            for q, quantity in enumerate(analysis.QUANTITIES):
                marginal = np.array([row[f"{quantity}_variance"] for row in readings[op.key]])
                diagonal = np.diag(covariances[op.key][q])
                _expect(bool(np.allclose(diagonal, marginal, rtol=1e-6, atol=1e-14)), f"{op.key} {quantity}: diagonal")
    stat = analysis.operand_stats(readings, covariances)["wide_o128_nullity_estimate"]
    _expect(stat["se"] > 1.5 * stat["marginal_se"], f"comonotone placements widen the sum: {stat}")


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


def test_interval_covers_the_ideal_sum_on_sampled_shots_and_widens_with_fewer_shots() -> None:
    tables = _tables()
    corrected = _stats_with(_entry(tables), tables, corrected=True)
    for key, value in IDEAL_SUM.items():
        stat = corrected[f"wide_{key}_nullity_estimate"]
        _expect(stat["lo"] <= value <= stat["hi"], f"{key}: {value} outside [{stat['lo']:.3f}, {stat['hi']:.3f}]")
    for op in ("o64", "o128"):
        stat = corrected[f"wide_{op}_nullity_estimate"]
        _expect(0.0 < stat["se"] < 0.1, f"{op}: standard error {stat['se']}")
    fewer_tables = _tables(shots=SHOTS // 100)
    wide = _stats_with(_entry(fewer_tables), fewer_tables, corrected=True)["wide_o128_nullity_estimate"]["se"]
    narrow = corrected["wide_o128_nullity_estimate"]["se"]
    _expect(abs(wide / narrow - 10.0) < 1.0, f"standard error ratio {wide / narrow:.2f} for a hundredth of the shots")


def _batch_o128_sum(draws: dict[str, np.ndarray], shots: int) -> np.ndarray:
    """The corrected o128 whole-operand sum of each run of a batch (draws[arm] has shape (runs, shots, placements))."""
    op = pw.BY_KEY["o128"]
    arms = (pw.member_name(op, "plus"), pw.member_name(op, "minus"))
    calibration = _calibration()
    runs = draws[arms[0]].shape[0]
    total = np.zeros(runs)
    for k in range(REPLICAS):
        pairs = [analysis.confusion(calibration, q) for q in WRITERS[k]]
        inverse = analysis.readout_matrix([p[0] for p in pairs], [p[1] for p in pairs])
        conditional = []
        for name in arms:
            offsets = (np.arange(runs)[:, None] * 16 + draws[name][:, :, k]).ravel()
            law = np.bincount(offsets, minlength=runs * 16).reshape(runs, 16) / shots @ inverse.T
            weight = law[:, :8] + law[:, 8:]
            conditional.append(np.divide(law[:, :8], weight, out=np.zeros_like(weight), where=weight > pw.ZERO))
        contrast = conditional[0] - conditional[1]
        ideal = pw.pcb.output_contrast(IDEAL[BODIES[arms[0]][k]], IDEAL[BODIES[arms[1]][k]])
        decided = np.abs(ideal) > pw.ZERO
        visibility = (contrast[:, decided] * np.sign(ideal[decided])).mean(axis=1)
        total += contrast.sum(axis=1) / 2.0 / visibility
    return total


def _whole_operand_spread(rho: float, antithetic: bool, shots: int, replicates: int, chunk: int) -> float:
    """Sampling spread of the corrected o128 whole-operand sum over independent coupled runs of the full estimator."""
    laws, orders = _channel_laws(), _influence_orders()
    op = pw.BY_KEY["o128"]
    arms = (pw.member_name(op, "plus"), pw.member_name(op, "minus"))
    rng = np.random.default_rng(COUPLING_SEED)
    sums = []
    for _ in range(replicates // chunk):
        draws = {
            name: _coupled_outcomes(rng, laws[name], orders[name], (chunk, shots), rho, antithetic) for name in arms
        }
        sums.append(_batch_o128_sum(draws, shots))
    return float(np.std(np.concatenate(sums), ddof=1))


def test_the_batch_estimator_of_the_simulation_is_the_analysis_estimator() -> None:
    tables = _tables(0.6, shots=3000)
    readings = _readings(_entry(tables), corrected=True)
    batch = _batch_o128_sum({name: table[None] for name, table in tables.items()}, 3000)
    _expect(abs(float(batch[0]) - sum(row["nullity"] for row in readings["o128"])) < 1e-9, f"{batch}")


@pytest.mark.audit
def test_coupled_placements_widen_or_narrow_the_interval_where_independent_placements_cannot() -> None:
    """Fixed marginal laws, varying joint coupling: the covariance interval follows the sampling spread of the
    whole-operand sum and the independent-placement interval does not."""
    shots, replicates = 12_000, 160
    laws, orders = _channel_laws(), _influence_orders()
    for rho, antithetic, direction, margin in ((0.6, False, "widens", 0.25), (1.0, True, "narrows", 0.10)):
        spread = _whole_operand_spread(rho, antithetic, shots, replicates, 20)
        tables = {
            name: _coupled_outcomes(
                np.random.default_rng(TABLE_SEED), laws[name], orders[name], (shots,), rho, antithetic
            )
            for name in BODIES
        }
        stat = _stats_with(_entry(tables), tables, corrected=True)["wide_o128_nullity_estimate"]
        _expect(
            abs(stat["se"] / spread - 1.0) < 0.15, f"{direction}: covariance se {stat['se']:.4f}, spread {spread:.4f}"
        )
        miss = abs(stat["marginal_se"] / spread - 1.0)
        _expect(
            miss > margin, f"{direction}: independent se {stat['marginal_se']:.4f} is within {miss:.2f} of {spread:.4f}"
        )
        _expect((stat["se"] > stat["marginal_se"]) == (direction == "widens"), f"{direction}: {stat}")


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


def _write_run(directory: Path, tables: dict[str, np.ndarray]) -> dict:
    """A retained-run directory: collect.json, record.json, the QPY archive and raw/<job_id>/ with an index."""
    entry = _entry(tables)
    corrected = _stats_with(entry, tables, corrected=True)
    pooled = {key: stat["mean"] for key, stat in corrected.items()}
    entry["measured_summary_readout_corrected"] = pooled
    (directory / "collect.json").write_text(json.dumps([{"jobs": {}}, entry]))
    (directory / "record.json").write_text(
        json.dumps({"groups": [{"group": "pathion_wide_coset", "summary_readout_corrected": pooled}]})
    )
    buffer = io.BytesIO()
    qpy.dump([_circuit(pub) for pub in PUBS.values()], buffer)
    run_archive.write_archive(directory, buffer.getvalue(), materialize=True)
    raw = directory / "raw" / entry["job_id"]
    raw.mkdir(parents=True)
    files = {}
    for index, (name, pub) in enumerate(PUBS.items()):
        shots = tables[name]
        registers = {
            f"g0_r{r}_c": {
                "bitstrings": [format(int(v), "04b") for v in shots[:, r]],
                "num_bits": 4,
                "num_shots": len(shots),
            }
            for r in range(REPLICAS)
        }
        path = raw / f"pub_{index:02d}.json"
        path.write_text(json.dumps({"pub_index": index, "pub_name": pub, "registers": registers}))
        files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (raw / "index.json").write_text(json.dumps({"files": files}))
    return entry


def test_analyze_run_reads_the_archive_and_raw_shots_and_agrees_with_the_pooled_value(tmp_path: Path) -> None:
    tables = _tables(0.6, shots=2000)
    _write_run(tmp_path, tables)
    result = analysis.analyze_run(tmp_path)
    _expect(result["pooled_difference"] < 1e-9, f"pooled difference {result['pooled_difference']}")
    _expect(abs(result["corrected"]["wide_o64_nullity_estimate"]["mean"] - 28.0) < 0.5, "o64 corrected")
    _expect(any("placement" in line for line in analysis.report_readings(result)), "per-placement report")
    per_run, pair, copies = analysis.rule_table([result])
    _expect(not pair and len(per_run[0]) == 6 + 2 + 2 + 4 + 6 + 2 + 1, "one run has no device rule")
    record = analysis.analysis_record([result])
    _expect(record["schema"] == analysis.SCHEMA and "synthetic" in record["backends"], "record")
    _expect(record["backends"]["synthetic"]["input_sha256"]["raw_index"], "the raw index digest is recorded")
    qubits = record["backends"]["synthetic"]["placement_qubits"]
    _expect(qubits["0"] == WRITERS[0], f"placement qubits {qubits['0']}")


def test_analyze_run_refuses_a_missing_altered_or_inconsistent_raw_record(tmp_path: Path) -> None:
    tables = _tables(shots=500)
    missing = tmp_path / "missing"
    missing.mkdir()
    _write_run(missing, tables)
    (missing / "raw" / "synthetic_job" / "index.json").unlink()
    try:
        analysis.analyze_run(missing)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("a run without its raw index must not fall back to the marginal interval")
    altered = tmp_path / "altered"
    altered.mkdir()
    _write_run(altered, tables)
    pub = altered / "raw" / "synthetic_job" / "pub_00.json"
    pub.write_text(pub.read_text().replace("0000", "0001", 1))
    try:
        analysis.analyze_run(altered)
    except ValueError as error:
        _expect("SHA-256" in str(error), str(error))
    else:
        raise AssertionError("an altered raw record must be refused")
    inconsistent = tmp_path / "inconsistent"
    inconsistent.mkdir()
    entry = _write_run(inconsistent, tables)
    other = {name: np.roll(shots, 1, axis=0)[::-1] for name, shots in tables.items()}
    other["wide_n64_minus"] = (other["wide_n64_minus"] + 1) % 16
    _write_run_raw_only(inconsistent, entry, other)
    try:
        analysis.analyze_run(inconsistent)
    except ValueError as error:
        _expect("collect.json's law" in str(error), str(error))
    else:
        raise AssertionError("raw shots that differ from collect.json's laws must be refused")


def _write_run_raw_only(directory: Path, entry: dict, tables: dict[str, np.ndarray]) -> None:
    raw = directory / "raw" / entry["job_id"]
    files = {}
    for index, (name, pub) in enumerate(PUBS.items()):
        registers = {
            f"g0_r{r}_c": {
                "bitstrings": [format(int(v), "04b") for v in tables[name][:, r]],
                "num_bits": 4,
                "num_shots": len(tables[name]),
            }
            for r in range(REPLICAS)
        }
        path = raw / f"pub_{index:02d}.json"
        path.write_text(json.dumps({"pub_index": index, "pub_name": pub, "registers": registers}))
        files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (raw / "index.json").write_text(json.dumps({"files": files}))


def test_nonpositive_shot_counts_and_a_same_backend_pair_are_refused(tmp_path: Path) -> None:
    law = IDEAL["wide_o128_k0_plus"]
    for shots in (0, -5):
        try:
            analysis.block_reading((law, law), (law, law), (shots, 100), None)
        except ValueError:
            continue
        raise AssertionError(f"{shots} shots must be refused before any variance is formed")
    for argv in ([], ["a", "b", "c"]):
        try:
            analysis.main(argv)
        except SystemExit as error:
            _expect(error.code == 2, f"{argv}: exit {error.code}")
        else:
            raise AssertionError(f"{argv}: the argument count must be refused")
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    _write_run(first, _tables(shots=500))
    shutil.copytree(first, second)
    try:
        analysis.main([str(first), str(second)])
    except SystemExit as error:
        _expect(error.code == 2, f"same backend: exit {error.code}")
    else:
        raise AssertionError("two runs of one backend are no device comparison")


def test_device_gap_skips_an_estimate_planned_on_one_device_only() -> None:
    fez = {"wide_o64_nullity_estimate": 28.1, "wide_ref32_n64_nullity_estimate": 0.0, "other": 1.0}
    kingston = {"wide_o64_nullity_estimate": 28.0}
    gap, unmatched = analysis.model_gap(fez, kingston)
    _expect(
        gap == {"wide_o64_nullity_estimate": fez["wide_o64_nullity_estimate"] - 28.0}, "gap over the shared estimates"
    )
    _expect(unmatched == ["wide_ref32_n64_nullity_estimate"], "the one-sided reference estimate is named")
