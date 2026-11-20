"""Diagnose the X- -> N- Cohen-Macaulay step over Q(i): stage timings."""
import sys, time, subprocess, json
from pathlib import Path
sys.path.insert(0, "docs/evidence/a5-kernel-attachments")
import weight_slice_fiber_relations as ws
import weight_slice_quadric_rings as wq
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
t = time.monotonic()
run = ws.run_singular(ws.fiber_script(ws.orbit_task("N-"), "xm", 0, 0))
summary = ws.summarize_fiber_run(run)
polys = wq.polynomials(sorted(run["relations"]))
print("regen_seconds", round(time.monotonic() - t, 1), summary["relations_sha256"], summary["generator_count"], len(polys), flush=True)
(out / "xm-N-.polys.txt").write_text(",\n".join(polys) + "\n")
(out / "xm-N-.n").write_text(str(summary["generator_count"]))
