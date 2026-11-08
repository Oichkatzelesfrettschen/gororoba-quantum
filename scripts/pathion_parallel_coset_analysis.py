"""Score the parallel coset-block drain runs against the preregistered rules of their written case.

Usage: "$PYTHON" scripts/pathion_parallel_coset_analysis.py --run RUN_DIR [RUN_DIR ...] --out FILE

The rules are those of results/live/2026-11-07T035554.327341Z/CASE.md ("Preregistered readout and decision rules"),
applied in the case's order to each run's retained record (record.json: the dry run's per-placement model values,
the placements; collect.json: the executed calibrations; raw/: the shot lists; isa.qpy: the measured qubit of every
classical bit). The module code of the group (gororoba_quantum/pathion_parallel_coset.py and the coset and four-term
block modules) computes every estimator; this script pairs, averages and compares.

Intervals are Student t at 95 percent over the placements (variance.interval, the function that produced the
collector's summary_interval). A paired difference subtracts the model value of the same placement index from the
measured one. No random draw enters: the verdicts are closed-form, so the script holds no seed.

Verdict. PASS: the literal rule holds and the 95 percent half-width of the tested mean does not exceed the rule's
band (the data resolve the band). FAIL: the literal rule is violated. UNINFORMATIVE: the literal rule holds while the
half-width exceeds the band, so a departure of the band's size would pass too; a rule's own unresolved outcome (the
crosstalk interval) reads the same. not run: an input the rule needs is absent, with the reason in the record.
Interval readings that the case words ambiguously are reported beside the verdict (`literal_*` and `*_mean_rule`
fields) and the verdict follows the more permissive wording.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]

import pathion_coset_block as pcb  # noqa: E402
import pathion_parallel_coset as ppc  # noqa: E402
import variance  # noqa: E402

SCHEMA = "pathion-parallel-coset-analysis-v1"
CASE = "results/live/2026-11-07T035554.327341Z/CASE.md"
NULL_OPERAND = "cmap_e1pe17"
NULL_BLOCKS = (0, 4, 8, 12)
ONE_CZ_BLOCKS = (4, 8, 12)
# Preregistered bands, in the order of the case's rules.
RESOLUTION_SIGNS = 31
RESOLUTION_VISIBILITY = 0.5
NULLITY_BAND = 0.5
NULLITY_CORRECTED_BAND = 0.15
SELECTOR_BAND = 0.006
SELECTOR_SE = 2.0
NULL_NHAT_BAND = 0.02
EVEN_BAND = 0.03
ODD_BAND = 0.04
SLOPE_RANGE = (0.7, 1.3)
R_SQUARED_MIN = 0.5
REPEAT_BAND = 0.02
CROSSTALK_BAND = 0.015
FOUR_VISIBILITY_MIN = 0.6
FOUR_CLOSURE_BAND = 0.03
FOUR_NULL_LEVEL_BAND = 0.02
FOUR_SEPARATION_FRACTION = 0.5
# Response of the k0 selector contrast to a coherent sx over-rotation, per radian (the case's signature table).
SX_RESPONSE = 0.57
CONFIDENCE = 0.95
DECIMALS = 6
OPERAND_KEY = re.compile(r"^cmap_(?:xor_|twin_)?e\d+[pm]e\d+_nullity_estimate$")
FOUR_KEY = re.compile(r"^(ftb_[A-Za-z0-9]+_c\d+)_visibility$")

# Model N_hat of the case's nullity rule for ibm_fez (CASE.md, from its binding dry run), in the operand order of
# the case's list; reported beside the model of the retained run's own dry run.
CASE_FACTS = {
    "ibm_fez": {
        "shots": 14336,
        "ceiling_seconds": 60,
        "binding_dry_run": "2026-11-07T035554.327341Z",
        "estimated_seconds": 52.3,
    },
    "ibm_kingston": {
        "shots": 8192,
        "ceiling_seconds": 40,
        "binding_dry_run": "2026-11-07T040239.842834Z",
        "estimated_seconds": 32.3,
    },
}
CASE_MODEL_NHAT_FEZ = {
    "cmap_e1pe17": 0.12,
    "cmap_e1pe26": 4.24,
    "cmap_e2pe27": 4.25,
    "cmap_e1pe10": 8.06,
    "cmap_e1pe18": 12.03,
    "cmap_e1pe24": 12.17,
    "cmap_twin_e17me2": 12.03,
    "cmap_xor_e1pe18": -2.19,
}


@cache
def parallel_group() -> Any:
    return ppc.pathion_parallel_coset_group()


@cache
def map_group() -> Any:
    return pcb.pathion_coset_map_group()


@dataclass
class Run:
    """One retained run, reduced to what the rules read."""

    directory: str
    backend: str
    job_id: str
    shots: int
    charge_seconds: int | None
    calibration: str
    members: list[str]
    ideal: dict[str, np.ndarray]
    dists: dict[str, list[np.ndarray]]
    isolated: np.ndarray | None
    isolated_member: str
    cz: dict[str, int]
    # readout[member][placement] = (e01, e10) per classical bit: P(read 1 | prepared 0), P(read 0 | prepared 1).
    readout: dict[str, list[tuple[list[float], list[float]]]]
    model: list[dict[str, float]]
    stored_summary: list[dict[str, float]] = field(default_factory=list)
    stored_corrected: dict[str, float] = field(default_factory=dict)
    stored_crosstalk: dict[str, Any] = field(default_factory=dict)
    digests: dict[str, str] = field(default_factory=dict)
    facts: dict[str, Any] = field(default_factory=dict)

    @property
    def placements(self) -> int:
        return len(self.model)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def counts_to_law(bitstrings: list[str], width: int) -> np.ndarray:
    """Outcome law indexed by int(bitstring, 2), the clbit 0 = rightmost convention of the collector."""
    tally = Counter(bitstrings)
    law = np.zeros(1 << width)
    for key, count in tally.items():
        law[int(key, 2)] = count
    return law / len(bitstrings)


def load_run(directory: Path) -> Run:
    """Read a retained run: shot lists from raw/, the measured qubit of each clbit from isa.qpy."""
    from qiskit import qpy

    record = json.loads((directory / "record.json").read_bytes())
    collected = json.loads((directory / "collect.json").read_bytes())[1]
    group = record["groups"][0]
    raw = next((directory / "raw").iterdir())
    with open(directory / "isa.qpy", "rb") as handle:
        circuits = qpy.load(handle)
    pubs = record["execution_pubs"]
    group_members = parallel_group().members
    names = [m.name for m in group_members]
    ideal = {m.name: np.asarray(m.ideal, dtype=float) for m in group_members}
    isolated_member = next(c["member"] for p in pubs for c in p["components"] if c["reference"])
    index = {c["member"]: (i, c) for i, p in enumerate(pubs) for c in p["components"]}
    executed = collected["executed"]
    dists: dict[str, list[np.ndarray]] = {}
    readout: dict[str, list[tuple[list[float], list[float]]]] = {}
    isolated = None
    for member in [*names, isolated_member]:
        position, component = index[member]
        pub = json.loads((raw / f"pub_{position:02d}.json").read_bytes())
        circuit = circuits[position]
        calibration = executed[member]["placed_qubit_calibration"]
        laws, lists = [], []
        for replica, registers in enumerate(component["registers_by_replica"]):
            (name,) = registers
            reg = pub["registers"][name]
            laws.append(counts_to_law(reg["bitstrings"], reg["num_bits"]))
            clreg = next(r for r in circuit.cregs if r.name == name)
            writer = {
                clreg.index(inst.clbits[0]): circuit.find_bit(inst.qubits[0]).index
                for inst in circuit.data
                if inst.operation.name == "measure" and inst.clbits[0] in clreg
            }
            qubits = [writer[bit] for bit in range(len(clreg))]
            lists.append(
                (
                    [calibration[str(q)]["prob_meas1_prep0"] for q in qubits],
                    [calibration[str(q)]["prob_meas0_prep1"] for q in qubits],
                )
            )
            del replica
        if member == isolated_member:
            isolated = laws[0]
        else:
            dists[member] = laws
            readout[member] = lists
    shot_counts = {e["shots"] for e in executed.values()}
    if len(shot_counts) != 1:
        raise ValueError(f"{directory}: executed shots differ across members: {sorted(shot_counts)}")
    usage = json.loads((directory / "collect.json").read_bytes())[0]["invocation_usage"]
    charge = usage.get("total_charge_seconds")
    return Run(
        directory=str(directory.relative_to(ROOT)) if directory.is_relative_to(ROOT) else str(directory),
        backend=group["backend"],
        job_id=collected["job_id"],
        shots=shot_counts.pop(),
        charge_seconds=int(charge) if charge is not None else None,
        calibration=executed[names[0]]["calibration"],
        members=names,
        ideal=ideal,
        dists=dists,
        isolated=isolated,
        isolated_member=isolated_member,
        cz={m["name"]: m["cz"] for m in group["members"]},
        readout=readout,
        model=group["summary_per_replica"],
        stored_summary=collected["measured_statistics"]["summary_per_replica"],
        stored_corrected=collected.get("measured_summary_readout_corrected", {}),
        stored_crosstalk=collected["measured_statistics"].get("global_packing_crosstalk", {}),
        digests={name: sha256(directory / name) for name in ("record.json", "collect.json", "isa.qpy")},
        facts={
            "approved_dry_run": record["prediction_reuse"]["approved_record"],
            "model_calibration": group["noise_model_calibration"],
            "ceiling_seconds": record["policy"]["max_execution_seconds"],
            "operator_excluded_qubits": record["policy"]["operator_excluded_qubits"],
        },
    )


# ---------------------------------------------------------------- statistics


def t_stats(values: list[float] | np.ndarray) -> dict[str, float]:
    """Mean, standard error and the 95 percent Student t interval over the placements (variance.interval)."""
    array = np.asarray(values, dtype=float)
    n = array.size
    interval = variance.interval([float(v) for v in array], 1, False)
    se = float(np.std(array, ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
    return {"n": float(n), "mean": float(array.mean()), "se": se, "lo": interval["lo"], "hi": interval["hi"]}


def half_width(summary: dict[str, float]) -> float:
    return (summary["hi"] - summary["lo"]) / 2.0


def column(rows: list[dict[str, float]], key: str) -> list[float]:
    return [row[key] for row in rows]


def paired(measured: list[dict[str, float]], model: list[dict[str, float]], key: str) -> list[float]:
    return [m[key] - p[key] for m, p in zip(measured, model, strict=True)]


def band_verdict(summary: dict[str, float], band: float, se_factor: float | None = None) -> dict[str, Any]:
    """PASS / FAIL / UNINFORMATIVE of |mean| within `band` (and within se_factor standard errors when given)."""
    mean, se = summary["mean"], summary["se"]
    literal = abs(mean) <= band and (se_factor is None or abs(mean) <= se_factor * se)
    resolved = half_width(summary) <= band
    verdict = "FAIL" if not literal else ("PASS" if resolved else "UNINFORMATIVE")
    return {"verdict": verdict, "literal_pass": bool(literal), "resolves_band": bool(resolved), "band": band}


def worst(verdicts: list[str]) -> str:
    for level in ("FAIL", "UNINFORMATIVE", "not run"):
        if level in verdicts:
            return level
    return "PASS"


def rule(rule_id: str, text: str, verdict: str, numbers: dict[str, Any]) -> dict[str, Any]:
    return {"id": rule_id, "rule": text, "verdict": verdict, **numbers}


# ---------------------------------------------------------------- derived summaries


def summaries(run: Run, laws: dict[str, list[np.ndarray]]) -> list[dict[str, float]]:
    group = parallel_group()
    return [group.summarize({name: laws[name][k] for name in run.members}) for k in range(run.placements)]


def corrected_laws(run: Run) -> dict[str, list[np.ndarray]]:
    """Every member's law with its placement's own confusion matrices inverted, in the raw (unflipped) frame."""
    return {
        name: [
            ppc.invert_readout(run.dists[name][k], *run.readout[name][k])
            if run.readout[name][k]
            else run.dists[name][k]
            for k in range(run.placements)
        ]
        for name in run.members
    }


def readout_only_laws(run: Run) -> dict[str, list[np.ndarray]]:
    """Every member's ideal law through its placement's executed confusion matrices alone (no gate noise): the odd
    part of this law is the calibrated readout asymmetry at the executed calibration."""
    out: dict[str, list[np.ndarray]] = {}
    for name in run.members:
        laws = []
        for k in range(run.placements):
            e01, e10 = run.readout[name][k]
            law = run.ideal[name]
            for bit in range(len(e01)):
                law = ppc.apply_readout_clbit(law, bit, e01[bit], e10[bit])
            laws.append(law)
        out[name] = laws
    return out


def pooled_laws(run: Run, prefix: str) -> dict[str, np.ndarray]:
    return {name: np.mean(laws, axis=0) for name, laws in run.dists.items() if name.startswith(prefix)}


# ---------------------------------------------------------------- rules


def rule_resolution(run: Run, measured: list[dict[str, float]]) -> dict[str, Any]:
    """Every two-term operand's pooled map keeps at least 31 of 32 signs and every block's visibility interval
    lies above 0.5."""
    pooled = map_group().summarize(pooled_laws(run, "cmap_"))
    operands = sorted(k[: -len("_nullity_estimate")] for k in measured[0] if OPERAND_KEY.match(k))
    signs = {op: int(round(pooled[f"{op}_sign_agreement"])) for op in operands}
    mean_signs = {op: float(np.mean(column(measured, f"{op}_sign_agreement"))) for op in operands}
    blocks = sorted(
        {k[: -len("_visibility")] for k in measured[0] if k.startswith("cmap_") and re.search(r"_k\d+_visibility$", k)}
    )
    visibility = {b: t_stats(column(measured, f"{b}_visibility")) for b in blocks}
    lowest = min(blocks, key=lambda b: visibility[b]["lo"])
    sign_ok = all(v >= RESOLUTION_SIGNS for v in signs.values())
    visibility_ok = all(v["lo"] > RESOLUTION_VISIBILITY for v in visibility.values())
    return rule(
        "resolution",
        "pooled map signs at least 31 of 32 per operand; every block's visibility interval above 0.5",
        "PASS" if sign_ok and visibility_ok else "FAIL",
        {
            "pooled_signs_of_32": signs,
            "mean_per_placement_signs_of_32": mean_signs,
            "blocks": len(blocks),
            "lowest_visibility_block": lowest,
            "lowest_visibility_interval": [visibility[lowest]["lo"], visibility[lowest]["hi"]],
            "visibility_mean_range": [
                min(v["mean"] for v in visibility.values()),
                max(v["mean"] for v in visibility.values()),
            ],
        },
    )


def rule_nullity(run: Run, measured: list[dict[str, float]], corrected: list[dict[str, float]]) -> dict[str, Any]:
    """Each operand's N_hat interval covers its model value within 0.5 and the readout-corrected value lies within
    0.15 of the integer nullity."""
    operands = sorted(k[: -len("_nullity_estimate")] for k in measured[0] if OPERAND_KEY.match(k))
    table: dict[str, Any] = {}
    verdicts: list[str] = []
    for op in operands:
        raw = t_stats(column(measured, f"{op}_nullity_estimate"))
        model = float(np.mean(column(run.model, f"{op}_nullity_estimate")))
        ideal = measured[0][f"{op}_nullity_ideal"]
        fixed = t_stats(column(corrected, f"{op}_nullity_estimate"))
        covers = raw["lo"] - NULLITY_BAND <= model <= raw["hi"] + NULLITY_BAND
        mean_rule = abs(raw["mean"] - model) <= NULLITY_BAND
        corrected_ok = abs(fixed["mean"] - round(ideal)) <= NULLITY_CORRECTED_BAND
        verdict = "PASS" if covers and corrected_ok else "FAIL"
        verdicts.append(verdict)
        table[op] = {
            "verdict": verdict,
            "nhat_mean": raw["mean"],
            "nhat_interval": [raw["lo"], raw["hi"]],
            "model_mean": model,
            "case_prose_model": CASE_MODEL_NHAT_FEZ.get(op) if run.backend == "ibm_fez" else None,
            "interval_covers_model_within_0.5": bool(covers),
            "mean_within_0.5_of_model": bool(mean_rule),
            "corrected_mean": fixed["mean"],
            "corrected_interval": [fixed["lo"], fixed["hi"]],
            "integer_nullity": int(round(ideal)),
            "corrected_within_0.15": bool(corrected_ok),
        }
    return rule(
        "nullity_bands",
        "N_hat interval covers its model value within 0.5; readout-corrected within 0.15 of the integer nullity",
        worst(verdicts),
        {"operands": table},
    )


def rule_selector(measured: list[dict[str, float]]) -> dict[str, Any]:
    """Null selector contrast of k0 and of each 1-CZ block, base and flip twin, within two standard errors of zero
    and within 0.006 (estimator-free)."""
    table: dict[str, Any] = {}
    verdicts: list[str] = []
    for k in NULL_BLOCKS:
        for label, key in (("base", "selector_contrast"), ("flip", "flip_selector_contrast")):
            summary = t_stats(column(measured, f"{NULL_OPERAND}_k{k}_{key}"))
            decision = band_verdict(summary, SELECTOR_BAND, SELECTOR_SE)
            verdicts.append(decision["verdict"])
            table[f"k{k}_{label}"] = {
                **decision,
                "mean": summary["mean"],
                "se": summary["se"],
                "interval": [summary["lo"], summary["hi"]],
            }
    k0 = table["k0_base"]
    one_cz_zero = all(
        table[f"k{k}_base"]["literal_pass"] and table[f"k{k}_flip"]["literal_pass"] for k in ONE_CZ_BLOCKS
    )
    signature = k0["mean"] > SELECTOR_BAND and one_cz_zero
    return rule(
        "null_selector_contrast",
        "mean selector contrast within two standard errors of zero and within 0.006 on k0, k4, k8, k12, base and flip",
        worst(verdicts),
        {"blocks": table, "sx_overrotation_signature": bool(signature)},
    )


def rule_null_nhat(measured: list[dict[str, float]], corrected: list[dict[str, float]]) -> dict[str, Any]:
    """Readout-corrected N_hat per placement: the mean of each 1-CZ null block within +-0.02 of zero."""
    table: dict[str, Any] = {}
    verdicts: list[str] = []
    for k in NULL_BLOCKS:
        prefix = f"{NULL_OPERAND}_k{k}"
        raw = t_stats(column(measured, f"{prefix}_nullity_estimate"))
        fixed = t_stats(column(corrected, f"{prefix}_nullity_estimate"))
        flip_fixed = t_stats(column(corrected, f"{prefix}_flip_nullity_estimate"))
        entry: dict[str, Any] = {
            "raw_mean": raw["mean"],
            "corrected_mean": fixed["mean"],
            "corrected_se": fixed["se"],
            "corrected_interval": [fixed["lo"], fixed["hi"]],
            "flip_corrected_mean": flip_fixed["mean"],
            "flip_corrected_se": flip_fixed["se"],
        }
        if k in ONE_CZ_BLOCKS:
            decision = band_verdict(fixed, NULL_NHAT_BAND)
            entry |= decision
            verdicts.append(decision["verdict"])
        table[f"k{k}"] = entry
    return rule(
        "null_nhat_per_placement",
        "readout-corrected N_hat of each 1-CZ null block within +-0.02 of 0 (k0 reported)",
        worst(verdicts),
        {"blocks": table},
    )


def regression(x: list[float], y: list[float]) -> dict[str, Any]:
    fit = stats.linregress(x, y)
    half = float(stats.t.ppf(0.5 + CONFIDENCE / 2, len(x) - 2)) * float(fit.stderr)
    return {
        "slope": float(fit.slope),
        "slope_se": float(fit.stderr),
        "slope_interval_95": [float(fit.slope) - half, float(fit.slope) + half],
        "r_squared": float(fit.rvalue**2),
        "intercept": float(fit.intercept),
    }


def rule_offset(measured: list[dict[str, float]], model: list[dict[str, float]]) -> list[dict[str, Any]]:
    """Odd and even parts of the null operand's N_hat against the model of the same placement."""
    out: list[dict[str, Any]] = []
    even_key, odd_key = f"{NULL_OPERAND}_even_nullity", f"{NULL_OPERAND}_odd_nullity"
    even = t_stats(paired(measured, model, even_key))
    odd = t_stats(paired(measured, model, odd_key))
    out.append(
        rule(
            "offset_even",
            "paired mean of E minus the model's E within +-0.03",
            band_verdict(even, EVEN_BAND)["verdict"],
            {
                **band_verdict(even, EVEN_BAND),
                "paired_mean": even["mean"],
                "paired_se": even["se"],
                "interval": [even["lo"], even["hi"]],
                "measured_mean": float(np.mean(column(measured, even_key))),
                "model_mean": float(np.mean(column(model, even_key))),
            },
        )
    )
    out.append(
        rule(
            "offset_odd",
            "paired mean of O minus the model's O within +-0.04",
            band_verdict(odd, ODD_BAND)["verdict"],
            {
                **band_verdict(odd, ODD_BAND),
                "paired_mean": odd["mean"],
                "paired_se": odd["se"],
                "interval": [odd["lo"], odd["hi"]],
                "measured_mean": float(np.mean(column(measured, odd_key))),
                "model_mean": float(np.mean(column(model, odd_key))),
            },
        )
    )
    fit = regression(column(model, odd_key), column(measured, odd_key))
    slope_ok = SLOPE_RANGE[0] <= fit["slope"] <= SLOPE_RANGE[1]
    r2_ok = fit["r_squared"] > R_SQUARED_MIN
    out.append(
        rule(
            "offset_spread",
            "regression of measured O on the model's O: slope in [0.7, 1.3] and R squared above 0.5",
            "PASS" if slope_ok and r2_ok else "FAIL",
            {
                **fit,
                "slope_in_range": bool(slope_ok),
                "r_squared_above_0.5": bool(r2_ok),
                "model_o_sd": float(np.std(column(model, odd_key), ddof=1)),
            },
        )
    )
    return out


def rule_repeats(measured: list[dict[str, float]]) -> dict[str, Any]:
    """Within-arm repeats of the null operand within two standard errors of zero and within 0.02."""
    table: dict[str, Any] = {}
    verdicts: list[str] = []
    for key in ("within_minus_half_sum", "within_plus_half_sum", "pair_half_sum_gap"):
        summary = t_stats(column(measured, f"{NULL_OPERAND}_{key}"))
        decision = band_verdict(summary, REPEAT_BAND, 2.0)
        verdicts.append(decision["verdict"])
        table[key] = {
            **decision,
            "mean": summary["mean"],
            "se": summary["se"],
            "interval": [summary["lo"], summary["hi"]],
        }
    return rule(
        "within_arm_repeats",
        "mean within two standard errors of zero and within 0.02 for the within-arm repeats and the pair gap",
        worst(verdicts),
        {"quantities": table},
    )


def bernoulli_score(ideal: np.ndarray) -> bool:
    peak = float(np.max(ideal))
    weight = ideal / peak
    return bool(np.all(np.isclose(weight, 0.0) | np.isclose(weight, 1.0)))


def rule_crosstalk(run: Run) -> dict[str, Any]:
    """The 90 percent Newcombe-Wilson interval of packed minus isolated replica-0 score of the null block k0 minus
    arm: inside +-0.015 passes, an interval below -0.015 that excludes zero shows crosstalk, any other is unresolved."""
    member = run.members[0]
    if run.isolated is None or member != "cmap_e1pe17_k0_minus":
        return rule(
            "parallel_crosstalk",
            "packed minus isolated replica-0 score",
            "not run",
            {"reason": "no isolated reference"},
        )
    ideal = run.ideal[member]
    packed, packed_var = variance.score(run.dists[member][0], ideal)
    isolated, isolated_var = variance.score(run.isolated, ideal)
    bernoulli = bernoulli_score(ideal)
    interval = variance.difference_interval(packed, packed_var, isolated, isolated_var, run.shots, bernoulli, 0.90)
    lo, hi = interval
    if -CROSSTALK_BAND <= lo and hi <= CROSSTALK_BAND:
        verdict = "PASS"
    elif hi < -CROSSTALK_BAND:
        verdict = "FAIL"
    else:
        verdict = "UNINFORMATIVE"
    stored = run.stored_crosstalk.get("difference_interval_90")
    return rule(
        "parallel_crosstalk",
        "90 percent Newcombe-Wilson interval of packed minus isolated k0 minus score inside +-0.015",
        verdict,
        {
            "packed_score": packed,
            "isolated_score": isolated,
            "difference": packed - isolated,
            "interval_90": [lo, hi],
            "half_width": (hi - lo) / 2.0,
            "method": "newcombe_wilson" if bernoulli else "hoeffding",
            "shots": run.shots,
            "collector_interval_90": stored,
            "recomputed_matches_collector": bool(
                stored is not None and max(abs(stored[0] - lo), abs(stored[1] - hi)) < 1e-9
            ),
        },
    )


def four_term_prefixes(measured: list[dict[str, float]]) -> list[str]:
    return sorted({m.group(1) for k in measured[0] if (m := FOUR_KEY.match(k))})


def rule_four_term(measured: list[dict[str, float]], model: list[dict[str, float]]) -> dict[str, Any]:
    """Per four-term block: visibility interval above 0.6, closures within 0.03 of the model's, separations at least
    half their ideal value, E0 and E1 levels within 0.02 of the model's."""
    table: dict[str, Any] = {}
    verdicts: list[str] = []
    for prefix in four_term_prefixes(measured):
        visibility = t_stats(column(measured, f"{prefix}_visibility"))
        model_visibility = float(np.mean(column(model, f"{prefix}_visibility")))
        vis_ok = visibility["lo"] > FOUR_VISIBILITY_MIN
        closures: dict[str, Any] = {}
        closure_ok = True
        for arm in ("D2", "F", "E0", "E1", "N", "C"):
            key = f"{prefix}_closure_{arm}"
            if key not in measured[0]:
                continue
            diff = t_stats(paired(measured, model, key))
            decision = band_verdict(diff, FOUR_CLOSURE_BAND)
            closure_ok &= decision["literal_pass"]
            closures[arm] = {
                "measured_mean": float(np.mean(column(measured, key))),
                "model_mean": float(np.mean(column(model, key))),
                "paired_mean": diff["mean"],
                "paired_se": diff["se"],
                "literal_pass": decision["literal_pass"],
            }
        separations: dict[str, Any] = {}
        separation_ok = True
        for arm in ("F", "C", "N"):
            ideal = measured[0][f"{prefix}_level_ideal_T"] - measured[0][f"{prefix}_level_ideal_{arm}"]
            summary = t_stats(column(measured, f"{prefix}_separation_{arm}"))
            reaches = summary["mean"] >= FOUR_SEPARATION_FRACTION * ideal
            separation_ok &= reaches
            separations[arm] = {
                "mean": summary["mean"],
                "ideal": ideal,
                "half_ideal": FOUR_SEPARATION_FRACTION * ideal,
                "reaches_half": bool(reaches),
            }
        null_levels: dict[str, Any] = {}
        null_ok = True
        for arm in ("E0", "E1"):
            diff = t_stats(paired(measured, model, f"{prefix}_level_{arm}"))
            decision = band_verdict(diff, FOUR_NULL_LEVEL_BAND)
            null_ok &= decision["literal_pass"]
            null_levels[arm] = {
                "measured_mean": float(np.mean(column(measured, f"{prefix}_level_{arm}"))),
                "paired_mean": diff["mean"],
                "literal_pass": decision["literal_pass"],
            }
        verdict = "PASS" if vis_ok and closure_ok and separation_ok and null_ok else "FAIL"
        verdicts.append(verdict)
        table[prefix] = {
            "verdict": verdict,
            "visibility_mean": visibility["mean"],
            "visibility_interval": [visibility["lo"], visibility["hi"]],
            "model_visibility": model_visibility,
            "visibility_above_0.6": bool(vis_ok),
            "closures": closures,
            "closures_within_0.03": bool(closure_ok),
            "separations": separations,
            "separations_reach_half": bool(separation_ok),
            "null_levels": null_levels,
            "null_levels_within_0.02": bool(null_ok),
        }
    return rule(
        "four_term_blocks",
        "visibility above 0.6, closures within 0.03 of the model's, separations at half their ideal, "
        "null levels within 0.02",
        worst(verdicts),
        {"blocks": table},
    )


# ---------------------------------------------------------------- one backend and the devices


def check_corrected(run: Run, corrected: list[dict[str, float]]) -> dict[str, Any]:
    """The per-placement correction against the collector's pooled readout-corrected summary."""
    if not run.stored_corrected:
        return {"status": "not run", "reason": "collect.json holds no measured_summary_readout_corrected"}
    keys = [
        k
        for k, v in run.stored_corrected.items()
        if isinstance(v, (int, float)) and k in corrected[0] and math.isfinite(v)
    ]
    gap = max(abs(float(np.mean(column(corrected, k))) - run.stored_corrected[k]) for k in keys)
    return {"status": "checked", "keys": len(keys), "max_abs_difference": gap}


def check_summaries(run: Run, measured: list[dict[str, float]]) -> dict[str, Any]:
    """The summaries recomputed from raw counts against collect.json's (its laws are rounded to 6 decimals)."""
    if not run.stored_summary:
        return {"status": "not run", "reason": "collect.json holds no per-placement summary"}
    keys = [k for k, v in run.stored_summary[0].items() if k in measured[0] and v is not None and math.isfinite(v)]
    gap = max(abs(measured[p][k] - run.stored_summary[p][k]) for p in range(run.placements) for k in keys)
    return {"status": "checked", "keys": len(keys), "max_abs_difference": gap}


def deviations(run: Run) -> dict[str, Any]:
    """How the executed run differs from the case as approved; the bands stay as the case wrote them."""
    case = CASE_FACTS[run.backend]
    return {
        "shots_per_member": {"case": case["shots"], "run": run.shots},
        "ceiling_seconds": {"case": case["ceiling_seconds"], "run": run.facts["ceiling_seconds"]},
        "binding_dry_run": {"case": case["binding_dry_run"], "model_of_record": run.facts["approved_dry_run"]},
        "estimated_seconds": case["estimated_seconds"],
        "charged_seconds": run.charge_seconds,
        "model_calibration": run.facts["model_calibration"],
        "executed_calibration": run.calibration,
    }


def analyze_run(run: Run) -> dict[str, Any]:
    measured = summaries(run, run.dists)
    corrected = summaries(run, corrected_laws(run))
    readout_only = summaries(run, readout_only_laws(run))
    odd_key = f"{NULL_OPERAND}_odd_nullity"
    drift = {
        "measured_minus_readout_only_odd": t_stats(paired(measured, readout_only, odd_key)),
        "model_minus_readout_only_odd": t_stats(paired(run.model, readout_only, odd_key)),
    }
    rules = [
        rule_resolution(run, measured),
        rule_nullity(run, measured, corrected),
        rule_selector(measured),
        rule_null_nhat(measured, corrected),
        *rule_offset(measured, run.model),
        rule_repeats(measured),
        rule_crosstalk(run),
        rule_four_term(measured, run.model),
    ]
    operands = sorted(k[: -len("_nullity_estimate")] for k in measured[0] if OPERAND_KEY.match(k))
    return {
        "backend": run.backend,
        "run": run.directory,
        "job_id": run.job_id,
        "shots_per_member": run.shots,
        "placements": run.placements,
        "charge_seconds": run.charge_seconds,
        "calibration": run.calibration,
        "deviations_from_case": deviations(run),
        "input_sha256": run.digests,
        "checks": {
            "summaries_vs_collect": check_summaries(run, measured),
            "corrected_vs_collect": check_corrected(run, corrected),
        },
        "rules": {r["id"]: r for r in rules},
        "operand_nhat": {op: t_stats(column(measured, f"{op}_nullity_estimate")) for op in operands},
        "per_placement": {
            "o_measured": column(measured, f"{NULL_OPERAND}_odd_nullity"),
            "o_model": column(run.model, f"{NULL_OPERAND}_odd_nullity"),
            "e_measured": column(measured, f"{NULL_OPERAND}_even_nullity"),
            "e_model": column(run.model, f"{NULL_OPERAND}_even_nullity"),
            "o_readout_only": column(readout_only, odd_key),
        },
        "calibration_drift_check": drift,
    }


def rule_devices(per_backend: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The two backends' operand N_hat agree within the sum of their intervals, and each backend's odd and even parts
    pass their bands against its own model."""
    names = sorted(per_backend)
    if len(names) < 2:
        return rule("devices", "two backends compared", "not run", {"reason": f"{len(names)} backend(s) given"})
    first, second = (per_backend[n] for n in names[:2])
    table: dict[str, Any] = {}
    agree = True
    for op in first["operand_nhat"]:
        a, b = first["operand_nhat"][op], second["operand_nhat"][op]
        reach = half_width(a) + half_width(b)
        gap = abs(a["mean"] - b["mean"])
        table[op] = {"difference": a["mean"] - b["mean"], "sum_of_half_widths": reach, "agree": bool(gap <= reach)}
        agree &= gap <= reach
    bands = {n: {rid: per_backend[n]["rules"][rid]["verdict"] for rid in ("offset_even", "offset_odd")} for n in names}
    verdict = worst(["PASS" if agree else "FAIL", *(v for n in names for v in bands[n].values())])
    return rule(
        "devices",
        "operand N_hat agree within the sum of the intervals; each backend's odd and even parts pass against its model",
        verdict,
        {"backends": names, "operands": table, "operand_agreement": bool(agree), "odd_even_verdicts": bands},
    )


def rounded(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): rounded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [rounded(v) for v in value]
    if isinstance(value, (np.floating, float)):
        return round(float(value), DECIMALS) if math.isfinite(float(value)) else None
    if isinstance(value, np.integer):
        return int(value)
    return value


def analyze(runs: list[Run]) -> dict[str, Any]:
    per_backend = {run.backend: analyze_run(run) for run in runs}
    return rounded(
        {
            "schema": SCHEMA,
            "case": CASE,
            "interval": "Student t, 95 percent, over placements",
            "backends": per_backend,
            "cross_device": rule_devices(per_backend),
        }
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", nargs="+", required=True, type=Path, help="retained run directories")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    result = analyze([load_run(path.resolve()) for path in args.run])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True, allow_nan=False) + "\n")
    for name, body in result["backends"].items():
        print(name, {rid: r["verdict"] for rid, r in body["rules"].items()})
    print("devices", result["cross_device"]["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
