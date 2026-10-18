"""Remote QX probe of cQASM `reset` on a qubit with weight on |1>, beside the register's phase.

cQASM 3.0 defines `reset q[k]` as measure-and-flip to |0>
(docs/notes/quantum_inspire/cqasm.md), so the rest of the register keeps
its relative phases. qxelarator 0.10.0 instead maps every amplitude pair
(a0x, a1x) over the other qubits' index x to the nonnegative real
sqrt(|a0x|^2 + |a1x|^2) (qx-simulator src/qx/quantum_state.cpp,
QuantumState::update_data_after_reset), which drops those phases. The
probe asks which map the hosted QX emulator applies. Three circuits on two
qubits each end deterministically under both maps:

- ``reset_phase``: q[0] in |1>, q[1] in |->, ``reset q[0]``, then H on q[1].
  The cQASM reset reads q[1] = 1 in every shot; the qxelarator map turns
  q[1] into |+> and reads 0.
- ``control_x``: the same program with X in place of the reset, which both
  maps read as q[1] = 1, so it separates the reset from the rest of the
  program and the register order.
- ``already_zero``: q[0] in |0> beside q[1] in |->; the reset acts as the
  identity under both maps, so q[1] reads 1.

Results are the measurement register, one character per bit with bit 0
rightmost, and ``b = measure q`` puts q[k] on bit k, so the cQASM outcome
of every circuit is "10". One shot off a circuit's outcome refutes that
map for the circuit.

- ``--write DIR`` writes DIR/qx_reset_phase/batch-00 (cases.json and the
  three programs); ``--check DIR`` regenerates them in memory and requires
  the retained bytes.
- ``--sanity RUN_DIR`` requires a collected run's raw shot lists to hold
  ``SHOTS`` two-character outcomes per circuit.
- ``--analyze OUT RUN_DIR`` writes the verdict record; ``--replay OUT``
  recomputes it from the retained run and requires the retained bytes.
- ``--self-test`` runs the analysis on synthetic runs of each map and on a
  run that matches neither.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SERIES = "qx_reset_phase"
BACKEND = "QXsinglenodesimulator"
BACKEND_TYPE_ID = 1
SHOTS = 2048
HEADER = "version 3.0\n\nqubit[2] q\nbit[2] b\n\n"
PROGRAMS = {
    "reset_phase": "X q[0]\nX q[1]\nH q[1]\nreset q[0]\nH q[1]\nb = measure q\n",
    "control_x": "X q[0]\nX q[1]\nH q[1]\nX q[0]\nH q[1]\nb = measure q\n",
    "already_zero": "X q[1]\nH q[1]\nreset q[0]\nH q[1]\nb = measure q\n",
}
# The deterministic outcome of each circuit under each reset map.
LAWS = {
    "reset_phase": {"cqasm": "10", "qxelarator": "00"},
    "control_x": {"cqasm": "10", "qxelarator": "10"},
    "already_zero": {"cqasm": "10", "qxelarator": "10"},
}
SCHEMA = "qx-reset-phase-cases-v1"
ANALYSIS_SCHEMA = "qx-reset-phase-analysis-v1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def batch_files() -> dict[str, bytes]:
    """Every file of the one batch, by name."""
    files = {f"{name}.cq": (HEADER + body).encode() for name, body in PROGRAMS.items()}
    cases = {
        "schema": SCHEMA,
        "family": SERIES,
        "backend": BACKEND,
        "backend_type_id": BACKEND_TYPE_ID,
        "nqubits": 2,
        "shots": SHOTS,
        "dialect": "qx",
        "bit_order": "bit 0 at the rightmost character (QX); b = measure q puts q[k] on bit k",
        "batch": "batch-00",
        "role": (
            "which reset map the hosted QX emulator applies: the cQASM measure-and-flip, which keeps the "
            "register's relative phases, or qxelarator 0.10.0's sqrt(|a0|^2 + |a1|^2) map, which drops them"
        ),
        "preregistered": {
            "falsifier": (
                "reset_phase reading 10 in every shot refutes the qxelarator map on the hosted emulator, and "
                "00 in every shot refutes the cQASM map; one shot of control_x or already_zero off 10 refutes "
                "the program or the register order"
            )
        },
        "circuits": [
            {"file": f"{name}.cq", "sha256": sha256(files[f"{name}.cq"]), "laws": LAWS[name]} for name in PROGRAMS
        ],
    }
    files["cases.json"] = (json.dumps(cases, indent=1) + "\n").encode()
    return files


def write(directory: Path) -> Path:
    batch = directory / SERIES / "batch-00"
    batch.mkdir(parents=True, exist_ok=True)
    for name, data in batch_files().items():
        (batch / name).write_bytes(data)
    return batch


def check(directory: Path) -> None:
    batch = directory / SERIES / "batch-00"
    expected = batch_files()
    found = sorted(path.name for path in batch.iterdir())
    if found != sorted(expected):
        raise SystemExit(f"{batch}: files {found}, expected {sorted(expected)}")
    for name, data in expected.items():
        if (batch / name).read_bytes() != data:
            raise SystemExit(f"{batch / name} differs from the generator")


def shots_of(run: Path) -> dict[str, list[str]]:
    """Each circuit's retained shot list, read from raw/<file>.json."""
    cases = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    return {
        row["file"].removesuffix(".cq"): json.loads((run / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
        for row in cases["circuits"]
    }


def sanity(run: Path) -> None:
    for name, shots in shots_of(run).items():
        if len(shots) != SHOTS or any(not isinstance(s, str) or len(s) != 2 or set(s) - {"0", "1"} for s in shots):
            raise SystemExit(f"{run}: {name} holds {len(shots)} shots, not {SHOTS} two-bit outcomes")


def verdict(counts: dict[str, dict[str, int]]) -> str:
    """The reset map every circuit's shots match, "neither", or "controls_fail"."""
    for name in ("control_x", "already_zero"):
        if counts[name] != {LAWS[name]["cqasm"]: SHOTS}:
            return "controls_fail"
    matched = [
        model for model in ("cqasm", "qxelarator") if counts["reset_phase"] == {LAWS["reset_phase"][model]: SHOTS}
    ]
    return matched[0] if matched else "neither"


def analysis(run: Path) -> dict[str, Any]:
    raw = {name: (run / "raw" / f"{name}.cq.json").read_bytes() for name in PROGRAMS}
    counts = {name: dict(sorted(Counter(shots).items())) for name, shots in shots_of(run).items()}
    return {
        "schema": ANALYSIS_SCHEMA,
        "run": run.resolve().relative_to(ROOT).as_posix() if run.resolve().is_relative_to(ROOT) else str(run),
        "cases_sha256": sha256((run / "cases.json").read_bytes()),
        "raw_sha256": {name: sha256(data) for name, data in raw.items()},
        "shots": SHOTS,
        "counts": counts,
        "laws": LAWS,
        "verdict": verdict(counts),
    }


def encode(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=1, sort_keys=True) + "\n").encode()


def replay(out: Path) -> None:
    retained = json.loads(out.read_text(encoding="utf-8"))
    run = ROOT / retained["run"]
    sanity(run)
    if encode(analysis(run)) != out.read_bytes():
        raise SystemExit(f"{out} differs from the analysis of {retained['run']}")
    print(f"qx reset phase: {retained['run']} replays to verdict {retained['verdict']}")


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="qx-reset-probe-") as scratch:
        batch = write(Path(scratch))
        check(Path(scratch))
        for model, override, expected in (
            ("cqasm", None, "cqasm"),
            ("qxelarator", None, "qxelarator"),
            ("cqasm", ("reset_phase", ["10"] * (SHOTS - 1) + ["00"]), "neither"),
            ("cqasm", ("control_x", ["00"] * SHOTS), "controls_fail"),
        ):
            (batch / "raw").mkdir(exist_ok=True)
            for name in PROGRAMS:
                shots = [LAWS[name][model]] * SHOTS
                if override and override[0] == name:
                    shots = override[1]
                (batch / "raw" / f"{name}.cq.json").write_text(json.dumps(shots), encoding="utf-8")
            sanity(batch)
            found = analysis(batch)["verdict"]
            if found != expected:
                raise SystemExit(
                    f"self-test: {model} shots with {override and override[0]} read {found}, not {expected}"
                )
        (batch / "raw" / "reset_phase.cq.json").write_text(json.dumps(["1"] * SHOTS), encoding="utf-8")
        try:
            sanity(batch)
        except SystemExit:
            pass
        else:
            raise SystemExit("self-test: one-bit outcomes pass the sanity check")
        (batch / "reset_phase.cq").write_bytes(b"version 3.0\n")
        try:
            check(Path(scratch))
        except SystemExit:
            pass
        else:
            raise SystemExit("self-test: an altered program passes --check")
    print("qx reset phase self-test: each map, a mixed run, a failed control, a malformed run and an altered program")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", type=Path, metavar="DIR")
    group.add_argument("--check", type=Path, metavar="DIR")
    group.add_argument("--sanity", type=Path, metavar="RUN_DIR")
    group.add_argument("--analyze", nargs=2, type=Path, metavar=("OUT", "RUN_DIR"))
    group.add_argument("--replay", type=Path, metavar="OUT")
    group.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.write:
        print(write(args.write))
    elif args.check:
        check(args.check)
        print(f"qx reset phase: {args.check / SERIES / 'batch-00'} matches the generator")
    elif args.sanity:
        sanity(args.sanity)
        print(f"qx reset phase: {args.sanity} holds {SHOTS} two-bit shots per circuit")
    elif args.analyze:
        out, run = args.analyze
        sanity(run)
        record = analysis(run)
        out.write_bytes(encode(record))
        print(f"qx reset phase: verdict {record['verdict']}, counts {record['counts']}")
    elif args.replay:
        replay(args.replay)
    else:
        self_test()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
