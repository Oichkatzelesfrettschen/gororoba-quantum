"""Preregistered analysis of the three qpu:belenos off-cone mechanism runs.

Case: docs/design/belenos-offcone-mechanisms-case.md.

The case fixes the observable, the contrasts, the void rules and the falsifiers (cases.json preregistered); this
script applies them to three validated runs and leaves every choice the case does not fix to the list below.

Analyst choices, fixed before the retained data was read:

- Test. cases.json names the test and alpha: the exact two-sided binomial test, summing the masses not above the
  observed mass (relative tolerance 1e-7), alpha 0.05, the rule of the builder's power table
  (belenos_offcone_mechanisms.rejection_region, binomial_pmf), which this script imports.
- Null shares. The case names the share of each contrast; the analyst choice is to build each from the observed
  exposures of the valid entries: the drift share is samples(job-02) / (samples(job-00) + samples(job-02)), the
  mitigation share is samples(job-01) over the three jobs, the source share is the samples of source 22 over the
  pooled samples, and the sample-law share of the level contrast is samples(1500) / (samples(1500) + samples(60000)).
  The time-law share weights the 1500 samples by the case's physical_perf(60000) / physical_perf(1500) = 17.6; the
  share from the observed physical_perf of each entry is recorded beside it and never decides.
- Episodes bound. A source-22 entry may return its own mesh, whose ideal output puts a share s of the photon on
  detectors 20 and 21; detector-resolved episodes then give source 22 the presence share
  s * samples(22) / (samples(20) + s * samples(22)) at most. The script tests the observed count against that share
  with the same test and records the result beside the case's source contrast.
- Pooling. The source and level contrasts pool job-00 and job-02, and also job-01 when the mitigation contrast does
  not reject.
- Two layers. A mechanism's falsifier (Pre-flight 3) gives survives or falsified: balancing fails when the mitigation
  contrast does not reject (or rejects with job-01 above its share); episodes fail when the source contrast does not
  reject (or rejects with source 22 above its share); window_samples fails when the sample-law share of the level
  contrast is rejected; window_time fails when the time-law share is rejected. The case's reading (cases.json
  readings) names the one mechanism the pattern attributes, or no attribution.
- Void job. A job is void when it holds no valid entry of some source. A void entry is dropped and reported. A
  trailing entry without its pair is dropped; a run that holds fewer entries than its settings is refused.

Usage: "$PYTHON" scripts/belenos_offcone_mechanisms_analyze.py (--write OUT RUN... | --check OUT RUN...)
RUN is the case directory of each job with its raw result, three runs, in any order.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import belenos_offcone_mechanisms as case_lib  # noqa: E402
import qd_belenos_cone as cone_lib  # noqa: E402
import qd_belenos_mesh as mesh_lib  # noqa: E402

import qd_records  # noqa: E402

SCHEMA = "qd-belenos-offcone-mechanisms-analysis-v1"
HOT_MODE = 5
PRESENCE_MIN = 32
ALPHA = case_lib.ALPHA
DETECTORS = (20, 21)
SOURCES = (20, 22)
SERVED_MESH = "29dc6ef8"
OFF_CONE_REQUIRED = (0, 1, 5)
LEVEL_LOW = 1500
LEVEL_HIGH = 60000
TIME_LAW_RATIO = case_lib.PHYSICAL_PERF[LEVEL_HIGH] / case_lib.PHYSICAL_PERF[LEVEL_LOW]
TIE_TOLERANCE = 1e-7
FAMILY = "belenos_offcone_mechanisms"
PREDICTED_PRESENCES_PER_JOB = 77.51
PREDICTED_PRESENCES_PER_SOURCE = 38.76
PREDICTED_MODE_5_PER_JOB = 49.04
PREDICTED_RATE = 1.0841e-04
CAVEAT = (
    "couplers_checked is unread at plan and collect for every job: only the 2026-10-17 catalogue stamp backs "
    "the carried architecture, so a coupler change between that stamp and the runs is unchecked"
)


class AnalysisError(RuntimeError):
    pass


def binomial_two_sided(k: int, n: int, p: float) -> float:
    """Exact two-sided p-value: the summed masses that do not exceed the mass of k (the builder's rule)."""
    if n == 0:
        return 1.0
    masses = [case_lib.binomial_pmf(n, i, p) for i in range(n + 1)]
    return min(1.0, sum(m for m in masses if m <= masses[k] * (1 + TIE_TOLERANCE)))


def poisson_two_sided(k: int, mean: float) -> float:
    """Descriptive two-sided Poisson p-value of a count against its predicted mean (masses not above the observed)."""

    def mass(i: int) -> float:
        return i * math.log(mean) - mean - math.lgamma(i + 1)

    observed = mass(k)
    top = max(k, int(mean)) * 4 + 50
    return min(1.0, sum(math.exp(mass(i)) for i in range(top + 1) if mass(i) <= observed + math.log1p(TIE_TOLERANCE)))


def photons_of(computed_input: str) -> int:
    return sum(int(v) for v in computed_input.rsplit("|", 1)[1].rstrip(">").split(","))


def ideal_share(computed_circuit: str, source: int) -> float:
    """Ideal output share of one photon on the source mode that lands on detectors 20 and 21 of the returned mesh."""
    elements = mesh_lib.decode(computed_circuit)
    arch = mesh_lib.run_architecture(elements)
    ideal = mesh_lib.propagate(arch, mesh_lib.mesh_phases(arch, elements), source)[0]
    return round(float(sum(ideal[q] for q in DETECTORS)), 6)


def entry_of(
    row: dict[str, Any], setting: dict[str, Any], computed_input: str, acquisition: float, share: float = 0.0
) -> dict[str, Any]:
    """One entry with the case's void rules applied to the returned mesh, source and recorded samples."""
    mode = setting["input_mode"]
    problems: list[str] = []
    try:
        source = cone_lib.source_mode(computed_input)
    except ValueError:
        source = None
    if source != mode or photons_of(computed_input) != 1:
        problems.append(f"computed_input {computed_input} is not one photon on input_mode {mode}")
    if row["samples"] != setting["max_samples"]:
        problems.append(f"samples {row['samples']} differ from max_samples {setting['max_samples']}")
    cone = row["cone_modes"]
    if mode == 20 and not row["mesh_sha256"].startswith(SERVED_MESH):
        problems.append(f"served mesh {row['mesh_sha256'][:8]} is not {SERVED_MESH}")
    if mode == 22 and [q for q in OFF_CONE_REQUIRED if q in cone]:
        problems.append(f"modes {[q for q in OFF_CONE_REQUIRED if q in cone]} lie inside the cone of the returned mesh")
    if mode not in SOURCES:
        problems.append(f"input_mode {mode} is outside the case's sources")
    off = {int(q): n for q, n in row["off_cone_by_mode"].items()}
    primary = {q: n for q, n in off.items() if q != HOT_MODE}
    return {
        "name": row["name"],
        "source": mode,
        "level": setting["max_samples"],
        "samples": row["samples"],
        "mesh_sha256": row["mesh_sha256"],
        "cone_size": len(cone),
        "ideal_share_detectors": share,
        "acquisition_s": acquisition,
        "presences": sum(1 for n in primary.values() if n >= PRESENCE_MIN),
        "breaks_1_to_31": sum(1 for n in primary.values() if 1 <= n < PRESENCE_MIN),
        "presence_modes": sorted(q for q, n in primary.items() if n >= PRESENCE_MIN),
        "mode_5_presence": int(off.get(HOT_MODE, 0) >= PRESENCE_MIN),
        "mode_5_clicks": off.get(HOT_MODE, 0),
        "void": problems,
    }


def complete_pairs(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Adjacent source pairs: a trailing entry without its partner is dropped."""
    return entries[: len(entries) - len(entries) % 2]


def run_entries(run: Path) -> dict[str, Any]:
    """The validated run's entries; a run that fails the shared reader's validation or holds a cut result is refused."""
    try:
        validated = qd_records.validate_run(qd_records.load_run(run))
    except qd_records.RecordError as err:
        raise AnalysisError(f"{run.name}: refused by qd_records.validate_run: {err}") from err
    manifest = validated.manifest
    settings = manifest["settings"]
    inner = mesh_lib.raw_result(run)
    results = inner.get("results_list") or []
    if len(results) != len(settings):
        raise AnalysisError(f"{run.name}: {len(results)} entries for {len(settings)} settings (a cut run is refused)")
    rows = cone_lib.run_cells(run)
    entries = [
        entry_of(
            row,
            setting,
            result["computed_input"],
            row["acquisition_s_estimate"] or 0.0,
            ideal_share(result["computed_circuit"], setting["input_mode"]),
        )
        for row, setting, result in zip(rows, settings, results, strict=True)
    ]
    return {
        "run": run.name,
        "job": manifest["job"],
        "mitigations_off": manifest.get("mitigations") == [],
        "cases_sha256": validated.cases_sha256,
        "result_sha256": validated.collected["result_sha256"],
        "architecture_source": validated.submission["architecture_source"],
        "couplers_checked": validated.collected["couplers_checked"],
        "entries": complete_pairs(entries),
        "dropped_unpaired": len(entries) - len(complete_pairs(entries)),
    }


def valid(job: dict[str, Any]) -> list[dict[str, Any]]:
    return [e for e in job["entries"] if not e["void"]]


def tally(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "entries": len(entries),
        "samples": sum(e["samples"] for e in entries),
        "presences": sum(e["presences"] for e in entries),
        "mode_5_presences": sum(e["mode_5_presence"] for e in entries),
        "breaks_1_to_31": sum(e["breaks_1_to_31"] for e in entries),
        "acquisition_s": round(sum(e["acquisition_s"] for e in entries), 6),
    }


def contrast(k: int, n: int, share: float) -> dict[str, Any]:
    p = binomial_two_sided(k, n, share)
    rejects = n > 0 and k in case_lib.rejection_region(n, share)
    return {
        "k": k,
        "n": n,
        "null_share": round(share, 9),
        "observed_share": round(k / n, 9) if n else None,
        "p": float(f"{p:.4g}"),
        "rejects": rejects,
        "direction": None if not n or k / n == share else ("below" if k / n < share else "above"),
    }


def time_law_share(low_samples: int, high_samples: int, ratio: float) -> float:
    """Presence share of the low level when presences per sample at it are ratio times those of the high level."""
    weighted = ratio * low_samples
    return weighted / (weighted + high_samples) if weighted + high_samples else 0.5


def episodes_share(entries: list[dict[str, Any]]) -> float:
    """The largest presence share of source 22 that detector-resolved episodes allow: each entry's presences follow its
    source's ideal share on detectors 20 and 21 of the entry's own returned mesh."""
    lit = {s: sum(e["samples"] * e["ideal_share_detectors"] for e in entries if e["source"] == s) for s in SOURCES}
    return lit[22] / (lit[20] + lit[22]) if lit[20] + lit[22] else 0.5


def contrasts(jobs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    j0, j1, j2 = (valid(jobs[name]) for name in ("job-00", "job-01", "job-02"))
    s0, s1, s2 = (sum(e["samples"] for e in x) for x in (j0, j1, j2))
    p0, p1, p2 = (sum(e["presences"] for e in x) for x in (j0, j1, j2))
    drift = contrast(p2, p0 + p2, s2 / (s0 + s2) if s0 + s2 else 0.5)
    mitigation = contrast(p1, p0 + p1 + p2, s1 / (s0 + s1 + s2) if s0 + s1 + s2 else 1 / 3)
    pooled = j0 + j2 if mitigation["rejects"] else j0 + j1 + j2
    by_source = {s: [e for e in pooled if e["source"] == s] for s in SOURCES}
    source_samples = {s: sum(e["samples"] for e in by_source[s]) for s in SOURCES}
    total_samples = sum(source_samples.values())
    source_k = sum(e["presences"] for e in by_source[22])
    source_n = sum(e["presences"] for e in pooled)
    source = contrast(source_k, source_n, source_samples[22] / total_samples if total_samples else 0.5)
    bound = contrast(source_k, source_n, episodes_share(pooled))
    low = [e for e in pooled if e["level"] == LEVEL_LOW]
    high = [e for e in pooled if e["level"] == LEVEL_HIGH]
    k = sum(e["presences"] for e in low)
    n = k + sum(e["presences"] for e in high)
    samples = (sum(e["samples"] for e in low), sum(e["samples"] for e in high))
    seconds = (sum(e["acquisition_s"] for e in low), sum(e["acquisition_s"] for e in high))
    return {
        "drift": drift,
        "mitigation": mitigation,
        "pooled_jobs": ["job-00", "job-02"] if mitigation["rejects"] else ["job-00", "job-01", "job-02"],
        "source": source,
        "source_episodes_bound": bound,
        "level_sample_law": contrast(k, n, samples[0] / sum(samples) if sum(samples) else 0.5),
        "level_time_law": contrast(k, n, time_law_share(samples[0], samples[1], TIME_LAW_RATIO)),
        "level_time_law_observed_perf": contrast(k, n, seconds[0] / sum(seconds) if sum(seconds) else 0.5),
        "time_law_ratio": round(TIME_LAW_RATIO, 3),
    }


def verdicts(jobs: dict[str, dict[str, Any]], c: dict[str, Any]) -> dict[str, Any]:
    void_jobs = [
        name for name, job in jobs.items() if any(not any(e["source"] == s for e in valid(job)) for s in SOURCES)
    ]
    drift, mitigation, source = c["drift"], c["mitigation"], c["source"]
    sample_law, time_law = c["level_sample_law"], c["level_time_law"]
    falsifiers = {
        "balancing": not mitigation["rejects"] or mitigation["direction"] == "above",
        "episodes": not source["rejects"] or source["direction"] == "above",
        "window_samples": sample_law["rejects"],
        "window_time": time_law["rejects"],
    }
    mechanisms = {m: "falsified" if failed else "survives" for m, failed in falsifiers.items()}
    neither = not mitigation["rejects"] and not source["rejects"]
    holds = {
        "balancing": mitigation["rejects"] and mitigation["direction"] == "below",
        "episodes": not mitigation["rejects"] and source["rejects"] and source["direction"] == "below",
        "window_samples": neither and not sample_law["rejects"] and time_law["rejects"],
        "window_time": neither and not time_law["rejects"] and sample_law["rejects"],
    }
    matched = [m for m, ok in holds.items() if ok]
    blocked = bool(void_jobs) or drift["rejects"]
    reading = matched[0] if len(matched) == 1 and not blocked else "no attribution"
    return {
        "falsifier_layer": mechanisms,
        "case_reading": reading,
        "reading_conditions_met": matched,
        "void_jobs": void_jobs,
        "drift_rejected": drift["rejects"],
        "episodes_exceeded_by_source_split": bool(c["source_episodes_bound"]["rejects"]),
    }


def prediction(jobs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for name, job in jobs.items():
        entries = valid(job)
        by_source = {str(s): sum(e["presences"] for e in entries if e["source"] == s) for s in SOURCES}
        total = sum(e["presences"] for e in entries)
        samples = sum(e["samples"] for e in entries)
        mode5 = sum(e["mode_5_presence"] for e in entries)
        rows[name] = {
            "presences": total,
            "predicted_presences": PREDICTED_PRESENCES_PER_JOB,
            "presences_poisson_p": float(f"{poisson_two_sided(total, PREDICTED_PRESENCES_PER_JOB):.3g}"),
            "presences_by_source": by_source,
            "predicted_by_source": PREDICTED_PRESENCES_PER_SOURCE,
            "mode_5_presences": mode5,
            "predicted_mode_5_presences": PREDICTED_MODE_5_PER_JOB,
            "mode_5_poisson_p": float(f"{poisson_two_sided(mode5, PREDICTED_MODE_5_PER_JOB):.3g}"),
            "presences_per_sample": round(total / samples, 9) if samples else None,
            "rate_over_predicted": round(total / samples / PREDICTED_RATE, 6) if samples else None,
        }
    return rows


def cells(jobs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for name in sorted(jobs):
        for source in SOURCES:
            for level in sorted({e["level"] for e in valid(jobs[name])}):
                members = [e for e in valid(jobs[name]) if e["source"] == source and e["level"] == level]
                out.append({"job": name, "source": source, "level": level} | tally(members))
    return out


def modes_of(jobs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Which off-cone modes carry the presences, per source, and the meshes each source returned."""
    entries = [e for job in jobs.values() for e in valid(job)]
    return {
        str(source): {
            "presence_modes": {
                str(q): sum(q in e["presence_modes"] for e in entries if e["source"] == source)
                for q in sorted({q for e in entries if e["source"] == source for q in e["presence_modes"]})
            },
            "returned_meshes": sorted({e["mesh_sha256"][:8] for e in entries if e["source"] == source}),
            "cone_sizes": sorted({e["cone_size"] for e in entries if e["source"] == source}),
            "max_mode_5_clicks": max((e["mode_5_clicks"] for e in entries if e["source"] == source), default=0),
        }
        for source in SOURCES
    }


def analysis(runs: list[Path]) -> dict[str, Any]:
    loaded = [run_entries(r) for r in runs]
    jobs = {j["job"]: j for j in loaded}
    if sorted(jobs) != ["job-00", "job-01", "job-02"] or len(jobs) != len(loaded):
        raise AnalysisError(f"expected job-00, job-01 and job-02 once each, got {[j['job'] for j in loaded]}")
    arms = {name: job["mitigations_off"] for name, job in jobs.items()}
    if arms != {"job-00": False, "job-01": True, "job-02": False}:
        raise AnalysisError(f"mitigation arms {arms} differ from the case (only job-01 sends mitigations = [])")
    c = contrasts(jobs)
    return {
        "schema": SCHEMA,
        "case": "docs/design/belenos-offcone-mechanisms-case.md",
        "presence_rule": (
            f"off-cone mode other than {HOT_MODE} with one-click count >= {PRESENCE_MIN}; mode {HOT_MODE} separate"
        ),
        "alpha": ALPHA,
        "caveat": CAVEAT,
        "jobs": {
            name: {
                "run": job["run"],
                "cases_sha256": job["cases_sha256"],
                "result_sha256": job["result_sha256"],
                "architecture_source": job["architecture_source"],
                "couplers_checked": job["couplers_checked"],
                "mitigations_off": job["mitigations_off"],
                "dropped_unpaired": job["dropped_unpaired"],
                "all_entries": tally(job["entries"]),
                "valid_entries": tally(valid(job)),
                "void_entries": [{"name": e["name"], "void": e["void"]} for e in job["entries"] if e["void"]],
                "distinct_returned_meshes": sorted({e["mesh_sha256"][:8] for e in job["entries"]}),
            }
            for name, job in sorted(jobs.items())
        },
        "cells": cells(jobs),
        "sources": modes_of(jobs),
        "contrasts": c,
        "verdict": verdicts(jobs, c),
        "prediction_vs_outcome": prediction(jobs),
        "entries": {
            name: [{k: v for k, v in e.items() if k != "void"} | {"void": bool(e["void"])} for e in job["entries"]]
            for name, job in sorted(jobs.items())
        },
    }


def dump(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path, metavar="OUT")
    mode.add_argument("--check", type=Path, metavar="OUT")
    parser.add_argument("runs", nargs=3, type=Path)
    args = parser.parse_args()
    try:
        text = dump(analysis(args.runs))
    except AnalysisError as err:
        print(f"refused: {err}", file=sys.stderr)
        return 2
    if args.write:
        args.write.write_text(text, encoding="utf-8")
        print(f"wrote {args.write}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        print(f"{args.check} differs from the recomputed record", file=sys.stderr)
        return 1
    print(f"{args.check} matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
