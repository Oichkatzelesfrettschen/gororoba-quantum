"""Replay the truncated-rank certificates of the A_5 fiber registry.

    replay.py plan            write manifest.json from ../claims.json and ../certificates.jsonl
    replay.py run OUTDIR [--budget-gb G] [--only SUBSTRING]

`plan` picks, for every fiber, prime and degree that a truncated rank certifies, the record with the smallest N; at
that N it prefers quotient mode, whose memory peak is lower. Every entry replays on engine/fiber_rank_v8.py: its
raw path is the v7 raw path, and its quotient export is byte-identical to v7 on the gate inputs. The memory estimate
is the measured peak of the original run where `PEAKS_KIB` holds one, else 1.3 times the engine's own preflight
estimate, at least 1 GiB.

`run` first checks the engine bytes against ENGINE_SHA16 and every manifest header against its recorded sha256, then
starts entries largest first while the sum of the running scopes' MemoryMax stays within --budget-gb. Each run executes
in its own systemd user scope with MemoryMax = 1.5 x estimate + 5 GiB (the engine's default 4 GiB table cache and a
margin) and no swap, under a deadline of three times the original wall time plus 600 s; the engine's --max-gb gets the
same cap. An interrupted runner terminates the process groups it started. Each run writes OUTDIR/<id>.out;
engine/gate_record.py binds it to the engine sha256, header sha256, d, N and the expected rank, and the bound record
joins OUTDIR/replay.jsonl. OUTDIR/summary.json counts reproduced and failed entries and records any mode change from the
original certificate. A replay is a fresh check by the successor engine, not a byte replay of the original run, and it
reproduces lower bounds only; the upper bound HF(k[y]/K2, d) and K2 contained in L rest on k2-hilbert.jsonl and the
degree-2 membership receipts.
"""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REG = HERE.parent
ENGINE = HERE / "engine" / "fiber_rank_v8.py"
CHECK = HERE / "engine" / "gate_record.py"
ENGINE_SHA16 = "ea56c9cab5baf1d9"

# Measured peak RSS of the original certifying runs, KiB, keyed by (fiber, prime, d, N, mode); the resources files of
# the run trees carry them.
PEAKS_KIB = {
    ("Iso", 32009, 5, 16, "raw"): 11260540,
    ("Iso", 32029, 5, 16, "raw"): 11491672,
    ("Iso", 32009, 4, 13, "raw"): 2620088,
    ("Iso", 32029, 4, 13, "raw"): 2614124,
    ("W8 -> N-", 32009, 4, 13, "raw"): 12547844,
    ("W8 -> N-", 32029, 4, 13, "raw"): 12556708,
    ("W8 -> N-", 32029, 3, 10, "raw"): 1643500,
    ("W8 -> N-", 32009, 3, 10, "quotient"): 4020912,
    ("E8-bar -> N-", 32009, 3, 11, "quotient"): 2528352,
    ("E8-bar -> N+", 32029, 3, 11, "quotient"): 2077208,
    ("E8-bar -> N-", 32029, 3, 11, "raw"): 34417700,
    ("E8-bar -> N+", 32009, 3, 11, "raw"): 34431920,
    ("X-", 32009, 5, 19, "quotient"): 5237296,
    ("E8-bar -> VB", 32009, 5, 16, "quotient"): 2480048,
    ("W8 -> N-", 32029, 3, 10, "quotient"): 1842136,
    ("Iso", 32009, 3, 10, "quotient"): 266136,
    ("E8-bar -> N-", 32009, 2, 8, "quotient"): 214348,
}
# A raw-only certificate above this peak replays in quotient mode, whose peak at E8-bar degree 3, N = 11 is 2.5 GB
# against 34 GB raw; equal ranks across the two modes are part of the check.
RAW_TO_QUOTIENT_GB = 16.0


def plan() -> int:
    claims = json.loads((REG / "claims.json").read_text())
    certs = [json.loads(ln) for ln in (REG / "certificates.jsonl").read_text().splitlines() if ln.strip()]
    entries = []
    for f in claims["fibers"]:
        for g in f["degrees"]:
            if g["status"] != "certified":
                continue
            cand = [
                c for c in certs if c["fiber"] == f["fiber"] and c["prime"] == f["prime"] and c["record"]["d"] == g["d"]
            ]
            if not cand:
                continue
            n_min = min(c["record"]["N"] for c in cand)
            at = [c for c in cand if c["record"]["N"] == n_min]
            pick = next((c for c in at if c["record"].get("mode") == "quotient"), at[0])
            r = pick["record"]
            mode = original_mode = r.get("mode", "raw")
            key = (f["fiber"], f["prime"], g["d"], n_min, mode)
            if key in PEAKS_KIB:
                est_gb, src = PEAKS_KIB[key] / 2**20, "measured peak"
            else:
                est_gb, src = max(1.0, 1.3 * r.get("preflight_bytes", 0) / 2**30), "1.3 x preflight estimate"
            if mode == "raw" and est_gb > RAW_TO_QUOTIENT_GB:
                mode = "quotient"
                q = [
                    v
                    for k, v in PEAKS_KIB.items()
                    if k[0].startswith("E8-bar -> N") and k[2:] == (g["d"], n_min, "quotient")
                ]
                est_gb, src = (
                    max(q) / 2**20 * 1.2,
                    "1.2 x measured quotient peak of the E8-bar -> N class at this d and N",
                )
            slug = f"{f['fiber']}-{f['prime']}-d{g['d']}-N{n_min}-{mode}".replace(" -> ", "-").replace("+", "p")
            entries.append(
                {
                    "id": slug.replace("-bar", "").replace(" ", ""),
                    "fiber": f["fiber"],
                    "prime": f["prime"],
                    "d": g["d"],
                    "N": n_min,
                    "mode": mode,
                    "original_mode": original_mode,
                    "expected_r_N": g["k2_count"],
                    "header": pick["header_input"],
                    "header_sha256_16": r["header_sha256_16"],
                    "original_engine": r.get("engine_sha256_16"),
                    "original_seconds": (r.get("seconds") or {}).get("total"),
                    "original_source": pick["source"],
                    "est_gb": round(est_gb, 2),
                    "est_source": src,
                }
            )
    entries.sort(key=lambda e: -e["est_gb"])
    (HERE / "manifest.json").write_text(
        json.dumps({"schema": "a5-fiber-replay-v1", "entries": entries}, indent=1) + "\n"
    )
    for e in entries:
        print(f"{e['id']:42s} {e['est_gb']:6.1f} GB  {e['original_seconds']} s")
    print(f"{len(entries)} entries, serial seconds {sum(e['original_seconds'] or 0 for e in entries):.0f}")
    return 0


def header_path(rel: str) -> Path:
    p = REG / "working" / rel
    return p if p.exists() else REG / rel


def preflight(entries: list[dict]) -> None:
    """Refuse to launch unless the engine and every manifest header still have their recorded bytes."""
    import hashlib

    if hashlib.sha256(ENGINE.read_bytes()).hexdigest()[:16] != ENGINE_SHA16:
        raise SystemExit(f"{ENGINE.name} differs from the replay engine {ENGINE_SHA16}")
    for e in entries:
        got = hashlib.sha256(header_path(e["header"]).read_bytes()).hexdigest()[:16]
        if got != e["header_sha256_16"]:
            raise SystemExit(f"{e['id']}: header {e['header']} has sha256 {got}, manifest {e['header_sha256_16']}")


def cap_gb(e: dict) -> float:
    return round(e["est_gb"] * 1.5 + 5, 1)


def launch(e: dict, outdir: Path, py: str) -> subprocess.Popen:
    """One engine run in its own systemd user scope (MemoryMax, no swap) under a wall-clock deadline."""
    cap = cap_gb(e)
    deadline = int(3 * (e["original_seconds"] or 600) + 600)
    cmd = [py, str(ENGINE), str(header_path(e["header"])), str(e["d"]), str(e["N"])]
    if e["mode"] == "quotient":
        cmd += ["--quotient", "--max-gb", str(cap)]
    scope = ["systemd-run", "--user", "--scope", "-q", "-p", f"MemoryMax={cap}G", "-p", "MemorySwapMax=0"]
    full = [*scope, "timeout", "-k", "30", str(deadline), *cmd]
    out = open(outdir / f"{e['id']}.out", "w")
    err = open(outdir / f"{e['id']}.err", "w")
    return subprocess.Popen(full, stdout=out, stderr=err, stdin=subprocess.DEVNULL, start_new_session=True)


def run(outdir: Path, budget: float, only: str | None) -> int:
    entries = json.loads((HERE / "manifest.json").read_text())["entries"]
    if only:
        entries = [e for e in entries if only in e["id"]]
    preflight(entries)
    outdir.mkdir(parents=True, exist_ok=True)
    py = os.environ.get("PYTHON", sys.executable)
    pending, done = list(entries), []
    running: dict[str, tuple[subprocess.Popen, dict, float]] = {}
    if any(cap_gb(e) > budget for e in pending):
        raise SystemExit(
            "an entry's estimate exceeds the budget: " + ", ".join(e["id"] for e in pending if cap_gb(e) > budget)
        )
    try:
        while pending or running:
            used = sum(cap_gb(running[k][1]) for k in running)
            for e in list(pending):
                if used + cap_gb(e) <= budget:
                    running[e["id"]] = (launch(e, outdir, py), e, time.time())
                    pending.remove(e)
                    used += cap_gb(e)
            time.sleep(5)
            for k in list(running):
                proc, e, t0 = running[k]
                if proc.poll() is None:
                    continue
                del running[k]
                chk = subprocess.run(
                    [py, str(CHECK), str(outdir / f"{k}.out"), str(ENGINE), str(header_path(e["header"])),
                     str(e["d"]), str(e["N"]), str(e["expected_r_N"])],
                    capture_output=True,
                    text=True,
                )  # fmt: skip
                ok = proc.returncode == 0 and chk.returncode == 0
                if ok:
                    with open(outdir / "replay.jsonl", "a") as fh:
                        fh.write(chk.stdout.strip() + "\n")
                done.append(
                    {"id": k, "ok": ok, "engine_exit": proc.returncode, "seconds": round(time.time() - t0, 1),
                     "mode": e["mode"], "original_mode": e.get("original_mode", e["mode"])}
                )  # fmt: skip
                print(json.dumps(done[-1]), flush=True)
    finally:
        for proc, _e, _t in running.values():
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
    summary = {
        "reproduced": sum(1 for d in done if d["ok"]),
        "failed": [d["id"] for d in done if not d["ok"]],
        "runs": done,
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return 0 if not summary["failed"] else 1


def main() -> int:
    args = sys.argv[1:]
    if args[:1] == ["plan"]:
        return plan()
    if args[:1] == ["run"] and len(args) >= 2:
        budget = float(args[args.index("--budget-gb") + 1]) if "--budget-gb" in args else 48.0
        only = args[args.index("--only") + 1] if "--only" in args else None
        return run(Path(args[1]), budget, only)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
