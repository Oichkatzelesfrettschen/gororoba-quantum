"""Ry emulator construct probe: which part of a cQASM program its reader rejects.

The one Ry program that failed ("Quantum backend error: RSP returned failure:
error interpreting cQASM script", run 2026-10-16T211635Z-Rydberg) declared an
unassigned `bit[9]` register and used H, CNOT and X with no measure statement
and no `INIT` block; libqasm 1.2.1 accepts it, so the emulator's own reader
rejects it. The only program that ran is X on q[0] with no bit register
(run 2026-10-16T213823Z-Rydberg-diagnostic). Each probe circuit below adds
one construct to that baseline on two qubits, so the first failing circuit
names the construct:

    batch-00  x-baseline   X q[0]                         (the form that ran)
              x-bitreg     bit[2] b declared, unassigned  (bit register)
              x-measure    bit[2] b, b = measure q        (measure statement)
    batch-01  h            H q[0]                         (H, which the compiler expands to Rx Rz Rx)
              x-cnot       X q[0], CNOT q[0], q[1]        (CNOT)
              rz-x         Rz(pi/2) q[0], X q[0]          (Rz)
    batch-02  h-cnot       H q[0], CNOT q[0], q[1]        (H with CNOT, no bit register)
              h-cnot-bits  the same with bit[2] b         (the failed program's combination)
              init-h-cnot  asm(Rydberg) INIT block, H, CNOT (the knowledge base's geometry block)

The Ry emulator measures every qubit at the end and writes qubit 0 as the
leftmost character (backends.md, ry-emulator.md), so the expected outcome
strings below read q[0] first. Every batch holds three circuits at 1024
shots, the backend's maximum; qi_platform.py submit applies the hardware
batch rule to it because the API flags it `is_hardware`.

--write DIR writes DIR/ry_probe/batch-NN/ (cases.json and the circuits);
--check DIR regenerates and compares bytes; --analyze OUT RUN_DIR... writes,
per circuit, its completion or failure message and the total-variation
distance of its counts from the expected distribution; --analyze --replay
compares OUT with the recomputation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SHOTS = 1024
SCHEMA = "qi-ry-probe-cases-v1"
DIRECTORY = "ry_probe"

HEADER = "version 3.0\n\nqubit[2] q\n"
INIT = "asm(Rydberg) '''\n    INIT(0, 0) q[0]\n    INIT(0, 1) q[1]\n'''\n"

# (name, body after the qubit declaration, construct it adds, expected outcome distribution, q[0] leftmost)
CIRCUITS: tuple[tuple[str, str, str, dict[str, float]], ...] = (
    ("x-baseline", "\nX q[0]\n", "none: the program that ran", {"10": 1.0}),
    ("x-bitreg", "bit[2] b\n\nX q[0]\n", "an unassigned bit register", {"10": 1.0}),
    ("x-measure", "bit[2] b\n\nX q[0]\nb = measure q\n", "a measure statement", {"10": 1.0}),
    ("h", "\nH q[0]\n", "H", {"00": 0.5, "10": 0.5}),
    ("x-cnot", "\nX q[0]\nCNOT q[0], q[1]\n", "CNOT", {"11": 1.0}),
    ("rz-x", "\nRz(1.5707963267948966) q[0]\nX q[0]\n", "Rz", {"10": 1.0}),
    ("h-cnot", "\nH q[0]\nCNOT q[0], q[1]\n", "H with CNOT", {"00": 0.5, "11": 0.5}),
    ("h-cnot-bits", "bit[2] b\n\nH q[0]\nCNOT q[0], q[1]\n", "H, CNOT and a bit register", {"00": 0.5, "11": 0.5}),
    (
        "init-h-cnot",
        "\n" + INIT + "\nH q[0]\nCNOT q[0], q[1]\n",
        "an INIT block with H and CNOT",
        {"00": 0.5, "11": 0.5},
    ),
)
BATCHES = (CIRCUITS[0:3], CIRCUITS[3:6], CIRCUITS[6:9])


def source(body: str) -> str:
    return HEADER + body


def cases() -> dict[str, dict[str, Any]]:
    """Every batch directory's files: name -> {file name: bytes as text}."""
    out: dict[str, dict[str, Any]] = {}
    for index, batch in enumerate(BATCHES):
        files = {f"{name}.cq": source(body) for name, body, _, _ in batch}
        manifest = {
            "schema": SCHEMA,
            "backend": "Rydberg",
            "backend_type_id": 5,
            "nqubits": 2,
            "shots": SHOTS,
            "purpose": (
                "Ry construct probe: each circuit adds one construct to the X-only program that ran, so the "
                "first failing circuit names what the emulator's reader rejects. Expected outcomes read q[0] "
                "as the leftmost character."
            ),
            "circuits": [
                {
                    "file": f"{name}.cq",
                    "construct": construct,
                    "expected": expected,
                    "sha256": hashlib.sha256(files[f"{name}.cq"].encode()).hexdigest(),
                }
                for name, _, construct, expected in batch
            ],
        }
        files["cases.json"] = json.dumps(manifest, indent=1) + "\n"
        out[f"batch-{index:02d}"] = files
    return out


def write(root: Path) -> None:
    for batch, files in cases().items():
        directory = root / DIRECTORY / batch
        directory.mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            (directory / name).write_text(text, encoding="utf-8")


def check(root: Path) -> None:
    for batch, files in cases().items():
        directory = root / DIRECTORY / batch
        present = sorted(p.name for p in directory.iterdir())
        if present != sorted(files):
            raise SystemExit(f"{directory}: files {present} differ from {sorted(files)}")
        for name, text in files.items():
            if (directory / name).read_text(encoding="utf-8") != text:
                raise SystemExit(f"{directory / name} differs from its regeneration")
    print(f"ry probe: {len(CIRCUITS)} circuits in {len(BATCHES)} batches match their regeneration")


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    rows = []
    for run in run_dirs:
        case = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        results = json.loads((run / "results.json").read_text(encoding="utf-8"))
        jobs = {row["file"]: row for row in results["jobs"]}
        for circuit in case["circuits"]:
            job = jobs[circuit["file"]]
            status = job["job"]["status"]
            row: dict[str, Any] = {
                "run": run.name,
                "file": circuit["file"],
                "construct": circuit["construct"],
                "status": status,
                "message": job["job"].get("message") or "",
            }
            raw = run / "raw" / f"{circuit['file']}.json"
            if status == "completed" and raw.exists():
                shots = json.loads(raw.read_text(encoding="utf-8"))
                total = len(shots)
                counts: dict[str, int] = {}
                for shot in shots:
                    counts[shot] = counts.get(shot, 0) + 1
                keys = set(counts) | set(circuit["expected"])
                row["shots"] = total
                row["counts"] = dict(sorted(counts.items()))
                row["tv_from_expected"] = round(
                    0.5 * sum(abs(counts.get(k, 0) / total - circuit["expected"].get(k, 0.0)) for k in keys), 6
                )
            rows.append(row)
    rejected = [row["construct"] for row in rows if row["status"] != "completed"]
    return {"schema": "qi-ry-probe-analysis-v1", "circuits": rows, "rejected_constructs": rejected}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--analyze", type=Path, nargs="+", metavar=("OUT", "RUN_DIR"))
    parser.add_argument("--replay", action="store_true", help="with --analyze: compare OUT with the recomputation")
    args = parser.parse_args()
    if args.write:
        write(args.write)
        return 0
    if args.check:
        check(args.check)
        return 0
    out, *runs = args.analyze
    text = json.dumps(analyze(runs), indent=1) + "\n"
    if args.replay:
        if out.read_text(encoding="utf-8") != text:
            raise SystemExit(f"{out} differs from its recomputation")
        print(f"{out}: reproduces")
        return 0
    out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
