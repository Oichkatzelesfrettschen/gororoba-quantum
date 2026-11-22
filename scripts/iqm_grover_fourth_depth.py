"""IQM Garnet fourth Grover depth with every depth arm at positions mirrored about the job's center.

The retained run grover-depth-sedenion-walsh (docs/design/iqm-garnet-grover-depth-sedenion-walsh.md) measured the
marked-state retention of the line-native Grover of mark 101 at depths 1, 2 and 3 as lambda = 0.831, 0.730, 0.519
and read f = lambda_3 - lambda_2^2 / lambda_1 = -0.122 against a geometric law's 0 (the model reads +0.010). Its
open hypothesis names two causes of the bend, a coherent error that accumulates with iterations and positional drift
across the job; the retained bytes exclude linear and symmetric positional drift
(docs/evidence/iqm-garnet-grover-positions on branch iqm-qb12-fault-models).

This case puts the arms of depth 1, 2, 3 and 4 at positions mirrored about the center of one job, so a drift linear
in position leaves every depth's pooled frequency unchanged, and adds the fourth depth. The ideal marked
probability is 0.781, 0.945, 0.330 and 0.012 at depths 1 to 4; the retained fits continue to depth 4 as lambda_4 =
A r^4 (geometric) or r^4 (Q_4(eps) - 1/8) / (P_4 - 1/8) (an oracle-phase error eps per iteration, gororoba_quantum/
grover_depth_families.py). The case's decisions are the bend at mirrored positions and the chi-square comparison of
the two families over four depths.

Job "grover" (three qubits, path QB20-QB16-QB17 of the retained case, as scripts/iqm_garnet_followup.py):
  m101-k{1,2,3,4}-c{n}  the line-native Grover of mark 101, COPIES[k] copies of each depth. The first half of the
                        job holds half the copies in an order chosen by arrangement(), the eight readout
                        preparations ro-xyz hold the center, and the second half repeats the first half reversed,
                        so each depth's summed position equals its copies times the job's center and the spread of
                        its squared offsets is the smallest the multiset allows.

Every prediction is the exact density matrix of iqm_grover_line.predicted's model through
iqm_garnet_followup.predicted: depolarizing PRX and CZ, idle T1 and T2 over the ASAP schedule, herald-conditioned
readout; no coherent error. The case draws no random number, so it takes no seed.

Usage: "$PYTHON" scripts/iqm_grover_fourth_depth.py (build DIR --calibration SRC | check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_garnet_followup as followup  # noqa: E402
import iqm_grover_line as grover  # noqa: E402
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, JOB_SECONDS, ceiling_credits, ceiling_seconds, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import CALIBRATION_FILES, OPTIONS  # noqa: E402

import grover_depth_families as families  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "grover-fourth-depth-mirrored"
QCS = ["garnet:mock", "garnet"]
PRICE = grover.PRICE
PATH = followup.FORWARD_PATH
MARKED = "101"
SHOTS = 20000
# Copies per depth; each is even so that every copy has a mirror image.
COPIES = {1: 4, 2: 4, 3: 4, 4: 6}
READOUTS = 8
# Kept fraction of the retained depth arms: 13,450 of 16,000, 3,377 and 3,383 of 4,000 (0.841, 0.844, 0.846).
KEPT_PLAN = 0.84
# Seconds per circuit-shot of the retained Grover depth job: 1.99852 s of execution over 144,000 circuit-shots is
# 13.9 us, which carries the job's fixed 0.13 s; the depth-4 circuits add about 14 CZ (40 ns each) to the retained
# depth-3 schedule, and 14.5 us bounds the job's mean.
CIRCUIT_SHOT_SECONDS = 14.5e-6
# Billed seconds the credit ceiling carries above the expected ones (iqm_jobs.ceiling_credits adds JOB_SECONDS).
CEILING_MARGIN_SECONDS = 3
RETAINED_ANALYSIS = ROOT / "results" / "iqm" / "garnet_grover_depth_sedenion_walsh_analysis.json"


def arrangement() -> list[int]:
    """Depths of the job's circuits in order: half of every depth's copies, the readout block, the first half
    reversed. Of the orderings of the first half, the one whose depths have the most nearly equal mean squared
    offset from the job's center (the first in sorted order among ties), so a drift quadratic in position also
    enters every depth equally to the first order the multiset allows."""
    half = [k for k in sorted(COPIES) for _ in range(COPIES[k] // 2)]
    total = 2 * len(half) + READOUTS
    center = (total - 1) / 2
    best: tuple[float, tuple[int, ...]] | None = None
    for order in sorted(set(itertools.permutations(half))):
        positions = {k: [] for k in COPIES}
        for p, k in enumerate(order):
            positions[k] += [p, total - 1 - p]
        spread = [sum((p - center) ** 2 for p in positions[k]) / len(positions[k]) for k in COPIES]
        score = max(spread) - min(spread)
        if best is None or score < best[0] - 1e-12:
            best = (score, order)
    if best is None:
        raise ValueError("no arrangement")
    return [*best[1], *([0] * READOUTS), *best[1][::-1]]


def depth_arms() -> list[dict[str, Any]]:
    order = arrangement()
    seen = {k: 0 for k in COPIES}
    out: list[dict[str, Any]] = []
    bits = ["".join(b) for b in itertools.product("01", repeat=3)]
    readout = 0
    for k in order:
        if k == 0:
            circuit = followup.readout_circuit(bits[readout], PATH, "ro")
            out.append({"name": circuit["name"], "circuit": circuit, "marked": None, "k": None})
            readout += 1
            continue
        name = f"m{MARKED}-k{k}-c{seen[k]}"
        seen[k] += 1
        out.append({"name": name, "circuit": grover.line_arm(MARKED, k, PATH, name)[1], "marked": MARKED, "k": k})
    if seen != COPIES or readout != READOUTS:
        raise AssertionError(f"arrangement holds {seen} and {readout} readouts")
    total = len(out)
    for k in COPIES:
        at = [n for n, a in enumerate(out) if a["k"] == k]
        if sum(at) != len(at) * (total - 1) / 2 or any(out[total - 1 - n]["k"] != k for n in at):
            raise AssertionError(f"depth {k} copies are not mirrored: positions {at}")
    return out


def retained_inputs() -> dict[str, Any]:
    """The retained job's raw retention at depths 1 to 3 and its kept shots, read from the retained analysis."""
    record = json.loads(RETAINED_ANALYSIS.read_text(encoding="utf-8"))
    lam = record["decisions"]["depth_law_101"]["lambda_raw"]
    arms = record["exploratory"]["grover"]["arms"]
    return {
        "lambda": [float(lam[str(k)]) for k in (1, 2, 3)],
        "kept": [int(arms[f"m101-k{k}"]["kept_shots"]) for k in (1, 2, 3)],
        "f_raw": record["decisions"]["depth_law_101"]["f_raw"],
    }


def planned_kept() -> list[float]:
    return [COPIES[k] * SHOTS * KEPT_PLAN for k in families.DEPTHS]


def rounded(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    if isinstance(x, list):
        return [rounded(v) for v in x]
    return round(x, 6) if isinstance(x, float) else x


def decisions(arm_records: dict[str, Any]) -> dict[str, Any]:
    retained = retained_inputs()
    cont = families.continuations(retained["lambda"], retained["kept"])
    # Each family's values at depths 1 to 4 are the data the rule would see if that family held exactly.
    kept = planned_kept()
    sep = families.separation(cont["geometric"], cont["coherent"], kept)
    model_lam = [
        families.retention(
            float(np.mean([a["predicted_marked"] for n, a in arm_records.items() if n.startswith(f"m101-k{k}-c")])), k
        )
        for k in families.DEPTHS
    ]
    model_f, model_f_se = families.bend(model_lam, kept)
    model_se = [families.standard_error(x, k, n) for x, k, n in zip(model_lam, families.DEPTHS, kept, strict=True)]
    model_geo = families.fit_geometric(model_lam, model_se, families.DEPTHS)
    model_coh = families.fit_coherent(model_lam, model_se, families.DEPTHS)
    last_se = families.standard_error(cont["geometric_next"], 4, kept[3])
    return rounded(
        {
            "z_resolve": families.Z_RESOLVE,
            "planned_kept_shots": {str(k): n for k, n in zip(families.DEPTHS, kept, strict=True)},
            "retained": {
                "source": RETAINED_ANALYSIS.relative_to(ROOT).as_posix(),
                "lambda_raw": dict(zip(("1", "2", "3"), retained["lambda"], strict=True)),
                "kept_shots": dict(zip(("1", "2", "3"), retained["kept"], strict=True)),
                "f_raw": retained["f_raw"],
                "geometric_fit": cont["geometric"],
                "coherent_fit": cont["coherent"],
                "geometric_lambda_4": cont["geometric_next"],
                "coherent_lambda_4": cont["coherent_next"],
            },
            "resolution": {
                "lambda_4_difference": sep["last_depth_difference"],
                "se_lambda_4_at_planned_shots": last_se,
                "z": sep["last_depth_z"],
                "chi2_geometric_fit_to_coherent_values": sep["chi2_geometric_on_coherent_data"],
                "chi2_coherent_fit_to_geometric_values": sep["chi2_coherent_on_geometric_data"],
                "rule": (
                    "the retained geometric and coherent fits continued to depth 4 differ by lambda_4_difference; "
                    "z is that difference over the binomial standard error of lambda_4 from the planned kept shots "
                    "of the larger-error value; each chi-square is what the other family leaves when the four "
                    "depths equal one family's values at the planned shots, to be compared with delta_resolve"
                ),
                "delta_resolve": families.DELTA_RESOLVE,
            },
            "model": {
                "lambda": dict(zip(("1", "2", "3", "4"), model_lam, strict=True)),
                "f": model_f,
                "f_se_at_planned_shots": model_f_se,
                "geometric_fit": model_geo,
                "coherent_fit": model_coh,
            },
            "rule": {
                "bend": (
                    "f = lambda_3 - lambda_2^2 / lambda_1 from raw pooled marked frequencies of the depth arms "
                    "(copies pooled, binomial variances at the observed frequencies, delta method over the three "
                    "arms), z = (f - model.f) / SE; z <= -3 reads 'the retention law bends at mirrored positions', "
                    "which excludes positional drift linear in position as the cause of the retained bend; z >= 3 "
                    "reads 'bends upward'; otherwise 'no bend resolved at mirrored positions'"
                ),
                "family": (
                    "weighted least squares of the geometric family A r^k and the coherent family "
                    "r^k (Q_k(eps) - 1/8) / (P_k - 1/8) to lambda_1 to lambda_4 (gororoba_quantum/"
                    "grover_depth_families.py); with chi2 of each fit (two degrees of freedom): 'neither family "
                    "fits' when both exceed 9.21; else 'coherent' when chi2_geometric - chi2_coherent >= 9, "
                    "'geometric' when it is <= -9, else 'unresolved'"
                ),
                "beside": (
                    "lambda_4 against the retained fits' continuations in standard errors, and whether the "
                    "retention decreases with depth; neither decides"
                ),
                "function": "grover_depth_families.verdict",
            },
        }
    )


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    retained_case = json.loads((followup.RETAINED_CASE / "prediction.json").read_text(encoding="utf-8"))
    if retained_case["path"] != PATH:
        raise ValueError(f"the retained case ran on {retained_case['path']}, not {PATH}")
    arms = depth_arms()
    files = {f"circuits/{a['name']}.json": dump(a["circuit"]) for a in arms}
    names = [a["name"] for a in arms]
    distributions = ordered_map(
        followup.predicted, [(files[f"circuits/{n}.json"], str(calibration_dir)) for n in names], min_items=1
    )
    predictions = dict(zip(names, distributions, strict=True))
    arm_records: dict[str, Any] = {}
    for position, arm in enumerate(arms):
        c = arm["circuit"]
        record: dict[str, Any] = {
            "job": "grover",
            "position": position,
            "locus": c["instructions"][-1]["locus"],
            "cz": followup.count(c, "cz"),
            "prx": followup.count(c, "prx"),
            "predicted": predictions[arm["name"]],
        }
        if arm["marked"] is not None:
            record |= {
                "marked": arm["marked"],
                "iterations": arm["k"],
                "ideal_marked": families.ideal_marked(arm["k"]),
                "predicted_marked": predictions[arm["name"]][arm["marked"]],
            }
        arm_records[arm["name"]] = record
    expected = round(len(arms) * SHOTS * CIRCUIT_SHOT_SECONDS, 3)
    ceiling = {qc: ceiling_credits(expected, PRICE[qc], JOB_SECONDS) for qc in QCS}
    max_credits = {
        qc: (ceiling_seconds(ceiling[qc], PRICE[qc]) + CEILING_MARGIN_SECONDS) * PRICE[qc] if PRICE[qc] else 0.0
        for qc in QCS
    }
    job = {
        "job": "grover",
        "circuits": [
            {"file": f"circuits/{a['name']}.json", "sha256": sha256(files[f"circuits/{a['name']}.json"].encode())}
            for a in arms
        ],
        "shots": SHOTS,
        "options": {**OPTIONS, "calibration_set_id": {"garnet": calibration.set_id}},
        "expected_seconds": expected,
        "max_credits": max_credits,
    }
    prediction = {
        "calibration_set": calibration.set_id,
        "forward_path": PATH,
        "copies": {str(k): n for k, n in COPIES.items()},
        "arms": arm_records,
        "decisions": decisions(arm_records),
        "model": (
            "exact density matrix: iqm_sim depolarizing PRX and CZ, ASAP idle T1/T2, herald-conditioned readout "
            "assignment; no coherent error, leakage or crosstalk"
        ),
    }
    files["prediction.json"] = dump(prediction)
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            # The approval quotes this file's digest, so the prediction the verdict decides against is bound.
            "prediction_sha256": sha256(files["prediction.json"].encode()),
            "question": (
                "With the line-native Grover of mark 101 at depths 1 to 4 placed at positions mirrored about the "
                "job's center on one Garnet calibration, does the retention law still bend at depth 3, and do the "
                "four retentions follow a geometric law or an oracle-phase coherent error that accumulates with "
                "iterations?"
            ),
            "qcs": QCS,
            "jobs": [job],
        }
    )
    return files, prediction


def write(directory: Path, source: Path) -> None:
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    for name in CALIBRATION_FILES:
        shutil.copyfile(source / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir)
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(json.dumps(prediction["decisions"], indent=1))


def check(directory: Path) -> None:
    files, _ = build_from(directory / "calibration")
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(files) | {f"calibration/{name}" for name in CALIBRATION_FILES}
    if present != expected:
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ expected)}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def counts_of(lam: list[float], kept: list[int]) -> list[int]:
    return [round(families.probability_of(x, k) * n) for x, k, n in zip(lam, families.DEPTHS, kept, strict=True)]


def self_test() -> str:
    """Circuits against their exact ideal, the arrangement's mirror invariants, the families, and the verdict on
    planted data."""
    arms = depth_arms()
    path = ["QA", "QB", "QC"]
    for arm in arms:
        if arm["k"] is None:
            continue
        circuit = grover.line_arm(MARKED, arm["k"], path, "t")[1]
        p = followup.ideal(circuit, path)[int(MARKED[::-1], 2)]
        require(abs(p - families.ideal_marked(arm["k"])) < 1e-9, f"depth {arm['k']}: P(marked) {p}")
        require(followup.count(circuit, "cz") == 14 * arm["k"], f"depth {arm['k']}: CZ count")
    require(len(arms) == sum(COPIES.values()) + READOUTS and len(arms) <= 100, "circuits per job")
    require(len(arms) * SHOTS <= 2_000_000 and SHOTS <= 20_000, "Garnet job limits")
    total = len(arms)
    center = (total - 1) / 2
    means = {
        k: float(np.mean([(n - center) ** 2 for n, a in enumerate(arms) if a["k"] == k])) for k in COPIES
    }
    require(max(means.values()) - min(means.values()) < 0.2 * min(means.values()), f"squared offsets {means}")
    require(
        all(arms[n]["name"][:7] == arms[total - 1 - n]["name"][:7] for n in range(total) if arms[n]["k"]),
        "mirror images carry the same depth",
    )
    # eps = 0 is the ideal rotation; the families agree with the exact two-dimensional recursion.
    zero = np.zeros(1)
    for k in families.DEPTHS:
        require(abs(float(families.oracle_phase_probability(k, zero)[0]) - families.ideal_marked(k)) < 1e-12, "eps 0")
    # Planted recovery: noise-free values of each family return their own parameters with chi2 near zero.
    kept = [int(n) for n in planned_kept()]
    geo_truth = {"A": 0.97, "r": 0.86}
    coh_truth = {"eps": 0.19, "r": 0.85}
    geo_lam = families.geometric_values(geo_truth, families.DEPTHS)
    coh_lam = families.coherent_values(coh_truth, families.DEPTHS)
    for lam, want in ((geo_lam, "geometric"), (coh_lam, "coherent")):
        read = families.verdict(counts_of(lam, kept), kept, 0.0, {"geometric_next": geo_lam[3], "coherent_next": coh_lam[3]})
        require(read["family"] == want, f"planted {want}: {read['family']} (delta {read['delta_chi2']})")
    # Planted bend: lambda_3 below the geometric value at the retained size reads as a bend.
    bent = [0.85, 0.72, 0.52, 0.45]
    read = families.verdict(counts_of(bent, kept), kept, 0.0, {"geometric_next": 0.5, "coherent_next": 0.5})
    require(read["bend"]["reading"] == "the retention law bends at mirrored positions", f"bend {read['bend']}")
    require(read["family"] == "neither family fits", f"bent data: {read['family']}")
    flat = families.verdict(counts_of(geo_lam, kept), kept, 0.0, {"geometric_next": 0.5, "coherent_next": 0.5})
    require(flat["bend"]["reading"] == "no bend resolved at mirrored positions", f"flat {flat['bend']}")
    for bad in ([1, 2, 3], [-1, 0, 0, 0]):
        try:
            families.verdict(bad, [10, 10, 10, 10][: len(bad)], 0.0, {})
        except ValueError:
            continue
        raise AssertionError(f"verdict accepted counts {bad}")
    # Billing arithmetic: the job's ceiling lies below max_credits, whose cancel threshold exceeds the expected run.
    expected = round(total * SHOTS * CIRCUIT_SHOT_SECONDS, 3)
    garnet_max = (ceiling_seconds(ceiling_credits(expected, PRICE["garnet"], JOB_SECONDS), PRICE["garnet"]) + CEILING_MARGIN_SECONDS) * PRICE["garnet"]
    require(ceiling_credits(expected, PRICE["garnet"], JOB_SECONDS) < garnet_max, "ceiling below max_credits")
    return "self-test passed: 3 depth circuits against ideal, mirror invariants, families, 4 planted verdicts, 2 refusals"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    b = sub.add_parser("build")
    b.add_argument("directory", type=Path)
    b.add_argument("--calibration", type=Path, required=True)
    sub.add_parser("check").add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.calibration)
    elif args.command == "check":
        check(args.directory)
    else:
        parser.error("choose build, check or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
