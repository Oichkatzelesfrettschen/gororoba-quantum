"""Gate-model scatter floor of the measurement-sequence pinching analysis, from the diagnostic family.

The measurement-sequence-diagnostic family (diagnostic_experiments.MSQD_*) runs the four signed unitary members at
N = 16, ro0 and ro1 on the main family's qubits and further qubits, all in six static PUBs. This module holds

- the calibration-only rule that picks the further qubits and the structural checks the planner applies to a layout;
- the per-qubit residual of the readout-corrected unitary N = 16 P0 against the analysis model, built through the
  functions the main analysis uses (measurement_sequence_analysis.model_tables, propagate_many, var);
- the floor rule: the root-mean-square residual over informative qubits, kept at the larger of the all-qubit and the
  main-qubit value, with the statistical noise left in;
- the descriptive test of the residual's sign pattern against T2;
- the scatter-floor.json document that measurement_sequence_analysis.bound_floor reads.

The rule is fixed in docs/design/measurement-sequence-pinching.md, "Source of the model-scatter floor", before any
diagnostic data exists. The module draws no random number.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

import measurement_sequence_analysis as msa
from diagnostic_experiments import MSQD_FAMILY, MSQD_MAIN_QUBITS, MSQD_MAIN_QUBITS_BY_BACKEND
from parallel import ordered_map

SCHEMA = "measurement-sequence-scatter-v1"
FLOOR_SCHEMA = msa.SCATTER_FLOOR_SCHEMA

# Calibration-only qubit rule. A further qubit is eligible when the live Target does not exclude it and reports a
# readout error and an sx error within these bounds and both coherence times at least COHERENCE_MIN_S. No bound
# selects on T1 or T2 beyond the minimum, so the T2 pattern test keeps its spread. The bounds cover the main qubits.
READOUT_ERROR_MAX = 0.01
SX_ERROR_MAX = 1.0e-3
COHERENCE_MIN_S = 20.0e-6
EXTRA_COUNT = 30
# The fewest diagnostic qubits, main and further together, a floor rests on: the eight main and thirty further qubits
# of the ibm_kingston diagnostic. A backend whose main layout blocks more of the coupling graph keeps fewer further
# qubits and still meets it with more main ones.
DIAGNOSTIC_MIN_QUBITS = 38
# Fewer informative qubits than this leave the root-mean-square without a usable sampling error (1 / sqrt(2 n)).
MIN_INFORMATIVE = 20

SELECTION_RULE = (
    f"eligible: not excluded by the live Target, readout error <= {READOUT_ERROR_MAX}, sx error <= {SX_ERROR_MAX}, "
    f"T1 and T2 >= {COHERENCE_MIN_S * 1e6:g} us, and coupled to no main qubit; scan the eligible qubits in ascending "
    f"readout error (ties by index) and keep a qubit coupled to no kept qubit, until {EXTRA_COUNT} are kept"
)
FLOOR_RULE = (
    "the floor is the larger of the root-mean-square, over informative diagnostic qubits, of the readout-corrected "
    "unitary N = 16 residual (observed minus the analysis model) taken over all of them and over the main qubits "
    "alone; statistical noise stays in"
)


class ScatterError(ValueError):
    pass


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ScatterError(message)


# --- calibration-only qubit rule ----------------------------------------------------------------------------


def calibration_from_snapshot(snapshot: Any) -> dict[str, Any]:
    """Per qubit readout error, sx error, T1 and T2 (seconds), the couplers and the excluded qubits of a Snapshot."""
    target = snapshot.backend.target
    properties = snapshot.properties

    def error(name: str, q: int) -> float | None:
        # The runtime's Target drops an instruction on a non-operational qubit; the qubit then reads ineligible.
        entry = target[name].get((q,))
        return None if entry is None else entry.error

    qubits: dict[int, dict[str, float | None]] = {}
    for q in range(target.num_qubits):
        qubit = properties.qubit_property(q)
        t1 = qubit.get("T1", (None,))[0]
        t2 = qubit.get("T2", (None,))[0]
        qubits[q] = {
            "readout_error": error("measure", q),
            "sx_error": error("sx", q),
            "t1_s": None if t1 is None else float(t1),
            "t2_s": None if t2 is None else float(t2),
        }
    edges = sorted({tuple(sorted(int(x) for x in edge)) for edge in target["cz"]})
    return {
        "qubits": qubits,
        "edges": [list(e) for e in edges],
        "excluded": sorted(int(q) for q in snapshot.excluded_qubits),
    }


def eligible(row: dict[str, float | None]) -> bool:
    values = (row["readout_error"], row["sx_error"], row["t1_s"], row["t2_s"])
    if any(v is None for v in values):
        return False
    readout, sx, t1, t2 = (float(v) for v in values if v is not None)
    return readout <= READOUT_ERROR_MAX and sx <= SX_ERROR_MAX and min(t1, t2) >= COHERENCE_MIN_S


def adjacency(edges: list[list[int]]) -> dict[int, set[int]]:
    graph: dict[int, set[int]] = {}
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)
    return graph


def diagnostic_main(backend: str) -> tuple[int, ...]:
    """The main qubits a diagnostic run on `backend` carries, from MSQD_MAIN_QUBITS_BY_BACKEND."""
    if backend not in MSQD_MAIN_QUBITS_BY_BACKEND:
        raise ScatterError(f"no diagnostic main qubits are registered for {backend}")
    return MSQD_MAIN_QUBITS_BY_BACKEND[backend]


def select_extra_qubits(
    calibration: dict[str, Any],
    main: tuple[int, ...] = MSQD_MAIN_QUBITS,
    count: int = EXTRA_COUNT,
    minimum: int | None = None,
) -> list[int]:
    """The further qubits SELECTION_RULE keeps, in the order it keeps them: up to `count`, refused below `minimum`
    diagnostic qubits in all (main and kept), which defaults to the main qubits plus all `count`."""
    graph = adjacency(calibration["edges"])
    excluded = set(calibration["excluded"])
    blocked = set(main)
    for q in main:
        blocked |= graph.get(q, set())
    kept: list[int] = []
    pool = sorted(
        (q for q, row in calibration["qubits"].items() if eligible(row) and q not in excluded),
        key=lambda q: (float(calibration["qubits"][q]["readout_error"]), q),
    )
    for q in pool:
        if q in blocked:
            continue
        kept.append(q)
        blocked |= {q} | graph.get(q, set())
        if len(kept) == count:
            break
    required = len(main) + count if minimum is None else minimum
    check(
        len(main) + len(kept) >= required,
        f"the rule keeps {len(kept)} of {count} further qubits beside {len(main)} main ones, "
        f"below {required} diagnostic qubits",
    )
    return kept


def layout_violations(qubits: list[int], edges: list[list[int]], excluded: set[int]) -> list[str]:
    """Structural faults of a diagnostic layout: a duplicate or excluded qubit or a coupled pair."""
    graph = adjacency(edges)
    faults = []
    if len(set(qubits)) != len(qubits):
        faults.append("the layout repeats a qubit")
    if bad := sorted(set(qubits) & excluded):
        faults.append(f"the calibration excludes {bad}")
    coupled = sorted((a, b) for a in qubits for b in qubits if a < b and b in graph.get(a, set()))
    if coupled:
        faults.append(f"coupled pairs {coupled}")
    return faults


# --- residual of one qubit ----------------------------------------------------------------------------------

TOP = str(msa.TOP_STEPS)


def planning_q() -> float:
    """q = z_eq / (1 - 2 p) at the planning excitation; the unitary arm's modeled P0 moves by under 1e-3 over
    T1 x 0.5 to x 2 and p from 0 to 0.1, because its 32 sx last about 1 us."""
    return 1 / (1 - 2 * msa.PLANNING_P_INIT)


def diagnostic_row(item: tuple[int, dict[str, tuple[int, int]], dict[str, Any]]) -> dict[str, Any]:
    """The unitary N = 16 residual of one qubit, with its statistical and sx-systematic standard errors."""
    qubit, member_counts, ctx = item
    pooled = {
        "ro0": msa.pooled_obs(member_counts, [msa.ro0_name(qubit)]),
        "t1-0": msa.pooled_obs(member_counts, [msa.t1_names(qubit)[0]]),
        "unitary": msa.pooled_obs(member_counts, msa.member_names("unitary", msa.TOP_STEPS, qubit)),
    }
    keys = ["ro0", "t1-0", "unitary", "sx_shift"]
    x = [pooled[k][0] / pooled[k][1] for k in keys[:3]] + [0.0]
    variances = [msa.var(*pooled[k]) for k in keys[:3]] + [(msa.SX_SYSTEMATIC * ctx["sx_error"]) ** 2]
    scale = x[1] - x[0]
    row: dict[str, Any] = {
        "qubit": qubit,
        "readout_scale": scale,
        "t1_cal_s": ctx["t1_cal_s"],
        "t2_s": ctx["t2_s"],
        "sx_error": ctx["sx_error"],
        "shots": pooled["unitary"][1],
    }
    if not scale >= msa.READOUT_CONTRAST_FLOOR:
        return {**row, "informative": False, "reason": f"readout scale {scale:.4f} lies below the floor"}
    q = planning_q()

    def figures(xs: list[float]) -> dict[str, float]:
        p = dict(zip(keys, xs, strict=True))
        z0, z1 = 1 - 2 * p["ro0"], 1 - 2 * p["t1-0"]
        s, offset = (z0 - z1) / 2, (z0 + z1) / 2
        p0 = (1 + ((1 - 2 * p["unitary"]) - offset) / s) / 2
        model = msa.model_tables(ctx["t1_cal_s"], q, ctx, p["sx_shift"], msa.WINDOW_RELAX_FRACTION)["unitary"][TOP]
        return {"p0": p0, "model": model, "residual": p0 - model}

    value, se, shared = msa.propagate_many(figures, x, variances, frozenset({3}))
    stat = math.sqrt(max(se["residual"] ** 2 - shared["residual"] ** 2, 0.0))
    return {
        **row,
        "informative": True,
        "reason": None,
        "p0": value["p0"],
        "modeled": value["model"],
        "ideal": msa.ideal_delay(),
        "residual": value["residual"],
        "se_statistical": stat,
        "se_sx_systematic": shared["residual"],
        "z_statistical": value["residual"] / stat if stat > 0 else None,
    }


# --- floor and T2 pattern -----------------------------------------------------------------------------------


def rms(values: list[float]) -> float:
    return math.sqrt(math.fsum(v * v for v in values) / len(values))


def floor_summary(rows: list[dict[str, Any]], main: tuple[int, ...] = MSQD_MAIN_QUBITS) -> dict[str, Any]:
    """The floor and the figures around it from the per-qubit rows; withheld below MIN_INFORMATIVE qubits."""
    informative = [r for r in rows if r["informative"]]
    main_rows = [r for r in informative if r["qubit"] in main]
    extra_rows = [r for r in informative if r["qubit"] not in main]
    out: dict[str, Any] = {
        "informative": len(informative),
        "informative_main": len(main_rows),
        "informative_extra": len(extra_rows),
        "min_informative": MIN_INFORMATIVE,
        "rule": FLOOR_RULE,
    }
    if len(informative) < MIN_INFORMATIVE:
        return {
            **out,
            "floor": None,
            "withheld": f"{len(informative)} informative qubits, fewer than {MIN_INFORMATIVE}",
        }
    residuals = [r["residual"] for r in informative]
    stat = rms([r["se_statistical"] for r in informative])
    all_rms = rms(residuals)
    main_rms = rms([r["residual"] for r in main_rows]) if main_rows else None
    out |= {
        "rms_all": all_rms,
        "rms_main": main_rms,
        "rms_extra": rms([r["residual"] for r in extra_rows]) if extra_rows else None,
        "rms_all_relative_sampling_error": 1 / math.sqrt(2 * len(informative)),
        "statistical_rms": stat,
        "rms_all_less_statistical_in_quadrature": math.sqrt(max(all_rms**2 - stat**2, 0.0)),
        "mean_residual": math.fsum(residuals) / len(residuals),
        "floor": max(all_rms, main_rms or 0.0),
    }
    return out


def t2_pattern(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Descriptive: Spearman correlation of the residual with T2 (and with sx error) and sign counts by T2 tercile.

    The drive-dephasing lead predicts residual > 0 on long-T2 qubits and < 0 on short-T2 qubits, that is a positive
    rank correlation. The p value is the two-sided t approximation, rho sqrt((n - 2) / (1 - rho ** 2)) on n - 2 degrees
    of freedom; nothing here enters a decision.
    """
    informative = sorted((r for r in rows if r["informative"]), key=lambda r: r["t2_s"])
    n = len(informative)
    if n < 6:
        return {"n": n, "withheld": "fewer than 6 informative qubits"}

    def spearman(xs: list[float], ys: list[float]) -> dict[str, float | None]:
        if len(set(xs)) < 2 or len(set(ys)) < 2:
            return {"rho": None, "p_two_sided": None}
        rho = float(stats.spearmanr(xs, ys).statistic)
        t = rho * math.sqrt((n - 2) / max(1 - rho * rho, 1e-300))
        return {"rho": rho, "p_two_sided": float(2 * stats.t.sf(abs(t), n - 2))}

    third = n // 3
    low, high = informative[:third], informative[n - third :]
    return {
        "n": n,
        "residual_vs_t2": spearman([r["t2_s"] for r in informative], [r["residual"] for r in informative]),
        "residual_vs_sx_error": spearman([r["sx_error"] for r in informative], [r["residual"] for r in informative]),
        "lowest_t2_tercile": {
            "qubits": [r["qubit"] for r in low],
            "t2_us_max": low[-1]["t2_s"] * 1e6,
            "negative": sum(r["residual"] < 0 for r in low),
            "of": len(low),
        },
        "highest_t2_tercile": {
            "qubits": [r["qubit"] for r in high],
            "t2_us_min": high[0]["t2_s"] * 1e6,
            "positive": sum(r["residual"] > 0 for r in high),
            "of": len(high),
        },
        "drive_dephasing_lead": "positive rank correlation of residual with T2, negative residuals on short T2",
    }


# --- collection glue ----------------------------------------------------------------------------------------


def analyze_members(
    member_counts: dict[int, dict[str, Any]],
    contexts: dict[int, dict[str, Any]],
    main: tuple[int, ...] = MSQD_MAIN_QUBITS,
) -> dict[str, Any]:
    qubits = list(contexts)
    items = [(q, {k: tuple(v) for k, v in member_counts[q]["final"].items()}, contexts[q]) for q in qubits]
    rows = list(ordered_map(diagnostic_row, items, min_items=2))
    return {
        "schema": SCHEMA,
        "qubits": {str(row["qubit"]): row for row in rows},
        "floor": floor_summary(rows, main),
        "t2_pattern": t2_pattern(rows),
    }


def collected(
    record: dict[str, Any], distributions: dict[str, list[np.ndarray]], executed: dict[str, Any]
) -> dict[str, Any]:
    """The scatter analysis of a collected diagnostic record, or a withheld reason."""
    configuration = record["family_configuration"]
    if configuration.get("name") != MSQD_FAMILY:
        return {"schema": SCHEMA, "withheld": f"not a {MSQD_FAMILY} record"}
    qubits = [int(q) for q in configuration["qubits"]]
    try:
        contexts = msa.contexts_from_record(record, executed)
        counts = msa.member_counts_from_distributions(distributions, executed, qubits)
        for q in qubits:
            needed = [*msa.member_names("unitary", msa.TOP_STEPS, q), msa.ro0_name(q), msa.t1_names(q)[0]]
            absent = [n for n in needed if n not in counts[q]["final"]]
            check(not absent, f"q{q}: missing measured members {absent}")
        return analyze_members(counts, contexts, tuple(int(q) for q in configuration.get("main_qubits", ())))
    except (msa.AnalysisError, ScatterError) as error:
        return {"schema": SCHEMA, "withheld": str(error)}


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same(a: Any, b: Any, rel: float = 1e-9) -> bool:
    """Structural equality with floats compared to a relative 1e-9, so a replay on another libm still matches."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k], rel) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y, rel) for x, y in zip(a, b, strict=True))
    if isinstance(a, float) and isinstance(b, float):
        return math.isclose(a, b, rel_tol=rel, abs_tol=1e-15)
    return bool(a == b)


def replay(run_dir: Path) -> dict[str, Any]:
    """The scatter analysis re-derived from a retained run's raw shots.

    Each raw PUB file (hashes checked against the job's index.json) holds one bit string per shot for every fused
    component's register; execution_pubs of record.json maps a PUB's components to member names, and the entries of
    collect.json after the header hold each member's execution-time calibration. The member laws are the exact shot
    fractions, as live_run.py --collect builds them, so the result equals collect.json's stored analysis.
    """
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    collect = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    check(isinstance(collect, list) and len(collect) > 1, "collect.json is not live_run.py's list of entries")
    jobs = sorted(path for path in (run_dir / "raw").iterdir() if path.is_dir())
    check(len(jobs) == 1, f"the run holds {len(jobs)} raw job archives, not one")
    index = json.loads((jobs[0] / "index.json").read_text(encoding="utf-8"))
    for name, digest in index["files"].items():
        check(sha256_of(jobs[0] / name) == digest, f"{name}: raw file differs from index.json")
    registers: dict[str, dict[str, Any]] = {}
    for name in index["files"]:
        if name.startswith("pub_"):
            raw = json.loads((jobs[0] / name).read_text(encoding="utf-8"))
            registers[raw["pub_name"]] = raw["registers"]
    distributions: dict[str, list[np.ndarray]] = {}
    for pub in record["execution_pubs"]:
        shots_by_register = registers[pub["name"]]
        for component in pub["components"]:
            bits = shots_by_register[component["registers_by_replica"][0][0]]["bitstrings"]
            ones = sum(1 for b in bits if b == "1")
            distributions[component["member"]] = [np.array([1 - ones / len(bits), ones / len(bits)])]
    executed: dict[str, Any] = {}
    for entry in collect[1:]:
        executed.update(entry["executed"])
    return collected(record, distributions, executed)


def stored_scatter(run_dir: Path) -> dict[str, Any]:
    collect = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    check(isinstance(collect, list) and bool(collect), "collect.json is not live_run.py's list of entries")
    return dict(collect[0]["family_analysis"]["scatter"])


def floor_document(run_dir: Path) -> dict[str, Any]:
    """The scatter-floor.json document of a collected diagnostic run directory (record.json, collect.json and the raw
    shots), built from the replayed analysis after it matches collect.json's stored one."""
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    scatter = replay(run_dir)
    check(same(scatter, stored_scatter(run_dir)), "the replayed analysis differs from collect.json's")
    check("withheld" not in scatter, f"the scatter analysis is withheld: {scatter.get('withheld')}")
    summary = scatter["floor"]
    check(summary.get("floor") is not None, f"no floor: {summary.get('withheld')}")
    configuration = record["family_configuration"]
    backends = sorted(msa.record_backends(record))
    check(len(backends) == 1, f"the record names backends {backends}")
    main = [int(q) for q in configuration["main_qubits"]]
    registered = list(diagnostic_main(backends[0]))
    check(sorted(main) == sorted(registered), f"the run's main qubits {main} are not {backends[0]}'s {registered}")
    return {
        "schema": FLOOR_SCHEMA,
        "floor": float(summary["floor"]),
        "unit": "probability, P0 of the unitary N = 16 member after readout correction",
        "backend": backends[0],
        "rule": FLOOR_RULE,
        "selection_rule": SELECTION_RULE,
        "main_qubits": main,
        "extra_qubits": [int(q) for q in configuration["extra_qubits"]],
        "summary": summary,
        "t2_pattern": scatter["t2_pattern"],
        "qubits": scatter["qubits"],
        "source": {
            "run": run_dir.name,
            "record_sha256": sha256_of(run_dir / "record.json"),
            "collect_sha256": sha256_of(run_dir / "collect.json"),
            "experiment_digest": record["experiment_digest"],
            "scatter_module_sha256": sha256_of(Path(__file__)),
            "analysis_module_sha256": sha256_of(Path(msa.__file__)),
        },
    }


def check_floor_file(run_dir: Path, path: Path) -> str:
    """Re-derive the floor document from the retained run and compare it with the registered file.

    Every field is compared (floats to a relative 1e-9) except the two module digests under source: the analysis module
    names the file's digest in its floor registry, so its bytes change once the file is bound, and either module's
    bytes record provenance while the re-derived floor, rows and summary carry the result.
    """
    registered = json.loads(path.read_text(encoding="utf-8"))
    derived = floor_document(run_dir)
    for document in (registered, derived):
        document["source"].pop("analysis_module_sha256", None)
        document["source"].pop("scatter_module_sha256", None)
    check(same(registered, derived), f"{path} differs from the floor re-derived from {run_dir}")
    return f"{path.name}: floor {registered['floor']:.6f} equals the re-derivation from {run_dir.name}"


def self_test() -> str:
    graph = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]]
    check(layout_violations(list(MSQD_MAIN_QUBITS), [], set()) == [], "a clean layout is refused")
    check(len(layout_violations([0, 1, *MSQD_MAIN_QUBITS], graph, set())) == 1, "a coupled pair passes")
    check(len(layout_violations([1, 2, 2], [], {2})) == 2, "an excluded or repeated qubit passes")
    rows = [
        {
            "informative": True,
            "qubit": q,
            "residual": 0.01 * (-1) ** q,
            "se_statistical": 0.001,
            "t2_s": 1e-4 + q * 1e-5,
            "sx_error": 1e-4,
        }
        for q in range(30)
    ]
    summary = floor_summary(rows)
    check(abs(summary["floor"] - 0.01) < 1e-12, f"the floor of a +-0.01 population is {summary['floor']}")
    check(floor_summary(rows[:5])["floor"] is None, "five qubits give a floor")
    return "measurement-sequence scatter: layout checks and the floor of a +-0.01 population hold"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Gate-model scatter floor of the measurement-sequence pinching analysis"
    )
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    sel = sub.add_parser("select", help="apply the calibration-only rule to a backend's live Target (a read, no job)")
    sel.add_argument("--backend", default="ibm_kingston")
    flo = sub.add_parser("floor", help="write scatter-floor.json from a collected diagnostic run directory")
    flo.add_argument("run_dir", type=Path)
    flo.add_argument("--out", type=Path, required=True)
    chk = sub.add_parser("check", help="re-derive the floor from a retained run and compare with scatter-floor.json")
    chk.add_argument("run_dir", type=Path)
    chk.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        print(self_test())
    elif args.command == "select":
        import io
        from contextlib import redirect_stdout

        import ibm_account
        import live_run

        with redirect_stdout(io.StringIO()):
            snapshot = live_run.take_snapshot(ibm_account.open_service(), args.backend)
        calibration = calibration_from_snapshot(snapshot)
        main = diagnostic_main(args.backend)
        extra = select_extra_qubits(calibration, main, minimum=DIAGNOSTIC_MIN_QUBITS)
        layout = [*main, *extra]
        faults = layout_violations(layout, calibration["edges"], set(calibration["excluded"]))
        check(not faults, "; ".join(faults))
        print(
            json.dumps({"backend": args.backend, "calibration": snapshot.calibration, "layout": layout, "extra": extra})
        )
    elif args.command == "floor":
        document = floor_document(args.run_dir)
        args.out.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif args.command == "check":
        print(check_floor_file(args.run_dir, args.path))
    else:
        parser.error("choose a subcommand or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
