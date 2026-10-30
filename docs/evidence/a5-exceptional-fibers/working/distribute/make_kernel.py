"""Write one Kaggle script kernel that runs A_5 fiber jobs concurrently on the session's CPU host.

Each job is a method-A degree chain (fiber_cone_driver.py, degrees in order, each degree reading the previous
cumulative relations) or a raw Singular script with its input files. The repository driver runs unchanged; a
`systemd-run` shim on PATH drops the cgroup flags, so the session's own RAM is the memory boundary.
"""

import base64
import io
import json
import sys
import tarfile
from pathlib import Path

WT = Path.home() / "worktrees/IBMQuantum/a5-kernel-attachments"
A5 = Path.home() / "Projects/IBMQuantum/docs/local/a5-failed-runs"
OWNER = "probablyeric"

SHIM = """#!/bin/sh
# Drop systemd-run options up to the wrapped command (it starts at `timeout`).
while [ "$#" -gt 0 ] && [ "$1" != timeout ]; do shift; done
export MALLOC_ARENA_MAX=2
exec "$@"
"""

RUNNER = r'''
import base64, io, json, os, subprocess, sys, sysconfig, tarfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
T0 = time.time(); OUT = Path("/kaggle/working"); W = Path("/kaggle/tmp/w"); W.mkdir(parents=True, exist_ok=True)
tarfile.open(fileobj=io.BytesIO(base64.b64decode(PAYLOAD))).extractall(W)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "passagemath-singular==10.8.13", "python-flint==0.9.0"], check=True)
cands = [Path(sysconfig.get_paths()[k]) / "sage_wheels/bin/Singular" for k in ("purelib", "platlib")]
binary = next(c for c in cands if c.exists())
BIN = W / "bin"; BIN.mkdir(exist_ok=True)
(BIN / "Singular").symlink_to(binary)
(BIN / "systemd-run").write_text(SHIM); (BIN / "systemd-run").chmod(0o755)
env = dict(os.environ, PATH=f"{BIN}:{os.environ['PATH']}", GLIBC_TUNABLES="glibc.rtld.optional_static_tls=4096")
DRIVER = W / "docs/evidence/a5-kernel-attachments/fiber_cone_driver.py"
def mem():
    return {l.split(":")[0]: l.split()[1] for l in open("/proc/meminfo") if l.split(":")[0] in ("MemTotal", "MemAvailable")}
def chain(job):
    prev = None; steps = []
    for d in job["degrees"]:
        o = OUT / job["name"] / f"d{d}"; s = time.time()
        cmd = [sys.executable, str(DRIVER), "--header", str(W / job["header"]), "--degree", str(d), "--out", str(o),
               "--prime", str(job["prime"]), "--memory-gib", "28", "--timeout", str(job["timeout"])]
        if prev: cmd += ["--previous-relations", str(prev)]
        p = subprocess.run(cmd, env=env, capture_output=True, text=True)
        o.mkdir(parents=True, exist_ok=True); (o / "driver.log").write_text(p.stdout + p.stderr)
        steps.append({"degree": d, "rc": p.returncode, "seconds": round(time.time() - s, 1), "tail": (p.stdout + p.stderr)[-600:]})
        prev = o / f"relations-upto-d{d}.rel"
        if p.returncode or not prev.exists(): break
    return job["name"], steps
def raw(job):
    d = W / "raw" / job["name"]; s = time.time(); (OUT / job["name"]).mkdir(parents=True, exist_ok=True)
    p = subprocess.run(["timeout", "-k", "10", str(job["timeout"]), str(binary), "-q", "--no-rc", job["script"]],
                       cwd=d, env=env, capture_output=True, text=True)
    (OUT / job["name"]).mkdir(parents=True, exist_ok=True); (OUT / job["name"] / "out.log").write_text(p.stdout + p.stderr)
    return job["name"], {"rc": p.returncode, "seconds": round(time.time() - s, 1),
                         "results": [l for l in p.stdout.splitlines() if l.startswith("RESULT")]}
rec = {"cpu_count": os.cpu_count(), "meminfo_kib": mem(), "python": sys.version.split()[0],
       "singular": subprocess.run([str(binary), "--dump-versiontuple"], capture_output=True, text=True).stdout.strip()}
with ThreadPoolExecutor(max_workers=min(WORKERS, len(JOBS))) as ex:
    rec["jobs"] = dict(ex.map(lambda j: chain(j) if j["kind"] == "chain" else raw(j), JOBS))
rec["meminfo_end_kib"] = mem(); rec["total_seconds"] = round(time.time() - T0, 1)
(OUT / "summary.json").write_text(json.dumps(rec, indent=1)); print(json.dumps(rec, indent=1))
'''


def payload(jobs: list[dict]) -> str:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(WT / "docs/evidence/a5-kernel-attachments/fiber_cone_driver.py",
                "docs/evidence/a5-kernel-attachments/fiber_cone_driver.py")
        tar.add(WT / "gororoba_quantum/parallel.py", "gororoba_quantum/parallel.py")
        for j in jobs:
            if j["kind"] == "chain":
                tar.add(A5 / "build/inputs" / j["header"], j["header"])
            else:
                for arc, src in j["files"].items():
                    tar.add(src, f"raw/{j['name']}/{arc}")
    return base64.b64encode(buf.getvalue()).decode()


CHART = """LIB "primdec.lib";
ring Y=32009,(y(1..{n})),dp; execute("ideal K="+read("k2.rel")+";");
ideal Kc=std(subst(K,y({i}),1)); "RESULT chart {i} dim",dim(Kc);
if(dim(Kc)>=0){{
ideal rc=std(radical(Kc)); "RESULT chart {i} radical",size(reduce(rc,Kc))==0;
list P=minAssChar(Kc); "RESULT chart {i} primes",size(P); int c;
for(c=1;c<=size(P);c++){{ideal q=std(P[c]); "RESULT chart {i} prime",c,"dim",dim(q),"linear_gens",size(jet(P[c],1));
write(":w /kaggle/working/{name}/prime"+string(c)+".txt",P[c]); kill q;}}
}}
quit;
"""


def chart_jobs(pair: str, n: int, rel_src: Path, timeout: int) -> list[dict]:
    jobs = []
    for i in range(1, n + 1):
        name = f"{pair}_c{i:02d}"
        script = A5 / "distribute/kernels" / f"{name}.sing"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(CHART.format(n=n, i=i, name=name))
        jobs.append({"kind": "raw", "name": name, "script": "input.sing", "timeout": timeout,
                     "files": {"input.sing": script, "k2.rel": rel_src}})
    return jobs


def write(slug: str, jobs: list[dict], gpu: bool, workers: int = 4) -> Path:
    d = A5 / "distribute/kernels" / slug
    d.mkdir(parents=True, exist_ok=True)
    clean = [{k: v for k, v in j.items() if k != "files"} for j in jobs]
    src = (f'"""A_5 fiber batch {slug}: {", ".join(j["name"] for j in jobs)}."""\n'
           f"PAYLOAD = {payload(jobs)!r}\nSHIM = {SHIM!r}\nWORKERS = {workers}\nJOBS = {json.dumps(clean)}\n" + RUNNER)
    (d / f"{slug}.py").write_text(src)
    meta = {"id": f"{OWNER}/{slug}", "title": slug, "code_file": f"{slug}.py", "language": "python",
            "kernel_type": "script", "is_private": True, "enable_gpu": gpu, "enable_internet": True,
            "dataset_sources": [], "kernel_sources": [], "competition_sources": []}
    if gpu:
        meta["machine_shape"] = "NvidiaTeslaT4"
    (d / "kernel-metadata.json").write_text(json.dumps(meta, indent=1))
    return d


def k2_job(name: str, sing: str, rel_src: Path, timeout: int) -> dict:
    text = (A5 / "runs/k2struct" / sing).read_text()
    start = text.index('read("') + 6
    end = text.index('")', start)
    script = A5 / "distribute/kernels" / f"{name}.sing"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(text[:start] + "k2.rel" + text[end:])
    return {"kind": "raw", "name": name, "script": "input.sing", "timeout": timeout,
            "files": {"input.sing": script, "k2.rel": rel_src}}


def chain_job(name: str, header: str, prime: int, degrees: list[int], timeout: int) -> dict:
    return {"kind": "chain", "name": name, "header": header, "prime": prime, "degrees": degrees, "timeout": timeout}


P2 = "p32029-r9115"
P1 = "p32009-r10754"
H = 3600
PLAN = {
    "a5-chart-iso": (False, chart_jobs("iso", 17, A5 / "runs/s3/iso_k2.rel", 2700)),
    "a5-chart-w8nm": (False, chart_jobs("w8nm", 24, A5 / "runs/w8_a2/w8_k2.rel", 2700)),
    "a5-p2-small": (False, [chain_job("vb_p2", f"{P2}/e8-vb.sing", 32029, [2, 3], 3 * H),
                            chain_job("xm_p2", f"{P2}/xm-nm.sing", 32029, [2, 3], 5 * H),
                            chain_job("xp_p2", f"{P2}/xp-np.sing", 32029, [2, 3], 5 * H)]),
    "a5-p2-iso": (False, [chain_job("iso_p2", f"{P2}/iso-np.sing", 32029, [2, 3], 10 * H)]),
    "a5-p2-w8": (True, [chain_job("w8_p2", f"{P2}/w8-nm.sing", 32029, [2, 3], 10 * H)]),
    "a5-e8-d2": (True, [chain_job("e8np_p2", f"{P2}/e8-np.sing", 32029, [2], 8 * H),
                        chain_job("e8nm_p2", f"{P2}/e8-nm.sing", 32029, [2], 8 * H),
                        chain_job("e8nm_p1", f"{P1}/e8-nm.sing", 32009, [2], 8 * H)]),
}

if __name__ == "__main__":
    for slug in sys.argv[1:] or list(PLAN):
        gpu, jobs = PLAN[slug]
        print(write(slug, jobs, gpu))
