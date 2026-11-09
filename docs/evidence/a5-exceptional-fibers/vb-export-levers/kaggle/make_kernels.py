"""Write the Kaggle CPU kernels of the E8-bar -> VB export-lever campaign.

Each kernel installs passagemath Singular 4.4.1 (the build the Windows workstation runs) and runs raw Singular jobs on
the session's four cores: slimgb of J + m^N at N = 21 and 22 for one prime, whose reduced basis must be byte-identical
to the engine-v13 export on the workstation (`s.txt` under ~/a5/exports/e8-vb-p<p>-n<N>-v13), and, in the 32009
kernel, six rotations of the variable order at N = 15 against the identity order. Every job writes its reduced basis,
its kbase and RESULT lines to /kaggle/working/<job>/ and the runner writes summary.json. The per-job deadline keeps the
session inside Kaggle's 12-hour limit. Run from the repository root:
"$PYTHON" docs/evidence/a5-exceptional-fibers/vb-export-levers/kaggle/make_kernels.py
"""

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

RUNNER = r"""
import hashlib, json, os, subprocess, sys, sysconfig, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
T0 = time.time(); OUT = Path("/kaggle/working")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "passagemath-singular==10.8.13"], check=True)
paths = sysconfig.get_paths()
binary = next(p for p in (Path(paths[k]) / "sage_wheels/bin/Singular" for k in ("purelib", "platlib")) if p.exists())
def run(job):
    d = OUT / job["name"]; d.mkdir(parents=True, exist_ok=True); (d / "input.sing").write_text(job["script"])
    s = time.time()
    p = subprocess.run(["timeout", "-k", "30", str(JOB_SECONDS), str(binary), "-q", "--no-rc", "input.sing"],
                       cwd=d, stdin=subprocess.DEVNULL, capture_output=True, text=True)
    (d / "out.log").write_text(p.stdout + p.stderr)
    digest = {f: hashlib.sha256((d / f).read_bytes()).hexdigest() for f in ("s.txt", "kbase.txt") if (d / f).exists()}
    return job["name"], {"rc": p.returncode, "seconds": round(time.time() - s, 1), "sha256": digest,
                         "results": [l for l in p.stdout.splitlines() if l.startswith("RESULT")]}
version = subprocess.run([str(binary), "--dump-versiontuple"], stdin=subprocess.DEVNULL, capture_output=True, text=True)
rec = {"cpu_count": os.cpu_count(), "singular": version.stdout.strip()}
with ThreadPoolExecutor(max_workers=4) as ex:
    rec["jobs"] = dict(ex.map(run, JOBS))
rec["total_seconds"] = round(time.time() - T0, 1)
(OUT / "summary.json").write_text(json.dumps(rec, indent=1)); print(json.dumps(rec, indent=1))
"""


def header(prime: int, root: int) -> tuple[str, str, list[str]]:
    lines = (INPUTS / f"p{prime}-r{root}" / "e8-vb.sing").read_text().splitlines()
    ring = lines[0]
    names = ring[ring.index("(") + 1 : ring.index(")")].split(",")
    return ring, next(line for line in lines if line.startswith("ideal J=")), names


def job(name: str, ring: str, j: str, n: int) -> dict:
    return {"name": name, "script": SCRIPT.format(ring=ring, J=j, N=n, name=name)}


def kernel(slug: str, jobs: list[dict]) -> None:
    d = HERE / slug
    d.mkdir(exist_ok=True)
    (d / f"{slug}.py").write_text(f'"""{slug}"""\nJOBS = {json.dumps(jobs)}\nJOB_SECONDS = {JOB_SECONDS}\n' + RUNNER)
    meta = {
        "id": f"{OWNER}/{slug}",
        "title": slug,
        "code_file": f"{slug}.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": False,
        "enable_internet": True,
        "dataset_sources": [],
        "kernel_sources": [],
        "competition_sources": [],
    }
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=1) + "\n")


def main() -> None:
    for prime, root in ((32009, 10754), (32029, 9115)):
        ring, j, names = header(prime, root)
        jobs = [job(f"slimgb-n{n}-p{prime}", ring, j, n) for n in (21, 22)]
        if prime == 32009:
            jobs.append(job("order-identity-n15", ring, j, 15))
            for k in range(1, 7):
                rotated = names[k:] + names[:k]
                jobs.append(job(f"order-rot{k}-n15", ring.replace(",".join(names), ",".join(rotated)), j, 15))
        kernel(f"a5-vb-d7-slimgb-p{prime}", jobs)


if __name__ == "__main__":
    main()
