"""Eliminate the Rees variable `a` from one A_5 graph ideal over F_32009 with msolve (F4) on a Kaggle CPU session.

The input is the graph ideal J + (y_i - a g_i); msolve -e 1 computes the reduced basis of the ordering that
eliminates `a`, whose `a`-free elements generate the Rees ideal. The session logs MemAvailable and the solver's
resident set every 30 seconds so an out-of-memory end is located in degree and bytes.
"""

import gzip
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import sysconfig
import threading
import time
from pathlib import Path

LABEL = "E8bar->VB Rees elimination"
INPUT = """a,t1,t2,t3,t4,t5,t6,t7,t8,y1,y2,y3,y4,y5,y6,y7,y8,y9,y10
32009
t3^2-t4^2-t5^2+t6^2,
t1^2-t2^2+t7^2-t8^2+4*t2+2*t8,
t4*t5*t8-t3*t6*t8-t3*t5-t4*t5+t3*t6+t4*t6,
t4^2*t8-t6^2*t8-t3*t4-t4^2-t5*t6+t6^2,
t3*t4*t8-t5*t6*t8-t3*t4-t4^2-t5^2+t5*t6,
t2*t4*t8+t1*t6*t8-t2*t4+t1*t5-t1*t6-2*t4*t8,
t1*t4*t8+t2*t6*t8-t1*t3-t1*t4-t2*t6-2*t6*t8,
t2*t3*t8+t1*t5*t8-t2*t3-t1*t5+t1*t6-2*t3*t8,
t1*t3*t8+t2*t5*t8-t1*t3-t1*t4-t2*t5-2*t5*t8,
t2*t3*t5+t1*t5^2-t2*t4*t6-t1*t6^2-2*t3*t5-2*t4*t5+2*t3*t6+2*t4*t6,
t2*t4^2+t1*t3*t5+t2*t5^2+t1*t4*t6-2*t3*t4-2*t4^2-2*t5^2+2*t5*t6,
t2*t3*t4+t1*t4*t5+t1*t3*t6+t2*t5*t6-2*t3*t4-2*t4^2-2*t5*t6+2*t6^2,
t7^2*t8^2-t8^4-2*t7^2*t8+4*t8^3+t2^2-4*t2*t8,
t6*t7^2*t8-t6*t8^3-t1*t2*t3-t2^2*t5+t5*t7^2-t6*t7^2-t5*t8^2+3*t6*t8^2+2*t1*t3+2*t1*t4+4*t2*t5-2*t2*t6+2*t5*t8+2*t6*t8,
t5*t7^2*t8-t5*t8^3-t1*t2*t4-t2^2*t6-t5*t7^2+t6*t7^2+3*t5*t8^2-t6*t8^2+2*t1*t3+2*t1*t4-2*t2*t5+4*t2*t6+2*t5*t8+2*t6*t8,
t4*t7^2*t8-t4*t8^3+t2^2*t3+t1*t2*t5-t3*t7^2-t4*t7^2+t3*t8^2+3*t4*t8^2-4*t2*t3-2*t2*t4-2*t1*t5+2*t1*t6-2*t3*t8+2*t4*t8,
t3*t7^2*t8-t3*t8^3+t2^2*t4+t1*t2*t6-t3*t7^2-t4*t7^2+3*t3*t8^2+t4*t8^2-2*t2*t3-4*t2*t4+2*t1*t5-2*t1*t6+2*t3*t8-2*t4*t8,
-2*a*t2*t4*t5*t7-2*a*t2*t3*t6*t7+4*a*t2*t5*t6*t8+2*a*t2*t5^2-4*a*t2*t5*t6+2*a*t2*t6^2+4*a*t1*t2*t7+4*a*t4*t5*t7+4*a*t3*t6*t7+4*a*t2^2*t8-8*a*t5*t6*t8+2*a*t1*t7*t8+2*a*t2*t8^2-4*a*t2^2-4*a*t5^2+8*a*t5*t6-4*a*t6^2-10*a*t1*t7-20*a*t2*t8-4*a*t8^2+10*a*t2+20*a*t8+y1,
-10501*a*t1*t4^2*t6+10501*a*t1*t6^3-10501*a*t1*t6*t7^2+10501*a*t1*t6*t8^2+11007*a*t2^2*t3+11007*a*t1*t2*t5+11007*a*t4*t5*t6+11007*a*t3*t6^2+11007*a*t1*t6*t8-12019*a*t2*t3+9995*a*t2*t4+9995*a*t1*t5+10501*a*t1*t6+9995*a*t6*t7+11007*a*t4*t8+1012*a*t3+1012*a*t4+y2,
-4*a*t2^2*t4*t6-4*a*t1*t2*t6^2+8*a*t2*t3*t6+16*a*t2*t4*t6+8*a*t1*t6^2+4*a*t5*t6*t7-4*a*t3*t6*t8-12*a*t3*t6-12*a*t4*t6+y3,
-10501*a*t5^2*t7^2+10501*a*t6^2*t7^2+11007*a*t2*t7^2*t8+10501*a*t5^2*t8^2-10501*a*t6^2*t8^2-11007*a*t2*t8^3+11007*a*t1*t4*t5-11007*a*t1*t3*t6-11007*a*t3*t6*t7-11007*a*t2*t7^2+11007*a*t5^2*t8+11007*a*t5*t6*t8-11007*a*t6^2*t8+9995*a*t7^2*t8+1012*a*t2*t8^2-9995*a*t8^3-11513*a*t2^2-9995*a*t5^2-11007*a*t5*t6-11007*a*t6^2+11513*a*t7^2+1012*a*t2*t8+8477*a*t8^2-8983*a*t2+8983*a*t8+y4,
-2*a*t1*t4^3+2*a*t1*t4*t6^2-2*a*t1*t4*t7^2-2*a*t2*t6*t8^2+4*a*t1*t2*t3+4*a*t2^2*t5-4*a*t4^2*t5-4*a*t3*t4*t6-2*a*t2*t5*t8+4*a*t2*t6*t8+4*a*t6*t8^2-8*a*t1*t3+2*a*t1*t4-14*a*t2*t5+6*a*t2*t6+8*a*t4*t7+4*a*t5*t8-8*a*t6*t8+12*a*t5-12*a*t6+y5,
-10501*a*t5^2*t7^2+10501*a*t6^2*t7^2-11007*a*t2*t7^2*t8+10501*a*t5^2*t8^2-10501*a*t6^2*t8^2+11007*a*t2*t8^3+11007*a*t1*t4*t5-11007*a*t1*t3*t6+11007*a*t4*t5*t7+11007*a*t2*t7^2+11007*a*t5^2*t8-11007*a*t5*t6*t8-11007*a*t6^2*t8-9995*a*t7^2*t8-1012*a*t2*t8^2+9995*a*t8^3+11513*a*t2^2+11007*a*t5^2+11007*a*t5*t6+9995*a*t6^2-11513*a*t7^2-1012*a*t2*t8-8477*a*t8^2+8983*a*t2-8983*a*t8+y6,
-4*a*t2^2*t4*t6-4*a*t1*t2*t6^2+4*a*t3*t5*t7^2+4*a*t4*t6*t7^2-4*a*t3*t5*t8^2-4*a*t4*t6*t8^2+8*a*t1*t3*t4+8*a*t2*t3*t6+16*a*t2*t4*t6-8*a*t1*t5*t6+8*a*t1*t6^2+4*a*t3*t4*t7+8*a*t3*t5*t8-4*a*t3*t6*t8+8*a*t4*t6*t8+12*a*t3*t5-12*a*t3*t6+y7,
2*a*t1*t2*t3*t7+2*a*t2^2*t5*t7+2*a*t3*t4*t6*t7+2*a*t5*t6^2*t7-2*a*t5*t7^3+4*a*t3*t6^2*t8+2*a*t5*t7*t8^2+2*a*t1*t2*t6+2*a*t3*t5*t6-4*a*t3*t6^2-2*a*t4*t6^2-4*a*t1*t3*t7-4*a*t1*t4*t7-8*a*t2*t5*t7-4*a*t2*t6*t7-4*a*t5*t7*t8-2*a*t6*t7*t8-2*a*t4*t8^2-4*a*t2*t3-4*a*t1*t5-4*a*t1*t6+10*a*t6*t7+2*a*t3*t8+4*a*t4*t8+6*a*t3+6*a*t4+y8,
10501*a*t2^2*t3*t7-10501*a*t3*t4^2*t7+10501*a*t1*t2*t5*t7-10501*a*t4*t5*t6*t7-10501*a*t3*t7^3+11007*a*t5*t6^2*t8+10501*a*t3*t7*t8^2-10501*a*t1*t2*t4-10501*a*t3*t4*t5-10501*a*t4^2*t6+11007*a*t5^2*t6-11007*a*t5*t6^2-9995*a*t2*t3*t7-11007*a*t2*t4*t7+11007*a*t1*t5*t7-11007*a*t1*t6*t7+11007*a*t3*t7*t8+10501*a*t4*t7*t8+10501*a*t6*t8^2+11007*a*t1*t3-11007*a*t1*t4+11007*a*t2*t5+11513*a*t4*t7+10501*a*t5*t8+11007*a*t6*t8-506*a*t5+506*a*t6+y9,
2*a*t2*t4*t5*t7+2*a*t2*t3*t6*t7+4*a*t2*t5*t6*t8-4*a*t1*t3*t5-2*a*t2*t5^2-4*a*t1*t4*t6-4*a*t2*t5*t6-2*a*t2*t6^2+4*a*t1*t2*t7-4*a*t4*t5*t7-4*a*t3*t6*t7-4*a*t2^2*t8-8*a*t5*t6*t8+2*a*t1*t7*t8-2*a*t2*t8^2+4*a*t2^2+4*a*t5^2-8*a*t5*t6+4*a*t6^2-10*a*t1*t7+20*a*t2*t8+4*a*t8^2-10*a*t2-20*a*t8+y10"""
WHEEL = "passagemath-msolve==10.8.13"
SOLVER_SECONDS = 31500
OUT = Path("/kaggle/working")


def meminfo(key):
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith(key + ":"):
            return int(line.split()[1])
    return -1


def rss(pid):
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except OSError:
        return -1
    return -1


def main():
    started = time.time()
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", WHEEL], check=True)
    candidates = [Path(sysconfig.get_paths()[k]) / "sage_wheels/bin/msolve" for k in ("purelib", "platlib")]
    binary = next(p for p in candidates if p.exists())
    binary.chmod(0o755)
    (OUT / "input.ms").write_text(INPUT + "\n")
    threads = os.cpu_count() or 4
    command = [str(binary), "-v", "2", "-t", str(threads), "-e", "1", "-g", "2",
               "-f", str(OUT / "input.ms"), "-o", str(OUT / "gb.out")]
    log = open(OUT / "msolve.log", "w")
    proc = subprocess.Popen(["timeout", str(SOLVER_SECONDS)] + command, stdout=log, stderr=subprocess.STDOUT)
    samples = open(OUT / "samples.tsv", "w")
    samples.write("elapsed_s\tsolver_rss_kib\tmem_available_kib\n")
    stop = threading.Event()

    def sample():
        while not stop.is_set():
            child = subprocess.run(["pgrep", "-P", str(proc.pid)], capture_output=True, text=True).stdout.split()
            kib = max([rss(int(c)) for c in child] + [rss(proc.pid)])
            samples.write(f"{time.time() - started:.0f}\t{kib}\t{meminfo('MemAvailable')}\n")
            samples.flush()
            stop.wait(30)

    sampler = threading.Thread(target=sample, daemon=True)
    sampler.start()
    code = proc.wait()
    stop.set()
    sampler.join()
    log.close()
    gb = OUT / "gb.out"
    if gb.exists() and gb.stat().st_size:
        with open(gb, "rb") as src, gzip.open(OUT / "gb.out.gz", "wb") as dst:
            shutil.copyfileobj(src, dst)
        gb.unlink()
    record = {
        "label": LABEL,
        "wheel": WHEEL,
        "command": command[1:],
        "return_code": code,
        "wall_seconds": round(time.time() - started, 1),
        "peak_child_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "mem_total_kib": meminfo("MemTotal"),
        "cpu_count": threads,
        "machine": platform.processor() or platform.machine(),
        "python": sys.version.split()[0],
    }
    (OUT / "result.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record))


main()
