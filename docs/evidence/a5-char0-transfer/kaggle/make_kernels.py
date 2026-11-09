"""Write the Kaggle CPU kernels that run the characteristic-0 checks of X- -> N- off the build host.

Each kernel clones the public repository at the integration branch, installs passagemath Singular 4.4.1, sympy and
python-flint, puts a `systemd-run` shim on PATH (the drivers wrap Singular in a user scope that a Kaggle container
lacks; the shim drops the scope options and runs the wrapped command, so the session's own RAM bounds it) and runs
one driver unchanged. It copies the driver's JSON record and logs to /kaggle/working. Run from the repository root:
"$PYTHON" docs/evidence/a5-char0-transfer/kaggle/make_kernels.py
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OWNER = "probablyeric"
BRANCH = "integration/gororoba-quantum-ultrareview"
REPO = "https://github.com/Oichkatzelesfrettschen/gororoba-quantum"

SHIM = """#!/bin/sh
while [ "$#" -gt 0 ] && [ "$1" != Singular ]; do shift; done
exec "$@"
"""

RUNNER = r"""
import json, os, shutil, subprocess, sys, sysconfig, time
from pathlib import Path
T0 = time.time(); OUT = Path("/kaggle/working"); W = Path("/kaggle/tmp"); W.mkdir(parents=True, exist_ok=True)
subprocess.run(["git", "clone", "-q", "--depth", "1", "-b", BRANCH, REPO, str(W / "repo")], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "passagemath-singular==10.8.13", "python-flint==0.9.0",
                "sympy"], check=True)
if not Path("/usr/bin/time").exists():
    subprocess.run(["apt-get", "install", "-y", "-q", "time"], check=False)
paths = sysconfig.get_paths()
binary = next(p for p in (Path(paths[k]) / "sage_wheels/bin/Singular" for k in ("purelib", "platlib")) if p.exists())
BIN = W / "bin"; BIN.mkdir(exist_ok=True)
(BIN / "Singular").symlink_to(binary)
(BIN / "systemd-run").write_text(SHIM); (BIN / "systemd-run").chmod(0o755)
env = dict(os.environ, PATH=f"{BIN}:{os.environ['PATH']}", GLIBC_TUNABLES="glibc.rtld.optional_static_tls=4096")
repo = W / "repo"
head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
s = time.time()
p = subprocess.run([sys.executable, *ARGS], cwd=repo, env=env, stdin=subprocess.DEVNULL, capture_output=True,
                   text=True)
(OUT / "driver.log").write_text(p.stdout + p.stderr)
for f in (repo / "docs/evidence/a5-char0-transfer").glob(RECORD_GLOB):
    shutil.copy(f, OUT / f.name)
rec = {"repo_head": head, "args": ARGS, "rc": p.returncode, "seconds": round(time.time() - s, 1),
       "total_seconds": round(time.time() - T0, 1), "cpu_count": os.cpu_count()}
(OUT / "summary.json").write_text(json.dumps(rec, indent=1)); print(json.dumps(rec, indent=1))
"""

JOBS = {
    "a5-char0-xm-quadrics": (
        ["docs/evidence/a5-char0-transfer/quadric_lift.py", "--slug", "xm-nm", "--timeout", "41000"],
        "quadrics-xm-nm.json",
    ),
    "a5-char0-xm-truncation-n22": (
        [
            "docs/evidence/a5-char0-transfer/truncation_check.py",
            "--slug",
            "xm-nm",
            "--order",
            "22",
            "--timeout",
            "20000",
        ],
        "truncation-xm-nm-n22.json",
    ),
}


def main() -> None:
    for slug, (args, record) in JOBS.items():
        d = HERE / slug
        d.mkdir(exist_ok=True)
        head = f'"""{slug}"""\nBRANCH = {BRANCH!r}\nREPO = {REPO!r}\nSHIM = {SHIM!r}\nARGS = {json.dumps(args)}\n'
        (d / f"{slug}.py").write_text(head + f"RECORD_GLOB = {record!r}\n" + RUNNER)
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


if __name__ == "__main__":
    main()
