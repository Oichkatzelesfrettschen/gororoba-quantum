"""Counter-arithmetic sweeps over scripts/, gororoba_quantum/ and docs/evidence/: findings and their classes.

counter-arithmetic.semgrep.yml is an intraprocedural taint rule from a provider counter field (nb_shots_used,
shots_used, physical_perf, logical_perf, global_perf, duration, number_of_shots, shots_done, shots_requested,
samples) to a division, product, difference or sum; counter-reads.ast-grep.yml lists every subscript or .get read
of those fields except samples. Every finding is named by file, line and enclosing function, and takes the class of
its (file, function) or else of its file from CLASSES. An unclassified finding exits 1, so a rule or code change
that reaches new arithmetic forces a classification. Without --write the collector compares findings.json; semgrep
and ast-grep come from SEMGREP and AST_GREP or the PATH, and their versions enter the output.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = HERE / "findings.json"
SEMGREP_RULES = HERE / "counter-arithmetic.semgrep.yml"
AST_GREP_RULES = HERE / "counter-reads.ast-grep.yml"
# A taint fixpoint that a per-rule timeout cuts short drops findings by machine load; no timeout and one
# worker make the finding set a function of the sources alone.
SEMGREP_FLAGS = ("--metrics=off", "--disable-version-check", "--timeout", "0", "--jobs", "1")
PATTERNS = ("scripts/*.py", "gororoba_quantum/*.py", "docs/evidence/*.py")

AUDIT = "audit replay: this bundle's own reconstruction"
INSTRUCTION = "outside counter scope: a Target or circuit instruction duration, not a provider result field"
GATE_SHOTS = "supported: gate-model shots compared or summed within one population"
DETECTIONS = "supported: Quandela nb_shots_used summed over disjoint iterations as detection events"
WALL = "supported as wall time: Quandela job duration, which includes compilation, read as elapsed time"
ECHO = "supported: counter echoed into a record without arithmetic"
LOCAL = "supported: a local Perceval simulator's documented filter share"
SINK = "inventoried sink: classified in the README sink table"
UNGATED = "model-dependent, labeled: wall time as an upper detector exposure (README sink table)"
DELIVERY = "supported as labeled: returned samples over the requested sample budget, a delivery state (README)"
ACCEPTANCE = "supported: accepted samples over detection events, an acceptance fraction (README sink table)"
FALSE = "false positive: taint reaches statevector probabilities through a mapping that also holds shots_done"

CLASSES: dict[str, str] = {
    "docs/evidence/provider-counter-audit/exposure_sensitivity.py": AUDIT,
    "docs/evidence/provider-counter-audit/gate_model_counter_census.py": AUDIT,
    "docs/evidence/provider-counter-audit/quandela_counter_table.py": AUDIT,
    "gororoba_quantum/provider_counters.py": AUDIT,
    "gororoba_quantum/calibration_snapshot.py": INSTRUCTION,
    "gororoba_quantum/heron_multiprogramming.py": INSTRUCTION,
    "gororoba_quantum/jax_bridge.py": INSTRUCTION,
    "gororoba_quantum/live_run.py": INSTRUCTION,
    "scripts/algebra_device_conjectures.py": INSTRUCTION,
    "scripts/ghost_event_scale.py": INSTRUCTION,
    "scripts/heron_feedforward_latency.py": INSTRUCTION,
    "scripts/heron_target_snapshot.py": INSTRUCTION,
    "scripts/iqm_measurement_sequence.py": INSTRUCTION,
    "scripts/iqm_measurement_sequence_aer_check.py": INSTRUCTION,
    "scripts/primorial_probe_case.py": INSTRUCTION,
    "scripts/qi_ibm_noise_replay.py": INSTRUCTION,
    "scripts/box_kite_analysis.py": GATE_SHOTS,
    "scripts/box_kite_follow_design.py": GATE_SHOTS,
    "scripts/check_qi_platform_retention.py": GATE_SHOTS,
    "scripts/local_simulation_replay.py": GATE_SHOTS,
    "scripts/n21_qx_conformance.py": GATE_SHOTS,
    "scripts/qi_coupler_zz_map.py": GATE_SHOTS,
    "scripts/qi_platform.py": GATE_SHOTS,
    "scripts/qi_readout_ringdown_cases.py": GATE_SHOTS,
    "scripts/qi_series_watch.py": GATE_SHOTS,
    "scripts/qi_zz_map_analysis.py": GATE_SHOTS,
    "scripts/qi_zz_map_qx.py": GATE_SHOTS,
    "scripts/research_state.py": GATE_SHOTS,
    "scripts/evidence_closure.py:quantum_inspire": GATE_SHOTS,
    "scripts/evidence_closure.py:quandela": DETECTIONS,
    "scripts/qd_platform.py": DETECTIONS,
    "scripts/ascella_new_mesh_score.py": WALL,
    "scripts/bdsc_stationarity.py": WALL,
    "scripts/bdsc_forensics.py": ECHO,
    "scripts/qd_schedule.py": WALL,
    "scripts/qd_belenos_mesh.py:bridge_record": WALL,
    "scripts/qd_belenos_mesh.py:dwell_record": WALL,
    "scripts/bdsc_diagnostic.py": SINK,
    "scripts/qd_belenos_cone.py": SINK,
    "scripts/qd_belenos_mesh.py:observed": SINK,
    "scripts/qd_belenos_mesh.py:analyze_run": SINK,
    "scripts/qd_box_kite_analysis.py": SINK,
    "scripts/qd_teleportation_rehearsal.py": SINK,
    "scripts/bdsc_stray_mode_veto.py:job_dark": UNGATED,
    "scripts/bdsc_stray_mode_veto.py:stray_report": UNGATED,
    "scripts/qd_rehearsal_secondary.py": DELIVERY,
    "scripts/experiment_analysis.py": ACCEPTANCE,
    "scripts/photonic_repeat_readout.py": ECHO,
    "scripts/bdsc_packages.py": LOCAL,
    "scripts/qd_mcp_server.py": LOCAL,
    "scripts/local_photonic_compiler_crosscheck.py": FALSE,
}


def tool(variable: str, name: str) -> str:
    found = os.environ.get(variable) or shutil.which(name)
    if not found:
        raise SystemExit(f"{name} is not on the PATH; set {variable}")
    return found


def enclosing(path: str, line: int, cache: dict[str, list[tuple[int, int, str]]]) -> str | None:
    if path not in cache:
        tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
        cache[path] = [
            (node.lineno, node.end_lineno or node.lineno, node.name)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        ]
    spans = [span for span in cache[path] if span[0] <= line <= span[1]]
    return min(spans, key=lambda span: span[1] - span[0])[2] if spans else None


def classify(path: str, function: str | None) -> str | None:
    return CLASSES.get(f"{path}:{function}") or CLASSES.get(path)


def sweep() -> dict[str, Any]:
    semgrep, ast_grep = tool("SEMGREP", "semgrep"), tool("AST_GREP", "ast-grep")
    files = subprocess.run(
        ["git", "ls-files", *PATTERNS], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.split()
    scan = subprocess.run(
        [semgrep, "scan", *SEMGREP_FLAGS, "--json", "--config", str(SEMGREP_RULES), *files],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    report = json.loads(scan.stdout)
    raw = [("semgrep", r["path"], r["start"]["line"]) for r in report["results"]]
    reads = subprocess.run(
        [ast_grep, "scan", "--rule", str(AST_GREP_RULES), "--json=stream", *files],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    raw += [
        ("ast-grep", r["file"], r["range"]["start"]["line"] + 1) for r in map(json.loads, reads.stdout.splitlines())
    ]
    cache: dict[str, list[tuple[int, int, str]]] = {}
    findings = []
    for name, path, line in sorted(set(raw)):
        function = enclosing(path, line, cache)
        text = (ROOT / path).read_text(encoding="utf-8").splitlines()[line - 1].strip()
        findings.append(
            {
                "tool": name,
                "file": path,
                "line": line,
                "function": function,
                "source": text,
                "class": classify(path, function),
            }
        )
    versions = {
        "semgrep": subprocess.run([semgrep, "--version"], check=True, capture_output=True, text=True).stdout.strip(),
        "ast-grep": subprocess.run([ast_grep, "--version"], check=True, capture_output=True, text=True).stdout.strip(),
    }
    return {
        "schema": "provider-counter-sweeps-v1",
        "versions": versions,
        "rules_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (SEMGREP_RULES, AST_GREP_RULES)},
        "parse_errors": sorted(e.get("path", "") for e in report.get("errors", [])),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    record = sweep()
    unclassified = [f for f in record["findings"] if f["class"] is None]
    for finding in unclassified:
        print(f"unclassified: {finding['file']}:{finding['line']} in {finding['function']}", file=sys.stderr)
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if args.write:
        OUT.write_text(text, encoding="utf-8")
    elif OUT.read_text(encoding="utf-8") != text:
        print(f"{OUT.relative_to(ROOT)} differs from the recomputed sweep", file=sys.stderr)
        return 1
    return 1 if unclassified else 0


if __name__ == "__main__":
    raise SystemExit(main())
