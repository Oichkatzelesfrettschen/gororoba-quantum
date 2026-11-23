"""Billing v4 sizing of the two PR 987 case variants, written to docs/evidence/iqm-garnet-grover-plane/variant_sizing.json.

The variants are grover-plane-mirrored (mark 101 and mark 011 arms, 52 circuits) and grover-plane-mirrored-101 (the mark 101
arms alone, 38 circuits). Each is priced by the three Garnet models of docs/evidence/iqm-billing-v4 (v3, v4_sum, v4_max; the
coefficients are pinned in billing_v4_inputs.json with the commit and digest of billing_v4.json): the schedule of the case
comes from the schedule model of that record, the models add their excess, and the band adds the model's largest
leave-one-out residual and the schedule model's relative error times the schedule, under the all-jobs error (the sizing
adopted) and under the Grover-jobs error (reported beside). The credits buy 1.5 times the worst case; the margins state how
many seconds of the cancel threshold remain at a runtime overrun of 1.5 and of 2.2 times the expected runtime.

Usage: "$PYTHON" scripts/iqm_grover_plane_sizing.py --out docs/evidence/iqm-garnet-grover-plane/variant_sizing.json
       "$PYTHON" scripts/iqm_grover_plane_sizing.py --check docs/evidence/iqm-garnet-grover-plane/variant_sizing.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import grover_plane_sizing as sizing  # noqa: E402
import iqm_grover_plane_case as case  # noqa: E402

SCHEMA = "iqm-grover-plane-variant-sizing-v1"
EVIDENCE = ROOT / "docs/evidence/iqm-garnet-grover-plane"
INPUTS = EVIDENCE / "billing_v4_inputs.json"
CASES = ROOT / "results/iqm/cases"
ROUND = 6


def durations_of(directory: Path) -> tuple[list[float], list[int], dict[str, Any]]:
    cases = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
    job = next(j for j in cases["jobs"] if j["job"] == "grover")
    circuits = [json.loads((directory / e["file"]).read_text(encoding="utf-8")) for e in job["circuits"]]
    seconds = [case.schedule_nanoseconds(c) * 1e-9 for c in circuits]
    mid = [sum(op["name"] == "measure" for op in c["instructions"]) - 1 for c in circuits]
    return seconds, mid, cases


def record() -> dict[str, Any]:
    inputs = sizing.load_inputs()
    cases_out: dict[str, Any] = {}
    for name in (case.CASE, case.CASE_101):
        directory = CASES / name
        seconds, mid, cases = durations_of(directory)
        job = cases["jobs"][0]
        prediction = json.loads((directory / "prediction.json").read_text(encoding="utf-8"))
        priced = sizing.price(inputs, seconds, mid, int(job["shots"]))
        chosen = sizing.adopted(inputs, priced)
        power = prediction["decisions"]["power"]["worst_resolved_truth"]
        cases_out[name] = {
            "cases_sha256": hashlib.sha256((directory / "cases.json").read_bytes()).hexdigest(),
            "circuits": len(seconds),
            "executions": len(seconds) * int(job["shots"]),
            "shots": int(job["shots"]),
            "mid_circuit_measures": sum(mid),
            "summed_duration_seconds": sum(seconds),
            "longest_circuit_seconds": max(seconds),
            "models": priced,
            "adopted": chosen,
            "case_max_credits": float(job["max_credits"]["garnet"]),
            "case_expected_seconds": float(job["expected_seconds"]),
            "primary_test": {
                "worst_resolved_truth": power["truth"],
                "coherent_rate": power["coherent"],
                "coherent_rate_se": power.get("coherent_se"),
                "design_effect_eps": prediction["decisions"]["power"]["design_effect_eps"],
            },
        }
    return {
        "schema": SCHEMA,
        "billing_v4_inputs_sha256": hashlib.sha256(INPUTS.read_bytes()).hexdigest(),
        "cases": cases_out,
    }


def rounded(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    if isinstance(x, list):
        return [rounded(v) for v in x]
    if isinstance(x, float):
        return round(x, ROUND)
    return x


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path)
    group.add_argument("--check", type=Path)
    args = parser.parse_args()
    text = json.dumps(rounded(record()), indent=1, sort_keys=True) + "\n"
    if args.check is not None:
        if args.check.read_text(encoding="utf-8") != text:
            raise SystemExit(f"{args.check}: differs from the recomputed record")
        print(f"{args.check}: matches the recomputed record")
        return 0
    args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
