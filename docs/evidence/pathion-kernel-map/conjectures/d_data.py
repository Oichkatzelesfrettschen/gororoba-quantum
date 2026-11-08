"""Inputs of the parallel-coset drain checks: the analysis record, the two retained run directories, shared constants."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
HERE = Path(__file__).resolve().parent
ANALYSIS = ROOT / "results/live/pathion_parallel_coset_analysis.json"
RUNS = {"ibm_fez": "2026-11-07T042521.359670Z", "ibm_kingston": "2026-11-07T042346.084449Z"}
ASCELLA = ROOT / "results/quandela/runs/2026-11-06T215343Z-qpu_ascella-ascella_pathion_four_term_blocks-job-00"
# Response of the k0 selector contrast to a coherent sx over-rotation per radian (the written case's signature table).
SX_RESPONSE = 0.57


def analysis() -> dict:
    return json.loads(ANALYSIS.read_bytes())


def run_dir(backend: str) -> Path:
    return ROOT / "results/live" / RUNS[backend]
