"""Build the pathion evidence table and its pivots from the retained IBM, Quantum Inspire and Quandela records.

Writes docs/evidence/pathion-kernel-map/evidence_table.csv (every reading, one row each; the schema is the module
docstring of gororoba_quantum/pathion_evidence_table.py) and evidence_pivots.md (four pivots computed from the CSV read
back from disk). The input selection lives here: the IBM runs are the results/live directories whose record is
`submitted` with a collect.json and a pathion group, the Quantum Inspire inputs are the series analyses with their
case manifests, and the Quandela inputs are the analyses under results/quandela/runs named for a pathion family. The
module takes every record as an argument, so a run directory enters the table by appearing in these lists.

Usage: `"$PYTHON" scripts/pathion_evidence_table_build.py [--out-dir DIR] [--check]`; --check rebuilds in memory and
exits 1 when the files in the output directory differ.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import Any

from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import pathion_evidence_table as pet  # noqa: E402

OUT_DIR = ROOT / "docs/evidence/pathion-kernel-map"
LEDGER = ROOT / "docs/evidence/a5-exceptional-fibers/ledger.tsv"
LIVE = ROOT / "results/live"
QI = ROOT / "results/quantum_inspire"
QUANDELA = ROOT / "results/quandela/runs"
# Each Quantum Inspire analysis with the manifest of one of its batches; the coin analysis also carries the pinned
# reading of the stopped first series, which `stopped` names. The .v2 QX files supersede the unversioned ones (same
# values, with outcome fields and null in place of the 1e6 sentinel), so the unversioned files stay unread.
QI_INPUTS = (
    ("pathion_coset_coin_tuna_17_analysis.json", "cases/pathion_coset_coin_tuna_17/batch-00/cases.json", True),
    ("pathion_coset_coin_qx_analysis.v2.json", "cases/pathion_coset_coin_qx/batch-00/cases.json", False),
    ("pathion_coset_block_qx_analysis.v2.json", "cases/pathion_coset_block_qx/batch-00/cases.json", False),
)
STOPPED_SERIES = "pathion_coset_block_tuna_17_analysis.json"
SUPERSEDED = ("pathion_coset_coin_qx_analysis.json", "pathion_coset_block_qx_analysis.json")
# Ascella analyses that fix the census class of each pathion block and the operand text of every Ascella row.
CLASS_SOURCE = "2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00"
Z_RESOLVE = 3.0
MIRROR_LIMIT = 0.07
# Preregistered band of the kernel-map case (results/live/2026-11-06T180755.872625Z/CASE.md, rule 2): N_hat within
# +-1 of the calibrated model's value; the e1+e18 value is the case's, the twin and flipped values are the findings
# table's model column (PATHION_KERNEL_MAP_FINDINGS.md, first table).
BAND = 1.0
MODEL_BRANCH = {("e1+e18", "primary"): 12.37, ("e17-e2", "twin"): 12.34, ("e1+e18", "mutation"): 11.50}

Row = dict[str, Any]


# ---------------------------------------------------------------- selection


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def ibm_candidates() -> list[Path]:
    """Every results/live directory whose case or record names a pathion experiment."""
    found = []
    for directory in sorted(p for p in LIVE.iterdir() if p.is_dir()):
        for name in ("CASE.md", "record.json"):
            path = directory / name
            if path.is_file() and b"pathion" in path.read_bytes().lower():
                found.append(directory)
                break
    return found


def ibm_selection() -> tuple[list[Path], list[tuple[str, str]]]:
    """Directories with collected results, and (name, reason) for each pathion directory without them."""
    included: list[Path] = []
    excluded: list[tuple[str, str]] = []
    for directory in ibm_candidates():
        record = json.loads((directory / "record.json").read_text(encoding="utf-8"))
        groups = [g["group"] for g in record.get("groups", [])]
        collected = (directory / "collect.json").is_file() and (directory / "raw").is_dir()
        if record.get("state") == "submitted" and collected and all(g.startswith("pathion_") for g in groups):
            included.append(directory)
            continue
        if (directory / "approval-consumed.json").is_file():
            reason = "binding dry run: record state planned, approval consumed, no job submitted"
        elif (directory / "CASE.md").is_file():
            reason = "written case and plan: record state planned, no job submitted"
        else:
            reason = "plan record: state planned, no job submitted"
        excluded.append((directory.name, f"{reason} ({', '.join(groups)}; no raw/ results)"))
    return included, excluded


# ---------------------------------------------------------------- table build


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_rows() -> tuple[list[Row], list[tuple[str, str]]]:
    ledger = pet.parse_ledger(LEDGER.read_text(encoding="utf-8"))
    source = QUANDELA / CLASS_SOURCE
    classes = pet.class_table(load(source / "analysis.json"))
    operand_terms = load(source / "cases.json")["operands"]
    four_term_operands = {name: pet.terms_text(terms) for name, terms in operand_terms.items()}
    rows: list[Row] = []
    included, excluded = ibm_selection()
    for directory in included:
        collect = load(directory / "collect.json")
        group = pet.find_group(collect)
        ideal, laws = pet.ideal_inputs(group["group"])
        run_dir, source_file = rel(directory), rel(directory / "collect.json")
        rows += pet.ibm_summary_rows(
            group,
            ideal,
            run_dir=run_dir,
            source_file=source_file,
            four_term_operands=four_term_operands,
            block_classes=classes,
            ledger=ledger,
        )
        rows += pet.ibm_bin_rows(group, laws, ideal, run_dir=run_dir, source_file=source_file, ledger=ledger)
    for analysis_name, manifest_name, stopped in QI_INPUTS:
        analysis_path = QI / analysis_name
        manifest_path = QI / manifest_name
        rows += pet.tuna_rows(
            load(analysis_path),
            load(manifest_path),
            run_dir=rel(analysis_path),
            source_file=rel(analysis_path),
            ledger=ledger,
            stopped_run_dir=rel(QI / STOPPED_SERIES) if stopped else None,
            shots_by_template=pet.template_shots(series_batches(manifest_path.parent.parent)),
        )
    for superseded in SUPERSEDED:
        check_superseded(load(QI / superseded), load(QI / superseded.replace(".json", ".v2.json")), superseded)
    for directory in sorted(QUANDELA.glob("*pathion*")):
        analysis_path = directory / "analysis.json"
        if not analysis_path.is_file():
            continue
        analysis = load(analysis_path)
        if pet.is_ascella_instrument_record(analysis):
            continue
        rows += pet.ascella_rows(
            analysis,
            load(directory / "cases.json")["operands"],
            run_dir=rel(directory),
            source_file=rel(analysis_path),
            classes=classes,
            ledger=ledger,
        )
    return rows, excluded


def series_batches(series_dir: Path) -> list[dict[str, Any]]:
    """The batch manifests (cases.json) of one Quantum Inspire series directory."""
    return [load(path) for path in sorted(series_dir.glob("batch-*/cases.json"))]


def check_superseded(old: dict[str, Any], new: dict[str, Any], name: str) -> None:
    """The .v2 file keeps every template value of its predecessor; a difference stops the build."""
    for template, entry in old["templates"].items():
        for field in ("selector_contrast", "selector_se", "visibility"):
            if entry[field] != new["templates"][template][field]:
                raise ValueError(f"{name}: template {template} {field} differs between the file and its v2 successor")


# ---------------------------------------------------------------- pivot helpers


def level_of(row: Row) -> str:
    if row["bin"] is not None:
        return "bin"
    return "block" if row["block"] else "operand"


def z_value(row: Row) -> float | None:
    se = row["standard_error"]
    if row["measured"] is None or not se:
        return None
    return (row["measured"] - row["ideal"]) / se


def md_table(header: Sequence[str], body: Iterable[Sequence[Any]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(str(c) for c in line) + " |" for line in body]
    return "\n".join(lines)


def f4(value: float | None, digits: int = 4) -> str:
    return "" if value is None else f"{value:.{digits}f}"


def pm(row: Row | None, digits: int = 4) -> str:
    if row is None or row["measured"] is None:
        return "-"
    if row["standard_error"]:
        return f"{row['measured']:.{digits}f} +- {row['standard_error']:.{digits}f}"
    return f"{row['measured']:.{digits}f}"


def select(rows: Iterable[Row], **fields: Any) -> list[Row]:
    return [r for r in rows if all(r[k] == v for k, v in fields.items())]


def name_of(run_dir: str) -> str:
    return run_dir.rsplit("/", 1)[-1]


def stamp(run_dir: str) -> str:
    return name_of(run_dir)[:17]


# ---------------------------------------------------------------- pivot (a)


def pivot_a(rows: list[Row]) -> str:
    groups: dict[tuple[str, str, str, str], list[Row]] = defaultdict(list)
    for row in rows:
        groups[(row["backend"], row["observable"], row["calibration"] or "raw", level_of(row))].append(row)
    body = []
    for key in sorted(groups):
        members = groups[key]
        defined = [r for r in members if r["measured"] is not None]
        decided = [r for r in defined if abs(r["ideal"]) > 1e-9] if key[1] in pet.SIGNED_OBSERVABLES else []
        agree = sum(math.copysign(1.0, r["measured"]) == math.copysign(1.0, r["ideal"]) for r in decided)
        deviations = [abs(r["measured"] - r["ideal"]) for r in defined]
        zs = [abs(z) for r in defined if (z := z_value(r)) is not None]
        body.append(
            (
                *key,
                len(members),
                len(members) - len(defined),
                f"{agree}/{len(decided)}" if decided else "-",
                f4(statistics.median(deviations)) if deviations else "-",
                f4(statistics.median(zs), 2) if zs else "-",
            )
        )
    header = (
        "backend",
        "observable",
        "calibration",
        "level",
        "n",
        "undefined",
        "sign agreement",
        "median abs dev",
        "median abs z",
    )
    return md_table(header, body)


# ---------------------------------------------------------------- pivot (b)


def pivot_b_two_term(rows: list[Row]) -> str:
    """Tuna-17 readout-corrected ratio c(y)/V of each bin against the IBM ratio at the same algebra output label."""
    ratios = [r for r in rows if r["observable"] == "output_ratio" and r["platform"] == "ibm" and r["block"]]
    runs = sorted({r["run_dir"] for r in ratios})
    by_run: dict[tuple[str, str, int], Row] = {
        (r["run_dir"], r["operand"], r["label"]): r for r in ratios if r["control"] in ("primary", "null")
    }
    tuna = [
        r
        for r in rows
        if r["backend"] == "tuna-17" and r["observable"] == "output_ratio" and r["calibration"] == "readout_corrected"
    ]
    diffs = [
        r
        for r in rows
        if r["observable"] == "D_y" and r["calibration"] == "readout_corrected" and r["backend"] == "tuna-17"
    ]
    out: list[str] = []
    summary = []
    for template in sorted({r["block"] for r in diffs}):
        for device in sorted({r["reference_backend"] for r in diffs}):
            sel = [r for r in diffs if r["block"] == template and r["reference_backend"] == device]
            within = sum(abs(r["measured"]) <= Z_RESOLVE * r["standard_error"] for r in sel)
            worst = max(sel, key=lambda r: abs(r["measured"]) / r["standard_error"])
            summary.append(
                (
                    template,
                    sel[0]["operand"],
                    device,
                    f"{within} of {len(sel)}",
                    f"bin {worst['bin']} at {f4(abs(worst['measured']) / worst['standard_error'], 1)}",
                )
            )
    out.append(
        md_table(
            (
                "Tuna-17 block",
                "operand",
                "IBM device",
                f"bins within {Z_RESOLVE:g} combined standard errors",
                "largest z",
            ),
            summary,
        )
    )
    for template in sorted({r["block"] for r in tuna if r["control"] != "cocycle-free"}):
        t_rows = sorted(select(tuna, block=template), key=lambda r: r["bin"])
        columns = [run for run in runs if all((run, t_rows[0]["operand"], r["label"]) in by_run for r in t_rows)]
        header = [
            "bin",
            "label",
            "ideal sign",
            "Tuna-17 corrected ratio",
            *[f"{select(ratios, run_dir=c)[0]['backend']} {stamp(c)}" for c in columns],
        ]
        for device in sorted({r["reference_backend"] for r in diffs}):
            header.append(f"D(y) z vs {device}")
        body = []
        for t in t_rows:
            line = [t["bin"], t["label"], f4(t["ideal"], 0), pm(t)]
            line += [pm(by_run[(c, t["operand"], t["label"])]) for c in columns]
            for device in sorted({r["reference_backend"] for r in diffs}):
                d = select(diffs, block=template, bin=t["bin"], reference_backend=device)[0]
                line.append(f4(d["measured"] / d["standard_error"], 2))
            body.append(line)
        out.append(
            f"Template `{template}` ({t_rows[0]['operand']}, {t_rows[0]['block_class']}):\n\n" + md_table(header, body)
        )
    return "\n\n".join(out)


def resolve_reference(rows: list[Row]) -> list[str]:
    """Name, for each D(y) device, the IBM run whose per-label ratio reproduces the stored difference."""
    ratios = {
        (r["run_dir"], r["operand"], r["label"]): r
        for r in rows
        if r["observable"] == "output_ratio" and r["platform"] == "ibm"
    }
    tuna = {
        (r["block"], r["bin"]): r
        for r in rows
        if r["backend"] == "tuna-17" and r["observable"] == "output_ratio" and r["calibration"] == "readout_corrected"
    }
    diffs = [
        r
        for r in rows
        if r["observable"] == "D_y" and r["calibration"] == "readout_corrected" and r["backend"] == "tuna-17"
    ]
    out = []
    for device in sorted({r["reference_backend"] for r in diffs}):
        matched = set()
        for run in sorted({k[0] for k in ratios}):
            if all(
                (run, d["operand"], d["label"]) in ratios
                and abs(
                    tuna[(d["block"], d["bin"])]["measured"]
                    - ratios[(run, d["operand"], d["label"])]["measured"]
                    - d["measured"]
                )
                < 1e-9
                for d in diffs
                if d["reference_backend"] == device
            ):
                matched.add(run)
        if len(matched) != 1:
            raise ValueError(f"{device}: the stored D(y) matches {len(matched)} IBM runs, not one")
        out.append(f"{device}: {name_of(next(iter(matched)))}")
    return out


def pivot_b_four_term(rows: list[Row]) -> str:
    """The four-term blocks both IBM parallel-coset runs and Ascella read: level of each arm by backend."""
    levels = [
        r for r in rows if r["observable"] == "level" and r["block"] and "/" in r["block"] and r["status"] == "ok"
    ]
    ibm = [r for r in levels if r["platform"] == "ibm"]
    blocks = sorted({r["block"] for r in ibm})
    ascella = [r for r in levels if r["platform"] == "quandela"]
    families = sorted({(r["backend"], "pairs" if "pairs" in r["run_dir"] else "four-term") for r in ascella})
    ibm_runs = sorted({(r["backend"], r["run_dir"]) for r in ibm})
    body = []
    for block in blocks:
        arms = sorted({r["arm"] for r in ibm if r["block"] == block})
        for arm in arms:
            line: list[Any] = [
                block,
                select(ibm, block=block, arm=arm)[0]["block_class"],
                arm,
                f4(select(ibm, block=block, arm=arm)[0]["ideal"]),
            ]
            for _backend, run in ibm_runs:
                line.append(pm(next(iter(select(ibm, run_dir=run, block=block, arm=arm, calibration="raw")), None)))
            for backend, family in families:
                for calibration in (
                    "raw",
                    "anchor_dark_normalized" if family == "four-term" else "per_slot_anchor_dark",
                ):
                    sel = [
                        r
                        for r in ascella
                        if r["backend"] == backend
                        and r["block"] == block
                        and r["arm"] == arm
                        and r["calibration"] == calibration
                        and (("pairs" in r["run_dir"]) == (family == "pairs"))
                    ]
                    if not sel:
                        line.append("-")
                    elif len(sel) == 1:
                        line.append(f4(sel[0]["measured"]))
                    else:
                        line.append(f"{statistics.mean(r['measured'] for r in sel):.4f} (mean of {len(sel)})")
            body.append(line)
    header = ["block", "census class", "arm", "ideal", *[f"{b} raw P(00) {stamp(r)}" for b, r in ibm_runs]]
    for backend, family in families:
        header += [f"{backend} {family} raw a", f"{backend} {family} {'a prime' if family == 'four-term' else 'l hat'}"]
    return md_table(header, body)


# ---------------------------------------------------------------- pivot (c)


def paired_ascella(rows: list[Row], observable: str, calibration: str, family: str) -> list[tuple[Row, Row]]:
    sub = [
        r
        for r in rows
        if r["platform"] == "quandela"
        and r["observable"] == observable
        and r["calibration"] == calibration
        and (("pairs" in r["run_dir"]) == (family == "pairs"))
    ]
    sim = {(r["setting"], r["block"], r["arm"], r["control"]): r for r in sub if r["substrate"] == "sim"}
    qpu = {(r["setting"], r["block"], r["arm"], r["control"]): r for r in sub if r["substrate"] == "qpu"}
    if len(sim) != len([r for r in sub if r["substrate"] == "sim"]) or set(sim) != set(qpu):
        raise ValueError(f"{family} {observable}: the sim and qpu readings do not pair one to one")
    return [(sim[k], qpu[k]) for k in sorted(sim)]


def pivot_c(rows: list[Row]) -> str:
    specs = (
        ("four-term", "level", "raw"),
        ("four-term", "level", "anchor_dark_normalized"),
        ("pairs", "level", "raw"),
        ("pairs", "level", "per_slot_anchor_dark"),
        ("pairs", "mirror_difference", "per_slot_anchor_dark"),
    )
    summary: list[Sequence[Any]] = []
    detail: list[str] = []
    for family, observable, calibration in specs:
        pairs = paired_ascella(rows, observable, calibration, family)
        deltas = [(q["measured"] - s["measured"], s, q) for s, q in pairs]
        absolute = [abs(d) for d, _, _ in deltas]
        worst = max(deltas, key=lambda t: abs(t[0]))
        summary.append(
            (
                family,
                observable,
                calibration,
                len(pairs),
                f4(statistics.median(d for d, _, _ in deltas)),
                f4(statistics.median(absolute)),
                f4(max(absolute)),
                f"{worst[1]['setting']} {worst[1]['block']} {worst[1]['arm']}",
            )
        )
        if (family, observable, calibration) in (
            ("four-term", "level", "anchor_dark_normalized"),
            ("pairs", "level", "per_slot_anchor_dark"),
            ("pairs", "mirror_difference", "per_slot_anchor_dark"),
        ):
            body = [
                (
                    s["setting"],
                    s["block"],
                    s["arm"],
                    s["control"],
                    f4(s["ideal"]),
                    f4(s["measured"]),
                    f4(q["measured"]),
                    f4(d),
                )
                for d, s, q in deltas
            ]
            detail.append(
                f"{family} {observable} ({calibration}), every reading:\n\n"
                + md_table(
                    ("setting", "block", "arm", "control", "ideal", "sim:ascella", "qpu:ascella", "qpu - sim"), body
                )
            )
    head = md_table(
        (
            "family",
            "observable",
            "calibration",
            "pairs",
            "median delta",
            "median abs delta",
            "max abs delta",
            "largest at (setting block arm)",
        ),
        summary,
    )
    return head + "\n\n" + "\n\n".join(detail)


# ---------------------------------------------------------------- pivot (d)


Verdict = tuple[str, str, str]


def replica_interval(row: Row) -> tuple[float, float]:
    """The Student t interval over replicas that the record reports: measured +- t(0.975, n - 1) standard errors."""
    half = float(stats.t.ppf(0.975, row["n_replicas"] - 1)) * row["standard_error"]
    return row["measured"] - half, row["measured"] + half


def ledger_checks(rows: list[Row]) -> dict[str, Callable[[], Verdict]]:
    """Per ledger row: (readings used, result, verdict) from the table rows alone."""

    def cited(row_id: str, **fields: Any) -> list[Row]:
        return [r for r in select(rows, **fields) if row_id in (r["ledger_row"] or "").split(";")]

    def a179() -> Verdict:
        vis = cited("A5-179", observable="visibility", calibration="raw", block=None, bin=None)
        deep = [r for r in vis if r["control"] != "cocycle-free"]
        free = [r for r in vis if r["control"] == "cocycle-free"]
        low, high = min(r["measured"] for r in deep), max(r["measured"] for r in deep)
        outside = [
            f"{r['operand']} ({r['control']}) {r['measured']:.3f}"
            for r in deep
            if not 0.09 <= round(r["measured"], 2) <= 0.24
        ]
        free_range = (min(r["measured"] for r in free), max(r["measured"] for r in free))
        result = (
            f"{len(deep)} deep visibilities span {low:.3f} to {high:.3f}, all below the model band's 0.49; "
            f"{len(free)} cocycle-free visibilities span {free_range[0]:.3f} to {free_range[1]:.3f} "
            "against a modeled 0.77 to 0.84"
        )
        if outside:
            result += "; the stated deep range 0.09 to 0.24 omits " + ", ".join(outside)
        verdict = "agrees on status" if high < 0.49 and free_range[1] < 0.77 else "disagrees"
        return f"{len(vis)} operand visibilities", result, verdict + ("; stated range disagrees" if outside else "")

    def a180() -> Verdict:
        n_hat = cited("A5-180", observable="N_hat", calibration="raw", block=None, bin=None)
        by_key = {(r["operand"], r["control"]): r for r in n_hat}
        notes = []
        ok = True
        for key, model in MODEL_BRANCH.items():
            r = by_key[key]
            low, high = replica_interval(r)
            inside = abs(r["measured"] - model) <= BAND
            ok = ok and inside
            notes.append(
                f"{key[0]} {key[1]} {r['measured']:.2f} (model {model:g}; point {'inside' if inside else 'outside'} "
                f"the +-{BAND:g} band, interval [{low:.2f}, {high:.2f}] "
                f"{'covers' if low <= r['ideal'] <= high else 'misses'} the cd_core ideal {r['ideal']:g})"
            )
        free = by_key[("e1+e10", "cocycle-free")]
        low, high = replica_interval(free)
        ok = ok and free["measured"] < 0
        notes.append(
            f"e1+e10 cocycle-free {free['measured']:.2f} (negative as rule 3 requires; interval [{low:.2f}, "
            f"{high:.2f}] {'covers' if low <= free['ideal'] <= high else 'misses'} the cd_core ideal {free['ideal']:g})"
        )
        step = by_key[("e1+e18", "mutation")]["measured"] - by_key[("e1+e18", "primary")]["measured"]
        signs = cited("A5-180", observable="sign_count", calibration="raw", block=None, bin=None)
        counts = sorted(int(r["measured"]) for r in signs if r["control"] in ("primary", "null", "twin"))
        return (
            f"4 named N_hat readings of {len(n_hat)} and {len(counts)} sign counts",
            "; ".join(notes)
            + f"; flipped minus unflipped e1+e18 {step:+.2f} (rule 3 predicts -1); criteria: the kernel-map "
            "case's preregistered rules 2 and 3; sign counts of the deep operands "
            f"{counts[0]} to {counts[-1]} of 32, {sum(c < 31 for c in counts)} below the preregistered 31",
            "agrees with the case rules; the cocycle-free interval misses the cd_core ideal" if ok else "disagrees",
        )

    def a182() -> Verdict:
        corrected = cited("A5-182", observable="N_hat", calibration="readout_corrected", block=None, bin=None)
        deviations = [
            (abs(r["measured"] - r["ideal"]), r)
            for r in corrected
            if r["control"] in ("primary", "null", "twin", "cocycle-free")
        ]
        # The row states its bound to two decimals, so a deviation that rounds to 0.15 meets it.
        over = [(d, r) for d, r in deviations if round(d, 2) > 0.15]
        counts = cited("A5-182", observable="sign_count", calibration="raw", block=None, bin=None)
        short = [r for r in counts if r["control"] in ("primary", "null", "twin") and r["measured"] != r["ideal"]]
        worst = max(deviations, key=lambda t: t[0])
        result = (
            f"{len(deviations)} corrected N_hat readings; largest deviation {worst[0]:.4f} "
            f"({worst[1]['backend']} {worst[1]['operand']} {worst[1]['control']}) against the stated 0.15, "
            f"{sum(d > 0.15 for d, _ in deviations)} above 0.15 unrounded and {len(over)} above it rounded to two "
            f"decimals; {len(counts) - len(short)} of {len(counts)} sign counts at 32"
        )
        return (
            f"{len(deviations)} corrected N_hat, {len(counts)} sign counts",
            result,
            "agrees at the stated precision" if not over and not short else "disagrees",
        )

    def a184() -> Verdict:
        bins = [
            r
            for r in cited("A5-184", observable="output_contrast", calibration="raw", backend="tuna-17")
            if r["block"] in ("ba", "bb")
        ]
        z = [r["measured"] * math.copysign(1.0, r["ideal"]) / r["standard_error"] for r in bins]
        signs = sum(math.copysign(1.0, r["measured"]) == math.copysign(1.0, r["ideal"]) for r in bins)
        sel = {r["block"]: r for r in cited("A5-184", observable="selector_contrast", backend="tuna-17")}
        ok = (
            signs == len(bins) == 16
            and round(min(z), 1) >= 25.5
            and sel["xor_ba"]["measured"] < 0 < sel["ba"]["measured"]
        )
        return (
            f"{len(bins)} bin contrasts, 3 selector contrasts",
            f"{signs} of {len(bins)} bins at the ideal sign, smallest z {min(z):.2f} "
            f"({round(min(z), 1):.1f} at the row's precision); selector contrast ba {sel['ba']['measured']:.4f}, "
            f"xor_ba {sel['xor_ba']['measured']:.4f}",
            "agrees" if ok else "disagrees",
        )

    def a185() -> Verdict:
        null = [
            r
            for r in cited("A5-185", observable="selector_contrast", block="b0")
            if r["run_dir"].endswith("coin_tuna_17_analysis.json")
        ][0]
        z = null["measured"] / null["standard_error"]
        diffs = [
            r for r in cited("A5-185", observable="D_y", calibration="readout_corrected") if r["backend"] == "tuna-17"
        ]
        counts: dict[tuple[str, str], int] = defaultdict(int)
        for r in diffs:
            counts[(r["block"], r["reference_backend"])] += abs(r["measured"]) <= Z_RESOLVE * r["standard_error"]
        failing = sorted(f"{t}/{d} {n} of 8" for (t, d), n in counts.items() if n < 7)
        claim_false = abs(z) > Z_RESOLVE and bool(failing)
        return (
            f"b0 selector contrast and {len(diffs)} D(y) bins",
            f"b0 selector contrast {null['measured']:.4f} +- {null['standard_error']:.4f} (z {z:.2f}); "
            f"template and device pairs under 7 of 8 bins: {', '.join(failing)}",
            "agrees" if claim_false else "disagrees",
        )

    def a186() -> Verdict:
        reads = [r for r in cited("A5-185", observable="selector_contrast", block="b0")]
        text = "; ".join(
            f"{name_of(r['run_dir'])} {r['measured']:+.4f} +- {r['standard_error']:.4f}"
            for r in sorted(reads, key=lambda r: r["run_dir"])
        )
        return (
            "premise only",
            "rests on conjecture logs, not table readings; the table holds the null offset the mechanism explains: "
            + text,
            "not decidable from the table",
        )

    def a187() -> Verdict:
        diffs = [
            r
            for r in select(rows, observable="D_y", calibration="readout_corrected", backend="tuna-17", block="ba")
            if "A5-187" in (r["ledger_row"] or "")
        ]
        failing: dict[str, list[int]] = defaultdict(list)
        for r in diffs:
            if abs(r["measured"]) > Z_RESOLVE * r["standard_error"]:
                failing[r["reference_backend"]].append(r["bin"])
        odd = all(y % 2 == 1 for bins in failing.values() for y in bins)
        text = "; ".join(f"{d}: bins {sorted(b)}" for d, b in sorted(failing.items()))
        return (
            f"{len(diffs)} D(y) bins, premise only",
            f"rests on conjecture logs, not table readings; failing `ba` bins ({text}) "
            f"{'all have' if odd else 'do not all have'} d0 = 1",
            "premise holds; mechanism not decidable from the table" if odd else "premise disagrees",
        )

    def a188() -> Verdict:
        qpu = [
            r
            for r in rows
            if "A5-188" in (r["ledger_row"] or "").split(";")
            and r["calibration"] == "anchor_dark_normalized"
            and r["observable"] == "level"
        ]
        top = [r for r in qpu if r["control"] == "primary" and r["arm"] == "T"]
        mutated = [r for r in qpu if r["control"] in ("cocycle-free", "mutation")]
        references = [r for r in qpu if r["control"] == "reference" and r["arm"] in ("T", "F")]
        within_ref = sum(abs(r["measured"] - r["ideal"]) <= MIRROR_LIMIT for r in references)
        c8 = [r["measured"] for r in top if r["operand"] == "e1+e8+e18+e27"]
        within_top = sum(abs(r["measured"] - r["ideal"]) <= MIRROR_LIMIT for r in top)
        within_mut = sum(abs(r["measured"] - r["ideal"]) <= MIRROR_LIMIT for r in mutated)
        spread = max(c8) - min(c8)
        ok = (
            within_top == len(top) == 8
            and within_mut == len(mutated) == 11
            and within_ref == len(references) == 2
            and spread < 0.05
        )
        return (
            f"{len(top)} top-vector levels, {len(mutated)} mutated-arm levels, {len(references)} reference levels",
            f"{within_top} of {len(top)} T levels, {within_mut} of {len(mutated)} C and N levels and {within_ref} of "
            f"{len(references)} reference T and F levels within {MIRROR_LIMIT}; C8 T spread {spread:.4f}",
            "agrees" if ok else "disagrees",
        )

    def mirrors(substrate: str) -> list[Row]:
        return [
            r
            for r in rows
            if r["observable"] == "mirror_difference" and r["substrate"] == substrate and "pairs" in r["run_dir"]
        ]

    def a189() -> Verdict:
        qpu, sim = mirrors("qpu"), mirrors("sim")
        failing = sum(r["measured"] > MIRROR_LIMIT for r in qpu)
        return (
            f"{len(qpu)} qpu and {len(sim)} sim mirror differences",
            f"{failing} of {len(qpu)} qpu mirror differences exceed {MIRROR_LIMIT} against an allowance of 4; "
            f"{sum(r['measured'] > MIRROR_LIMIT for r in sim)} of {len(sim)} on sim:ascella",
            "agrees" if failing > 4 else "disagrees",
        )

    def a190() -> Verdict:
        qpu = [r["measured"] for r in mirrors("qpu")]
        median, maximum = statistics.median(qpu), max(qpu)
        ok = round(median, 4) == 0.0259 and round(maximum, 4) == 0.1082
        return (
            f"{len(qpu)} qpu mirror differences",
            f"observed median {median:.4f} and maximum {maximum:.4f}; the efficiency model's prediction "
            "(median 0.0026, maximum 0.0155) is in conjecture logs, not the table",
            "observed values agree" if ok else "observed values disagree",
        )

    def a191() -> Verdict:
        sim = [r["measured"] for r in mirrors("sim")]
        ok = round(max(sim), 4) == 0.0066 and not any(m > MIRROR_LIMIT for m in sim)
        return (
            f"{len(sim)} sim mirror differences",
            f"sim:ascella maximum {max(sim):.4f}, 0 of {len(sim)} over {MIRROR_LIMIT}; the anchor and phase "
            "mechanism rests on conjecture logs",
            "sim statement agrees" if ok else "sim statement disagrees",
        )

    return {
        "A5-179": a179,
        "A5-180": a180,
        "A5-182": a182,
        "A5-184": a184,
        "A5-185": a185,
        "A5-186": a186,
        "A5-187": a187,
        "A5-188": a188,
        "A5-189": a189,
        "A5-190": a190,
        "A5-191": a191,
    }


def pivot_d(rows: list[Row], ledger: list[dict[str, str]]) -> str:
    status = {r["id"]: (r["status"], r["claim"]) for r in ledger}
    checks = ledger_checks(rows)
    body = []
    for row_id, check in checks.items():
        readings, result, verdict = check()
        stated, claim = status[row_id]
        body.append((row_id, stated, claim if len(claim) < 110 else claim[:107] + "...", readings, result, verdict))
    census = [
        (
            i,
            status[i][0],
            status[i][1][:107] + "...",
            "none",
            "exhaustive census (census.json); no hardware reading",
            "not a table claim",
        )
        for i in ("A5-177", "A5-178")
    ]
    return md_table(
        ("ledger row", "stated status", "claim", "readings used", "what the table shows", "agreement"), census + body
    )


# ---------------------------------------------------------------- document


def render_pivots(
    rows: list[Row], excluded: list[tuple[str, str]], ledger: list[dict[str, str]], ibm_included: list[str]
) -> str:
    backends: dict[str, int] = defaultdict(int)
    for r in rows:
        backends[r["backend"]] += 1
    counts = md_table(
        ("backend", "platform", "substrate", "rows"),
        [
            (b, select(rows, backend=b)[0]["platform"], select(rows, backend=b)[0]["substrate"], n)
            for b, n in sorted(backends.items())
        ],
    )
    runs = md_table(
        ("run", "backend", "rows"),
        [
            (name_of(run), select(rows, run_dir=run)[0]["backend"], len(select(rows, run_dir=run)))
            for run in sorted({r["run_dir"] for r in rows})
        ],
    )
    excluded_table = md_table(("directory under results/live", "reason"), excluded)
    resolution = "; ".join(resolve_reference(rows))
    parts = [
        "# Pathion evidence pivots",
        "",
        "`evidence_table.csv` holds one row per measured pathion reading on IBM Heron r2, Quantum Inspire and Quandela "
        "Ascella, each with its ideal, its standard error where the record's estimator produces one, and the claim "
        "ledger rows that cite its run. `scripts/pathion_evidence_table_build.py` writes both files; the pivots below "
        "are computed from the CSV read back from disk. The column definitions are the module docstring of "
        "`gororoba_quantum/pathion_evidence_table.py`.",
        "",
        "## Inputs",
        "",
        counts,
        "",
        runs,
        "",
        "The build uses the stdlib csv module (pandas is not in the interpreter's environment). IBM standard errors "
        "are the standard deviation over replicas divided by the square root of their count; readout-corrected IBM "
        "values, every four-term Ascella level and the pair job's raw level, normalized level and mirror difference "
        "carry no standard error because their records store no replica or counting variance for them (the pair "
        "job's per-slot level keeps the record's own error). Quantum Inspire values keep the series analysis's "
        "delta-method errors; their shots column sums each template's data circuits over its batches, and the "
        "stopped series' pinned reading has none. The unversioned QX analyses are superseded by their `.v2` "
        "successors, which the build compares template by template; the stopped Tuna-17 block series retains no "
        "template reading beyond the null selector contrast that the coin analysis pins, which enters as one row "
        "under the stopped series' path.",
        "",
        "Pathion directories under `results/live` without collected results:",
        "",
        excluded_table,
        "",
        "## Pivot a: readings per backend and observable",
        "",
        "Sign agreement counts readings whose ideal is nonzero, for observables with a signed ideal. The medians run "
        "over defined readings; the z of a reading is (measured - ideal) / standard error where the standard error "
        "exists.",
        "",
        pivot_a(rows),
        "",
        "## Pivot b: the same blocks on several backends",
        "",
        "Two-term blocks. A Tuna-17 bin and an IBM bin meet at their algebra output label, never at a coset index. "
        "D(y) is the Tuna-17 readout-corrected ratio c(y)/V minus the IBM raw ratio at the same label, its standard "
        "error the quadrature sum of the Tuna-17 delta-method error and the IBM replica spread, as "
        "`pathion_coset_analysis.cross_platform` computes it. The stored D(y) of each device matches the IBM run named "
        f"here (resolved by value): {resolution}.",
        "",
        pivot_b_two_term(rows),
        "",
        "Four-term blocks. Both IBM parallel-coset runs and both Ascella jobs read blocks B12/2 and C8/5 of the same "
        "four-term operands (the Ascella block ordinal equals the IBM coset). IBM levels are raw P(selector = 00) per "
        "arm; Ascella levels appear raw (a) and normalized by the job's anchor and dark readings (a prime; l hat for "
        "the pair job, normalized per slot).",
        "",
        pivot_b_four_term(rows),
        "",
        "## Pivot c: sim:ascella against qpu:ascella",
        "",
        "Each pair is one reading of the simulator job and the same reading of the QPU job (the same setting, block "
        "and arm); the delta is qpu minus sim.",
        "",
        pivot_c(rows),
        "",
        "## Pivot d: ledger rows against their readings",
        "",
        "Each check applies the row's own threshold to the table readings that the row's evidence column cites. Rows "
        "whose evidence is a conjecture log are marked as such and checked only for the table premise they use.",
        "",
        pivot_d(rows, ledger),
        "",
    ]
    return "\n".join(parts)


def build(out_dir: Path) -> dict[str, str]:
    rows, excluded = build_rows()
    csv_text = pet.render_csv(rows)
    parsed = pet.parse_table(csv_text)
    ledger = pet.parse_ledger(LEDGER.read_text(encoding="utf-8"))
    included = sorted({r["run_dir"] for r in parsed if r["platform"] == "ibm"})
    return {
        "evidence_table.csv": csv_text,
        "evidence_pivots.md": render_pivots(parsed, excluded, ledger, included),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--check", action="store_true", help="exit 1 when the files in --out-dir differ from a rebuild")
    args = parser.parse_args(argv)
    outputs = build(args.out_dir)
    if args.check:
        stale = [
            name
            for name, text in outputs.items()
            if not (args.out_dir / name).is_file() or (args.out_dir / name).read_text(encoding="utf-8") != text
        ]
        for name in stale:
            print(f"{name} differs from a rebuild", file=sys.stderr)
        return 1 if stale else 0
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in outputs.items():
        (args.out_dir / name).write_text(text, encoding="utf-8", newline="")
    print(f"wrote {len(outputs['evidence_table.csv'].splitlines()) - 1} rows to {args.out_dir / 'evidence_table.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
