"""Replicated matched-response analysis: Stein rule, exchangeability, binding, refusals, synthetic end-to-end."""

import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-replicated-q11"
# Seeds: docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json, indices 13, 14, 15 in order.
TEST_SEEDS = (38219, 9144, 11079)
IDEAL = {"dark": 0.0, "bright": 1.0, "fixture": 0.5}
ALPHA = 0.03
BETA = 0.05
BATCH_OFFSET = (0.04, 0.10, 0.06)
REGION_OFFSET = (0.03, 0.08)


def _check(condition: object) -> None:
    if not condition:
        raise AssertionError


def _rule() -> Any:
    import qi_replicated_response

    return qi_replicated_response


def _load(count: int, shots: int | None = None) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    proposal = json.loads((PROPOSAL / "proposal.json").read_text())
    manifests = {}
    for index in range(count):
        name = f"rep-{index:02d}"
        manifests[name] = json.loads((PROPOSAL / name / "cases.json").read_text())
        if shots is not None:
            manifests[name]["shots"] = shots
    if shots is not None:
        proposal["shots_per_job"] = shots
    return proposal, manifests


def _outcomes(read1: tuple[float, float]) -> tuple[list[str], list[float]]:
    selectors = _rule().SELECTORS
    strings, probabilities = [], []
    for first in (0, 1):
        for second in (0, 1):
            bits = ["0"] * 17
            bits[16 - selectors[0]] = str(first)
            bits[16 - selectors[1]] = str(second)
            strings.append("".join(bits))
            probabilities.append((read1[0] if first else 1 - read1[0]) * (read1[1] if second else 1 - read1[1]))
    return strings, probabilities


def _series(
    rng: Any,
    proposal: dict[str, Any],
    manifests: dict[str, dict[str, Any]],
    effect: float = 0.0,
    noise: float = 0.0,
) -> tuple[dict[tuple[str, str], list[str]], dict[str, list[tuple[str, int]]]]:
    """Shots under p_zero = batch + region offset + g_region ideal + noise; effect = (g2 - g1) / 2."""
    gain = (0.8, 0.8 + 2 * effect)
    rule = _rule()
    shots: dict[tuple[str, str], list[str]] = {}
    orders: dict[str, list[tuple[str, int]]] = {}
    job = 1000
    for index, (name, manifest) in enumerate(manifests.items()):
        orders[name] = []
        for file in [row["file"] for row in manifest["circuits"]]:
            if file == rule.READOUT_ZERO:
                read1 = (ALPHA, ALPHA)
            elif file == rule.READOUT_ONE:
                read1 = (1 - BETA, 1 - BETA)
            else:
                cases = rule.WITNESS_CASES[file]
                zero = [
                    BATCH_OFFSET[index % 3] + REGION_OFFSET[r] + gain[r] * IDEAL[cases[r]] + noise * rng.normal()
                    for r in range(2)
                ]
                read1 = tuple(BETA + (1 - ALPHA - BETA) * (1 - value) for value in zero)
            strings, probabilities = _outcomes(read1)
            counts = rng.multinomial(manifest["shots"], probabilities)
            shots[name, file] = [s for s, c in zip(strings, counts, strict=True) for _ in range(int(c))]
            job += 1
            orders[name].append((file, job))
    return shots, orders


def _analyze(
    proposal: dict[str, Any],
    manifests: dict[str, dict[str, Any]],
    shots: dict[tuple[str, str], list[str]],
    orders: dict[str, list[tuple[str, int]]],
) -> dict[str, Any]:
    return _rule().analyze_replicated_series(proposal, manifests, shots, job_order=orders)


def test_frozen_constants_equal_the_stein_derivation() -> None:
    from scipy import optimize, stats

    rule = _rule()
    law = stats.t(rule.DF)
    critical = float(law.ppf(1 - rule.ALPHA / 2))
    shift = optimize.brentq(lambda s: law.sf(critical - s) + law.cdf(-critical - s) - rule.POWER, 0, 10, xtol=1e-14)
    _check(rule.T_CRIT == pytest.approx(critical, rel=1e-12))
    _check(rule.SHIFT == pytest.approx(shift, rel=1e-12))
    _check(rule.C == pytest.approx(rule.DELTA**2 / shift**2, rel=1e-12))
    _check(rule.DF == rule.N1 - 1 and rule.CAP == 60)


def test_total_rule_depends_on_the_stage_one_sd_alone() -> None:
    rule = _rule()
    _check(int(rule.required_replicates(0.038)) == 40)
    _check(int(rule.required_replicates(0.001)) == rule.N1)
    # the cap binds at s1 = sqrt(CAP C)
    edge = float(np.sqrt(rule.CAP * rule.C))
    _check(int(rule.required_replicates(edge * 0.999)) == rule.CAP)
    _check(int(rule.required_replicates(edge * 1.001)) == rule.CAP + 1)
    rng = np.random.default_rng(TEST_SEEDS[0])
    first = 0.03 * rng.standard_normal(rule.N1)
    low = rule.stein_decision(np.concatenate([first, np.zeros(0)]))
    _check(low["required_total"] == int(rule.required_replicates(float(np.std(first, ddof=1)))))
    shifted = rule.stein_decision(first + 5.0)  # the stage-1 mean never enters the rule
    _check(shifted["required_total"] == low["required_total"])


def test_statistic_uses_the_stage_one_sd_whatever_the_later_scatter() -> None:
    rule = _rule()
    rng = np.random.default_rng(TEST_SEEDS[1])
    first = 0.02 * rng.standard_normal(rule.N1)
    required = int(rule.required_replicates(float(np.std(first, ddof=1))))
    _check(required > rule.N1)
    extra = required - rule.N1
    tails = [np.full(extra, 0.01), 0.01 + np.where(np.arange(extra) % 2 == 0, 1.0, -1.0) * 0.5]
    results = [rule.stein_decision(np.concatenate([first, tail - tail.mean() + 0.01])) for tail in tails]
    _check(results[0]["t"] == pytest.approx(results[1]["t"], rel=1e-12))
    manual = np.concatenate([first, np.full(extra, 0.01)]).mean() * np.sqrt(required) / np.std(first, ddof=1)
    _check(results[0]["t"] == pytest.approx(manual, rel=1e-12))
    _check(results[0]["degrees_of_freedom"] == 11)


def test_decision_refuses_missing_extra_and_post_cap_replicates() -> None:
    rule = _rule()
    rng = np.random.default_rng(TEST_SEEDS[2])
    wide = 0.02 * rng.standard_normal(rule.N1)
    required = int(rule.required_replicates(float(np.std(wide, ddof=1))))
    _check(rule.N1 < required <= rule.CAP)
    _check(rule.stein_decision(wide)["status"] == "continue")
    with pytest.raises(ValueError, match="stage 1 needs"):
        rule.stein_decision(wide[:-1])
    with pytest.raises(ValueError, match="differ from the rule's N"):
        rule.stein_decision(np.concatenate([wide, np.zeros(required - rule.N1 - 1)]))
    with pytest.raises(ValueError, match="differ from the rule's N"):
        rule.stein_decision(np.concatenate([wide, np.zeros(required - rule.N1 + 1)]))
    huge = wide * 10
    verdict = rule.stein_decision(huge)
    _check(verdict["status"] == "undecided_at_cap" and verdict["n"] == rule.N1)
    _check(verdict["interval_99"][0] < verdict["mean"] < verdict["interval_99"][1])
    with pytest.raises(ValueError, match="stops at the cap"):
        rule.stein_decision(np.concatenate([huge, np.zeros(3)]))


def test_simulated_level_and_power_of_the_rule() -> None:
    from qi_replicated_stein_simulation import simulate

    rows = simulate(0.038, (0.0, -0.024), 20000, TEST_SEEDS[0])
    _check(abs(rows[0]["reject_uncapped_rule"] - 0.01) < 4 * np.sqrt(0.01 * 0.99 / 20000))
    _check(rows[1]["reject_uncapped_rule"] > 0.80 - 4 * np.sqrt(0.8 * 0.2 / 20000))
    _check(0.05 < rows[1]["undecided_at_cap"] < 0.2)


def test_schedule_alternates_witness_order_and_readout_in_blocks_of_four() -> None:
    rule = _rule()
    block = [tuple(rule.schedule(index)) for index in range(4)]
    _check(len(set(block)) == 4)
    _check(
        {(order[0], order[2]) for order in block}
        == {
            (rule.WITNESS_A, rule.READOUT_ZERO),
            (rule.WITNESS_B, rule.READOUT_ZERO),
            (rule.WITNESS_A, rule.READOUT_ONE),
            (rule.WITNESS_B, rule.READOUT_ONE),
        }
    )
    _check(all(rule.schedule(index) == rule.schedule(index + 4) for index in range(rule.CAP - 4)))


def test_null_series_is_not_rejected_and_effect_series_is() -> None:
    rule = _rule()
    proposal, manifests = _load(rule.N1)
    rng = np.random.default_rng(TEST_SEEDS[0])
    shots, orders = _series(rng, proposal, manifests, effect=0.0, noise=0.002)
    null = _analyze(proposal, manifests, shots, orders)
    decision = null["decision"]
    _check(decision["status"] == "not_rejected" and decision["n"] == rule.N1)
    _check(abs(decision["mean"]) < 4 * decision["s1"] / np.sqrt(rule.N1))
    _check(null["exploratory_block_corrected"]["replicates_outside_complete_blocks"] == 0)
    _check(len(null["exploratory_block_corrected"]["block_residuals"]) == 3)
    shots, orders = _series(rng, proposal, manifests, effect=-0.024, noise=0.002)
    effect = _analyze(proposal, manifests, shots, orders)
    _check(effect["decision"]["status"] == "rejected")
    _check(abs(effect["decision"]["mean"] + 0.024) < 4 * effect["decision"]["s1"] / np.sqrt(rule.N1))
    corrected = np.mean(effect["exploratory_block_corrected"]["block_residuals"])
    _check(abs(corrected + 0.024) < 0.02)
    _check(set(effect["exchangeability"]) == {"lag1", "order_difference"})
    _check(effect["exchangeability"]["lag1"]["unreliable"] in (True, False))


def test_two_stage_series_decides_at_the_rules_total() -> None:
    rule = _rule()
    proposal, manifests = _load(rule.CAP, 1024)
    rng = np.random.default_rng(TEST_SEEDS[1])
    shots, orders = _series(rng, proposal, manifests, effect=0.0, noise=0.02)

    def subset(count: int) -> dict[str, Any]:
        names = [f"rep-{index:02d}" for index in range(count)]
        return _analyze(
            proposal,
            {name: manifests[name] for name in names},
            {key: value for key, value in shots.items() if key[0] in names},
            {name: orders[name] for name in names},
        )

    first = subset(rule.N1)["decision"]
    _check(first["status"] in {"continue", "undecided_at_cap"})
    if first["status"] == "continue":
        final = subset(first["required_total"])["decision"]
        _check(final["status"] in {"rejected", "not_rejected"} and final["n"] == first["required_total"])
        _check(final["s1"] == first["s1"])
        with pytest.raises(ValueError, match="differ from the rule's N"):
            subset(first["required_total"] + 1)


@pytest.mark.parametrize(
    "fault",
    [
        "missing-replicate",
        "reordered-manifest",
        "job-order",
        "job-ids",
        "short-witness",
        "missing-readout",
        "wrong-witness-cases",
        "wrong-backend",
        "wrong-proposal-design",
        "readout-error",
        "too-few",
    ],
)
def test_analysis_refuses_each_fault(fault: str) -> None:
    rule = _rule()
    proposal, manifests = _load(rule.N1, 256)
    rng = np.random.default_rng(TEST_SEEDS[2])
    shots, orders = _series(rng, proposal, manifests, noise=0.002)
    _check(len(_analyze(proposal, manifests, shots, orders)["replicates"]) == rule.N1)
    match = None
    if fault == "missing-replicate":
        del manifests["rep-05"]
        match = "missing or out of sequence"
    elif fault == "reordered-manifest":
        manifests["rep-02"]["circuits"][0], manifests["rep-02"]["circuits"][1] = (
            manifests["rep-02"]["circuits"][1],
            manifests["rep-02"]["circuits"][0],
        )
        orders["rep-02"] = [(row["file"], 2000 + i) for i, row in enumerate(manifests["rep-02"]["circuits"])]
        match = "circuit order differs"
    elif fault == "job-order":
        (first, a), (second, b) = orders["rep-03"][0], orders["rep-03"][1]
        orders["rep-03"][0], orders["rep-03"][1] = (second, a), (first, b)
        match = "job order differs"
    elif fault == "job-ids":
        orders["rep-04"][2] = (orders["rep-04"][2][0], orders["rep-04"][0][1])
        match = "job ids do not rise"
    elif fault == "short-witness":
        shots["rep-01", "witness-a.cq"].pop()
        match = "the manifest requests"
    elif fault == "missing-readout":
        del shots["rep-00", "readout-0.cq"]
        match = "no collected shots"
    elif fault == "wrong-witness-cases":
        manifests["rep-06"]["witnesses"]["witness-a.cq"] = ["dark", "fixture"]
        match = "witness case assignment"
    elif fault == "wrong-backend":
        manifests["rep-07"]["backend"] = "qx"
        match = "backend or shots"
    elif fault == "wrong-proposal-design":
        proposal["design"]["c"] = 1e-4
        match = "frozen rule"
    elif fault == "readout-error":
        selector = rule.SELECTORS[1]
        rows = shots["rep-00", "readout-0.cq"]
        shots["rep-00", "readout-0.cq"] = [
            row[: 16 - selector] + "1" + row[17 - selector :] if index < len(rows) // 3 else row
            for index, row in enumerate(rows)
        ]
        match = "readout error exceeds"
    else:
        manifests.pop("rep-11")
        match = "stage 1 needs"
    with pytest.raises(ValueError, match=match):
        _analyze(proposal, manifests, shots, orders)


def test_job_order_check_accepts_the_schedule_and_refuses_a_swap() -> None:
    rule = _rule()
    _, manifests = _load(2)
    files = [row["file"] for row in manifests["rep-01"]["circuits"]]
    rule.verify_job_order("rep-01", manifests["rep-01"], list(zip(files, (5, 6, 7), strict=True)))
    with pytest.raises(ValueError, match="job order differs"):
        rule.verify_job_order("rep-01", manifests["rep-01"], list(zip(files[::-1], (5, 6, 7), strict=True)))
    with pytest.raises(ValueError, match="do not rise"):
        rule.verify_job_order("rep-01", manifests["rep-01"], list(zip(files, (5, 7, 6), strict=True)))


def test_proposal_binding_accepts_the_bytes_and_refuses_each_mutation(tmp_path: Path) -> None:
    rule = _rule()
    binding = rule.proposal_digests(PROPOSAL)
    _check(len(binding["batches"]) == rule.CAP and binding["proposal.json"] == rule.PROPOSAL_SHA256)
    for mutation in ("circuit", "manifest", "proposal", "schedule"):
        copy = tmp_path / mutation
        shutil.copytree(PROPOSAL, copy)
        if mutation == "circuit":
            path = copy / "rep-07" / "witness-a.cq"
            data = bytearray(path.read_bytes())
            data[-5] ^= 1
            path.write_bytes(bytes(data))
            match = "circuit differs"
        elif mutation == "manifest":
            path = copy / "rep-09" / "cases.json"
            path.write_text(path.read_text().replace("16384", "8192"))
            match = "manifest differs"
        else:
            path = copy / "proposal.json"
            document = json.loads(path.read_text())
            if mutation == "schedule":
                document["schedule"][3]["order"][0], document["schedule"][3]["order"][1] = (
                    document["schedule"][3]["order"][1],
                    document["schedule"][3]["order"][0],
                )
                match = "schedule differs"
            else:
                document["design"]["cap"] = 61
                match = "differs from the approved proposal"
            path.write_text(json.dumps(document, indent=1) + "\n")
        if mutation == "schedule":
            original = rule.PROPOSAL_SHA256
            import hashlib

            rule.PROPOSAL_SHA256 = hashlib.sha256((copy / "proposal.json").read_bytes()).hexdigest()
            try:
                with pytest.raises(ValueError, match=match):
                    rule.proposal_digests(copy)
            finally:
                rule.PROPOSAL_SHA256 = original
        else:
            with pytest.raises(ValueError, match=match):
                rule.proposal_digests(copy)


def test_predecessor_proposal_is_refused_as_the_wrong_proposal() -> None:
    predecessor = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-region2-selector-q11"
    with pytest.raises((ValueError, KeyError), match="proposal|schedule"):
        _rule().proposal_digests(predecessor)


@pytest.mark.parametrize("mutation", ["none", "circuit", "manifest"])
def test_run_binding_accepts_the_proposal_bytes_and_refuses_a_changed_run(tmp_path: Path, mutation: str) -> None:
    from qi_matched_response import verify_run_binding
    from qi_records import load_run

    run = tmp_path / "run"
    shutil.copytree(PROPOSAL / "rep-03", run)
    if mutation == "circuit":
        data = bytearray((run / "witness-b.cq").read_bytes())
        data[-5] ^= 1
        (run / "witness-b.cq").write_bytes(bytes(data))
    elif mutation == "manifest":
        manifest = json.loads((run / "cases.json").read_text())
        manifest["shots"] = 8192
        (run / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n")
    binding = _rule().proposal_digests(PROPOSAL)
    if mutation == "none":
        _check(len(verify_run_binding(binding, "rep-03", load_run(run))["circuits"]) == 3)
    else:
        with pytest.raises(ValueError, match="differ"):
            verify_run_binding(binding, "rep-03", load_run(run))


def test_lag_and_order_diagnostics_detect_their_failure_classes() -> None:
    rule = _rule()
    rng = np.random.default_rng(TEST_SEEDS[0])
    white = rng.standard_normal(40)
    _check(rule.lag1(white)["unreliable"] is False)
    trend = np.cumsum(rng.standard_normal(40))
    _check(rule.lag1(trend)["unreliable"] is True)
    alternating = white * 0.1 + np.where(np.arange(40) % 2 == 0, 1.0, -1.0)
    difference = rule.order_difference(alternating)
    _check(difference["interval_95"][0] > 1.5)
    _check(rule.order_difference(white)["interval_95"][0] < 0 < rule.order_difference(white)["interval_95"][1])
