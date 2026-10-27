"""Exposure sensitivity of every retained Quandela analysis whose dark subtraction depends on an exposure model.

qd_box_kite_analysis.acquisition_seconds models the detector exposure as samples / (physical_perf x clock), a
timing model no Quandela document confirms. Two retained consumers subtract dark counts over it: the Belenos leakage
root-cause record (qd_belenos_mesh.rca_record, docs/evidence/quandela/belenos_leakage_rca.json) and the one-photon
block's dark_corrected figures of qd_box_kite_analysis.analyze. This replay recomputes both from the raw runs under
three exposures: none (no subtraction), the retained physical_perf model, and the whole job duration. For the
root-cause record it reports the decisive comparisons the registry claim rests on (the ideal compiled mesh against
the shot-noise floor, the best single-parameter model against that floor, the convention ranking); for each
one-photon block it reports the dark-corrected in_block and a under each exposure beside the uncorrected values, and
whether the physical_perf scenario replays the retained analysis.json. Retained records and runs stay byte-identical;
`--check` recomputes and compares the retained output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RETAINED = ROOT / "docs/evidence/quandela/belenos_leakage_rca.json"
OUT = Path(__file__).with_name("exposure_sensitivity.json")
SCHEMA = "quandela-exposure-sensitivity-v1"


def scenario(scale: str) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    import qd_belenos_mesh
    import qd_box_kite_analysis

    model = qd_box_kite_analysis.acquisition_seconds
    run = qd_belenos_mesh.RUNS / qd_belenos_mesh.Q1_RUN
    duration = float(json.loads((run / "raw/result.json").read_text(encoding="utf-8"))["duration"])

    def exposure(samples: int, physical_perf: Any, clock_mhz: Any) -> float | None:
        seconds = model(samples, physical_perf, clock_mhz)
        if seconds is None:
            return None
        return {"none": 0.0, "physical_perf_model": seconds, "job_duration": duration}[scale]

    retained = json.loads(RETAINED.read_text(encoding="utf-8"))
    sources = [int(k) for k in retained["hypotheses"]["single_wrong_source"]]
    qd_box_kite_analysis.acquisition_seconds = exposure  # observed() imports the name at call time
    try:
        record = qd_belenos_mesh.rca_record(sources)
    finally:
        qd_box_kite_analysis.acquisition_seconds = model
    h = record["hypotheses"]
    floor = h["shot_noise_floor"]
    single = {
        "gain": h["gain"]["tvd"],
        "crosstalk": h["crosstalk"]["tvd"],
        "ceiling": h["ceiling"]["tvd"],
        "phase_noise": min(h["phase_noise"].values()),
        "wrong_source": min(h["single_wrong_source"].values()),
    }
    observed = record["observed"]
    counts = observed["single_click"]
    dark = observed["dark_expected"]
    return {
        "exposure": scale,
        "exposure_s": observed["acquisition_s_estimate"],
        "dark_expected_total": round(sum(dark), 3),
        "modes_with_dark_above_counts": [m for m, (c, d) in enumerate(zip(counts, dark, strict=True)) if d > c],
        "shot_noise_floor": floor,
        "ideal_compiled_mesh_tvd": h["ideal_compiled_mesh"],
        "best_single_parameter": min(single, key=lambda k: single[k]),
        "best_single_parameter_tvd": min(single.values()),
        "convention_order": sorted(h["conventions"], key=lambda k: h["conventions"][k]),
        "ideal_exceeds_floor": h["ideal_compiled_mesh"] > floor,
        "no_single_parameter_reaches_floor": min(single.values()) > floor,
    }


SCENARIOS = ("none", "physical_perf_model", "job_duration")


def corrected_blocks(analysis: dict[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    return [(i, b) for i, b in enumerate(analysis.get("blocks", [])) if b.get("dark_corrected") is not None]


def box_kite(run: Path) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    import qd_box_kite_analysis

    model = qd_box_kite_analysis.acquisition_seconds
    duration = float(json.loads((run / "raw/result.json").read_text(encoding="utf-8"))["duration"])
    retained = json.loads((run / "analysis.json").read_text(encoding="utf-8"))
    rows: dict[str, Any] = {}
    replays = None
    for scale in SCENARIOS:

        def exposure(samples: int, physical_perf: Any, clock_mhz: Any, scale: str = scale) -> float | None:
            seconds = model(samples, physical_perf, clock_mhz)
            if seconds is None:
                return None
            return {"none": 0.0, "physical_perf_model": seconds, "job_duration": duration}[scale]

        qd_box_kite_analysis.acquisition_seconds = exposure  # dark_expectation reads the module name per call
        try:
            fresh = qd_box_kite_analysis.analyze(run)
        finally:
            qd_box_kite_analysis.acquisition_seconds = model
        if scale == "physical_perf_model":
            replays = qd_box_kite_analysis.text(fresh) == qd_box_kite_analysis.text(retained)
        rows[scale] = {str(i): b["dark_corrected"] for i, b in corrected_blocks(fresh)}
    blocks = {}
    for i, block in corrected_blocks(retained):
        values = [rows[s][str(i)] for s in SCENARIOS]
        blocks[str(i)] = {
            "config": block.get("config"),
            "uncorrected": {"in_block": block["in_block"], "a": block.get("a")},
            "by_exposure": dict(zip(SCENARIOS, values, strict=True)),
            "in_block_span": round(max(v["in_block"] for v in values) - min(v["in_block"] for v in values), 9),
            "a_span": round(max(v["a"] for v in values) - min(v["a"] for v in values), 9)
            if all(v.get("a") is not None for v in values)
            else None,
        }
    return {"run": run.name, "duration_s": duration, "replays_retained": replays, "blocks": blocks}


def record() -> dict[str, Any]:
    rows = [scenario(s) for s in SCENARIOS]
    keys = ("ideal_exceeds_floor", "no_single_parameter_reaches_floor", "convention_order")
    runs = sorted(
        p.parent
        for p in (ROOT / "results/quandela/runs").glob("*/analysis.json")
        if corrected_blocks(json.loads(p.read_text(encoding="utf-8")))
    )
    return {
        "schema": SCHEMA,
        "root_cause": {
            "retained_record": str(RETAINED.relative_to(ROOT)),
            "scenarios": rows,
            "conclusions_invariant": all(all(r[k] == rows[0][k] for k in keys) for r in rows),
        },
        "one_photon_blocks": [box_kite(run) for run in runs],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(record(), indent=1, sort_keys=True) + "\n"
    if args.check:
        # The root-cause TVDs come from 24 x 24 complex unitaries whose last bits differ between BLAS builds, so
        # numbers compare within qd_belenos_mesh.close_relative and strings, flags and orders compare exactly.
        import qd_belenos_mesh

        try:
            qd_belenos_mesh.close_relative(json.loads(text), json.loads(OUT.read_text(encoding="utf-8")))
        except qd_belenos_mesh.MeshError as error:
            print(f"{OUT.relative_to(ROOT)} differs from the recomputed sensitivity: {error}", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
