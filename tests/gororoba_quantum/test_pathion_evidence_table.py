"""Contracts of the pathion evidence table: row counts per input, one known reading per platform, the byte-identical
CSV on a rerun, and the key parser.

The fast tests read the small cuts under tests/data/pathion_evidence/, each cut from a retained record by the
functions below (running this file as a script, with ci/, gororoba_quantum/ and scripts/ on PYTHONPATH, rewrites
them):

- coset_map_group.json and kernel_map_group.json keep the whole summary of an IBM group (every key, every replica,
  the readout-corrected summary) and the measured laws of two operands, from results/live/2026-11-06T200832.558771Z
  (sha256 003031ac...) and results/live/2026-11-06T183538.809814Z (sha256 79eaf03b...);
- coin_tuna.json keeps the templates, decisions and manifest of the coin series, from
  results/quantum_inspire/pathion_coset_coin_tuna_17_analysis.json (sha256 c6013cdb...) and its batch manifests;
- ascella_*.json keep the classes and readings of three Quandela analyses.

The audit tests compare each cut with its retained record, count the rows of every IBM run, and compare the IBM
per-output ratios with the reference reader of the Tuna-17 series, which verifies the record's digest.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping
from functools import cache
from pathlib import Path
from typing import Any

import pytest

import pathion_evidence_table as pet

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "tests/data/pathion_evidence"
LIVE = ROOT / "results/live"
QI = ROOT / "results/quantum_inspire"
QUANDELA = ROOT / "results/quandela/runs"
LEDGER = ROOT / "docs/evidence/a5-exceptional-fibers/ledger.tsv"
KERNEL_MAP = "2026-11-06T183538.809814Z"
MARRAKESH_COSET = "2026-11-06T200832.558771Z"
FOUR_TERM_QPU = "2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00"
PAIRS_QPU = "2026-11-07T003204Z-qpu_ascella-ascella_pathion_coset_block_pairs-job-00"
PAIRS_SIM = "2026-11-07T002936Z-sim_ascella-ascella_pathion_coset_block_pairs-sim-00"
COIN_ANALYSIS = "pathion_coset_coin_tuna_17_analysis.json"
STOPPED_ANALYSIS = "pathion_coset_block_tuna_17_analysis.json"
SOURCE_SHA256 = {
    f"results/live/{KERNEL_MAP}/collect.json": ("79eaf03b9c5f0af8dda754b780b7a3d497f55fc548a087a089c0213d5fc0f6e8"),
    f"results/live/{MARRAKESH_COSET}/collect.json": (
        "003031ac080ca40af9c20924109b5659c38b06554591eb65ef1f68e853c76093"
    ),
    f"results/quantum_inspire/{COIN_ANALYSIS}": ("c6013cdbb707dc1282c722bd73b5b33fce00b872a0e18bfaa782104436395daf"),
    f"results/quandela/runs/{FOUR_TERM_QPU}/analysis.json": (
        "81624d7ed0d1818592d03c0b474a5a987339b8add7945f8f3cfb02eef384a84d"
    ),
    f"results/quandela/runs/{PAIRS_QPU}/analysis.json": (
        "bcda45d21f20b039166b60b13e8ee593559977d0e8c03e92b5b5bc4ccc43015e"
    ),
    f"results/quandela/runs/{PAIRS_SIM}/analysis.json": (
        "eccd2973bd1512601a453ef2d0215193224dc5d9ba327c9ab2110195408111fe"
    ),
}
# IBM runs and their row counts (summary rows, per-output rows) over the whole retained record.
IBM_RUNS = {
    KERNEL_MAP: (214, 704),
    MARRAKESH_COSET: (306, 512),
    "2026-11-06T201037.234804Z": (306, 512),
    "2026-11-07T042346.084449Z": (742, 512),
    "2026-11-07T042521.359670Z": (742, 512),
}
KEEP = {"kernel_map_group": ("kmap_e1pe18_",), "coset_map_group": ("cmap_e1pe18_k", "cmap_e1pe17_k0_")}


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _close(value: float | None, expected: float, tolerance: float, message: str) -> None:
    _check(value is not None and abs(value - expected) <= tolerance, f"{message}: {value} against {expected}")


# ---------------------------------------------------------------- cutting the fixtures from the retained records


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def cut_group(group: Mapping[str, Any], prefixes: Iterable[str]) -> dict[str, Any]:
    keep = tuple(prefixes)

    def kept(name: str) -> bool:
        return name.startswith(keep)

    statistics = group["measured_statistics"]
    return {
        "group": group["group"],
        "backend": group["backend"],
        "job_id": group["job_id"],
        "executed": {k: {"shots": v["shots"]} for k, v in group["executed"].items() if kept(k)},
        "measured": {k: v for k, v in group["measured"].items() if kept(k)},
        "measured_statistics": {
            "summary": statistics["summary"],
            "summary_per_replica": statistics["summary_per_replica"],
        },
        "measured_summary_readout_corrected": group["measured_summary_readout_corrected"],
    }


def cut_tuna() -> dict[str, Any]:
    series = QI / "cases/pathion_coset_coin_tuna_17"
    manifest = _read(series / "batch-00/cases.json")
    analysis = _read(QI / COIN_ANALYSIS)
    batches = [_read(p) for p in sorted(series.glob("batch-*/cases.json"))]
    return {
        "analysis": {k: analysis[k] for k in ("backend", "templates", "decisions")},
        "manifest": {k: manifest[k] for k in ("templates", "labels")},
        "batches": [
            {
                "shots": b["shots"],
                "circuits": [{"kind": c["kind"], "template": c.get("template")} for c in b["circuits"]],
            }
            for b in batches
        ],
    }


def cut_ascella(name: str) -> dict[str, Any]:
    analysis = _read(QUANDELA / name / "analysis.json")
    return {
        "analysis": {k: analysis[k] for k in ("schema", "backend", "classes", "readings") if k in analysis},
        "operands": _read(QUANDELA / name / "cases.json")["operands"],
    }


def cuts() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for fixture, directory in (("kernel_map_group", KERNEL_MAP), ("coset_map_group", MARRAKESH_COSET)):
        group = pet.find_group(_read(LIVE / directory / "collect.json"))
        out[fixture] = cut_group(group, KEEP[fixture])
    out["coin_tuna"] = cut_tuna()
    out["ascella_four_term_qpu"] = cut_ascella(FOUR_TERM_QPU)
    out["ascella_pairs_qpu"] = cut_ascella(PAIRS_QPU)
    out["ascella_pairs_sim"] = cut_ascella(PAIRS_SIM)
    return out


def render(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


# ---------------------------------------------------------------- rows from the fixtures


@cache
def _fixture(name: str) -> dict[str, Any]:
    return _read(DATA / f"{name}.json")


@cache
def _ledger() -> list[dict[str, str]]:
    return pet.parse_ledger(LEDGER.read_text(encoding="utf-8"))


@cache
def _classes_and_operands() -> tuple[dict[tuple[str, int], str], dict[str, str]]:
    cut = _fixture("ascella_four_term_qpu")
    return pet.class_table(cut["analysis"]), {n: pet.terms_text(t) for n, t in cut["operands"].items()}


def _ibm_rows(group: dict[str, Any], run_dir: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    classes, operands = _classes_and_operands()
    ideal, laws = pet.ideal_inputs(group["group"])
    source_file = f"{run_dir}/collect.json"
    summary = pet.ibm_summary_rows(
        group,
        ideal,
        run_dir=run_dir,
        source_file=source_file,
        four_term_operands=operands,
        block_classes=classes,
        ledger=_ledger(),
    )
    bins = pet.ibm_bin_rows(group, laws, ideal, run_dir=run_dir, source_file=source_file, ledger=_ledger())
    return summary, bins


@cache
def _ibm_fixture(name: str, directory: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _ibm_rows(_fixture(name), f"results/live/{directory}")


@cache
def _quandela(fixture: str, name: str) -> list[dict[str, Any]]:
    cut = _fixture(fixture)
    classes, _ = _classes_and_operands()
    return pet.ascella_rows(
        cut["analysis"],
        cut["operands"],
        run_dir=f"results/quandela/runs/{name}",
        source_file=f"results/quandela/runs/{name}/analysis.json",
        classes=classes,
        ledger=_ledger(),
    )


@cache
def _tuna() -> list[dict[str, Any]]:
    cut = _fixture("coin_tuna")
    run_dir = f"results/quantum_inspire/{COIN_ANALYSIS}"
    return pet.tuna_rows(
        cut["analysis"],
        cut["manifest"],
        run_dir=run_dir,
        source_file=run_dir,
        ledger=_ledger(),
        stopped_run_dir=f"results/quantum_inspire/{STOPPED_ANALYSIS}",
        shots_by_template=pet.template_shots(cut["batches"]),
    )


def _pick(rows: list[dict[str, Any]], **fields: Any) -> list[dict[str, Any]]:
    return [r for r in rows if all(r[k] == v for k, v in fields.items())]


def _one(rows: list[dict[str, Any]], **fields: Any) -> dict[str, Any]:
    found = _pick(rows, **fields)
    _check(len(found) == 1, f"{fields} matches {len(found)} rows")
    return found[0]


# ---------------------------------------------------------------- fast tests


def test_ibm_kernel_map_rows_and_the_nullity_of_the_ledger() -> None:
    summary, bins = _ibm_fixture("kernel_map_group", KERNEL_MAP)
    _check((len(summary), len(bins)) == (214, 64), f"row counts {(len(summary), len(bins))}")
    n_hat = _one(summary, observable="N_hat", operand="e1+e18", control="primary", block=None, calibration="raw")
    _close(n_hat["measured"], 12.65, 0.005, "A5-180 N_hat of e1+e18")
    _check(n_hat["ideal"] == 12.0 and n_hat["ledger_row"] == "A5-179;A5-180", "ideal and ledger rows of the kernel map")
    _check(n_hat["backend"] == "ibm_fez" and n_hat["standard_error"] is not None, "backend and standard error")
    twin = _one(summary, observable="N_hat", operand="e17-e2", control="twin", block=None, calibration="raw")
    _close(twin["measured"], 11.87, 0.005, "A5-180 N_hat of the twin")
    skeleton = _one(summary, observable="skeleton_p0", calibration="raw")
    _close(skeleton["ideal"], 1.0, 1e-9, "skeleton ideal")
    _check(skeleton["measured"] is not None and skeleton["measured"] > 0.97, "skeleton reads one minus readout error")
    undefined = [r for r in summary + bins if r["status"] == "undefined"]
    _check(len(undefined) == 2 and all(r["observable"] == "contrast_ratio" for r in undefined), "undefined readings")
    _check(len(_pick(bins, observable="output_contrast")) == 32, "the kernel map reads 32 outputs")


def test_ibm_coset_map_rows_and_the_marrakesh_reading_of_the_findings() -> None:
    summary, bins = _ibm_fixture("coset_map_group", MARRAKESH_COSET)
    _check((len(summary), len(bins)) == (306, 80), f"row counts {(len(summary), len(bins))}")
    raw = _one(summary, observable="N_hat", operand="e1+e18", control="primary", block=None, calibration="raw")
    corrected = _one(
        summary, observable="N_hat", operand="e1+e18", control="primary", block=None, calibration="readout_corrected"
    )
    _close(raw["measured"], 12.02, 0.005, "Marrakesh e1+e18 raw N_hat")
    _close(corrected["measured"], 11.99, 0.005, "Marrakesh e1+e18 corrected N_hat")
    _check(corrected["standard_error"] is None and corrected["readout_corrected"], "a corrected value carries no error")
    _check(raw["n_replicas"] == 11 and raw["ledger_row"] == "A5-182", "replica count and ledger row")
    free = _one(summary, observable="N_hat", control="cocycle-free", block=None, calibration="readout_corrected")
    _close(free["measured"], -1.85, 0.005, "Marrakesh cocycle-free corrected N_hat")
    block = _one(summary, observable="N_hat", operand="e1+e18", control="primary", block="k0", calibration="raw")
    _check(block["block_class"].startswith("nullity-") and block["shots"] == 8192, "block class and shots")
    labels = sorted(r["label"] for r in _pick(bins, observable="output_ratio", operand="e1+e18"))
    _check(labels == list(range(32)), "the four blocks of e1+e18 cover the 32 output labels once")


def test_tuna_rows_reproduce_the_coin_series_findings_and_the_stored_differences() -> None:
    rows = _tuna()
    _check(len(rows) == 226, f"{len(rows)} rows")
    run_dir = f"results/quantum_inspire/{COIN_ANALYSIS}"
    selector = _one(rows, observable="selector_contrast", block="ba", run_dir=run_dir)
    _close(selector["measured"], 0.2350, 5e-5, "ba selector contrast")
    _close(selector["standard_error"], 0.0038, 5e-5, "ba selector standard error")
    xor = _one(rows, observable="selector_contrast", block="xor_ba")
    _close(xor["measured"], -0.7181, 5e-5, "cocycle-free selector contrast")
    _check(xor["control"] == "cocycle-free" and selector["ledger_row"] == "A5-184;A5-185;A5-187", "control, ledger")
    _check((selector["shots"], xor["shots"]) == (65536, 16384), "shots come from the batch that ran the template")
    stopped = _one(rows, observable="selector_contrast", run_dir=f"results/quantum_inspire/{STOPPED_ANALYSIS}")
    _close(stopped["measured"], 0.0167, 5e-5, "stopped series null selector contrast")
    _check(stopped["shots"] is None and stopped["ledger_row"] == "A5-185", "stopped series: no shots, ledger row")
    differences = _pick(
        rows, observable="D_y", calibration="readout_corrected", block="ba", reference_backend="ibm_fez"
    )
    within = sum(abs(r["measured"]) <= 3.0 * r["standard_error"] for r in differences)
    _check(len(differences) == 8 and within == 5, f"{within} of {len(differences)} ba bins within 3 se of ibm_fez")
    visibility = _one(rows, observable="visibility", block="ba", calibration="raw")
    _close(visibility["ideal"], 0.999817, 1e-12, "the visibility ideal is the rounded circuit's")


def test_template_shots_sum_the_data_circuits_of_each_batch() -> None:
    batches = [
        {"shots": 100, "circuits": [{"kind": "readout", "template": None}, {"kind": "arm", "template": "ba"}]},
        {"shots": 50, "circuits": [{"kind": "arm", "template": "ba"}, {"kind": "arm", "template": "bb"}]},
    ]
    _check(pet.template_shots(batches) == {"ba": 150, "bb": 50}, "template shots")


def test_ascella_rows_per_run_and_the_findings_readings() -> None:
    four_term = _quandela("ascella_four_term_qpu", FOUR_TERM_QPU)
    pairs, simulated = _quandela("ascella_pairs_qpu", PAIRS_QPU), _quandela("ascella_pairs_sim", PAIRS_SIM)
    _check((len(four_term), len(pairs), len(simulated)) == (132, 184, 184), "row counts")
    top = _one(four_term, setting="c8-4", arm="T", calibration="anchor_dark_normalized")
    _close(top["measured"], 0.6311, 5e-5, "qpu C8 block 4 T level")
    _close(top["ideal"] - top["measured"], 0.0234, 5e-5, "the 0.0234 shortfall of C8 block 4")
    _check(top["dimension"] == 32 and top["block_class"] == "census-4415", "dimension and census class")
    _check(top["ledger_row"] == "A5-188" and top["standard_error"] is None, "ledger row; no standard error stored")
    anchor = _pick(four_term, control="anchor", calibration="raw")
    _check(len(anchor) == 4 and all(r["dimension"] == 32 for r in anchor), "A16 anchor readings sit in A_5")
    mirrors = _pick(pairs, observable="mirror_difference")
    _check(len(mirrors) == 46 and sum(r["measured"] > 0.07 for r in mirrors) == 9, "9 of 46 mirrors fail on the QPU")
    _check(max(r["measured"] for r in _pick(simulated, observable="mirror_difference")) < 0.0067, "sim mirrors")
    _check(_pick(simulated, observable="level")[0]["ledger_row"] is None, "sim:ascella cites no ledger row")


def test_csv_bytes_are_deterministic_and_round_trip() -> None:
    rows = _quandela("ascella_pairs_qpu", PAIRS_QPU) + _quandela("ascella_four_term_qpu", FOUR_TERM_QPU) + _tuna()
    first = pet.render_csv(rows)
    second = pet.render_csv(list(reversed(rows)))
    _check(first == second, "the CSV depends on the order of its input rows")
    _check("\r" not in first and first.endswith("\n"), "the CSV is LF-terminated")
    parsed = pet.parse_table(first)
    _check(len(parsed) == len(rows), "a row was lost in the round trip")
    _check(pet.render_csv(parsed) == first, "the parsed table does not render to the same bytes")
    _check(tuple(first.splitlines()[0].split(",")) == pet.COLUMNS, "the header differs from COLUMNS")
    for row in parsed:
        _check(row["measured"] is None or math.isfinite(row["measured"]), "a non-finite measured value was written")


def test_row_builder_rejects_unknown_columns_and_a_missing_ideal() -> None:
    with pytest.raises(ValueError, match="unknown columns"):
        pet.make_row(run_dir="x", colour="red")
    with pytest.raises(ValueError, match="no ideal"):
        pet.make_row(run_dir="x", observable="level", measured=0.5)
    row = pet.make_row(run_dir="x", observable="level", measured=float("nan"))
    _check(row["status"] == "undefined" and row["measured"] is None, "a non-finite reading is undefined")


def test_ledger_citation_matches_the_run_directory_and_its_files() -> None:
    ledger = [
        {"id": "A5-1", "evidence": "results/live/RUN/collect.json;docs/x.md"},
        {"id": "A5-2", "evidence": "results/live/RUN2/collect.json"},
        {"id": "A5-3", "evidence": "results/live/RUN"},
    ]
    _check(pet.ledger_cites(ledger, "results/live/RUN") == "A5-1;A5-3", "citation by directory or file")
    _check(pet.ledger_cites(ledger, "results/live/NONE") == "", "no citation")


def test_key_parser_names_every_family_and_refuses_an_unknown_key() -> None:
    nullity = {"cmap_e1pe17": 0.0}
    operands = {"B12": "e1+e10+e20+e31"}
    cases = {
        "cmap_e1pe17_k4_nullity_estimate": ("N_hat", "null", "k4"),
        "cmap_twin_e17me2_k0_visibility": ("visibility", "twin", "k0"),
        "cmap_xor_e1pe18_nullity_estimate": ("N_hat", "cocycle-free", ""),
        "cmap_e1pe18_k8_flip_selector_contrast": ("selector_contrast", "readout-flip", "k8"),
        "kmap_flip3_e1pe18_contrast": ("selector_contrast", "mutation", ""),
        "ftb_B12_c2_closure_N": ("closure", "mutation", "B12/2"),
        "ftb_B12_c2_level_E0": ("level", "null", "B12/2"),
    }
    for key, (observable, control, block) in cases.items():
        parsed = pet.parse_key(key, nullity, operands)
        if parsed is None:
            raise AssertionError(f"{key} did not parse")
        _check((parsed.observable, parsed.control, parsed.block) == (observable, control, block), f"{key}: {parsed}")
    _check(pet.parse_key("cmap_e1pe18_k8_nullity_ideal", nullity, operands) is None, "ideal-only keys are skipped")
    with pytest.raises(ValueError, match="unparsed"):
        pet.parse_key("zmap_e1pe18_contrast", nullity, operands)


# ---------------------------------------------------------------- audit tests over the retained records


@pytest.mark.audit
def test_fixtures_are_the_cuts_of_the_retained_records() -> None:
    for relative, digest in SOURCE_SHA256.items():
        _check(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, f"{relative} changed")
    for name, cut in cuts().items():
        _check((DATA / f"{name}.json").read_text(encoding="utf-8") == render(cut), f"{name}.json differs from its cut")


@pytest.mark.audit
@pytest.mark.parametrize("directory", sorted(IBM_RUNS))
def test_ibm_row_counts_over_every_retained_run(directory: str) -> None:
    group = pet.find_group(_read(LIVE / directory / "collect.json"))
    summary, bins = _ibm_rows(group, f"results/live/{directory}")
    _check((len(summary), len(bins)) == IBM_RUNS[directory], f"{directory}: {(len(summary), len(bins))}")


@pytest.mark.audit
def test_ibm_per_output_ratios_equal_the_reference_reader_of_the_tuna_series() -> None:
    import qi_pathion_coset_block_cases as cases

    group = pet.find_group(_read(LIVE / MARRAKESH_COSET / "collect.json"))
    _, bins = _ibm_rows(group, f"results/live/{MARRAKESH_COSET}")
    reference = cases.ibm_reference("ibm_marrakesh")
    worst = 0.0
    for tag, operand in (("e1pe18", "e1+e18"), ("e1pe26", "e1+e26"), ("e1pe17", "e1+e17")):
        rows = _pick(bins, observable="output_ratio", operand=operand, calibration="raw")
        rows = [r for r in rows if r["control"] in ("primary", "null")]
        _check(sorted(r["label"] for r in rows) == list(range(32)), f"{operand}: the blocks cover 32 labels once")
        for row in rows:
            entry = reference[tag]["labels"][row["label"]]
            worst = max(worst, abs(entry["ratio"] - row["measured"]), abs(entry["se_mean"] - row["standard_error"]))
    _check(worst < 1e-12, f"ratio and standard error differ from ibm_reference by {worst}")


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    for name, cut in cuts().items():
        (DATA / f"{name}.json").write_text(render(cut), encoding="utf-8", newline="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
