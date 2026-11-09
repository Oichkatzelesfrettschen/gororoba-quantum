"""a5-char0-xm-quadrics"""
BRANCH = 'integration/gororoba-quantum-ultrareview'
REPO = 'https://github.com/Oichkatzelesfrettschen/gororoba-quantum'
SHIM = '#!/bin/sh\nwhile [ "$#" -gt 0 ] && [ "$1" != Singular ]; do shift; done\nexec "$@"\n'
ARGS = ["docs/evidence/a5-char0-transfer/quadric_lift.py", "--slug", "xm-nm", "--timeout", "41000"]
RECORD_GLOB = 'quadrics-xm-nm.json'

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
