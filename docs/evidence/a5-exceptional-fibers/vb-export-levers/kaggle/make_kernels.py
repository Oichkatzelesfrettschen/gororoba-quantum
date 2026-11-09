"""Write the Kaggle CPU kernels of the E8-bar -> VB export-lever campaign.

Each kernel installs passagemath Singular 4.4.1 (the build the Windows workstation runs) and runs raw Singular jobs on
the session's four cores: slimgb of J + m^N at N = 21 and 22 for one prime, whose reduced basis must be byte-identical
to the engine-v13 export on the workstation (`s.txt` under ~/a5/exports/e8-vb-p<p>-n<N>-v13), and, in the 32009
kernel, six rotations of the variable order at N = 15 against the identity order. Every job writes its reduced basis,
its kbase and RESULT lines to /kaggle/working/<job>/ and the runner writes summary.json. The per-job deadline keeps the
session inside Kaggle's 12-hour limit. The kernel body is runner.py,
which exits 1 when a job fails. Run from the repository root:
"$PYTHON" docs/evidence/a5-exceptional-fibers/vb-export-levers/kaggle/make_kernels.py
"""

import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = HERE.parents[1] / "working" / "build" / "inputs"
OWNER = "probablyeric"
JOB_SECONDS = 41_000

SCRIPT = """{ring}
{J}
option(redSB); system("--ticks-per-sec",1000); int t0=rtimer;
ideal s=slimgb(J+maxideal({N}));
"RESULT ms",rtimer-t0,"sb_size",ncols(s);
ideal B=kbase(s); "RESULT kbase_size",ncols(B);
short=0; write(":w /kaggle/working/{name}/s.txt",s); write(":w /kaggle/working/{name}/kbase.txt",B);
quit;
"""


def header(prime: int, root: int) -> tuple[str, str, list[str]]:
    lines = (INPUTS / f"p{prime}-r{root}" / "e8-vb.sing").read_text().splitlines()
    ring = lines[0]
    names = ring[ring.index("(") + 1 : ring.index(")")].split(",")
    return ring, next(line for line in lines if line.startswith("ideal J=")), names


def job(name: str, ring: str, j: str, n: int) -> dict:
    return {"name": name, "script": SCRIPT.format(ring=ring, J=j, N=n, name=name)}


def kernel(slug: str, jobs: list[dict], out: Path = HERE, gpu: bool = False) -> None:
    """Write OUT/SLUG/SLUG.py (runner.py with its job list as base64 in CONFIG_B64) and its kernel-metadata.json.

    A GPU kernel runs the same CPU-only Singular jobs on the four cores of a GPU session, which draws on the weekly
    GPU quota instead of the CPU queue."""
    d = out / slug
    d.mkdir(parents=True, exist_ok=True)
    blob = base64.b64encode(json.dumps({"jobs": jobs, "job_seconds": JOB_SECONDS}).encode()).decode()
    chunks = "".join(f'    "{blob[i : i + 100]}"\n' for i in range(0, len(blob), 100))
    runner = (HERE / "runner.py").read_text()
    if runner.count('CONFIG_B64 = ""\n') != 1:
        raise SystemExit("runner.py must hold exactly one CONFIG_B64 placeholder")
    (d / f"{slug}.py").write_text(runner.replace('CONFIG_B64 = ""\n', f"CONFIG_B64 = (\n{chunks})\n"))
    meta = {
        "id": f"{OWNER}/{slug}",
        "title": slug,
        "code_file": f"{slug}.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": gpu,
        "enable_internet": True,
        "dataset_sources": [],
        "kernel_sources": [],
        "competition_sources": [],
    }
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=1) + "\n")


def main(out: Path = HERE) -> None:
    for prime, root in ((32009, 10754), (32029, 9115)):
        ring, j, names = header(prime, root)
        jobs = [job(f"slimgb-n{n}-p{prime}", ring, j, n) for n in (21, 22)]
        if prime == 32009:
            order = [job("order-identity-n15", ring, j, 15)]
            for k in range(1, 7):
                rotated = names[k:] + names[:k]
                order.append(job(f"order-rot{k}-n15", ring.replace(",".join(names), ",".join(rotated)), j, 15))
            jobs += order
            # A GPU-session kernel runs N = 22 and the order jobs again on its own cores, so the export and the order
            # comparison finish on whichever session starts first, and two sessions that both finish must agree byte
            # for byte.
            kernel(f"a5-vb-d7-slimgb-gpu-p{prime}", [jobs[1], *order], out, gpu=True)
        kernel(f"a5-vb-d7-slimgb-p{prime}", jobs, out)


if __name__ == "__main__":
    main()
