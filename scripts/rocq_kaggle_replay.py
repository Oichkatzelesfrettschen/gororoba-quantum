"""Replay the retained Rocq proof receipts on a Kaggle kernel or a CI runner under the pinned toolchain.

The replay scripts under docs/evidence run only where a pinned toolchain
exists. A Kaggle CPU kernel builds one from the pinned opam repository in a fresh
temporary OPAMROOT. Opam (Ubuntu's package, sandboxing off) creates a switch on
ocaml-base-compiler OCAML and installs rocq-runtime, rocq-core and
rocq-stdlib at ROCQ_PACKAGES, then this script requires ``rocq --version`` to
equal docs/evidence/c881_exhaustive/toolchain.txt before any replay runs.
open_gororoba, whose sources three replays hash, is cloned at the commit
``--gororoba-commit`` names.

The ci.yml job rocq-replay supplies the toolchain and the checkout itself:
``--rocq PATH`` skips the build and keeps the version equality,
``--gororoba-root DIR`` skips the clone and requires the checkout's HEAD to
equal ``--gororoba-commit``, and ``--only NAME...`` selects replays by name
(formal_certificates, c881_exhaustive, stiefel_witness, folding_proofs,
TargetFlipN21; the default is the Kaggle set).

Independent replays run through parallel.ordered_map with the detected CPU
allowance capped by GOROROBA_WORKERS. Each replay uses separate temporary
proof storage and returns its record in the requested order. Each replay runs
unchanged, with ROCQ pointing at the built executable:

- formal_certificates/replay_rocq.sh (repository proofs and receipts),
- c881_exhaustive/replay_rocq.sh and stiefel_witness/replay_rocq.sh
  (GOROROBA_ROOT set to the clone),
- folding_proofs/replay_rocq.sh when ``--folding`` is given, whose complete
  stdout must equal the retained folding_proofs/rocq_replay.log,
- the TargetFlipN21 procedure of AGENTS.md: ``rocq compile -q -w +all``, no
  warning, ``rocq check -silent -o``.

``--out FILE`` receives the toolchain identity, the build and replay wall
times, and each replay's exit code, every output line carrying ``Warning:``
and the output tail. The run passes only when
every replay exits 0. Push it with scripts/kaggle_run.py --machine cpu and
--include for ci/rocq_toolchain.pin, gororoba_quantum/parallel.py, the proofs/
and docs/evidence/ directories, and the result files
the formal certificates hash.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402

TOOLCHAIN = ROOT / "docs/evidence/c881_exhaustive/toolchain.txt"
OCAML = "ocaml-base-compiler.5.5.1"
ROCQ_PACKAGES = ("rocq-runtime.9.3.0", "rocq-core.9.3.0", "rocq-stdlib.9.2.0")
SYSTEM_PACKAGES = ("opam", "m4", "pkg-config", "libgmp-dev", "git", "make", "gcc", "unzip", "bubblewrap")
GOROROBA_URL = "https://github.com/Oichkatzelesfrettschen/open_gororoba.git"
SWITCH = "rocq-9.3"
REPLAYS = ("formal_certificates", "c881_exhaustive", "stiefel_witness")
SELECTABLE = (*REPLAYS, "folding_proofs", "TargetFlipN21")


def run(
    cmd: list[str], env: dict[str, str] | None = None, cwd: Path | None = None, retained_log: Path | None = None
) -> dict[str, Any]:
    """Run cmd; warning lines are read from the complete output before the tail is cut.

    With retained_log, the complete stdout must equal that file byte for byte,
    or the entry's return code is 1.
    """
    start = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd)
    output = proc.stdout + proc.stderr
    entry = {
        "command": " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else ""),
        "returncode": proc.returncode,
        "seconds": round(time.time() - start, 1),
        "warning_lines": [line for line in output.splitlines() if "arning:" in line],
        "tail": output[-2500:],
    }
    if retained_log is not None:
        entry["matches_retained_log"] = proc.stdout == retained_log.read_text(encoding="utf-8")
        if not entry["matches_retained_log"]:
            entry["returncode"] = entry["returncode"] or 1
    return entry


def build_toolchain(steps: list[dict[str, Any]]) -> Path:
    pin = dict(line.split("=", 1) for line in (ROOT / "ci/rocq_toolchain.pin").read_text().splitlines())
    env = dict(
        os.environ,
        OPAMYES="1",
        OPAMROOTISOK="1",
        OPAMJOBS=str(parallel.workers()),
        OPAMROOT=tempfile.mkdtemp(prefix="quantum-rocq-opam-"),
    )
    for cmd in (
        ["apt-get", "update", "-qq"],
        ["apt-get", "install", "-y", "-qq", *SYSTEM_PACKAGES],
        [
            "opam",
            "init",
            "--bare",
            "--disable-sandboxing",
            "-n",
            "default",
            "https://github.com/ocaml/opam-repository.git#" + pin["opam_repository"],
        ],
        ["opam", "switch", "create", SWITCH, OCAML],
        ["opam", "install", "--switch", SWITCH, *ROCQ_PACKAGES],
    ):
        steps.append(run(cmd, env=env))
        if steps[-1]["returncode"]:
            raise SystemExit(f"toolchain step failed: {steps[-1]['command']}\n{steps[-1]['tail']}")
    prefix = subprocess.run(
        ["opam", "var", "--switch", SWITCH, "bin"], capture_output=True, text=True, env=env, check=True
    ).stdout.strip()
    return Path(prefix) / "rocq"


def target_flip(rocq: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch)
        (work / "TargetFlipN21.v").write_bytes((ROOT / "proofs/TargetFlipN21.v").read_bytes())
        compiled = run([str(rocq), "compile", "-q", "-w", "+all", "TargetFlipN21.v"], cwd=work)
        if compiled["returncode"] == 0 and compiled["warning_lines"]:
            compiled["returncode"] = 1
        checked = run([str(rocq), "check", "-silent", "-o", "TargetFlipN21"], cwd=work)
    return {
        "returncode": compiled["returncode"] or checked["returncode"],
        "seconds": round(compiled["seconds"] + checked["seconds"], 1),
        "warning_lines": compiled["warning_lines"] + checked["warning_lines"],
        "tail": compiled["tail"] + checked["tail"],
    }


def replay_entry(arguments: tuple[str, Path, Path]) -> tuple[str, dict[str, Any]]:
    """Run one independent bundle in its own temporary proof storage."""
    name, rocq, gororoba = arguments
    if name == "TargetFlipN21":
        return name, target_flip(rocq)
    evidence = ROOT / "docs/evidence" / name
    retained = evidence / "rocq_replay.log" if name == "folding_proofs" else None
    env = dict(os.environ, ROCQ=str(rocq), GOROROBA_ROOT=str(gororoba))
    return name, run(["sh", str(evidence / "replay_rocq.sh")], env=env, cwd=ROOT, retained_log=retained)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--gororoba-commit", required=True)
    parser.add_argument("--folding", action="store_true", help="also replay folding_proofs")
    parser.add_argument("--rocq", type=Path, help="use this rocq executable and skip the opam build")
    parser.add_argument("--gororoba-root", type=Path, help="use this open_gororoba checkout and skip the clone")
    parser.add_argument("--only", nargs="+", choices=SELECTABLE, help="replay only these entries")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    steps: list[dict[str, Any]] = []
    rocq = args.rocq if args.rocq is not None else build_toolchain(steps)
    version = subprocess.run([str(rocq), "--version"], capture_output=True, text=True, check=True).stdout
    expected = TOOLCHAIN.read_text(encoding="utf-8")
    if version != expected:
        raise SystemExit(f"toolchain reports {version!r}, expected {expected!r}")
    if args.gororoba_root is not None:
        gororoba = args.gororoba_root
        head = subprocess.run(
            ["git", "-C", str(gororoba), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        if head != args.gororoba_commit:
            raise SystemExit(f"open_gororoba HEAD {head} differs from --gororoba-commit {args.gororoba_commit}")
    else:
        gororoba = Path(tempfile.mkdtemp()) / "open_gororoba"
        steps.append(run(["git", "clone", "-q", "--filter=blob:none", GOROROBA_URL, str(gororoba)]))
        steps.append(run(["git", "-C", str(gororoba), "checkout", "-q", args.gororoba_commit]))
        if steps[-1]["returncode"]:
            raise SystemExit(f"open_gororoba checkout failed\n{steps[-1]['tail']}")
    selected = args.only or (*REPLAYS, *(("folding_proofs",) if args.folding else ()), "TargetFlipN21")
    replays = dict(parallel.ordered_map(replay_entry, [(name, rocq, gororoba) for name in selected], min_items=2))
    result = {
        "schema": "rocq-kaggle-replay-v2",
        "toolchain": version,
        "opam_packages": [OCAML, *ROCQ_PACKAGES],
        "open_gororoba_commit": args.gororoba_commit,
        "build_steps": steps,
        "replays": replays,
        "passed": all(entry["returncode"] == 0 for entry in replays.values()),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({name: entry["returncode"] for name, entry in replays.items()}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
