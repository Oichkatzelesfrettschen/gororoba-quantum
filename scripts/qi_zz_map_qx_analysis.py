"""Analyze retained QX preflight acquisitions of the Tuna-17 ZZ map against their reviewed plan.

The retained plan binds scripts/qi_zz_map_qx.py byte for byte through
qx_builder_sha256, so that module stays the pinned producer of the proposal
and this entry point succeeds its --analyze mode. It binds the design (the
plan schema, sanity policy, QX backend, shot count and marginal criteria of
the pinned module) and calls gororoba_quantum/qi_zz_preflight.py, which
reads every batch through gororoba_quantum/qi_records.py. The report binds
the digests of the analyzer, the reader and the criteria.

Usage: "$PYTHON" scripts/qi_zz_map_qx_analysis.py --runs RUNS_ROOT --plan PLAN --out NEWFILE
       "$PYTHON" scripts/qi_zz_map_qx_analysis.py --self-test
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_zz_map import json_text  # noqa: E402
from qi_zz_map_qx import PLAN_SCHEMA, POLICY, SHOTS, check_counts  # noqa: E402

import qi_zz_preflight  # noqa: E402

DESIGN = qi_zz_preflight.Design(
    plan_schema=PLAN_SCHEMA,
    policy=POLICY,
    backend="QXsinglenodesimulator",
    shots=SHOTS,
    check_counts=check_counts,
    sources={
        "analyzer": ROOT / "gororoba_quantum/qi_zz_preflight.py",
        "reader": ROOT / "gororoba_quantum/qi_records.py",
        "criteria": ROOT / "scripts/qi_zz_map_qx.py",
    },
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--runs", type=Path, metavar="RUNS_ROOT")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        qi_zz_preflight.self_test(DESIGN)
        return 0
    if args.plan is None or args.out is None:
        parser.error("--runs requires --plan PLAN and --out NEWFILE")
    text = json_text(qi_zz_preflight.analyze(args.plan, args.runs, DESIGN))
    with args.out.open("x", encoding="utf-8") as handle:
        handle.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
